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

def get_jaccard_similarities_two_levels(entry_name, min_jacc=0.0):
    """
    Récupère les similarités Jaccard jusqu'à deux niveaux pour une protéine centrale.
    Retourne un dictionnaire contenant les nœuds et les arêtes.
    """
    try:
        central = Protein.nodes.get(entryName=entry_name)
    except Protein.DoesNotExist:
        return {'nodes': [], 'edges': []}

    central_interpros = set(central.interPro)

    # Première requête pour obtenir les voisins de premier niveau
    query = """
    MATCH (p:Protein)
    WHERE ANY(x IN p.interPro WHERE x IN $centralList)
    RETURN p
    """
    params = {"centralList": list(central_interpros)}
    results, _ = db.cypher_query(query, params)
    candidates_level1 = [Protein.inflate(row[0]) for row in results]

    edges = []
    nodes = set()
    central_id = central.entryName or central.entry
    nodes.add(central_id)

    similarities_level1 = []

    # Traitement des similarités de premier niveau
    for c in candidates_level1:
        if c.entryName == entry_name:
            continue
        c_set = set(c.interPro)
        intersection = central_interpros.intersection(c_set)
        union = central_interpros.union(c_set)
        if len(union) == 0:
            continue
        jacc = len(intersection) / len(union)
        if jacc >= min_jacc:
            neighbor_id = c.entryName or c.entry
            edges.append({'from': central_id, 'to': neighbor_id, 'similarity': jacc})
            nodes.add(neighbor_id)
            similarities_level1.append(c)

    # Traitement des similarités de second niveau si nécessaire
    for neighbor in similarities_level1:
        neighbor_id = neighbor.entryName or neighbor.entry
        neighbor_interpros = set(neighbor.interPro)

        query2 = """
        MATCH (p:Protein)
        WHERE ANY(x IN p.interPro WHERE x IN $neighborList)
        RETURN p
        """
        params2 = {"neighborList": list(neighbor_interpros)}
        results2, _ = db.cypher_query(query2, params2)
        candidates_level2 = [Protein.inflate(row[0]) for row in results2]

        for c2 in candidates_level2:
            if c2.entryName in [entry_name, neighbor.entryName]:
                continue
            c2_set = set(c2.interPro)
            intersection2 = neighbor_interpros.intersection(c2_set)
            union2 = neighbor_interpros.union(c2_set)
            if len(union2) == 0:
                continue
            jacc2 = len(intersection2) / len(union2)
            if jacc2 >= min_jacc:
                neighbor2_id = c2.entryName or c2.entry
                edges.append({'from': neighbor_id, 'to': neighbor2_id, 'similarity': jacc2})
                nodes.add(neighbor2_id)

    # Éliminer les arêtes en double
    unique_edges = []
    seen = set()
    for edge in edges:
        key = (edge['from'], edge['to'])
        if key not in seen:
            unique_edges.append(edge)
            seen.add(key)

    # Créer la liste des nœuds
    nodes_list = [{'id': n, 'label': n} for n in nodes]

    return {'nodes': nodes_list, 'edges': unique_edges}


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

