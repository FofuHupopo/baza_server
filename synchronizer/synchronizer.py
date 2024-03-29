import os
import requests
from sqlalchemy.orm import Session
from sqlalchemy import or_
from pathlib import Path
from slugify import slugify

import models
from models import engine
from moy_sklad import MoySklad


class NoBundleComplectException(Exception):
    pass


class MoySkaldSynchronizer(MoySklad):
    def __init__(self, django_media_path: Path, product_media_path: Path, root_path: str, only_valid: bool=True) -> None:
        self.django_media_path = django_media_path
        self.product_media_path = product_media_path
        self.root_path = root_path
        self.default_product_image = "product_images/Заглушка фото карточки товара.jpg"
        self.only_valid = only_valid
    
    def sync_all(self):
        self.sync_products()
        self.sync_bundles()

    def sync_products(self):
        response = MoySkaldSynchronizer.moysklad_request()
        
        products_count = len(response["rows"])
    
        synchronized_counter = 0
        
        for ind, product in enumerate(response["rows"], start=1):
                status = self._sync_product(product)
                
                if status:
                    print(f"{product['name']} synchronized ({ind}/{products_count})")
                    synchronized_counter += 1
                                
        print(f"Total syncronized: {synchronized_counter}")
    
    def sync_product_by_id(self, product_id: str):
        response = self.moysklad_request("PRODUCT_DETAIL", [product_id])

        self._sync_product(response)

    def _sync_product(self, product: dict):
        if not self._checking_product_sync(product):
            return False

        product_path = self._sync_product_path(product)
        
        if not product_path:
            return
        
        product_instance = self._sync_product_detail(product, product_path)
        self._sync_product_modifications(product["id"])
        
        return True

    def _checking_product_sync(self, product: dict) -> bool:        
        if product["images"]["meta"]["size"] < 0:
            return False
        
        response = MoySkaldSynchronizer.moysklad_request("MODIFICATIONS", [product["id"]])
        if not response["rows"]:
            return False

        return True

    def _sync_product_path(self, product: dict):
        with Session(engine) as session:
            full_path = product["pathName"].split("/")

            if not full_path or full_path[0].lower() != self.root_path:
                return

            full_path = full_path[1:]
            
            full_path[0] = {
                "ЖЕНЩИНЫ": "woman",
                "МУЖЧИНЫ": "man",
                "ДЕТИ": "children"                
            }.get(full_path[0], full_path[0])

            last_path = None
            for ind, path in enumerate(full_path):
                slug = slugify(" ".join(full_path[:ind + 1]))

                instances = session.query(
                    models.ProductPathModel
                ).filter(
                    (models.ProductPathModel.name == path) |
                    (models.ProductPathModel.slug == slug)
                )

                for inst in instances:
                    inst_slug = inst.full_path().lower()

                    if inst_slug in ("женщины", "мужчины", "дети") or inst_slug == "/".join(full_path[:ind + 1]).lower():
                        instance = inst
                        break
                else:
                    instance = None

                if instance:
                    last_path = instance
                    continue
                
                if path in ("woman", "man", "children"):
                    instance = models.ProductPathModel(
                        name={
                            "woman": "ЖЕНЩИНЫ",
                            "man": "МУЖЧИНЫ",
                            "children": "ДЕТИ"
                        }.get(path),
                        slug=slugify(" ".join(full_path[:ind + 1]))
                    )
                else:
                    instance = models.ProductPathModel(
                        name=path,
                        slug=slugify(" ".join(full_path[:ind + 1]))
                    )

                if last_path:
                    instance.parent_id = last_path.id

                session.add(instance)
                session.commit()

                last_path = instance

        return last_path

    def _sync_product_detail(self, product: dict, product_path: models.ProductPathModel):
        with Session(engine) as session:
            session.add(product_path)

            category_name = product_path.name        
            category_instance = session.query(models.ProductCategoryModel).filter(
                models.ProductCategoryModel.name == category_name
            ).first()
            
            if not category_instance:
                category_instance = models.ProductCategoryModel(
                    name=category_name
                )
                
                session.add(category_instance)
    
            product_instance: models.ProductModel = session.query(models.ProductModel).filter(
                models.ProductModel.product_id == product["id"]
            ).first()
            
            if not product_instance:
                product_instance = models.ProductModel()
                product_instance.visible = False
                session.add(product_instance)
            
            product_instance.product_id = product["id"]
            product_instance.name = product["name"]
            product_instance.code = product["code"]
            product_instance.description = product.get("description", "")
            product_instance.path_id = product_path.id
            
            product_instance.price = int(product["salePrices"][0]["value"])
            
            if len(product["salePrices"]) > 1:
                product_instance.old_price = int(product["salePrices"][1]["value"])

            product_instance.category_id = category_instance.id
            product_instance.image = self._sync_product_image(product["id"])

            session.add(product_instance)
            session.commit()

        return product_instance
        
    def _sync_product_image(self, product_id: str) -> str | None:
        response = MoySkaldSynchronizer.moysklad_request("PRODUCT_IMAGES", [product_id])
        
        if not response["rows"]:
            return self.default_product_image

        image_data = response["rows"][0]

        image_response = requests.get(
            image_data["meta"]["downloadHref"],
            headers=MoySkaldSynchronizer.HEADERS
        )
        image_filename = image_data["filename"]

        image_folder_path = self.django_media_path / self.product_media_path / product_id
        
        if not image_folder_path.exists():
            os.makedirs(image_folder_path)
        
        image_path = image_folder_path / image_filename
        
        with open(image_path, "wb") as file:
            file.write(image_response.content)

        return str(self.product_media_path / product_id / image_filename)
    
    def _sync_product_modifications(self, product_id: str) -> None:
        response = MoySkaldSynchronizer.moysklad_request("MODIFICATIONS", [product_id])
        
        for modification in response["rows"]:
            with Session(engine) as session:
                product_instance = session.query(models.ProductModel).filter(
                    models.ProductModel.product_id == product_id
                ).first()

                color_name = "Стандартный"
                size_name = "OS"

                for characteristic in modification["characteristics"]:
                    if characteristic["name"].lower() == "цвет":
                        color_name = characteristic["value"]
                        
                    if characteristic["name"].lower() == "размер":
                        size_name = characteristic["value"]


                color_instance = session.query(models.ProductColorModel).filter(
                    models.ProductColorModel.name == color_name
                ).first()
                
                if not color_instance:
                    color_instance = models.ProductColorModel(
                        name=color_name,
                        eng_name=slugify(color_name)
                    )

                    session.add(color_instance)
                    session.commit()
                
                color_instance_id = color_instance.id


                size_instance = session.query(models.ProductSizeModel).filter(
                    models.ProductSizeModel.name == size_name
                ).first()
                
                if not size_instance:
                    size_instance = models.ProductSizeModel(
                        name=size_name
                    )
                    
                    session.add(size_instance)
                    session.commit()
                
                size_instance_id = size_instance.id


                modification_instance = session.query(models.ProductModificationModel).filter(
                    models.ProductModificationModel.product_id == product_instance.id,
                    models.ProductModificationModel.modification_id == modification["id"]
                ).first()

                if not modification_instance:
                    modification_instance = models.ProductModificationModel(
                        product=product_instance,
                        modification_id=modification["id"],
                        visible = False
                    )

                modification_assortment = self._sync_product_modification_assortment(modification_instance.modification_id)
                modification_instance.weight = modification_assortment["weight"]
                modification_instance.quantity = modification_assortment["quantity"]

                modification_instance.color_id = color_instance_id
                modification_instance.size_id = size_instance_id
                modification_instance.slug = slugify(f"{product_instance.name} {product_instance.code} {color_instance.name} {size_instance.name}")

                session.add(modification_instance)
                session.commit()

                self._add_standart_product_modification_image(product_instance.id, modification_instance)
        
    def _sync_product_modification_assortment(self, modification_id: str):
        response = MoySkaldSynchronizer.moysklad_request("ASSORTMENT", [modification_id])
        return {
            "quantity": int(response["rows"][0].get("quantity", 0)),
            "weight": int(response["rows"][0].get("weight", 0)),
        }
                
    def _add_standart_product_modification_image(self, product_id: str, modification_instance: models.ProductModificationModel) -> None:
        # if self._sync_product_modification_images(product_id, modification_instance):
        #     return

        with Session(engine) as session:
            color_id: int = modification_instance.color_id
            
            product_color_images_instance = session.query(models.ProductColorImagesModel).filter(
                models.ProductColorImagesModel.product_id == product_id,
                models.ProductColorImagesModel.color_id == color_id
            ).first()
            
            if not product_color_images_instance:
                product_color_images_instance = models.ProductColorImagesModel(
                    product_id=product_id,
                    color_id=color_id
                )
                
                session.add(product_color_images_instance)
                session.commit()
            
            images = session.query(models.ColorImageModel).filter(
                models.ColorImageModel.product_color_id == product_color_images_instance.id
            ).first()
            
            if not images:
                image = models.ColorImageModel(
                    product_color_id=product_color_images_instance.id,
                    image=self.default_product_image
                )
                
                session.add(image)
                session.commit()

    def _sync_product_modification_images(self, product_id: str, modification_instance: models.ProductModificationModel) -> bool:
        with Session(engine) as session:
            response = MoySkaldSynchronizer.moysklad_request("MODIFICATION_IMAGES", [modification_instance.modification_id])
            
            if not response["rows"]:
                return False
            
            for image in response["rows"]:
                image_response = requests.get(
                    image["meta"]["downloadHref"],
                    headers=MoySkaldSynchronizer.HEADERS
                )
                image_filename = image["filename"]

                image_folder_path = self.django_media_path / self.product_media_path / product_id / str(modification_instance.id)
                
                if not image_folder_path.exists():
                    os.makedirs(image_folder_path)
                
                image_path = image_folder_path / image_filename
                
                with open(image_path, "wb") as file:
                    file.write(image_response.content)
                    
                django_image_path = str(self.product_media_path / product_id / str(modification_instance.id) / image_filename)
                
                image_instance = session.query(models.ProductModificationImageModel).filter(
                    models.ProductModificationImageModel.image == django_image_path
                ).first()

                if not image_instance:
                    image_instance = models.ProductModificationImageModel(
                        product_modification_id=modification_instance.id,
                        image=django_image_path
                    )

                    session.add(image_instance)
                    session.commit()

        return True

    def sync_bundles(self):
        response = MoySkaldSynchronizer.moysklad_request("BUNDLES")
        
        bundles_count = len(response["rows"])
    
        for ind, bundle in enumerate(response["rows"]):
            try:
                self._sync_bundle(bundle)

                print(f"{bundle['name']} synchronized ({ind}/{bundles_count})")
            except Exception as e:
                print(e)
                print(f"{bundle['name']} not synchronized ({ind}/{bundles_count})")
    
    def sync_bundle_by_id(self, bundle_id: str):
        response = self.moysklad_request("BUNDLE_DETAIL", [bundle_id])

        self._sync_bundle(response)

    def _sync_bundle(self, bundle: dict):
        if not self._checking_product_sync(bundle):
            return

        bundle_path = self._sync_product_path(bundle)
        
        if not bundle_path:
            return
        
        self._sync_bundle_detail(bundle, bundle_path)
        self._sync_bundle_complect(bundle["id"])
        self._sync_bundle_images(bundle["id"])

    def _sync_bundle_image(self, bundle_id: str) -> str | None:
        response = MoySkaldSynchronizer.moysklad_request("BUNDLE_IMAGES", [bundle_id])
        
        if not response.get("rows"):
            return self.default_product_image

        image_data = response["rows"][0]

        image_response = requests.get(
            image_data["meta"]["downloadHref"],
            headers=MoySkaldSynchronizer.HEADERS
        )
        image_filename = image_data["filename"]

        image_folder_path = self.django_media_path / self.product_media_path / bundle_id
        
        if not image_folder_path.exists():
            os.makedirs(image_folder_path)
        
        image_path = image_folder_path / image_filename
        
        with open(image_path, "wb") as file:
            file.write(image_response.content)

        return str(self.product_media_path / bundle_id / image_filename)

    def _sync_bundle_detail(self, bundle: dict, bundle_path: models.ProductPathModel):
        with Session(engine) as session:
            category_name = bundle_path.name
            category_instance = session.query(models.ProductCategoryModel).filter(
                models.ProductCategoryModel.name == category_name
            ).first()
            
            if not category_instance:
                category_instance = models.ProductCategoryModel(
                    name=category_name
                )
                
                session.add(category_instance)
                session.commit()
            
            bundle_instance: models.BundleModel = session.query(models.BundleModel).filter(
                models.BundleModel.bundle_id == bundle["id"]
            ).first()
            
            if not bundle_instance:
                bundle_instance = models.BundleModel()
                session.add(bundle_instance)
            
            bundle_instance.bundle_id = bundle["id"]
            bundle_instance.name = bundle["name"]
            bundle_instance.description = bundle.get("description", "")
            bundle_instance.price = int(bundle["salePrices"][0]["value"])
            bundle_instance.path_id = bundle_path.id
            
            bundle_instance.category = category_instance
            bundle_instance.image = self._sync_bundle_image(bundle["id"])

            session.commit()

        return bundle_instance
    
    def _sync_bundle_complect(self, bundle_id: str) -> None:
        response = MoySkaldSynchronizer.moysklad_request("COMPONENTS", [bundle_id])
        
        with Session(engine) as session:
            bundle_instance: models.BundleModel = session.query(models.BundleModel).filter(
                models.BundleModel.bundle_id == bundle_id
            ).first()
            
            if not bundle_instance:
                return
        
        for component in response["rows"][1:]:
            component_id = component["assortment"]["meta"]["href"].split("/")[-1]
            
            with Session(engine) as session:
                session.expunge_all()
                session.add(bundle_instance)
                
                component_instance = session.query(models.ProductModificationModel).filter(
                    models.ProductModificationModel.modification_id == component_id
                ).first()
                
                if not component_instance:
                    raise NoBundleComplectException(f"{bundle_id=}, {component_id=}")
                
                connection_exists = bool(
                    session.query(models.BundleProductModificationsModel).filter(
                        models.BundleProductModificationsModel.bundlemodel_id == bundle_instance.id,
                        models.BundleProductModificationsModel.productmodificationmodel_id == component_instance.id,
                    ).first()
                )
                
                if connection_exists:
                    continue
                
                connection_instance = models.BundleProductModificationsModel(
                    bundlemodel_id=bundle_instance.id,
                    productmodificationmodel_id=component_instance.id
                )
                
                session.add(connection_instance)
                session.commit()
                
    def _sync_bundle_images(self, bundle_id: str) -> None:
        with Session(engine) as session:
            bundle_instance = session.query(models.BundleModel).filter(
                models.BundleModel.bundle_id == bundle_id
            ).first()
            
            if not bundle_instance:
                return
            
            response = MoySkaldSynchronizer.moysklad_request("BUNDLE_IMAGES", [bundle_id])
        
            if not response.get("rows") or len(response.get("rows", [])) <= 1:
                return
            
            for image in response["rows"]:
                image_response = requests.get(
                    image["meta"]["downloadHref"],
                    headers=MoySkaldSynchronizer.HEADERS
                )

                image_filename = image["filename"]

                image_folder_path = self.django_media_path / self.product_media_path / bundle_id
         
                if not image_folder_path.exists():
                    os.makedirs(image_folder_path)
            
                image_path = image_folder_path / image_filename
    
                with open(image_path, "wb") as file:
                    file.write(image_response.content)

                django_image_path = str(self.product_media_path / bundle_id / image_filename)
                
                image_instance = session.query(models.BundleImageModel).filter(
                    models.BundleImageModel.image == django_image_path
                ).first()
                
                if image_instance:
                    continue
                
                image_instance = models.BundleImageModel(
                    bundle_id=bundle_instance.id,
                    image=django_image_path
                )
                
                session.add(image_instance)
                session.commit()


class BonusMoneySynchronizer:
    MOYSKLAD_TOKEN = "9ad7b79af08525d5313361e63b77f8439cd185f7"
    HEADERS = {
        "Authorization": f"Bearer {MOYSKLAD_TOKEN}",
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.1 Safari/605.1.15"
    }
    MOYSKLAD_URLS = {
        "PRODUCTS": "https://online.moysklad.ru/api/remap/1.2/entity/product?filter=archived=false",
        "PRODUCT_DETAIL": "https://online.moysklad.ru/api/remap/1.2/entity/product/{}",
        "MODIFICATIONS": "https://online.moysklad.ru/api/remap/1.2/entity/variant?filter=productid={}",
        "MODIFICATION_IMAGES": "https://online.moysklad.ru/api/remap/1.2/entity/variant/{}/images",
        "PRODUCT_IMAGES": "https://online.moysklad.ru/api/remap/1.2/entity/product/{}/images",
        "DOWNLOAD": "https://online.moysklad.ru/api/remap/1.2/download/{}",
        "BUNDLES": "https://online.moysklad.ru/api/remap/1.2/entity/bundle",
        "BUNDLE_DETAIL": "https://online.moysklad.ru/api/remap/1.2/entity/bundle/{}",
        "BUNDLE_IMAGES": "https://online.moysklad.ru/api/remap/1.2/entity/bundle/{}/images",
        "COMPONENTS": "https://online.moysklad.ru/api/remap/1.2/entity/bundle/{}/components",
    }
