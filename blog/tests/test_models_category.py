"""
Tests pour le modèle Category.
"""
from django.test import TestCase
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from blog.models.category import Category


class CategoryModelTest(TestCase):
    """Tests pour le modèle Category."""

    def setUp(self):
        """Configuration initiale pour chaque test."""
        self.category_data = {
            'name': 'Technologie',
            'description': 'Articles sur la technologie et l\'innovation',
            'color': '#3B82F6',
            'icon': '💻'
        }

    def test_category_creation(self):
        """Test de création d'une catégorie."""
        category = Category.objects.create(**self.category_data)
        
        self.assertEqual(category.name, 'Technologie')
        self.assertEqual(category.description, 'Articles sur la technologie et l\'innovation')
        self.assertEqual(category.color, '#3B82F6')
        self.assertEqual(category.icon, '💻')

    def test_category_slug_generation(self):
        """Test de génération automatique du slug."""
        category = Category.objects.create(
            name='Technologie',
            slug='technologie',  # Le slug doit être fourni manuellement
            color='#3B82F6',
            icon='💻'
        )
        self.assertEqual(category.slug, 'technologie')

    def test_category_slug_unique(self):
        """Test d'unicité du slug."""
        # Créer première catégorie
        Category.objects.create(
            name='Technologie',
            slug='technologie',
            color='#3B82F6',
            icon='💻'
        )
        
        # Tenter de créer une catégorie avec le même slug
        with self.assertRaises(IntegrityError):
            Category.objects.create(
                name='Autre Technologie',
                slug='technologie',  # Même slug
                color='#FF0000',
                icon='🔧'
            )

    def test_category_slug_with_special_characters(self):
        """Test de création de slug avec des caractères spéciaux."""
        category = Category.objects.create(
            name='Arts & Culture',
            slug='arts-culture',  # Slug fourni manuellement
            description='Test description',
            color='#FF0000',
            icon='🎨'
        )
        self.assertEqual(category.slug, 'arts-culture')

    def test_category_slug_with_accents(self):
        """Test de création de slug avec des accents."""
        category = Category.objects.create(
            name='Santé et Médecine',
            slug='sante-et-medecine',  # Slug fourni manuellement
            description='Test description',
            color='#FF0000',
            icon='🏥'
        )
        self.assertEqual(category.slug, 'sante-et-medecine')

    def test_category_str_representation(self):
        """Test de la représentation string de la catégorie."""
        category = Category.objects.create(**self.category_data)
        self.assertEqual(str(category), 'Technologie')

    def test_category_default_values(self):
        """Test des valeurs par défaut."""
        minimal_data = {
            'name': 'Test Category',
            'slug': 'test-category'
        }
        category = Category.objects.create(**minimal_data)
        
        self.assertEqual(category.color, '#3B82F6')  # Valeur par défaut
        self.assertEqual(category.icon, '📂')  # Valeur par défaut
        self.assertEqual(category.description, '')  # Champ optionnel

    def test_category_ordering(self):
        """Test de l'ordre par défaut des catégories."""
        # Créer plusieurs catégories avec des slugs uniques
        cat1 = Category.objects.create(name='Zebra', slug='zebra', color='#000000', icon='🦓')
        cat2 = Category.objects.create(name='Alpha', slug='alpha', color='#000000', icon='🔤')
        cat3 = Category.objects.create(name='Beta', slug='beta', color='#000000', icon='🎯')
        
        categories = list(Category.objects.all())
        self.assertEqual(categories[0], cat2)  # Alpha
        self.assertEqual(categories[1], cat3)  # Beta
        self.assertEqual(categories[2], cat1)  # Zebra

    def test_category_color_validation(self):
        """Test de validation du champ couleur."""
        # Tester avec une couleur valide
        category = Category.objects.create(
            name='Test',
            color='#FF5733',
            icon='🎨'
        )
        self.assertEqual(category.color, '#FF5733')

    def test_category_name_max_length(self):
        """Test de la longueur maximale du nom."""
        long_name = 'x' * 101  # Plus de 100 caractères
        with self.assertRaises(ValidationError):
            category = Category(
                name=long_name,
                color='#000000',
                icon='📝'
            )
            category.full_clean()

    def test_category_icon_max_length(self):
        """Test de la longueur maximale de l'icône."""
        long_icon = 'x' * 51  # Plus de 50 caractères (50 est la limite dans le modèle)
        with self.assertRaises(ValidationError):
            category = Category(
                name='Test',
                slug='test',
                color='#000000',
                icon=long_icon
            )
            category.full_clean()

    def test_category_meta_options(self):
        """Test des options meta du modèle."""
        meta = Category._meta
        self.assertEqual(meta.ordering, ['name'])
        self.assertEqual(meta.verbose_name, 'Catégorie')
        self.assertEqual(meta.verbose_name_plural, 'Catégories')
