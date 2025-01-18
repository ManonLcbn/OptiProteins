from django.shortcuts import render
from .requetesmongo import trouver_proteine_par_nom  # Import de la fonction

def recherche_prots(request):
    """
    Gère la recherche d'une protéine par son nom et l'affichage du formulaire.
    """
    if request.method == "POST":
        nom = request.POST.get("nom", "").strip()  # Récupère le nom du formulaire
        if not nom:
            return render(request, "main/main.html", {"erreur": "Veuillez entrer un nom."})
        
        proteine = trouver_proteine_par_nom(nom)  # Utilisation de la fonction externalisée
        
        if proteine:
            proteine["_id"] = str(proteine["_id"])  # Convertit l'ID MongoDB pour l'affichage
            return render(request, "main/main.html", {"proteine": proteine})
        else:
            return render(request, "main/main.html", {"erreur": f"Aucune protéine trouvée avec le nom '{nom}'."})
    
    # Affiche simplement le formulaire si ce n'est pas une requête POST
    return render(request, "main/main.html")
