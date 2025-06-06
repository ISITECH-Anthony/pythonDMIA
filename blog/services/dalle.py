import requests
import json
import logging
import uuid
import os
from typing import Optional
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.conf import settings
from decouple import config

logger = logging.getLogger(__name__)


class DalleService:
    """Service pour la génération d'images avec DALL-E 3"""

    def __init__(self):
        # Configuration de l'API OpenAI
        self.api_key = config("OPENAI_API_KEY", default="")
        if not self.api_key:
            raise ValueError(
                "La clé API OpenAI n'est pas configurée. Ajoutez OPENAI_API_KEY dans votre fichier .env"
            )

        self.base_url = "https://api.openai.com/v1/images/generations"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    def create_image_prompt(self, article_title: str, article_content: str) -> str:
        """
        Crée un prompt optimisé pour DALL-E basé sur le titre et contenu de l'article
        """
        # Extraire les mots-clés principaux du titre
        title_keywords = article_title.lower()

        # Créer un prompt visuel optimisé
        prompt = f"""Create a professional, high-quality illustration for a blog article titled "{article_title}". 
        The image should be modern, clean, and visually appealing. Style: minimalist, professional, 
        suitable for a blog header. Colors: use a harmonious color palette. 
        The image should represent the main concept without text overlays. 
        High resolution, suitable for web use."""

        # Limiter à 1000 caractères (limite DALL-E)
        if len(prompt) > 1000:
            prompt = prompt[:997] + "..."

        logger.info(f"Prompt DALL-E généré: {prompt}")
        return prompt

    def generate_image(self, article_title: str, article_content: str) -> Optional[str]:
        """
        Génère une image avec DALL-E et la sauvegarde

        Args:
            article_title: Titre de l'article
            article_content: Contenu de l'article

        Returns:
            str: Chemin relatif de l'image sauvegardée ou None si erreur
        """
        try:
            # Créer le prompt optimisé
            prompt = self.create_image_prompt(article_title, article_content)

            # Préparer la requête pour DALL-E 3
            payload = {
                "model": "dall-e-3",
                "prompt": prompt,
                "n": 1,
                "size": "1024x1024",
                "quality": "standard",
                "style": "natural",
            }

            logger.info("Envoi de la requête à DALL-E...")

            # Appel à l'API DALL-E
            response = requests.post(
                self.base_url,
                headers=self.headers,
                json=payload,
                timeout=60,  # 60 secondes timeout
            )

            if response.status_code != 200:
                logger.error(
                    f"Erreur API DALL-E: {response.status_code} - {response.text}"
                )
                return None

            # Parser la réponse
            data = response.json()

            if not data.get("data") or len(data["data"]) == 0:
                logger.error("Aucune image générée par DALL-E")
                return None

            # Récupérer l'URL de l'image générée
            image_url = data["data"][0]["url"]
            logger.info(f"Image générée avec succès: {image_url}")

            # Télécharger et sauvegarder l'image
            saved_path = self._download_and_save_image(image_url)

            return saved_path

        except requests.exceptions.Timeout:
            logger.error("Timeout lors de la génération d'image avec DALL-E")
            return None
        except requests.exceptions.RequestException as e:
            logger.error(f"Erreur de requête DALL-E: {str(e)}")
            return None
        except json.JSONDecodeError as e:
            logger.error(f"Erreur de parsing JSON DALL-E: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Erreur inattendue lors de la génération d'image: {str(e)}")
            return None

    def _download_and_save_image(self, image_url: str) -> Optional[str]:
        """
        Télécharge l'image depuis l'URL et la sauvegarde dans le système de fichiers Django

        Args:
            image_url: URL de l'image à télécharger

        Returns:
            str: Chemin relatif de l'image sauvegardée ou None si erreur
        """
        try:
            # Télécharger l'image
            logger.info(f"Téléchargement de l'image depuis: {image_url}")
            response = requests.get(image_url, timeout=30)
            response.raise_for_status()

            # Générer un nom de fichier unique
            filename = f"ai_generated_{uuid.uuid4().hex[:8]}.png"
            filepath = f"articles/{filename}"

            # Créer un objet ContentFile
            content_file = ContentFile(response.content, name=filename)

            # Sauvegarder avec le système de stockage Django
            saved_path = default_storage.save(filepath, content_file)

            logger.info(f"Image sauvegardée avec succès: {saved_path}")
            return saved_path

        except requests.exceptions.RequestException as e:
            logger.error(f"Erreur lors du téléchargement de l'image: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Erreur lors de la sauvegarde de l'image: {str(e)}")
            return None

    def get_image_url(self, image_path: str) -> str:
        """
        Retourne l'URL complète d'une image sauvegardée

        Args:
            image_path: Chemin relatif de l'image

        Returns:
            str: URL complète de l'image
        """
        if image_path:
            return default_storage.url(image_path)
        return ""
