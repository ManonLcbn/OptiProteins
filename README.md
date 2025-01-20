# Projet OptiProteins

Ce projet Django permet de rechercher des protéines, de les afficher et de tracer un graphe de similarités (basé sur la similarité de Jaccard) à l’aide de Neo4j.

## Prérequis

- Python 3.8+ (ou version ultérieure)
- Pip (pour installer les dépendances)
- MongoDB (installé et en cours d’exécution)
- Neo4j (installé et en cours d’exécution)

## Installation

- Créer un environnement virtuel (fortement recommandé) :

  ```bash
  python -m venv venv
  source venv/bin/activate   # Sur Linux/Mac
  # ou bien
  venv\Scripts\activate.bat  # Sur Windows
  ```

- Installer les dépendances :

  ```bash
  pip install -r requirements.txt
  ```

## Configuration

Les informations de connexion pour MongoDB et Neo4j se trouvent dans le fichier `settings.py`.

- Pour MongoDB, modifier la section suivante si nécessaire :

  ```python
  MONGO_DB_SETTINGS = {
      'NAME': 'db_mongo_project',
      'HOST': 'localhost',
      'PORT': 27017,
  }
  ```

- Pour Neo4j, vérifier la variable :

  ```python
  NEOMODEL_NEO4J_BOLT_URL = "bolt://neo4j:proteindb@localhost:7687"
  ```

Changer ces paramètres (utilisateur, mot de passe, nom d’hôte) en fonction de votre configuration locale.

## Lancement de l’application

- Vérifier que vos bases MongoDB et Neo4j sont actives et accessibles.
- Depuis la racine du projet, où se trouve le fichier `manage.py`, exécuter le serveur Django :

  ```bash
  python manage.py runserver
  ```

- Ouvrir un navigateur et se rendre à l’adresse [http://127.0.0.1:8000/](http://127.0.0.1:8000/) pour utiliser l’interface.