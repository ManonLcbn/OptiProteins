from django.shortcuts import render
from .requetesmongo import trouver_proteine_par_nom
from .utils import get_jaccard_similarities

def recherche_prots(request):
    if request.method == "POST":
        nom = request.POST.get("nom", "").strip()
        if not nom:
            return render(request, "main/main.html", {"erreur": "Veuillez entrer un nom."})
        
        try:
            proteine = trouver_proteine_par_nom(nom)
            if proteine:
                
                proteine_cleaned = {key.replace(" ", "_"): value for key, value in proteine.items()}
                
                jaccard_data = get_jaccard_similarities(nom, min_jacc=0.5)
                
                context = {
                    "proteine": proteine_cleaned,  
                    "similarities": jaccard_data,
                }
                
                return render(request, "main/main.html", context)
            else:
                return render(request, "main/main.html", {"erreur": f"Aucune protéine trouvée avec le nom '{nom}'."})
        except ConnectionError as e:
            return render(request, "main/main.html", {"erreur": "Problème de connexion à la base de données."})
        except ValueError as e:
            return render(request, "main/main.html", {"erreur": str(e)})

    return render(request, "main/main.html")
