from django.shortcuts import render
from .requetesmongo import trouver_proteine_par_id,trouver_proteine_par_nom,trouver_proteine_par_description
from .utils import get_jaccard_similarities

def recherche_prots(request):
    if request.method == "POST":
        id = request.POST.get("id", "").strip()
        name = request.POST.get("name", "").strip()
        description = request.POST.get("description", "").strip()
        if not id and not name and not description:
            return render(request, "main/main.html", {"erreur": "Veuillez remplir un champ."})
        if id:
            try:
                proteine = trouver_proteine_par_id(id)
                if proteine:
                    
                    proteine_cleaned = {key.replace(" ", "_"): value for key, value in proteine.items()}
                    
                    jaccard_data = get_jaccard_similarities(proteine_cleaned['Entry_Name'], min_jacc=0.5)
                    
                    context = {
                        "proteine": proteine_cleaned,  
                        "similarities": jaccard_data,
                    }
                    
                    return render(request, "main/main.html", context)
                else:
                    return render(request, "main/main.html", {"erreur": f"Aucune protéine trouvée avec l'id '{id}'."})
            except ConnectionError as e:
                return render(request, "main/main.html", {"erreur": "Problème de connexion à la base de données."})
            except ValueError as e:
                return render(request, "main/main.html", {"erreur": str(e)})
        elif name:
            try:
                proteine = trouver_proteine_par_nom(name)
                if proteine:
                    
                    proteine_cleaned = {key.replace(" ", "_"): value for key, value in proteine.items()}
                    
                    jaccard_data = get_jaccard_similarities(name, min_jacc=0.5)
                    
                    context = {
                        "proteine": proteine_cleaned,  
                        "similarities": jaccard_data,
                    }
                    
                    return render(request, "main/main.html", context)
                else:
                    return render(request, "main/main.html", {"erreur": f"Aucune protéine trouvée avec le nom '{name}'."})
            except ConnectionError as e:
                return render(request, "main/main.html", {"erreur": "Problème de connexion à la base de données."})
            except ValueError as e:
                return render(request, "main/main.html", {"erreur": str(e)})
        elif description:
            try:
                proteine = trouver_proteine_par_description(description)
                if proteine:
                    
                    proteine_cleaned = {key.replace(" ", "_"): value for key, value in proteine.items()}
                    
                    jaccard_data = get_jaccard_similarities(proteine_cleaned['Entry_Name'], min_jacc=0.5)
                    
                    context = {
                        "proteine": proteine_cleaned,  
                        "similarities": jaccard_data,
                    }
                    
                    return render(request, "main/main.html", context)
                else:
                    return render(request, "main/main.html", {"erreur": f"Aucune protéine trouvée avec la description '{description}'."})
            except ConnectionError as e:
                return render(request, "main/main.html", {"erreur": "Problème de connexion à la base de données."})
            except ValueError as e:
                return render(request, "main/main.html", {"erreur": str(e)})

    return render(request, "main/main.html")
