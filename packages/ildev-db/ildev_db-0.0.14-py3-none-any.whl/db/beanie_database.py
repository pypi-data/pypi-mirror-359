from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from db.base_database import BaseDatabase
from log.base_log import BaseLog

class BeanieDatabase(BaseDatabase):
    def __init__(self, mongo_url: str, models: list, logger: BaseLog):
        super().__init__(logger)
        self.mongo_url = mongo_url
        self.models = models

    async def initialize(self):
        self.logger.info("Initializing Beanie (MongoDB) connection")
        client = AsyncIOMotorClient(self.mongo_url)
        await init_beanie(database=client.get_default_database(), document_models=self.models)
