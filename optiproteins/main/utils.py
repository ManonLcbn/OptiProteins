from .models import Protein

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

    from neomodel import db
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
        if c.entry == entry_name:
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
