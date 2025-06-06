# 🌟 BlogHub

![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![Django](https://img.shields.io/badge/django-4.x-green.svg)
![PostgreSQL](https://img.shields.io/badge/postgresql-12+-blue.svg)
![Tailwind CSS](https://img.shields.io/badge/tailwind-2.x-blue.svg)

**BlogHub** est une plateforme de blog moderne et complète développée avec Django, offrant un système de gestion d'articles avancé avec des fonctionnalités sociales, un système d'authentification robuste, et une interface utilisateur moderne avec support du mode sombre.

## 📋 Table des Matières

- [🚀 Fonctionnalités Principales](#-fonctionnalités-principales)
- [🛠️ Technologies Utilisées](#-technologies-utilisées)
- [📦 Installation](#-installation)
- [⚙️ Configuration](#-configuration)
- [🎯 Guide d'Utilisation](#-guide-dutilisation)
- [🔧 Commandes de Gestion](#-commandes-de-gestion)
- [🌐 Structure des URLs](#-structure-des-urls)
- [📊 Modèles de Données](#-modèles-de-données)
- [🔐 Système d'Authentification](#-système-dauthentification)
- [📝 Logging et Monitoring](#-logging-et-monitoring)
- [🎨 Interface Utilisateur](#-interface-utilisateur)
- [🤖 Intégration IA](#-intégration-ia)
- [🧪 Tests](#-tests)
- [🚀 Déploiement](#-déploiement)
- [📋 TODO](#-todo)

## Avant de commencer
Tout ce qu'on devait faire est dans le fichier [TODO](TODO.md).
Et tout a été fait, même plus que demandé.

## 🚀 Fonctionnalités Principales

### 📝 Gestion des Articles
- ✅ Création, édition et suppression d'articles
- ✅ Système de slugs SEO-friendly
- ✅ Catégorisation des articles
- ✅ Publication programmée avec horodatage
- ✅ Comptage des vues automatique
- ✅ Génération d'articles avec IA (Google Gemini)
- ✅ Articles recommandés sur la page de détail

### 👥 Système Social
- ✅ Likes et bookmarks AJAX
- ✅ Système de commentaires
- ✅ Profils d'auteurs détaillés
- ✅ Tableaux de bord utilisateur
- ✅ Restrictions : impossible de liker/bookmarker ses propres articles

### 🔐 Authentification et Sécurité
- ✅ Inscription et connexion personnalisées
- ✅ Gestion des rôles (Admin, Utilisateur, Visiteur)
- ✅ Middleware de sécurité et logging
- ✅ Protection CSRF et validations robustes

### 🎨 Interface Moderne
- ✅ Mode sombre/clair
- ✅ Interface responsive
- ✅ Support multi-langues (i18n)
- ✅ Interactions AJAX fluides
- ✅ Design moderne et intuitif
- ✅ Recherche JavaScript pure (sans AJAX)

## 🛠️ Technologies Utilisées

- **Backend**: Django 4.x, Python 3.x
- **Base de données**: PostgreSQL
- **Frontend**: HTML5, Tailwind x CSS3, JavaScript (Vanilla)
- **Styles**: Tailwind CSS
- **IA**: Google Gemini API
- **Logging**: Django Logging Framework
- **Sécurité**: Django Security Middleware

## 📦 Installation

### Prérequis
- Python 3.8+
- pip
- Git

### 1. Cloner le Projet
```bash
git clone git@github.com:ISITECH-Anthony/pythonDMIA.git
cd pythonDMIA/mon_site_web
```

### 2. Créer un Environnement Virtuel
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate     # Windows
```

### 3. Installer les Dépendances
```bash
pip install -r requirements.txt
```

### 4. Configuration Initiale
```bash
# Copier le fichier de configuration d'exemple
cp .env.example .env

# Éditer le fichier .env avec vos valeurs (éditeur de votre choix)
nano .env  # ou vim .env, code .env, etc.
```

#### 4.1 Commandes utiles

```bash
# Migrations de base de données
python manage.py makemigrations
python manage.py migrate

# Créer un superutilisateur
python manage.py createsuperuser
```

#### 4.2 Autres Commandes Utiles (Commandes personnalisées)

```bash
# Configuration automatique complète du projet
python manage.py setup_project

# Configuration avec options
python manage.py setup_project --skip-migrations --skip-superuser --skip-data

# Peupler la base de données avec des données de test
python manage.py populate_db

# Peupler avec des quantités personnalisées
python manage.py populate_db --users 50 --articles 100 --comments 300

# Nettoyer et repeupler les données
python manage.py populate_db --clear --users 30 --articles 75
```

**Commandes disponibles :**
- `setup_project` : Configure automatiquement le projet (migrations, superuser, données de test)
- `populate_db` : Génère des données de test réalistes pour le blog
- `clean_logs` : Nettoie les fichiers de logs anciens
- `analyze_logs` : Analyse les logs pour détecter des patterns

### 5. Lancer le Serveur de Développement
```bash
python manage.py runserver
```

Accédez à `http://127.0.0.1:8000` pour voir votre application.

## ⚙️ Configuration

### Variables d'Environnement (.env)

Créez un fichier `.env` à la racine du projet en copiant le fichier d'exemple fourni :

```bash
cp .env.example .env
```

Puis éditez le fichier `.env` créé avec vos valeurs spécifiques. Le fichier `.env.example` contient toutes les variables nécessaires avec des valeurs d'exemple :

- **Django Configuration** : `SECRET_KEY`, `DEBUG`, `ALLOWED_HOSTS`
- **Database** : Configuration PostgreSQL
- **Email** : Configuration SMTP pour l'envoi d'emails
- **AI APIs** : Clés API pour Google Gemini et OpenAI DALL-E

⚠️ **Important** : N'oubliez pas de configurer :
- `SECRET_KEY` : Générez une clé secrète unique
- `GEMINI_API_KEY` : Pour les fonctionnalités IA
- `OPENAI_API_KEY` : Pour la génération d'images


#### **SECRET_KEY**
Vous pouvez réutiliser cette clé :
```plaintext
django-insecure-z4a%&v%@34(g+rl7@m%rfhk&fwzw=$r!1c$c)o!b8o(*inc%yq
```

#### **📧 Email (MAILTRAP recommandé)**
Vous pouvez utiliser [Mailtrap](https://mailtrap.io/)

#### **🤖 Google Gemini API (Gratuit)**
Vous pouvez obtenir une clé API gratuite : [Google AI Studio](https://ai.google.dev/gemini-api/docs/pricing?hl=fr)

#### **🎨 OpenAI DALL-E (Optionnel)**
Vous devez vous même avoir une clé API OpenAI pour utiliser DALL-E.

## 🎯 Guide d'Utilisation

### Rôles et Permissions

#### 👤 Visiteur (Non connecté)
- ✅ Lire les articles
- ✅ Parcourir les catégories
- ✅ Voir les profils d'auteurs
- ❌ Liker, bookmarker, commenter

#### 🔵 Utilisateur Connecté (User)
- ✅ Toutes les permissions visiteur
- ✅ Créer, éditer, supprimer ses articles
- ✅ Liker et bookmarker (sauf ses propres articles)
- ✅ Commenter
- ✅ Supprimer ses propres commentaires
- ✅ Gérer son profil

#### 🔴 Administrateur (Admin)
- ✅ Toutes les permissions utilisateur
- ✅ Accès au panel d'administration
- ✅ Gérer tous les utilisateurs et contenus
- ✅ Supprimer tous les commentaires de tous les articles
- ✅ Accéder aux logs et analytics

### Fonctionnalités Spéciales

#### 🚫 Restrictions Importantes
- **Auto-interaction interdite** : Un utilisateur ne peut pas liker ou bookmarker ses propres articles
- **Commentaires** : Seuls les administrateurs peuvent supprimer tous les commentaires, les utilisateurs ne peuvent supprimer que les leurs

#### 🔍 Recherche et Navigation
- **Slugs SEO** : Toutes les URLs utilisent des slugs pour les articles, catégories et auteurs
- **Recherche catégories** : La barre de recherche sur la page catégories fonctionne en JavaScript pur (toutes les catégories sont chargées au chargement de la page)

#### 📊 Articles Recommandés
- Système de `recommended_articles_queryset` sur la page de détail d'un article
- Suggestions basées sur la catégorie et la popularité

## 🔧 Commandes de Gestion

### Analyse des Logs
```bash
# Analyser les logs de requêtes
python manage.py analyze_logs

# Nettoyer les anciens logs
python manage.py clean_logs --days 30
```

### Configuration du Projet
```bash
# Initialiser la configuration du projet
python manage.py setup_project
```

## 🌐 Structure des URLs

```
/                          # Page d'accueil
├── articles/              # Articles
│   ├── create/           # Créer un article
│   ├── <slug>/           # Détail d'un article (avec articles recommandés)
│   ├── <slug>/edit/      # Éditer un article
│   └── category/<slug>/  # Articles par catégorie (slug)
├── authors/              # Auteurs
│   └── <id>/             # Profil d'un auteur (ID)
├── profile/              # Profil utilisateur
│   ├── dashboard/        # Tableau de bord
│   ├── articles/         # Mes articles
│   ├── bookmarks/        # Mes favoris
│   └── settings/         # Paramètres
├── auth/                 # Authentification
│   ├── login/           # Connexion
│   ├── register/        # Inscription
│   └── logout/          # Déconnexion
├── api/                  # API AJAX
│   ├── like/            # Liker un article (AJAX)
│   ├── bookmark/        # Bookmarker un article (AJAX)
│   └── generate/        # Générer avec IA
└── admin/               # Administration Django
```

## 📊 Modèles de Données

### User (Utilisateur)
```python
- username: Nom d'utilisateur unique
- email: Adresse email
- first_name, last_name: Nom et prénom
- bio: Biographie
- avatar: Photo de profil
- created_at: Date de création
```

### Article
```python
- title: Titre
- slug: URL slug (généré automatiquement)
- content: Contenu
- author: Auteur (ForeignKey vers User)
- category: Catégorie (ForeignKey vers Category)
- published_at: Date de publication (peuplée par migration)
- created_at, updated_at: Dates de création/modification
- is_published: Statut de publication
```

### Category (Catégorie)
```python
- name: Nom de la catégorie
- slug: URL slug
- description: Description
- created_at: Date de création
```

### Tags
```python
- name: Nom du tag
- color
- article: Article (ForeignKey vers Article)
- created_at: Date de création
```

### Like (J'aime)
```python
- user: Utilisateur (ForeignKey vers User)
- article: Article (ForeignKey vers Article)
- created_at: Date de création
# Restriction: Un utilisateur ne peut pas liker ses propres articles
```

### Bookmark (Favori)
```python
- user: Utilisateur (ForeignKey vers User)
- article: Article (ForeignKey vers Article)
- created_at: Date de création
# Restriction: Un utilisateur ne peut pas bookmarker ses propres articles
```

### Comment (Commentaire)
```python
- content: Contenu
- author: Auteur (ForeignKey vers User)
- article: Article (ForeignKey vers Article)
- created_at: Date de création
# Les utilisateurs peuvent supprimer leurs commentaires
# Les admins peuvent supprimer tous les commentaires
```

### ArticleView (Vue d'Article)
```python
- article: Article (ForeignKey vers Article)
- user: Utilisateur (ForeignKey vers User, nullable)
- ip_address: Adresse IP
- created_at: Date de vue
```

## 🔐 Système d'Authentification

### Formulaires Personnalisés
- Formulaires d'inscription et de connexion avec validation Django
- Protection CSRF sur tous les formulaires
- Validation côté serveur et client

### Middleware de Sécurité
- Logging automatique des tentatives de connexion
- Tracking des requêtes suspectes
- Gestion des sessions sécurisées

## 📝 Logging et Monitoring

### Système de Logs Personnalisé
Le projet implémente un système de logging complet avec des middlewares dédiés :

#### Types de Logs
1. **Request Logs** : Toutes les requêtes HTTP avec middleware personnalisé
2. **Security Logs** : Tentatives de connexion, erreurs d'authentification
3. **Application Logs** : Erreurs application, actions utilisateur importantes
4. **Performance Logs** : Temps de réponse, requêtes lentes

#### Middleware Implémentés
- **RequestLoggingMiddleware** : Log de toutes les requêtes
- **SecurityMiddleware** : Monitoring des tentatives de sécurité

## 🎨 Interface Utilisateur

### Composants HTML Modulaires
Le projet utilise une architecture de templates Django avec des composants réutilisables :

- **Base Templates** : Structures de page principales
- **Includes** : Composants réutilisables (header, footer, sidebar)
- **Blocks** : Sections personnalisables par page
- **Forms** : Widgets Django personnalisés

### Thèmes et Modes
- **Mode Clair** : Interface lumineuse par défaut
- **Mode Sombre** : Thème sombre pour un confort visuel
- **Toggle dynamique** : Changement de thème en temps réel avec JavaScript

### Fonctionnalités JavaScript
- **AJAX Likes/Bookmarks** : Interactions sans rechargement de page
- **Recherche JavaScript** : Filtrage des catégories côté client
- **Form Validation** : Validation côté client
- **Dynamic Content** : Chargement de contenu dynamique

### Internationalisation (i18n) (FR, EN, ES)
- Support multi-langues configuré
- Changement de langue dynamique
- Templates traduits

## 🤖 Intégration IA

### Fonctionnalités IA
- Génération d'articles d'un article à partir d'un prompt utilisateur
- Paramètres supplémentaires :
    - Longueur de l'article
    - Style d'écriture
    - Génération d'images avec OpenAI DALL-E

## 🧪 Tests

### Tests Unitaires
Le projet inclut une suite de tests complète pour valider la plupart les fonctionnalités :

### Exécuter les Tests
```bash
# Tous les tests
python manage.py test

# Tests spécifiques
python manage.py test blog.tests.test_models
```

## 📈 Performance et Optimisation

### Optimisations Implémentées
- **Query Optimization** : `select_related()` et `prefetch_related()`
- **Database Indexing** : Index sur les champs fréquemment recherchés
- **AJAX Operations** : Likes et bookmarks sans rechargement
- **Static Files** : Configuration optimisée pour la production
- **Slugs SEO** : URLs optimisées pour le référencement

### Fonctionnalités Spéciales
- **Articles Recommandés** : Algorithme de recommandation sur la page de détail
- **Comptage des Vues** : Tracking automatique des consultations d'articles
- **Recherche Optimisée** : Recherche JavaScript pure pour les catégories

## 📋 TODO

Pour voir la liste des fonctionnalités à implémenter et les améliorations futures, consultez le fichier [TODO.md](TODO.md).

## 🔧 Maintenance

### Commandes Utiles
```bash
# Analyser les logs
python manage.py analyze_logs

# Nettoyer les anciens logs
python manage.py clean_logs --days 30
```

### Monitoring
- Logs de performance automatiques
- Tracking des requêtes avec middleware
- Monitoring des erreurs 500/404
- Analytics des vues d'articles
