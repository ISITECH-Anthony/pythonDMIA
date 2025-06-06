"""
Tests pour le modèle Comment - Version simplifiée.
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from blog.models.article import Article
from blog.models.category import Category
from blog.models.comment import Comment

User = get_user_model()


class CommentModelTest(TestCase):
    """Tests pour le modèle Comment."""

    def setUp(self):
        """Configuration initiale pour chaque test."""
        # Créer un utilisateur
        self.user = User.objects.create_user(
            email='testuser@example.com',
            username='testuser',
            password='testpass123',
            first_name='Test',
            last_name='User'
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
            author=self.user,
            category=self.category,
            image=image,
            is_published=True
        )

    def test_comment_creation(self):
        """Test de création d'un commentaire."""
        comment = Comment.objects.create(
            article=self.article,
            author=self.user,
            content="Ceci est un commentaire de test."
        )
        
        self.assertEqual(comment.article, self.article)
        self.assertEqual(comment.author, self.user)
        self.assertEqual(comment.content, "Ceci est un commentaire de test.")
        self.assertIsNotNone(comment.created_at)

    def test_comment_str_representation(self):
        """Test de la représentation string du commentaire."""
        comment = Comment.objects.create(
            article=self.article,
            author=self.user,
            content="Ceci est un commentaire de test."
        )
        expected = f'Commentaire de {self.user.get_full_name()} sur {self.article.title}'
        self.assertEqual(str(comment), expected)

    def test_comment_ordering(self):
        """Test de l'ordre des commentaires."""
        # Créer plusieurs commentaires
        comment1 = Comment.objects.create(
            article=self.article,
            author=self.user,
            content='Premier commentaire'
        )
        
        comment2 = Comment.objects.create(
            article=self.article,
            author=self.user,
            content='Deuxième commentaire'
        )
        
        comment3 = Comment.objects.create(
            article=self.article,
            author=self.user,
            content='Troisième commentaire'
        )
        
        # Les commentaires doivent être ordonnés par date de création (plus récent en premier)
        comments = list(Comment.objects.all())
        self.assertEqual(comments[0], comment3)
        self.assertEqual(comments[1], comment2)
        self.assertEqual(comments[2], comment1)

    def test_comment_meta_options(self):
        """Test des options meta du modèle."""
        meta = Comment._meta
        self.assertEqual(meta.ordering, ['-created_at'])
        self.assertEqual(meta.verbose_name, 'Commentaire')
        self.assertEqual(meta.verbose_name_plural, 'Commentaires')

    def test_comment_cascade_delete_with_article(self):
        """Test de suppression en cascade avec l'article."""
        comment = Comment.objects.create(
            article=self.article,
            author=self.user,
            content="Commentaire de test"
        )
        comment_id = comment.id
        
        # Supprimer l'article
        self.article.delete()
        
        # Le commentaire doit aussi être supprimé
        self.assertFalse(Comment.objects.filter(id=comment_id).exists())

    def test_comment_cascade_delete_with_user(self):
        """Test de suppression en cascade avec l'utilisateur."""
        comment = Comment.objects.create(
            article=self.article,
            author=self.user,
            content="Commentaire de test"
        )
        comment_id = comment.id
        
        # Supprimer l'utilisateur
        self.user.delete()
        
        # Le commentaire doit aussi être supprimé
        self.assertFalse(Comment.objects.filter(id=comment_id).exists())
