from django.shortcuts import render
from .requetesmongo import trouver_proteine_par_id,trouver_proteine_par_nom,trouver_proteine_par_description
from .utils import get_jaccard_similarities, propagate_ec_numbers

def recherche_prots(request):
    if request.method == "POST":
        id = request.POST.get("id", "").strip()
        name = request.POST.get("name", "").strip()
        description = request.POST.get("description", "").strip()
        min_jacc_str = request.POST.get("min_jacc", "").strip()
        action = request.POST.get("action", "") 

        min_jacc = None
        if min_jacc_str:
            try:
                min_jacc = float(min_jacc_str)
                if min_jacc < 0 or min_jacc > 1:
                    raise ValueError("La valeur de min_jacc doit être comprise entre 0 et 1.")
            except ValueError as e:
                return render(request, "main/main.html", {"erreur": str(e)})
        
        if not id and not name and not description:
            return render(request, "main/main.html", {"erreur": "Veuillez remplir un champ."})
        
        if action == "rechercher":
            
            if id or name or description:
                try:
                    proteine = None
                    if id:
                        proteine = trouver_proteine_par_id(id)
                    elif name:
                        proteine = trouver_proteine_par_nom(name)
                    elif description:
                        proteine = trouver_proteine_par_description(description)
                    
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
            if id or name or description:
                try:
                    proteine = None
                    if id:
                        proteine = trouver_proteine_par_id(id)
                    elif name:
                        proteine = trouver_proteine_par_nom(name)
                    elif description:
                        proteine = trouver_proteine_par_description(description)
                    
                    if proteine:
                        proteine_cleaned = {key.replace(" ", "_"): value for key, value in proteine.items()}
                        jaccard_data = get_jaccard_similarities(proteine_cleaned['Entry_Name'], min_jacc=0)
                        ec_propagation = propagate_ec_numbers(jaccard_data)
                        print(ec_propagation)
                        return render(request, "main/main.html", {
                            "similarities": [item for item in jaccard_data if item['similarity'] >= min_jacc],
                            "min_jacc": min_jacc,
                            "ec_propagation": ec_propagation
                        })
                    else:
                        return render(request, "main/main.html", {"erreur": "Protéine non trouvée pour afficher le graphe."})
                except Exception as e:
                    return render(request, "main/main.html", {"erreur": str(e)})
            else:
                return render(request, "main/main.html", {"erreur": "Veuillez entrer des informations pour afficher le graphe."})

    return render(request, "main/main.html")

