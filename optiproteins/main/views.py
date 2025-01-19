from django.shortcuts import render
from .utils import find_protein_mongo,get_jaccard_similarities, propagate_ec_numbers
import json
from django.http import JsonResponse
from optiproteins.mongodb import mongo_db

def recherche_prots(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            if data.get("action") == "autocomplete":
                query = data.get("query", "").strip()
                search_type = data.get("type", "").strip()
                suggestions = []

                if query and search_type:
                    collection = mongo_db["proteins"]
                    if search_type == "id":
                        suggestions = collection.distinct("Entry", {"Entry": {"$regex": f"^{query}", "$options": "i"}})
                    elif search_type == "name":
                        suggestions = collection.distinct("Entry Name", {"Entry Name": {"$regex": f"^{query}", "$options": "i"}})
                    elif search_type == "description":
                        suggestions = collection.distinct("Protein names", {"Protein names": {"$regex": f"^{query}", "$options": "i"}})

                return JsonResponse(suggestions[:10], safe=False)  # Limite à 10 suggestions
        except json.JSONDecodeError:
            pass
        
        search_type=request.POST.get("search_type", "").strip()
        search_input = request.POST.get("search_input", "").strip()
        min_jacc_str = request.POST.get("min_jacc", "").strip()
        action = request.POST.get("action", "") 
        two_levels = request.POST.get("two_levels", "")

        min_jacc = None
        if min_jacc_str:
            try:
                min_jacc = float(min_jacc_str)
                if min_jacc < 0 or min_jacc > 1:
                    raise ValueError("La valeur de min_jacc doit être comprise entre 0 et 1.")
            except ValueError as e:
                return render(request, "main/main.html", {"erreur": str(e)})
        else :
            min_jacc = 0.8
        
        if not search_input:
            return render(request, "main/main.html", {"erreur": "Veuillez remplir un champ."})
        
        if action == "rechercher":
            try:
                proteine = find_protein_mongo(search_input, search_type)
                if proteine:
                    proteine_cleaned = {key.replace(" ", "_"): value for key, value in proteine.items()}
                    return render(request, "main/main.html", {"proteine": proteine_cleaned})
                else:
                    return render(request, "main/main.html", {"erreur": f"Aucune protéine trouvée."})
            except Exception as e:
                return render(request, "main/main.html", {"erreur": str(e)})
            
        elif action == "afficher_graphe":
            if min_jacc is None:
                return render(request, "main/main.html", {"erreur": "Veuillez fournir une valeur pour min_jacc."})
            # Recherche pour graphe
            if search_input:
                try:
                    proteine = find_protein_mongo(search_input, search_type)
                    
                    if proteine:
                        proteine_cleaned = {key.replace(" ", "_"): value for key, value in proteine.items()}
                        
                        entry_name = proteine_cleaned['Entry_Name']
                        similarities = get_jaccard_similarities(entry_name, min_jacc = 0)
                        neighbors_similarities=[s for s in similarities if s['similarity'] >= min_jacc]
                        graph_data = {
                            'nodes': [{'id': entry_name, 'label': entry_name, 'color': 'red'}] + 
                                        [{'id': s['protein'].entryName or s['protein'].entry, 'label': s['protein'].entryName or s['protein'].entry} for s in neighbors_similarities],
                            'edges': [{'from': entry_name, 'to': (s['protein'].entryName or s['protein'].entry), 'similarity': s['similarity']} for s in neighbors_similarities]
                        }
                        
                        # Préparer les données pour le graphe
                        nodes_json = json.dumps(graph_data['nodes'])
                        edges_json = json.dumps(graph_data['edges'])
                        
                        # Propagation des EC Numbers basée sur toutes les similarités
                        if two_levels:
                            graph_data_two_levels={'nodes': graph_data['nodes'], 'edges': graph_data['edges']}
                            similarities_two_levels=[]
                            for s in neighbors_similarities:
                                existing_node_ids = {node['id'] for node in graph_data_two_levels['nodes']} 
                                similarities_two_levels.extend(get_jaccard_similarities(s['protein'].entryName, min_jacc = min_jacc))
                                graph_data_two_levels['nodes'].extend([{'id': s2['protein'].entryName or s2['protein'].entry, 'label': s2['protein'].entryName or s2['protein'].entry} for s2 in similarities_two_levels if s2['similarity'] >= min_jacc and s2['protein'].entryName not in existing_node_ids])
                                graph_data_two_levels['edges'].extend([{'from': s['protein'].entryName, 'to': (s2['protein'].entryName or s2['protein'].entry), 'similarity': s2['similarity']} for s2 in similarities_two_levels if s2['similarity'] >= min_jacc and s['protein'].entryName!=s2['protein'].entryName and s2['protein'].entryName!=entry_name])                             
                            nodes_json = json.dumps(graph_data['nodes'])
                            edges_json = json.dumps(graph_data['edges'])
                            
                        ec_propagation = propagate_ec_numbers(similarities)
                        
                        return render(request, "main/main.html", {
                            "nodes_json": nodes_json,
                            "edges_json": edges_json,
                            "min_jacc": min_jacc,
                            "ec_propagation": ec_propagation,
                            "proteine": proteine_cleaned
                        })
                    else:
                        return render(request, "main/main.html", {"erreur": "Protéine non trouvée pour afficher le graphe."})
                except Exception as e:
                    return render(request, "main/main.html", {"erreur": str(e)})
            else:
                return render(request, "main/main.html", {"erreur": "Veuillez entrer des informations pour afficher le graphe."})

    return render(request, "main/main.html")

