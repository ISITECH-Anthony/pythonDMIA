from django.test import TestCase
from blog.models import User, Article, Category, ArticleView
from django.core.files.uploadedfile import SimpleUploadedFile


class UserModelTest(TestCase):
    """Tests pour le modèle User"""

    def setUp(self):
        """Configuration initiale pour chaque test"""
        self.user = User.objects.create_user(
            email="test@example.com",
            username="testuser",
            first_name="Jean",
            last_name="Dupont",
            password="testpass123"
        )

    def test_get_full_name(self):
        """Test de la méthode get_full_name()"""
        self.assertEqual(self.user.get_full_name(), "Jean Dupont")

    def test_get_full_name_with_empty_fields(self):
        """Test get_full_name() avec des champs vides"""
        user_no_names = User.objects.create_user(
            email="noname@example.com",
            username="noname",
            first_name="",
            last_name="",
            password="testpass123"
        )
        
        self.assertEqual(user_no_names.get_full_name(), " ")

    def test_get_initials(self):
        """Test de la méthode get_initials()"""
        self.assertEqual(self.user.get_initials(), "JD")

    def test_get_initials_with_empty_names(self):
        """Test get_initials() avec des noms vides"""
        user_no_names = User.objects.create_user(
            email="noname@example.com",
            username="noname",
            first_name="",
            last_name="",
            password="testpass123"
        )
        
        self.assertEqual(user_no_names.get_initials(), "")

    def test_get_initials_with_partial_names(self):
        """Test get_initials() avec seulement un prénom ou nom"""
        user_first_only = User.objects.create_user(
            email="first@example.com",
            username="firstonly",
            first_name="Marie",
            last_name="",
            password="testpass123"
        )
        
        user_last_only = User.objects.create_user(
            email="last@example.com",
            username="lastonly",
            first_name="",
            last_name="Martin",
            password="testpass123"
        )
        
        self.assertEqual(user_first_only.get_initials(), "M")
        self.assertEqual(user_last_only.get_initials(), "M")

    def test_get_total_views(self):
        """Test de la méthode get_total_views()"""
        # Créer une catégorie pour les articles
        category = Category.objects.create(
            name="Test Category",
            slug="test-category",
            description="Description test"
        )
        
        # Créer des articles pour cet utilisateur
        article1 = Article.objects.create(
            title="Article 1",
            content="Contenu 1",
            author=self.user,
            category=category,
            image=SimpleUploadedFile('test1.jpg', b'content1', 'image/jpeg')
        )
        
        article2 = Article.objects.create(
            title="Article 2",
            content="Contenu 2",
            author=self.user,
            category=category,
            image=SimpleUploadedFile('test2.jpg', b'content2', 'image/jpeg')
        )
        
        # Créer un autre utilisateur avec un article
        other_user = User.objects.create_user(
            email="other@example.com",
            username="otheruser",
            first_name="Other",
            last_name="User",
            password="testpass123"
        )
        
        other_article = Article.objects.create(
            title="Other Article",
            content="Autre contenu",
            author=other_user,
            category=category,
            image=SimpleUploadedFile('other.jpg', b'content', 'image/jpeg')
        )
        
        # Ajouter des vues aux articles
        ArticleView.objects.create(article=article1, ip_address="192.168.1.1")
        ArticleView.objects.create(article=article1, ip_address="192.168.1.2")
        ArticleView.objects.create(article=article2, ip_address="192.168.1.3")
        ArticleView.objects.create(article=other_article, ip_address="192.168.1.4")
        
        # Vérifier que get_total_views() ne compte que les vues des articles de l'utilisateur
        self.assertEqual(self.user.get_total_views(), 3)
        self.assertEqual(other_user.get_total_views(), 1)

    def test_get_total_views_with_no_articles(self):
        """Test get_total_views() pour un utilisateur sans articles"""
        new_user = User.objects.create_user(
            email="newuser@example.com",
            username="newuser",
            first_name="New",
            last_name="User",
            password="testpass123"
        )
        
        self.assertEqual(new_user.get_total_views(), 0)

    def test_string_representation(self):
        """Test de la représentation string du modèle"""
        self.assertEqual(str(self.user), "Jean Dupont")

    def test_string_representation_with_empty_names(self):
        """Test de la représentation string avec des noms vides"""
        user_no_names = User.objects.create_user(
            email="noname@example.com",
            username="noname",
            first_name="",
            last_name="",
            password="testpass123"
        )
        
        self.assertEqual(str(user_no_names), " ")

    def test_username_field_is_email(self):
        """Test que le champ de connexion est bien l'email"""
        self.assertEqual(User.USERNAME_FIELD, "email")

    def test_required_fields(self):
        """Test des champs requis"""
        expected_fields = ["username", "first_name", "last_name"]
        self.assertEqual(User.REQUIRED_FIELDS, expected_fields)

    def test_email_uniqueness(self):
        """Test que l'email doit être unique"""
        with self.assertRaises(Exception):  # IntegrityError
            User.objects.create_user(
                email="test@example.com",  # Email déjà utilisé
                username="testuser2",
                first_name="Jane",
                last_name="Doe",
                password="testpass123"
            )
