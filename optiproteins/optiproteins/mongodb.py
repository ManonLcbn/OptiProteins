from pymongo import MongoClient
from django.conf import settings

# Connexion MongoDB centralisée
mongo_client = MongoClient(
    host=settings.MONGO_DB_SETTINGS['HOST'],
    port=settings.MONGO_DB_SETTINGS['PORT']
)
mongo_db = mongo_client[settings.MONGO_DB_SETTINGS['NAME']]
