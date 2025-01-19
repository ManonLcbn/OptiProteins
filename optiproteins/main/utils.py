from .models import Protein
from neomodel import db
from collections import defaultdict


def get_jaccard_similarities(entry_name, min_jacc=0.0):
    """
    Pour une protéine donnée (entry_id), calcule la similarité Jaccard
    avec toutes les autres protéines partageant au moins un domaine InterPro.
    Retourne une liste de dict { 'protein': prot, 'similarity': jaccard }
    avec jaccard >= min_jacc.
    """
    try:
        central = Protein.nodes.get(entryName=entry_name)
    except Protein.DoesNotExist:
        return []

    central_interpros = set(central.interPro)

    query = """
    MATCH (p:Protein)
    WHERE ANY(x IN p.interPro WHERE x IN $centralList)
    RETURN p
    """
    params = {"centralList": list(central_interpros)}
    results, meta = db.cypher_query(query, params)
    candidates = [Protein.inflate(row[0]) for row in results]

    output = []
    for c in candidates:
        if c.entryName == entry_name:
            continue
        c_set = set(c.interPro)
        intersection = central_interpros.intersection(c_set)
        union = central_interpros.union(c_set)
        if len(union) == 0:
            continue

        jacc = len(intersection) / len(union)
        if jacc >= min_jacc:
            output.append({"protein": c, "similarity": jacc})

    return output

def propagate_ec_numbers(similarities, top_n=10):
    """
    Propage les EC Numbers vers la protéine cible basée sur les similarités.
    Retourne un tableau des top_n EC Numbers avec les plus hautes probabilités.
    """
    ec_prob = defaultdict(float)

    for item in similarities:
        protein = item['protein']
        similarity = item['similarity']
        ec_numbers = protein.ecNumbers or []  
        for ec in ec_numbers:
            ec_prob[ec] += similarity 

    sorted_ec = sorted(ec_prob.items(), key=lambda x: x[1], reverse=True)

    top_ec = sorted_ec[:top_n]

    result = [{"ec_number": ec, "probability": prob} for ec, prob in top_ec]

    return result

