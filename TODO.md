# TP Django Master 2 - Fonctionnalités à Implémenter

## Blog### **3.1 Vues P- [x]  **Page d'accueil**
    - Articles récents et populaires (les plus vues en premiers)
    - Catégories avec statistiques
    - Auteurs populaires (qui ont le plus d'abonnement)
- [x]  **Liste des articles**
    - Pagination avec Django Paginator
    - Filtrage par catégorie, auteur
    - Tri (récent, populaire, alphabétique)
    - Recherche full-text PostgreSQL
- [x]  **Détail d'article**
    - Affichage complet
    - Articles similaires (algorithme) par catégories
    - Système de likes simple [x]  **Page d'accueil**
    - Articles récents et populaires (les plus vues en premiers)
    - Catégories avec statistiques
    - Auteurs populaires (qui ont le plus d'abonnement)
- [x]  **Liste des articles**
    - Pagination avec Django Paginator
    - Filtrage par catégorie, auteur
    - Tri (récent, populaire, alphabétique)
    - Recherche full-text PostgreSQL
- [x]  **Détail d'article**
    - Affichage complet
    - Articles similaires (algorithme) par catégories
    - Système de likes simpleversitaire - Liste Simplifiée

---

## **JOUR 1 - FONDATIONS ET ARCHITECTURE**

### **1.1 Configuration Projet**

- [x]  Créer un environnement virtuel Python
- [x]  Installer Django 4.2+ et dépendances (PostgreSQL, Pillow)
- [x]  Configurer settings.py multi-environnements (dev/staging/prod)
- [x]  Paramétrer PostgreSQL avec variables d'environnement
- [x]  Configurer les fichiers statiques et médias

### **1.2 Système d'Authentification**

- [x]  Modèle User personnalisé avec champs étendus
- [x]  Système de rôles un role visiteur (lecture seul sans connexion) , user ( connectez lecture écriture ) , admin
- [x]  Inscription/connexion/déconnexion basique
- [x]  Reset password simple

### **1.3 Configuration Avancée**

- [x]  Logging simple
- [x]  Analytics ( compteur de vue like )
- [x]  Tests unitaires de base (si toutes les fonctionnalités fonctionne)
    - De gros tests unitaires ont été fait mais pas tous j'ai compris la logique

---

## **JOUR 2 - MODÈLES ET BASE DE DONNÉES**

### **2.1 Modèles de Base**

- [x]  **Modèle Category**
    - Nom, description, slug
    - Compteur d'articles
- [x]  **Modèle Tag (SLUG)**
    - Nom,
- [x]  **Modèle Article**
    - Titre, slug, contenu, extrait
    - Auteur (ForeignKey User), catégorie, tags
    - Statut (brouillon/publié/archivé)
    - Image de couverture, dates de création/modification (la dernière)
    - Compteurs (vues, likes)

### **2.2 Modèles Avancés**

- [x]  **Modèle Comment**
    - Contenu, auteur, article,
    - Système de modération basique DELETE
- [x]  **Modèle Like/Bookmark**
    - Relations utilisateur-article
    - Timestamps pour analytics
    

---

## **JOUR 3 - VUES ET LOGIQUE MÉTIER**

### **3.1 Vues Publiques**

- [x]  **Page d'accueil**
    - Articles récents et populaires (les plus vues en premiers)
    - Catégories avec statistiques
    - Auteurs populaires (qui ont le plus d’abonnement)
- [x]  **Liste des articles**
    - Pagination avec Django Paginator
    - Filtrage par catégorie, auteur
    - Tri (récent, populaire, alphabétique)
    - Recherche full-text PostgreSQL
- [x]  **Détail d'article**
    - Affichage complet
    - Articles similaires (algorithme) par catégories
    - Système de likes simple
    

### **3.2 Vues Utilisateur**

- [x]  **Profil utilisateur basique**
    - Articles de l'auteur
    - Statistiques personnelles
    - Articles bookmarkés
- [x]  **Dashboard auteur**
    - Mes articles (brouillons/publiés/archivés)
    - Statistiques détaillées
    - Commentaires reçus

### **3.3 Système de Recherche**

- [x]  Recherche full-text avec PostgreSQL
- [x]  Filtres avancés (date, catégorie, auteur)

### **3.4 API REST**

- [x]  articles
- [x]  (CRUD)pour commentaires
- [x]  (CRUD)pour likes/bookmarks

## **JOUR 4 - INTERFACE ET EXPÉRIENCE UTILISATEUR**

### **4.1 Templates Avancés**

- [x]  **Système de templates modulaires**
    - Base template avec blocks
    - Includes réutilisables
- [x]  LECTURE
    - Calculs de temps de lecture
- [x]  **UX Avancée**
    - Mode sombre/clair persistant

### **4.4 Internationalisation**

- [x]  Configuration i18n Django
- [x]  Traduction des templates (FR/EN/ES)
    - base.html
    - Home
    - About

### **4.5 IA
- [x]  Création d'articles avec IA
- [x]  Génération d'images avec IA