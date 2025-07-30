from motor.motor_asyncio import AsyncIOMotorClient
from ..interfaces.metadb import IMetaDatabase
from ..models.dsp.v2025_1_rc2.low_level import Offer
from typing import List
import os

class MongoStorage(IMetaDatabase):
    def __init__(self):
        url = os.getenv('MONGO_URL', 'localhost:27017')
        db_name = os.getenv('DB_NAME', 'SingularSpace')
        user = os.getenv('DB_USER', 'singular-connector')
        pwd = os.getenv('DB_PWD', 'mySecretCombination')

        # Construct Mongo URI
        motor_url = f"mongodb://{user}:{pwd}@{url}/{db_name}?authSource={db_name}"
        self.client = AsyncIOMotorClient(motor_url)
        self.db = self.client[db_name]
        self.offers = self.db["offers"]

    async def create_offer(self, offer: Offer) -> Offer:
        offer_dict = offer.model_dump(by_alias=True)  # Use `model_dump` if using Pydantic v2
        await self.offers.insert_one(offer_dict)
        return offer

    async def get_offer(self, offer_id: str) -> Offer:
        doc = await self.offers.find_one({"_id": offer_id})
        if doc:
            return Offer(**doc)
        return None

    async def list_offers(self) -> List[Offer]:
        cursor = self.offers.find()
        docs = await cursor.to_list(length=1000)
        return [Offer(**doc) for doc in docs]

    async def update_offer(self, offer: Offer) -> bool:
        offer_dict = offer.model_dump(by_alias=True)
        result = await self.offers.replace_one({"_id": offer_dict["_id"]}, offer_dict)
        return result.modified_count == 1

    async def delete_offer(self, offer_id: str) -> bool:
        result = await self.offers.delete_one({"_id": offer_id})
        return result.deleted_count == 1
