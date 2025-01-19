from optiproteins.mongodb import mongo_db

def trouver_proteine_par_id(id):
    collection = mongo_db["proteins"]
    return collection.find_one({"Entry": {"$regex": id, "$options": "i"}})

def trouver_proteine_par_nom(name):
    collection = mongo_db["proteins"]
    return collection.find_one({"Entry Name": {"$regex": name, "$options": "i"}})

def trouver_proteine_par_description(description):
    collection = mongo_db["proteins"]
    return collection.find_one({"Protein names": {"$regex": description, "$options": "i"}})
