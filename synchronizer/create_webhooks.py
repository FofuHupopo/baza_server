import os
from dotenv import load_dotenv

from app.moy_sklad import MoySklad


load_dotenv()


ACTIONS = ["CREATE", "UPDATE", "DELETE"]
ENTITIES = ["product", "variant", "bundle"]

def delete_webhook(webhook_id):
    MoySklad.moysklad_delete("WEBHOOK_ID", [webhook_id])
        
        
def create_webhook(action, entity):
    MoySklad.moysklad_post("WEBHOOK", data_params={
        "url": os.getenv("WEBHOOK_URL"),
        "action": action,
        "entityType": entity
    })


def main():
    data = MoySklad.moysklad_request("WEBHOOK")
    
    for row in data.get("rows", []):
        delete_webhook(row["id"])
    
    for action in ACTIONS:
        for entity in ENTITIES:
            create_webhook(action, entity)


if __name__ == "__main__":
    main()
