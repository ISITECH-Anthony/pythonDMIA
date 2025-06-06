"""
Tests pour le modèle Bookmark.
"""
from django.test import TestCase
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db import IntegrityError
from blog.models.article import Article
from blog.models.category import Category
from blog.models.bookmark import Bookmark

User = get_user_model()


class BookmarkModelTest(TestCase):
    """Tests pour le modèle Bookmark."""

    def setUp(self):
        """Configuration initiale pour chaque test."""
        # Créer des utilisateurs
        self.user1 = User.objects.create_user(
            email='user1@example.com',
            username='user1',
            password='testpass123',
            first_name='User',
            last_name='One'
        )
        
        self.user2 = User.objects.create_user(
            email='user2@example.com',
            username='user2',
            password='testpass123',
            first_name='User',
            last_name='Two'
        )
        
        # Créer une catégorie
        self.category = Category.objects.create(
            name='Test Category',
            color='#000000',
            icon='📝'
        )
        
        # Créer un article
        image = SimpleUploadedFile(
            "test_image.jpg",
            b"fake image content",
            content_type="image/jpeg"
        )
        
        self.article = Article.objects.create(
            title='Test Article',
            content='Contenu de test pour l\'article',
            author=self.user1,
            category=self.category,
            image=image,
            is_published=True
        )

    def test_bookmark_creation(self):
        """Test de création d'un marque-page."""
        bookmark = Bookmark.objects.create(
            user=self.user2,
            article=self.article
        )
        
        self.assertEqual(bookmark.user, self.user2)
        self.assertEqual(bookmark.article, self.article)
        self.assertIsNotNone(bookmark.created_at)

    def test_bookmark_str_representation(self):
        """Test de la représentation string du marque-page."""
        bookmark = Bookmark.objects.create(
            user=self.user2,
            article=self.article
        )
        
        expected = f'{self.user2} bookmarked {self.article.title}'
        self.assertEqual(str(bookmark), expected)

    def test_bookmark_unique_constraint(self):
        """Test de contrainte d'unicité (un utilisateur ne peut marquer qu'une fois un article)."""
        # Créer un premier marque-page
        Bookmark.objects.create(
            user=self.user2,
            article=self.article
        )
        
        # Tenter de créer un second marque-page avec le même utilisateur et article
        with self.assertRaises(IntegrityError):
            Bookmark.objects.create(
                user=self.user2,
                article=self.article
            )

    def test_bookmark_different_users_same_article(self):
        """Test que différents utilisateurs peuvent marquer le même article."""
        bookmark1 = Bookmark.objects.create(
            user=self.user1,
            article=self.article
        )
        
        bookmark2 = Bookmark.objects.create(
            user=self.user2,
            article=self.article
        )
        
        self.assertEqual(Bookmark.objects.filter(article=self.article).count(), 2)
        self.assertNotEqual(bookmark1.user, bookmark2.user)

    def test_bookmark_same_user_different_articles(self):
        """Test qu'un utilisateur peut marquer différents articles."""
        # Créer un second article
        image2 = SimpleUploadedFile(
            "test_image2.jpg",
            b"fake image content 2",
            content_type="image/jpeg"
        )
        
        article2 = Article.objects.create(
            title='Second Test Article',
            content='Contenu du second article de test',
            author=self.user1,
            category=self.category,
            image=image2,
            is_published=True
        )
        
        bookmark1 = Bookmark.objects.create(
            user=self.user2,
            article=self.article
        )
        
        bookmark2 = Bookmark.objects.create(
            user=self.user2,
            article=article2
        )
        
        self.assertEqual(Bookmark.objects.filter(user=self.user2).count(), 2)
        self.assertNotEqual(bookmark1.article, bookmark2.article)

    def test_bookmark_ordering(self):
        """Test de l'ordre des marque-pages."""
        # Créer un second article pour tester l'ordre
        image2 = SimpleUploadedFile(
            "test_image2.jpg",
            b"fake image content 2",
            content_type="image/jpeg"
        )
        
        article2 = Article.objects.create(
            title='Second Test Article',
            content='Contenu du second article de test',
            author=self.user1,
            category=self.category,
            image=image2,
            is_published=True
        )
        
        # Créer plusieurs marque-pages
        bookmark1 = Bookmark.objects.create(
            user=self.user2,
            article=self.article
        )
        
        bookmark2 = Bookmark.objects.create(
            user=self.user2,
            article=article2
        )
        
        # Les marque-pages doivent être ordonnés par date de création (plus récent en premier)
        bookmarks = list(Bookmark.objects.filter(user=self.user2))
        self.assertEqual(bookmarks[0], bookmark2)
        self.assertEqual(bookmarks[1], bookmark1)

    def test_bookmark_cascade_delete_with_user(self):
        """Test de suppression en cascade avec l'utilisateur."""
        bookmark = Bookmark.objects.create(
            user=self.user2,
            article=self.article
        )
        bookmark_id = bookmark.id
        
        # Supprimer l'utilisateur
        self.user2.delete()
        
        # Le marque-page doit aussi être supprimé
        self.assertFalse(Bookmark.objects.filter(id=bookmark_id).exists())

    def test_bookmark_cascade_delete_with_article(self):
        """Test de suppression en cascade avec l'article."""
        bookmark = Bookmark.objects.create(
            user=self.user2,
            article=self.article
        )
        bookmark_id = bookmark.id
        
        # Supprimer l'article
        self.article.delete()
        
        # Le marque-page doit aussi être supprimé
        self.assertFalse(Bookmark.objects.filter(id=bookmark_id).exists())

    def test_bookmark_count_for_article(self):
        """Test du comptage des marque-pages pour un article."""
        # Initialement, aucun marque-page
        self.assertEqual(Bookmark.objects.filter(article=self.article).count(), 0)
        
        # Ajouter un marque-page
        Bookmark.objects.create(user=self.user1, article=self.article)
        self.assertEqual(Bookmark.objects.filter(article=self.article).count(), 1)
        
        # Ajouter un second marque-page
        Bookmark.objects.create(user=self.user2, article=self.article)
        self.assertEqual(Bookmark.objects.filter(article=self.article).count(), 2)

    def test_bookmark_count_for_user(self):
        """Test du comptage des marque-pages d'un utilisateur."""
        # Créer un second article
        image2 = SimpleUploadedFile(
            "test_image2.jpg",
            b"fake image content 2",
            content_type="image/jpeg"
        )
        
        article2 = Article.objects.create(
            title='Second Test Article',
            content='Contenu du second article de test',
            author=self.user1,
            category=self.category,
            image=image2,
            is_published=True
        )
        
        # Initialement, aucun marque-page
        self.assertEqual(Bookmark.objects.filter(user=self.user2).count(), 0)
        
        # Ajouter des marque-pages
        Bookmark.objects.create(user=self.user2, article=self.article)
        Bookmark.objects.create(user=self.user2, article=article2)
        
        self.assertEqual(Bookmark.objects.filter(user=self.user2).count(), 2)

    def test_bookmark_meta_options(self):
        """Test des options meta du modèle."""
        meta = Bookmark._meta
        self.assertEqual(meta.ordering, ['-created_at'])
        self.assertEqual(meta.verbose_name, 'Favori')
        self.assertEqual(meta.verbose_name_plural, 'Favoris')
        
        # Vérifier la contrainte unique
        unique_together = getattr(meta, 'unique_together', None)
        constraints = getattr(meta, 'constraints', [])
        
        # La contrainte peut être définie soit avec unique_together soit avec constraints
        has_unique_constraint = (
            unique_together and ('user', 'article') in unique_together
        ) or any(
            hasattr(constraint, 'fields') and 
            set(constraint.fields) == {'user', 'article'}
            for constraint in constraints
        )
        
        self.assertTrue(has_unique_constraint)

    def test_bookmark_created_at_auto_now_add(self):
        """Test que created_at est automatiquement défini à la création."""
        bookmark = Bookmark.objects.create(
            user=self.user2,
            article=self.article
        )
        
        self.assertIsNotNone(bookmark.created_at)
        
        # Créer un second marque-page et vérifier que created_at est différent
        import time
        time.sleep(0.1)
        
        # Créer un second article pour éviter la contrainte unique
        image2 = SimpleUploadedFile(
            "test_image2.jpg",
            b"fake image content 2",
            content_type="image/jpeg"
        )
        
        article2 = Article.objects.create(
            title='Second Test Article',
            content='Contenu du second article de test',
            author=self.user1,
            category=self.category,
            image=image2,
            is_published=True
        )
        
        bookmark2 = Bookmark.objects.create(
            user=self.user2,
            article=article2
        )
        
        self.assertGreater(bookmark2.created_at, bookmark.created_at)

    def test_bookmark_user_bookmarked_articles(self):
        """Test de récupération des articles marqués par un utilisateur."""
        # Créer plusieurs articles
        image2 = SimpleUploadedFile(
            "test_image2.jpg",
            b"fake image content 2",
            content_type="image/jpeg"
        )
        
        article2 = Article.objects.create(
            title='Second Test Article',
            content='Contenu du second article de test',
            author=self.user1,
            category=self.category,
            image=image2,
            is_published=True
        )
        
        image3 = SimpleUploadedFile(
            "test_image3.jpg",
            b"fake image content 3",
            content_type="image/jpeg"
        )
        
        article3 = Article.objects.create(
            title='Third Test Article',
            content='Contenu du troisième article de test',
            author=self.user1,
            category=self.category,
            image=image3,
            is_published=True
        )
        
        # Marquer certains articles
        Bookmark.objects.create(user=self.user2, article=self.article)
        Bookmark.objects.create(user=self.user2, article=article3)
        
        # Récupérer les articles marqués
        bookmarked_articles = Article.objects.filter(
            bookmarks__user=self.user2
        ).distinct()
        
        self.assertEqual(bookmarked_articles.count(), 2)
        self.assertIn(self.article, bookmarked_articles)
        self.assertIn(article3, bookmarked_articles)
        self.assertNotIn(article2, bookmarked_articles)
