# StreamBox

Application de streaming inspirée par les interfaces Netflix / Xalaflix. Elle inclut :

- une page d'accueil immersive avec carrousels dynamiques ;
- des fiches détaillées pour chaque programme avec liste d'épisodes pour les séries ;
- un système d'authentification (inscription, connexion, déconnexion) ;
- un panneau d'administration pour gérer les films et séries ;
- une base de données SQLite initialisée avec du contenu de démonstration.

## Prérequis

- Python 3.11+
- `pip`

## Installation

```bash
python -m venv .venv
source .venv/bin/activate  # sous Windows : .venv\\Scripts\\activate
pip install -r requirements.txt
```

## Lancer le serveur

```bash
flask --app wsgi run
```

Le site est alors accessible sur [http://localhost:5000](http://localhost:5000).

Un compte administrateur par défaut est créé lors du premier démarrage :

- **Identifiant :** `admin`
- **Mot de passe :** `admin123`

## Personnalisation

Depuis le panneau d'administration, vous pouvez :

- créer, modifier et supprimer des programmes ;
- déclarer qu'un programme est une série puis gérer ses épisodes (saisons, numéros, vidéos) ;
- ajouter des liens vers vos propres vidéos (hébergées ailleurs) ;
- enrichir les métadonnées (catégories, notes, slogans, etc.).

Les fichiers clés sont :

- `app/models.py` — modèles de données et génération du jeu d'essai ;
- `app/routes.py` — pages publiques (accueil, recherche, fiche) ;
- `app/auth.py` — authentification des utilisateurs ;
- `app/admin.py` — panneau d'administration ;
- `app/templates/` — vues HTML ;
- `app/static/` — styles et scripts.

## Déploiement

Vous pouvez héberger StreamBox sur n'importe quelle plateforme compatible WSGI (Railway, Render, Heroku, etc.). Pensez à :

- définir une clé secrète forte (`SECRET_KEY`) via les variables d'environnement ;
- utiliser une base de données persistante (PostgreSQL, MySQL) pour un usage en production ;
- placer vos vidéos sur un CDN ou service d'hébergement spécialisé.
