"""
Configuration et outils pour les tests.
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from blog.models.category import Category
from blog.models.article import Article

User = get_user_model()


class BaseTestCase(TestCase):
    """Classe de base pour les tests avec des fixtures communes."""

    def setUp(self):
        """Configuration commune pour tous les tests."""
        self.user = self.create_test_user()
        self.category = self.create_test_category()
        self.article = self.create_test_article()

    def create_test_user(self, email='testuser@example.com', **kwargs):
        """Crée un utilisateur de test."""
        defaults = {
            'email': email,
            'password': 'testpass123',
            'first_name': 'Test',
            'last_name': 'User'
        }
        defaults.update(kwargs)
        return User.objects.create_user(**defaults)

    def create_test_category(self, name='Test Category', **kwargs):
        """Crée une catégorie de test."""
        defaults = {
            'name': name,
            'color': '#000000',
            'icon': '📝'
        }
        defaults.update(kwargs)
        return Category.objects.create(**defaults)

    def create_test_article(self, title='Test Article', **kwargs):
        """Crée un article de test."""
        image = SimpleUploadedFile(
            "test_image.jpg",
            b"fake image content",
            content_type="image/jpeg"
        )
        
        defaults = {
            'title': title,
            'content': 'Contenu de test pour l\'article',
            'author': getattr(self, 'user', self.create_test_user()),
            'category': getattr(self, 'category', self.create_test_category()),
            'featured_image': image,
            'status': 'published'
        }
        defaults.update(kwargs)
        return Article.objects.create(**defaults)

    def assertContainsText(self, response, text):
        """Assertion personnalisée pour vérifier qu'un texte est présent dans la réponse."""
        self.assertContains(response, text, msg_prefix=f"Le texte '{text}' n'a pas été trouvé dans la réponse")

    def assertNotContainsText(self, response, text):
        """Assertion personnalisée pour vérifier qu'un texte n'est pas présent dans la réponse."""
        self.assertNotContains(response, text, msg_prefix=f"Le texte '{text}' a été trouvé dans la réponse alors qu'il ne devrait pas y être")


class TestDataMixin:
    """Mixin pour fournir des données de test communes."""

    @staticmethod
    def get_sample_article_data():
        """Retourne des données d'exemple pour un article."""
        return {
            'title': 'Article de Test',
            'content': 'Contenu détaillé de l\'article de test. ' * 50,  # ~200 mots
            'status': 'published'
        }

    @staticmethod
    def get_sample_user_data():
        """Retourne des données d'exemple pour un utilisateur."""
        return {
            'email': 'newuser@example.com',
            'password': 'newpassword123',
            'first_name': 'Nouveau',
            'last_name': 'Utilisateur'
        }

    @staticmethod
    def get_sample_category_data():
        """Retourne des données d'exemple pour une catégorie."""
        return {
            'name': 'Nouvelle Catégorie',
            'description': 'Description de la nouvelle catégorie',
            'color': '#FF5733',
            'icon': '🆕'
        }

    @staticmethod
    def get_sample_comment_data():
        """Retourne des données d'exemple pour un commentaire."""
        return {
            'content': 'Ceci est un commentaire de test très intéressant.'
        }


class TestFilesMixin:
    """Mixin pour gérer les fichiers de test."""

    def create_test_image(self, name="test_image.jpg", content=b"fake image content"):
        """Crée une image de test."""
        return SimpleUploadedFile(
            name,
            content,
            content_type="image/jpeg"
        )

    def create_test_file(self, name="test_file.txt", content=b"fake file content"):
        """Crée un fichier de test."""
        return SimpleUploadedFile(
            name,
            content,
            content_type="text/plain"
        )
