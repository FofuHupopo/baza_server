from sqlalchemy import Column, Integer, String, Text, Boolean, ForeignKey, create_engine
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()


class ProductPathModel(Base):
    __tablename__ = "product__path"
    
    id = Column(Integer, primary_key=True)
    parent_id = Column(Integer, ForeignKey('product__path.id'), nullable=True)
    name = Column(String(63))
    slug = Column(String(255), unique=True, nullable=True)

    parent = relationship('ProductPathModel', remote_side=[id])

    def __repr__(self):
        return f"ProductPathModel(id={self.id}, parent_id={self.parent_id}, name='{self.name}', slug='{self.slug}')"
    
    def full_path(self):
        return f"{self.parent.full_path()}/{self.name}" if self.parent else f"{self.name}"


class ProductCategoryModel(Base):
    __tablename__ = "product__product_category"
    
    id = Column(Integer, primary_key=True)
    category = Column(String(127))
    size_image = Column(String(511), default="product_images/Заглушка фото карточки товара.jpg")

    def __repr__(self):
        return f"ProductCategoryModel(id={self.id}, category='{self.category}')"


class ProductModel(Base):
    __tablename__ = "product__product"
    
    id = Column(Integer, primary_key=True)
    product_id = Column(String(63))
    name = Column(String(255))
    description = Column(Text, nullable=True)
    price = Column(Integer)
    visible = Column(Boolean, default=True)
    image = Column(String(511), default="product_images/Заглушка фото карточки товара.jpg")
    category_id = Column(Integer, ForeignKey('product__product_category.id'))
    path_id = Column(Integer, ForeignKey('product__path.id'))

    category = relationship('ProductCategoryModel')
    path = relationship('ProductPathModel')

    def __repr__(self):
        return f"ProductModel(id={self.id}, product_id='{self.product_id}', name='{self.name}', description='{self.description}', price={self.price}, visible={self.visible}, image='{self.image}', category_id={self.category_id}, path_id={self.path_id})"


class ProductColorModel(Base):
    __tablename__ = "product__product_color"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(127))
    hex_code = Column(String(6), nullable=True)

    def __repr__(self):
        return f"ProductColorModel(id={self.id}, name='{self.name}', hex_code='{self.hex_code}')"


class ProductSizeModel(Base):
    __tablename__ = "product__product_size"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(63))

    def __repr__(self):
        return f"ProductSizeModel(id={self.id}, name='{self.name}')"


class ProductModificationModel(Base):
    __tablename__ = "product__product_modification"

    id = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey('product__product.id'))
    modification_id = Column(String(63))
    color_id = Column(Integer, ForeignKey('product__product_color.id'), nullable=True)
    size_id = Column(Integer, ForeignKey('product__product_size.id'), nullable=True)
    quantity = Column(Integer, default=0)

    product = relationship('ProductModel')
    color = relationship('ProductColorModel', backref='modifications', uselist=False)
    size = relationship('ProductSizeModel')

    def __repr__(self):
        if self.color:
            return f"ProductModificationModel(id={self.id}, product_id={self.product_id}, modification_id='{self.modification_id}', color_id={self.color_id}, size_id={self.size_id}, quantity={self.quantity})"
        else:
            return f"ProductModificationModel(id={self.id}, product_id={self.product_id}, modification_id='{self.modification_id}', size_id={self.size_id}, quantity={self.quantity})"


class ProductModificationImageModel(Base):
    __tablename__ = "product__product_modification_image"

    id = Column(Integer, primary_key=True)
    product_modification_id = Column(Integer, ForeignKey('product__product_modification.id'))
    image = Column(String(511), default="product_images/Заглушка фото карточки товара.jpg")

    modification = relationship('ProductModificationModel', backref='images')

    def __repr__(self):
        return f"ProductModificationImageModel(id={self.id}, modification_id={self.modification_id}, image='{self.image}')"


class BundleModel(Base):
    __tablename__ = "product__bundle"

    id = Column(Integer, primary_key=True)
    bundle_id = Column(String(63))
    name = Column(String(255))
    description = Column(Text, nullable=True)
    visible = Column(Boolean, default=True)
    price = Column(Integer)
    image = Column(String(511), default="product_images/Заглушка фото карточки товара.jpg")
    category_id = Column(Integer, ForeignKey('product__product_category.id'))
    path_id = Column(Integer, ForeignKey('product__path.id'))

    category = relationship('ProductCategoryModel')
    path = relationship('ProductPathModel')


    def __repr__(self):
        return f"BundleModel(id={self.id}, bundle_id='{self.bundle_id}', name='{self.name}', description='{self.description}', visible={self.visible}, price={self.price}, image='{self.image}')"


class BundleImageModel(Base):
    __tablename__ = "product__bundle_image"

    id = Column(Integer, primary_key=True)
    bundle_id = Column(Integer, ForeignKey('product__bundle.id'))
    image = Column(String(511), default="product_images/Заглушка фото карточки товара.jpg")


    def __repr__(self):
        return f"BundleImageModel(id={self.id}, bundle_id={self.bundle_id}, image='{self.image}')"


class BundleProductModificationsModel(Base):
    __tablename__ = 'product__bundle_product_modifications'

    id = Column(Integer, primary_key=True)
    bundlemodel_id = Column(String(63), ForeignKey("product__bundle.id"))
    productmodificationmodel_id = Column(String(63), ForeignKey("product__product.id"))
    
    def save(self, session):
        session.add(self)
        session.commit()


engine = create_engine('postgresql://postgres:postgres@iizhukov.site:5432/baza_store')
