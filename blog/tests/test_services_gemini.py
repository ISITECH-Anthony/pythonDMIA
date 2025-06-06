"""
Tests pour le service Gemini - Version simplifiée.
"""
from django.test import TestCase, override_settings
from django.contrib.auth import get_user_model
from unittest.mock import patch, MagicMock
from blog.models.category import Category
from blog.services.gemini import GeminiService

User = get_user_model()


class GeminiServiceTest(TestCase):
    """Tests pour le service Gemini."""

    def setUp(self):
        """Configuration initiale pour chaque test."""
        # Créer une catégorie de test
        self.category = Category.objects.create(
            name='Technologie',
            color='#0000FF',
            icon='💻',
            description='Articles sur la technologie'
        )

    @override_settings(GEMINI_API_KEY='test-api-key')
    @patch('blog.services.gemini.genai.configure')
    @patch('blog.services.gemini.config')
    def test_gemini_service_initialization(self, mock_config, mock_configure):
        """Test d'initialisation du service Gemini."""
        mock_config.return_value = 'test-api-key'
        
        service = GeminiService()
        
        mock_configure.assert_called_once_with(api_key='test-api-key')

    @patch('blog.services.gemini.config')
    def test_missing_api_key(self, mock_config):
        """Test de gestion de clé API manquante."""
        mock_config.return_value = ""
        
        with self.assertRaises(ValueError):
            GeminiService()

    @patch('blog.services.gemini.config')
    def test_empty_api_key(self, mock_config):
        """Test de gestion de clé API vide."""
        mock_config.return_value = None
        
        with self.assertRaises(ValueError):
            GeminiService()

    @override_settings(GEMINI_API_KEY='test-api-key')
    @patch('blog.services.gemini.genai.configure')
    @patch('blog.services.gemini.config')
    def test_get_available_categories(self, mock_config, mock_configure):
        """Test de récupération des catégories disponibles."""
        mock_config.return_value = 'test-api-key'
        
        service = GeminiService()
        categories = service.get_available_categories()
        
        self.assertEqual(len(categories), 1)
        self.assertEqual(categories[0]['name'], 'Technologie')

    @override_settings(GEMINI_API_KEY='test-api-key')
    @patch('blog.services.gemini.genai.configure')
    @patch('blog.services.gemini.config')
    def test_build_prompt(self, mock_config, mock_configure):
        """Test de construction du prompt."""
        mock_config.return_value = 'test-api-key'
        
        service = GeminiService()
        user_prompt = "Écris un article sur l'IA"
        options = {"length": "medium", "tone": "professional"}
        
        prompt = service.build_prompt(user_prompt, options)
        
        self.assertIn(user_prompt, prompt)
        self.assertIn("moyen (400-800 mots)", prompt)
        self.assertIn("professionnel et formel", prompt)
        self.assertIn("Technologie", prompt)

    @override_settings(GEMINI_API_KEY='test-api-key')
    @patch('blog.services.gemini.genai.configure')
    @patch('blog.services.gemini.config')
    def test_generate_article_success(self, mock_config, mock_configure):
        """Test de génération d'article réussie."""
        mock_config.return_value = 'test-api-key'
        
        service = GeminiService()
        
        # Mock de la réponse Gemini
        mock_response = MagicMock()
        mock_response.text = '''
        {
            "title": "Intelligence Artificielle : L'avenir de la technologie",
            "content": "L'intelligence artificielle représente une révolution technologique majeure...",
            "category_id": ''' + str(self.category.id) + ''',
            "tags": ["IA", "technologie", "innovation", "futur", "automatisation"]
        }
        '''
        
        with patch.object(service.model, 'generate_content', return_value=mock_response):
            result = service.generate_article(
                user_prompt="Intelligence Artificielle",
                options={"length": "medium", "tone": "professional"}
            )
        
        self.assertTrue(result['success'])
        data = result['data']
        self.assertEqual(data['title'], "Intelligence Artificielle : L'avenir de la technologie")
        self.assertIn("révolution technologique", data['content'])
        self.assertEqual(data['category_id'], self.category.id)
        self.assertEqual(len(data['tags']), 5)

    @override_settings(GEMINI_API_KEY='test-api-key')
    @patch('blog.services.gemini.genai.configure')
    @patch('blog.services.gemini.config')
    def test_generate_article_empty_response(self, mock_config, mock_configure):
        """Test de gestion de réponse vide."""
        mock_config.return_value = 'test-api-key'
        
        service = GeminiService()
        
        # Mock de réponse vide
        mock_response = MagicMock()
        mock_response.text = ""
        
        with patch.object(service.model, 'generate_content', return_value=mock_response):
            result = service.generate_article(
                user_prompt="Test Topic",
                options={"length": "medium", "tone": "professional"}
            )
            # Le service retourne un dict avec success=False en cas d'erreur
            self.assertFalse(result['success'])
            self.assertIn('error', result)

    @override_settings(GEMINI_API_KEY='test-api-key')
    @patch('blog.services.gemini.genai.configure')
    @patch('blog.services.gemini.config')
    def test_generate_article_invalid_json(self, mock_config, mock_configure):
        """Test de gestion de JSON invalide."""
        mock_config.return_value = 'test-api-key'
        
        service = GeminiService()
        
        # Mock de réponse avec JSON invalide
        mock_response = MagicMock()
        mock_response.text = "Ceci n'est pas du JSON valide"
        
        with patch.object(service.model, 'generate_content', return_value=mock_response):
            result = service.generate_article(
                user_prompt="Test Topic",
                options={"length": "medium", "tone": "professional"}
            )
            # Le service retourne un dict avec success=False en cas d'erreur
            self.assertFalse(result['success'])
            self.assertIn('error', result)
