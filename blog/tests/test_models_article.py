from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from django.utils import timezone
from blog.models import Article, User, Category


class ArticleModelTest(TestCase):
    """Tests pour le modèle Article"""

    def setUp(self):
        """Configuration initiale pour chaque test"""
        # Créer un utilisateur de test
        self.user = User.objects.create_user(
            email="test@example.com",
            username="testuser",
            first_name="Test",
            last_name="User",
            password="testpass123"
        )
        
        # Créer une catégorie de test
        self.category = Category.objects.create(
            name="Technologie",
            slug="technologie",
            description="Articles sur la technologie",
            icon="💻",
            color="#3B82F6"
        )
        
        # Créer une image de test
        self.test_image = SimpleUploadedFile(
            name='test_image.jpg',
            content=b'test image content',
            content_type='image/jpeg'
        )

    def test_slug_generation_from_title(self):
        """Test que le slug est généré automatiquement à partir du titre"""
        article = Article.objects.create(
            title="Mon Premier Article",
            content="Contenu de test",
            author=self.user,
            category=self.category,
            image=self.test_image
        )
        
        self.assertEqual(article.slug, "mon-premier-article")

    def test_slug_uniqueness(self):
        """Test que les slugs sont uniques même avec des titres identiques"""
        # Premier article
        article1 = Article.objects.create(
            title="Article Test",
            content="Contenu 1",
            author=self.user,
            category=self.category,
            image=SimpleUploadedFile('test1.jpg', b'content1', 'image/jpeg')
        )
        
        # Deuxième article avec le même titre
        article2 = Article.objects.create(
            title="Article Test",
            content="Contenu 2",
            author=self.user,
            category=self.category,
            image=SimpleUploadedFile('test2.jpg', b'content2', 'image/jpeg')
        )
        
        self.assertEqual(article1.slug, "article-test")
        self.assertEqual(article2.slug, "article-test-1")

    def test_reading_time_calculation(self):
        """Test du calcul du temps de lecture"""
        # Article court (100 mots)
        short_content = " ".join(["mot"] * 100)
        article_short = Article.objects.create(
            title="Article Court",
            content=short_content,
            author=self.user,
            category=self.category,
            image=SimpleUploadedFile('short.jpg', b'content', 'image/jpeg')
        )
        
        # Article long (500 mots)
        long_content = " ".join(["mot"] * 500)
        article_long = Article.objects.create(
            title="Article Long",
            content=long_content,
            author=self.user,
            category=self.category,
            image=SimpleUploadedFile('long.jpg', b'content', 'image/jpeg')
        )
        
        # 100 mots / 200 mots par minute = 0.5 min, arrondi à 1 min minimum
        self.assertEqual(article_short.reading_time, 1)
        
        # 500 mots / 200 mots par minute = 2.5 min, arrondi à 2 min
        self.assertEqual(article_long.reading_time, 2)

    def test_word_count_property(self):
        """Test du comptage de mots"""
        content = "Ceci est un test avec cinq mots"
        article = Article.objects.create(
            title="Test Word Count",
            content=content,
            author=self.user,
            category=self.category,
            image=SimpleUploadedFile('test.jpg', b'content', 'image/jpeg')
        )
        
        self.assertEqual(article.word_count, 7)

    def test_excerpt_property(self):
        """Test de l'extrait d'article"""
        # Article avec moins de 20 mots
        short_content = "Un contenu court de test"
        article_short = Article.objects.create(
            title="Article Court",
            content=short_content,
            author=self.user,
            category=self.category,
            image=SimpleUploadedFile('short.jpg', b'content', 'image/jpeg')
        )
        
        # Article avec plus de 20 mots
        long_content = " ".join(["mot"] * 25)
        article_long = Article.objects.create(
            title="Article Long",
            content=long_content,
            author=self.user,
            category=self.category,
            image=SimpleUploadedFile('long.jpg', b'content', 'image/jpeg')
        )
        
        self.assertEqual(article_short.excerpt, "Un contenu court de test")
        
        # Vérifier que l'extrait long se termine par "..."
        self.assertTrue(article_long.excerpt.endswith("..."))
        # Vérifier qu'il contient exactement 20 mots + "..."
        excerpt_words = article_long.excerpt.split()
        self.assertEqual(len(excerpt_words), 21)  # 20 mots + "..."

    def test_publish_method(self):
        """Test de la méthode publish()"""
        article = Article.objects.create(
            title="Article à Publier",
            content="Contenu de test",
            author=self.user,
            category=self.category,
            image=SimpleUploadedFile('test.jpg', b'content', 'image/jpeg'),
            is_published=False
        )
        
        # Vérifier l'état initial
        self.assertFalse(article.is_published)
        self.assertIsNone(article.published_at)
        
        # Publier l'article
        article.publish()
        
        # Vérifier le nouvel état
        self.assertTrue(article.is_published)
        self.assertIsNotNone(article.published_at)
        self.assertAlmostEqual(
            article.published_at,
            timezone.now(),
            delta=timezone.timedelta(seconds=1)
        )

    def test_unpublish_method(self):
        """Test de la méthode unpublish()"""
        # Créer un article publié
        article = Article.objects.create(
            title="Article Publié",
            content="Contenu de test",
            author=self.user,
            category=self.category,
            image=SimpleUploadedFile('test.jpg', b'content', 'image/jpeg'),
            is_published=True
        )
        article.publish()  # Pour avoir une date de publication
        
        published_at = article.published_at
        
        # Dépublier l'article
        article.unpublish()
        
        # Vérifier que l'article est dépublié mais garde sa date de publication
        self.assertFalse(article.is_published)
        self.assertEqual(article.published_at, published_at)

    def test_status_properties(self):
        """Test des propriétés de statut"""
        # Article brouillon (jamais publié)
        draft_article = Article.objects.create(
            title="Brouillon",
            content="Contenu",
            author=self.user,
            category=self.category,
            image=SimpleUploadedFile('draft.jpg', b'content', 'image/jpeg'),
            is_published=False
        )
        
        self.assertTrue(draft_article.is_draft)
        self.assertFalse(draft_article.is_unpublished)
        self.assertEqual(draft_article.status_display, "Brouillon")
        
        # Article publié
        published_article = Article.objects.create(
            title="Publié",
            content="Contenu",
            author=self.user,
            category=self.category,
            image=SimpleUploadedFile('published.jpg', b'content', 'image/jpeg'),
            is_published=True
        )
        published_article.publish()
        
        self.assertFalse(published_article.is_draft)
        self.assertFalse(published_article.is_unpublished)
        self.assertEqual(published_article.status_display, "Publié")
        
        # Article dépublié
        published_article.unpublish()
        
        self.assertFalse(published_article.is_draft)
        self.assertTrue(published_article.is_unpublished)
        self.assertEqual(published_article.status_display, "Dépublié")

    def test_string_representation(self):
        """Test de la représentation string du modèle"""
        article = Article.objects.create(
            title="Mon Article",
            content="Contenu de test",
            author=self.user,
            category=self.category,
            image=SimpleUploadedFile('test.jpg', b'content', 'image/jpeg')
        )
        
        self.assertEqual(str(article), "Mon Article")

    def test_meta_ordering(self):
        """Test de l'ordre par défaut des articles"""
        # Créer plusieurs articles avec des dates différentes
        old_article = Article.objects.create(
            title="Ancien Article",
            content="Contenu",
            author=self.user,
            category=self.category,
            image=SimpleUploadedFile('old.jpg', b'content', 'image/jpeg')
        )
        
        new_article = Article.objects.create(
            title="Nouvel Article",
            content="Contenu",
            author=self.user,
            category=self.category,
            image=SimpleUploadedFile('new.jpg', b'content', 'image/jpeg')
        )
        
        # Vérifier que les articles sont ordonnés par date de création décroissante
        articles = list(Article.objects.all())
        self.assertEqual(articles[0], new_article)
        self.assertEqual(articles[1], old_article)
