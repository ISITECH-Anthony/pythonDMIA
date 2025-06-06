from django import forms
from ..models import Article, Comment, Tag


class ArticleForm(forms.ModelForm):
    """Formulaire pour créer et modifier des articles"""

    tags_input = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={
                "placeholder": "Ajoutez un tag...",
                "class": "w-full px-4 py-3 pr-20 border border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-200 bg-gray-50 focus:bg-white dark:bg-gray-700 dark:border-gray-600 dark:text-white dark:focus:border-blue-400 dark:focus:ring-blue-400",
                "id": "tags-input",
                "autocomplete": "off",
                "data-no-submit": "true",
            }
        ),
        help_text="Les tags aident à catégoriser votre article et le rendre plus facilement trouvable",
    )

    tags_data = forms.CharField(
        required=False,
        widget=forms.HiddenInput(attrs={"id": "tags-data"}),
        help_text="Données des tags (géré automatiquement)",
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Rendre certains champs obligatoires
        self.fields["title"].required = True
        self.fields["category"].required = True
        self.fields["content"].required = True

        # L'image est conditionnellement requise (pas requise si image IA fournie)
        # La validation se fait dans clean_image()
        self.fields["image"].required = False

        # Si nous éditons un article existant, pré-remplir les tags
        if self.instance and self.instance.pk:
            import json

            existing_tags = []
            for tag in self.instance.tags.all():
                existing_tags.append(
                    {"id": tag.id, "name": tag.name, "color": tag.color}
                )

            # Pré-remplir le champ caché avec les tags existants
            self.fields["tags_data"].initial = json.dumps(existing_tags)

    class Meta:
        model = Article
        fields = ["title", "category", "content", "image", "is_published"]
        widgets = {
            "title": forms.TextInput(
                attrs={
                    "placeholder": "Entrez un titre accrocheur...",
                    "class": "w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-200 bg-gray-50 focus:bg-white dark:bg-gray-700 dark:border-gray-600 dark:text-white dark:focus:border-blue-400 dark:focus:ring-blue-400",
                }
            ),
            "category": forms.HiddenInput(),
            "content": forms.Textarea(
                attrs={
                    "rows": 8,
                    "placeholder": "Rédigez votre article ici... Partagez vos idées, expériences et connaissances avec la communauté.",
                    "class": "w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-200 bg-gray-50 focus:bg-white resize-none dark:bg-gray-700 dark:border-gray-600 dark:text-white dark:focus:border-blue-400 dark:focus:ring-blue-400",
                }
            ),
            "image": forms.FileInput(
                attrs={
                    "class": "w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-200 bg-gray-50 focus:bg-white file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-sm file:font-medium file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100 dark:bg-gray-700 dark:border-gray-600 dark:text-white dark:focus:border-blue-400 dark:focus:ring-blue-400 dark:file:bg-blue-900 dark:file:text-blue-300 dark:hover:file:bg-blue-800",
                    "accept": ".jpg,.jpeg,.png,.webp",
                }
            ),
            "is_published": forms.CheckboxInput(
                attrs={
                    "class": "h-5 w-5 text-blue-600 border-gray-300 rounded focus:ring-blue-500 focus:ring-2 dark:border-gray-600 dark:bg-gray-700 dark:checked:bg-blue-600 dark:focus:ring-blue-500"
                }
            ),
        }
        labels = {
            "title": "Titre *",
            "category": "Catégorie *",
            "content": "Contenu *",
            "image": "Image d'illustration *",
            "is_published": "Publier immédiatement",
        }

    def clean_title(self):
        """Validation du titre"""
        title = self.cleaned_data.get("title")
        if not title or not title.strip():
            raise forms.ValidationError("Le titre est obligatoire.")
        if len(title.strip()) < 3:
            raise forms.ValidationError("Le titre doit contenir au moins 3 caractères.")
        if len(title.strip()) > 200:
            raise forms.ValidationError("Le titre ne peut pas dépasser 200 caractères.")
        return title.strip()

    def clean_category(self):
        """Validation de la catégorie"""
        category = self.cleaned_data.get("category")
        if not category:
            raise forms.ValidationError("Veuillez sélectionner une catégorie.")
        return category

    def clean_content(self):
        """Validation du contenu"""
        content = self.cleaned_data.get("content")
        if not content or not content.strip():
            raise forms.ValidationError("Le contenu de l'article est obligatoire.")
        if len(content.strip()) < 50:
            raise forms.ValidationError(
                "Le contenu doit contenir au moins 50 caractères."
            )
        return content.strip()

    def clean_image(self):
        """Validation de l'image"""
        image = self.cleaned_data.get("image")

        # Vérifier s'il y a une image générée par IA dans les données POST
        ai_image_path = None
        if hasattr(self, "data") and self.data:
            ai_image_path = self.data.get("ai_generated_image_path", "").strip()

        # Si pas d'image uploadée ET pas d'image IA, erreur
        if not image and not ai_image_path:
            raise forms.ValidationError(
                "Une image d'illustration est obligatoire pour publier votre article."
            )

        # Si une image est uploadée, valider ses propriétés
        if image:
            import os

            # Vérifier la taille du fichier (max 5MB)
            if hasattr(image, "size") and image.size > 5 * 1024 * 1024:
                raise forms.ValidationError("L'image ne peut pas dépasser 5 MB.")

            # Vérifier l'extension du fichier
            file_name = getattr(image, "name", "")
            if file_name:
                file_extension = os.path.splitext(file_name)[1].lower()
                allowed_extensions = [".jpg", ".jpeg", ".png", ".webp"]
                if file_extension not in allowed_extensions:
                    raise forms.ValidationError(
                        "Extension de fichier non supportée. Utilisez .jpg, .jpeg, .png ou .webp uniquement."
                    )

            # Vérifier le format de l'image (type MIME)
            if hasattr(image, "content_type"):
                allowed_types = ["image/jpeg", "image/png", "image/webp"]
                if image.content_type not in allowed_types:
                    raise forms.ValidationError(
                        "Format d'image non supporté. Utilisez JPG, PNG ou WebP uniquement."
                    )

        return image

    def clean(self):
        """Validation globale du formulaire"""
        cleaned_data = super().clean()

        # Vérifier que tous les champs obligatoires sont présents
        required_fields = ["title", "category", "content", "image"]
        missing_fields = []

        for field_name in required_fields:
            field_value = cleaned_data.get(field_name)
            if not field_value:
                missing_fields.append(self.Meta.labels.get(field_name, field_name))

        if missing_fields:
            raise forms.ValidationError(
                f"Les champs suivants sont obligatoires : {', '.join(missing_fields)}"
            )

        return cleaned_data

    def save(self, commit=True):
        import json
        import re

        instance = super().save(commit=commit)

        if commit:
            # Récupérer les données des tags depuis le champ caché
            tags_data_raw = self.cleaned_data.get("tags_data", "")

            try:
                if tags_data_raw:
                    tags_data = json.loads(tags_data_raw)
                else:
                    tags_data = []
            except json.JSONDecodeError:
                tags_data = []

            # Validations des tags
            MAX_TAGS = 5
            MIN_TAG_LENGTH = 2
            MAX_TAG_LENGTH = 20

            # Filtrer et valider les tags
            valid_tags = []
            for tag_data in tags_data:
                if not isinstance(tag_data, dict) or not tag_data.get("name"):
                    continue

                tag_name = tag_data["name"].strip()

                # Vérifications de validité
                if len(tag_name) < MIN_TAG_LENGTH or len(tag_name) > MAX_TAG_LENGTH:
                    continue

                # Vérifier les caractères autorisés
                if not re.match(
                    r"^[a-zA-Z0-9\s\-_àáâäèéêëìíîïòóôöùúûüýÿñç]+$", tag_name
                ):
                    continue

                valid_tags.append(tag_data)

                # Limiter le nombre de tags
                if len(valid_tags) >= MAX_TAGS:
                    break

            # Récupérer les tags existants
            existing_tags = instance.tags.all()
            existing_tag_ids = [tag.id for tag in existing_tags]

            # Identifier les tags à supprimer (existants mais pas dans la nouvelle liste)
            new_tag_ids = [tag.get("id") for tag in valid_tags if tag.get("id")]
            tags_to_delete_ids = [
                tag_id for tag_id in existing_tag_ids if tag_id not in new_tag_ids
            ]

            # Supprimer les tags qui ne sont plus présents
            if tags_to_delete_ids:
                Tag.objects.filter(id__in=tags_to_delete_ids, article=instance).delete()

            # Créer les nouveaux tags (ceux sans ID)
            for tag_data in valid_tags:
                if not tag_data.get("id") and tag_data.get("name"):
                    Tag.objects.create(
                        name=tag_data["name"],
                        color=tag_data.get("color", "#3B82F6"),
                        article=instance,
                    )

        return instance


class CommentForm(forms.ModelForm):
    """Formulaire pour créer des commentaires (utilisateurs connectés uniquement)"""

    class Meta:
        model = Comment
        fields = ["content"]
        widgets = {
            "content": forms.Textarea(
                attrs={
                    "rows": 4,
                    "placeholder": "Partagez votre opinion sur cet article...",
                    "class": "w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-200 bg-gray-50 focus:bg-white resize-none dark:bg-gray-700 dark:border-gray-600 dark:text-white dark:focus:border-blue-400 dark:focus:ring-blue-400",
                }
            ),
        }
        labels = {"content": "Votre commentaire"}
