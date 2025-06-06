"""
Tests pour le modèle Like.
"""
from django.test import TestCase
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db import IntegrityError
from blog.models.article import Article
from blog.models.category import Category
from blog.models.like import Like

User = get_user_model()


class LikeModelTest(TestCase):
    """Tests pour le modèle Like."""

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

    def test_like_creation(self):
        """Test de création d'un like."""
        like = Like.objects.create(
            user=self.user2,
            article=self.article
        )
        
        self.assertEqual(like.user, self.user2)
        self.assertEqual(like.article, self.article)
        self.assertIsNotNone(like.created_at)

    def test_like_str_representation(self):
        """Test de la représentation string du like."""
        like = Like.objects.create(
            user=self.user2,
            article=self.article
        )
        
        expected = f'{self.user2} likes {self.article.title}'
        self.assertEqual(str(like), expected)

    def test_like_unique_constraint(self):
        """Test de contrainte d'unicité (un utilisateur ne peut liker qu'une fois un article)."""
        # Créer un premier like
        Like.objects.create(
            user=self.user2,
            article=self.article
        )
        
        # Tenter de créer un second like avec le même utilisateur et article
        with self.assertRaises(IntegrityError):
            Like.objects.create(
                user=self.user2,
                article=self.article
            )

    def test_like_different_users_same_article(self):
        """Test que différents utilisateurs peuvent liker le même article."""
        like1 = Like.objects.create(
            user=self.user1,
            article=self.article
        )
        
        like2 = Like.objects.create(
            user=self.user2,
            article=self.article
        )
        
        self.assertEqual(Like.objects.filter(article=self.article).count(), 2)
        self.assertNotEqual(like1.user, like2.user)

    def test_like_same_user_different_articles(self):
        """Test qu'un utilisateur peut liker différents articles."""
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
        
        like1 = Like.objects.create(
            user=self.user2,
            article=self.article
        )
        
        like2 = Like.objects.create(
            user=self.user2,
            article=article2
        )
        
        self.assertEqual(Like.objects.filter(user=self.user2).count(), 2)
        self.assertNotEqual(like1.article, like2.article)

    def test_like_ordering(self):
        """Test de l'ordre des likes."""
        # Créer plusieurs likes
        like1 = Like.objects.create(
            user=self.user1,
            article=self.article
        )
        
        like2 = Like.objects.create(
            user=self.user2,
            article=self.article
        )
        
        # Les likes sont ordonnés par id (ordre de création) car pas d'ordering défini
        likes = list(Like.objects.all())
        self.assertEqual(likes[0], like1)
        self.assertEqual(likes[1], like2)

    def test_like_cascade_delete_with_user(self):
        """Test de suppression en cascade avec l'utilisateur."""
        like = Like.objects.create(
            user=self.user2,
            article=self.article
        )
        like_id = like.id
        
        # Supprimer l'utilisateur
        self.user2.delete()
        
        # Le like doit aussi être supprimé
        self.assertFalse(Like.objects.filter(id=like_id).exists())

    def test_like_cascade_delete_with_article(self):
        """Test de suppression en cascade avec l'article."""
        like = Like.objects.create(
            user=self.user2,
            article=self.article
        )
        like_id = like.id
        
        # Supprimer l'article
        self.article.delete()
        
        # Le like doit aussi être supprimé
        self.assertFalse(Like.objects.filter(id=like_id).exists())

    def test_like_count_for_article(self):
        """Test du comptage des likes pour un article."""
        # Initialement, aucun like
        self.assertEqual(Like.objects.filter(article=self.article).count(), 0)
        
        # Ajouter un like
        Like.objects.create(user=self.user1, article=self.article)
        self.assertEqual(Like.objects.filter(article=self.article).count(), 1)
        
        # Ajouter un second like
        Like.objects.create(user=self.user2, article=self.article)
        self.assertEqual(Like.objects.filter(article=self.article).count(), 2)

    def test_like_count_for_user(self):
        """Test du comptage des likes d'un utilisateur."""
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
        
        # Initialement, aucun like
        self.assertEqual(Like.objects.filter(user=self.user2).count(), 0)
        
        # Ajouter des likes
        Like.objects.create(user=self.user2, article=self.article)
        Like.objects.create(user=self.user2, article=article2)
        
        self.assertEqual(Like.objects.filter(user=self.user2).count(), 2)

    def test_like_meta_options(self):
        """Test des options meta du modèle."""
        meta = Like._meta
        self.assertEqual(meta.ordering, [])  # Pas d'ordering défini
        self.assertEqual(meta.verbose_name, 'Like')
        self.assertEqual(meta.verbose_name_plural, 'Likes')
        
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

    def test_like_created_at_auto_now_add(self):
        """Test que created_at est automatiquement défini à la création."""
        like = Like.objects.create(
            user=self.user2,
            article=self.article
        )
        
        self.assertIsNotNone(like.created_at)
        
        # Créer un second like et vérifier que created_at est différent
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
        
        like2 = Like.objects.create(
            user=self.user2,
            article=article2
        )
        
        self.assertGreater(like2.created_at, like.created_at)
