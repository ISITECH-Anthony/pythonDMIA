import google.generativeai as genai
import json
import logging
import base64
import requests
from typing import Dict, Any, List, Optional
from django.conf import settings
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from decouple import config
from blog.models import Category, Tag
from .dalle import DalleService
import uuid
import os

logger = logging.getLogger(__name__)


class GeminiService:
    """Service pour la génération d'articles avec Google Gemini"""

    def __init__(self):
        # Configuration de l'API Gemini
        api_key = config("GEMINI_API_KEY", default="")
        if not api_key:
            raise ValueError(
                "La clé API Gemini n'est pas configurée. Ajoutez GEMINI_API_KEY dans votre fichier .env"
            )

        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel("gemini-2.0-flash")

        # Initialiser le service DALL-E
        try:
            self.dalle_service = DalleService()
        except ValueError as e:
            logger.warning(f"Service DALL-E non disponible: {str(e)}")
            self.dalle_service = None

    def get_available_categories(self) -> List[Dict[str, Any]]:
        """Récupère la liste des catégories disponibles"""
        categories = Category.objects.all().values("id", "name", "description")
        return list(categories)

    def build_prompt(self, user_prompt: str, options: Dict[str, str]) -> str:
        """Construit le prompt complet pour Gemini"""
        categories = self.get_available_categories()
        categories_list = "\n".join(
            [
                f"- ID: {cat['id']}, Nom: {cat['name']}, Description: {cat['description']}"
                for cat in categories
            ]
        )

        # Mappage des options
        length_mapping = {
            "short": "court (200-400 mots)",
            "medium": "moyen (400-800 mots)",
            "long": "long (800-1500 mots)",
        }

        tone_mapping = {
            "professional": "professionnel et formel",
            "casual": "décontracté et accessible",
            "educational": "éducatif et pédagogique",
            "entertaining": "divertissant et engageant",
            "persuasive": "persuasif et convaincant",
        }

        article_length = length_mapping.get(
            options.get("length", "medium"), "moyen (400-800 mots)"
        )
        article_tone = tone_mapping.get(
            options.get("tone", "professional"), "professionnel et formel"
        )

        prompt = f"""
Tu es un expert rédacteur de blog. Tu dois générer un article de blog complet en français basé sur la demande de l'utilisateur.

DEMANDE DE L'UTILISATEUR:
{user_prompt}

PARAMÈTRES DE L'ARTICLE:
- Longueur: {article_length}
- Ton: {article_tone}

CATÉGORIES DISPONIBLES:
{categories_list}

INSTRUCTIONS:
1. Génère un titre accrocheur et pertinent
2. Rédige un contenu de qualité avec une structure claire (introduction, développement, conclusion)
3. Sélectionne la catégorie la plus appropriée parmi celles disponibles
4. Crée jusqu'à 5 tags pertinents en rapport avec le sujet
5. Respecte le ton et la longueur demandés

RÉPONSE REQUISE:
Tu dois répondre UNIQUEMENT avec un objet JSON valide dans ce format exact:
{{
    "title": "Titre de l'article",
    "content": "Contenu complet de l'article avec des paragraphes bien structurés",
    "category_id": 1,
    "tags": ["tag1", "tag2", "tag3", "tag4", "tag5"]
}}

IMPORTANT: 
- La réponse doit être un JSON valide UNIQUEMENT
- Le contenu doit être riche et bien structuré
- Les tags doivent être pertinents et en français
- Choisis la category_id qui correspond le mieux au sujet
- Maximum 5 tags
"""

        return prompt

    def generate_image(self, title: str, content: str) -> Optional[str]:
        """
        Génère une image pour l'article avec DALL-E

        Args:
            title: Titre de l'article
            content: Contenu de l'article

        Returns:
            Chemin vers l'image générée ou None en cas d'erreur
        """
        if not self.dalle_service:
            logger.warning("Service DALL-E non disponible")
            return None

        try:
            logger.info(f"Génération d'image DALL-E pour l'article: {title[:50]}...")

            # Utiliser le service DALL-E pour générer l'image
            image_path = self.dalle_service.generate_image(title, content)

            if image_path:
                logger.info(f"Image DALL-E générée avec succès: {image_path}")
                return image_path
            else:
                logger.warning("Échec de la génération d'image avec DALL-E")
                return None

        except Exception as e:
            logger.error(f"Erreur lors de la génération d'image DALL-E: {str(e)}")
            return None

    def generate_article(
        self, user_prompt: str, options: Dict[str, str]
    ) -> Dict[str, Any]:
        """
        Génère un article avec Gemini et optionnellement une image

        Args:
            user_prompt: Prompt de l'utilisateur
            options: Options de génération (length, tone, generate_image)

        Returns:
            Dict contenant title, content, category_id, tags, et optionnellement image_path
        """
        try:
            # Construction du prompt complet
            full_prompt = self.build_prompt(user_prompt, options)

            logger.info(
                f"Génération d'article avec Gemini pour le prompt: {user_prompt[:50]}..."
            )

            # Génération avec Gemini
            response = self.model.generate_content(full_prompt)

            if not response.text:
                raise ValueError("Aucune réponse reçue de Gemini")

            # Tentative de parsing JSON
            try:
                result = json.loads(response.text.strip())
            except json.JSONDecodeError:
                # Si le JSON n'est pas valide, on essaie d'extraire le JSON du texte
                text = response.text.strip()
                start_idx = text.find("{")
                end_idx = text.rfind("}") + 1
                if start_idx != -1 and end_idx > start_idx:
                    json_text = text[start_idx:end_idx]
                    result = json.loads(json_text)
                else:
                    raise ValueError("Impossible de parser la réponse JSON de Gemini")

            # Validation des champs requis
            required_fields = ["title", "content", "category_id", "tags"]
            for field in required_fields:
                if field not in result:
                    raise ValueError(f"Champ manquant dans la réponse: {field}")

            # Validation de la catégorie
            if not Category.objects.filter(id=result["category_id"]).exists():
                # Si la catégorie n'existe pas, on prend la première disponible
                first_category = Category.objects.first()
                if first_category:
                    result["category_id"] = first_category.id
                    logger.warning(
                        f"Catégorie ID {result['category_id']} non trouvée, utilisation de {first_category.id}"
                    )
                else:
                    raise ValueError(
                        "Aucune catégorie disponible dans la base de données"
                    )

            # Validation et nettoyage des tags
            if not isinstance(result["tags"], list):
                result["tags"] = []

            # Limiter à 5 tags maximum et nettoyer
            result["tags"] = [tag.strip() for tag in result["tags"][:5] if tag.strip()]

            # Génération d'image si demandée
            generate_image = options.get("generate_image", False)
            if generate_image:
                logger.info("Génération d'image demandée...")
                image_path = self.generate_image(result["title"], result["content"])
                if image_path:
                    # Convertir le chemin relatif en URL complète pour le frontend
                    if self.dalle_service:
                        image_url = self.dalle_service.get_image_url(image_path)
                        result["image_path"] = image_url
                        result["image_file_path"] = (
                            image_path  # Garder aussi le chemin relatif pour la sauvegarde
                        )
                        logger.info(
                            f"Image générée avec succès: {image_path} -> {image_url}"
                        )
                    else:
                        result["image_path"] = image_path
                        logger.info(f"Image générée avec succès: {image_path}")
                else:
                    logger.warning(
                        "Échec de la génération d'image, l'article sera créé sans image"
                    )

            logger.info(f"Article généré avec succès: '{result['title'][:50]}...'")

            return {"success": True, "data": result}

        except Exception as e:
            logger.error(
                f"Erreur lors de la génération d'article avec Gemini: {str(e)}"
            )
            return {
                "success": False,
                "error": f"Erreur lors de la génération: {str(e)}",
            }

    def validate_api_key(self) -> bool:
        """Valide que l'API key Gemini fonctionne"""
        try:
            # Test simple avec un prompt minimal
            response = self.model.generate_content("Test de connexion")
            return bool(response.text)
        except Exception as e:
            logger.error(f"Validation API key Gemini échouée: {str(e)}")
            return False
