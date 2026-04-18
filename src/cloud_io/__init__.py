import os
import sys

import pandas as pd
from pymongo import MongoClient

from src.constants import *
from src.exception import CustomException


DEFAULT_MONGO_DB_URL = (
    "mongodb+srv://imran:TdPLW9Ad0OzpSSD2@cluster0.fv0lm61.mongodb.net/"
    "?retryWrites=true&w=majority&appName=Cluster0"
)


class MongoIO:
    mongo_db = None

    def __init__(self):
        self.mongo_db = MongoIO.mongo_db
        if self.mongo_db is not None:
            return

        mongo_db_url = os.getenv(MONGODB_URL_KEY, DEFAULT_MONGO_DB_URL)
        if not mongo_db_url:
            return

        try:
            client = MongoClient(mongo_db_url, serverSelectionTimeoutMS=5000)
            client.admin.command("ping")
            MongoIO.mongo_db = client[MONGO_DATABASE_NAME]
            self.mongo_db = MongoIO.mongo_db
        except Exception:
            # Let the scraper continue even when MongoDB is unavailable.
            self.mongo_db = None

    def store_reviews(
        self,
        product_name: str,
        reviews: pd.DataFrame,
    ):
        try:
            if self.mongo_db is None or reviews is None or reviews.empty:
                return False

            collection_name = product_name.replace(" ", "_")
            records = reviews.to_dict(orient="records")
            self.mongo_db[collection_name].insert_many(records)
            return True

        except Exception as e:
            raise CustomException(e, sys)

    def get_reviews(self, product_name: str):
        try:
            if self.mongo_db is None:
                return []

            collection_name = product_name.replace(" ", "_")
            data = list(self.mongo_db[collection_name].find({}, {"_id": 0}))
            return data

        except Exception as e:
            raise CustomException(e, sys)

