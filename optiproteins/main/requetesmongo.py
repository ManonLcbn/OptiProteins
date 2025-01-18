from optiproteins.mongodb import mongo_db

def trouver_proteine_par_nom(nom):
    """
    Recherche une protéine dans la collection 'proteins' selon son nom.
    """
    collection = mongo_db["proteins"]
    return collection.find_one({"Entry name": nom})
