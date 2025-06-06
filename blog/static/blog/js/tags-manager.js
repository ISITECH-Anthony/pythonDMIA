/**
 * Gestionnaire de tags pour les articles
 * Permet d'ajouter/supprimer des tags avec une interface interactive
 */

class TagsManager {
    constructor() {
        this.tagsContainer = document.getElementById('tags-container');
        this.tagsInput = document.getElementById('tags-input');
        this.tagsDataInput = document.getElementById('tags-data');
        this.tags = [];

        // Limitations
        this.maxTags = 5;           // Nombre maximum de tags
        this.minTagLength = 2;      // Longueur minimale d'un tag
        this.maxTagLength = 20;     // Longueur maximale d'un tag

        // Couleurs prédéfinies pour les tags (noms de couleurs Tailwind)
        this.colors = [
            'blue',
            'green', 
            'yellow',
            'orange',
            'red',
            'purple',
            'pink',
            'indigo',
            'teal',
            'cyan',
            'lime',
            'emerald',
            'violet',
            'fuchsia',
            'rose',
            'sky',
            'amber',
            'slate'
        ];

        this.init();
    }

    init() {
        if (!this.tagsContainer || !this.tagsInput || !this.tagsDataInput) {
            return;
        }

        // Charger les tags existants depuis le champ caché
        this.loadExistingTags();

        // Initialiser les références aux éléments du DOM
        this.initDOMReferences();

        // Empêcher la soumission du formulaire par l'input des tags
        this.preventFormSubmission();

        // Événements
        this.tagsInput.addEventListener('keydown', (e) => this.handleKeyDown(e));
        this.tagsInput.addEventListener('keypress', (e) => this.handleKeyPress(e));
        this.tagsInput.addEventListener('blur', () => this.addTagFromInput());
        this.tagsInput.addEventListener('input', (e) => this.validateInput(e));

        // Mettre à jour l'affichage initial
        this.updateDisplay();
        this.updateHiddenField();
        this.updateInputPlaceholder();
        this.updateTagsCounter();
        
        // Émettre l'événement initial pour synchroniser tous les compteurs
        this.emitTagsChangeEvent();
    }

    initDOMReferences() {
        // Références aux éléments de messages
        this.helpElement = document.getElementById('tags-help');
        this.errorElement = document.getElementById('tags-error');
        this.errorTextElement = document.getElementById('tags-error-text');
        this.charCounterElement = document.getElementById('tags-char-counter');
        this.tagsCountElement = document.getElementById('tags-count');

        // Vérifier que tous les éléments existent
        if (!this.helpElement || !this.errorElement || !this.errorTextElement || !this.charCounterElement || !this.tagsCountElement) {
            console.error('Éléments de message des tags non trouvés dans le DOM');
            return;
        }

        // Charger les messages prédéfinis
        this.loadMessages();
    }

    loadMessages() {
        // Charger tous les messages depuis les attributs data-msg
        this.messages = {};
        const messageElements = document.querySelectorAll('[data-msg]');
        messageElements.forEach(el => {
            const key = el.getAttribute('data-msg');
            this.messages[key] = el.textContent;
        });
    }

    preventFormSubmission() {
        // Ajouter l'attribut pour empêcher la soumission du formulaire
        this.tagsInput.setAttribute('data-no-submit', 'true');

        // Trouver le formulaire parent
        const form = this.tagsInput.closest('form');
        if (form) {
            // Intercepter la soumission du formulaire
            form.addEventListener('submit', (e) => {
                // Si le focus est sur l'input des tags, empêcher la soumission
                if (document.activeElement === this.tagsInput) {
                    e.preventDefault();
                    this.addTagFromInput();
                    return false;
                }
            });

            // Gestionnaire keydown au niveau du formulaire
            form.addEventListener('keydown', (e) => {
                if (e.target === this.tagsInput && e.key === 'Enter') {
                    e.preventDefault();
                    e.stopPropagation();
                    e.stopImmediatePropagation();
                    this.addTagFromInput();
                    return false;
                }
            });

            // Gestionnaire keypress au niveau du formulaire
            form.addEventListener('keypress', (e) => {
                if (e.target === this.tagsInput && e.key === 'Enter') {
                    e.preventDefault();
                    e.stopPropagation();
                    e.stopImmediatePropagation();
                    return false;
                }
            });
        }
    }

    loadExistingTags() {
        const tagsDataValue = this.tagsDataInput.value;
        if (tagsDataValue) {
            try {
                this.tags = JSON.parse(tagsDataValue);
            } catch (e) {
                console.error('Erreur lors du chargement des tags existants:', e);
                this.tags = [];
            }
        }
    }

    handleKeyDown(e) {
        if (e.key === 'Enter') {
            e.preventDefault();
            e.stopPropagation();
            e.stopImmediatePropagation();
            this.addTagFromInput();
            return false;
        } else if (e.key === 'Backspace' && this.tagsInput.value === '') {
            // Supprimer le dernier tag si l'input est vide
            e.preventDefault();
            this.removeLastTag();
        }
    }

    handleKeyPress(e) {
        if (e.key === 'Enter') {
            e.preventDefault();
            e.stopPropagation();
            e.stopImmediatePropagation();
            return false;
        }
    }

    addTagFromInput() {
        const value = this.tagsInput.value.trim();
        if (value) {
            const success = this.addTag(value);
            if (success) {
                this.tagsInput.value = '';
                this.updateCharCounter(); // Mettre à jour le compteur après vidage
            }
        }
    }

    validateInput(e) {
        const value = e.target.value;
        this.updateCharCounter(value);
    }

    updateCharCounter(value = null) {
        const length = value !== null ? value.length : this.tagsInput.value.length;

        // Vérifier que le compteur existe
        if (!this.charCounterElement) {
            console.warn('Compteur de caractères non trouvé');
            return;
        }

        // Mettre à jour le compteur de caractères
        this.charCounterElement.textContent = `${length}/${this.maxTagLength}`;

        // Gérer les couleurs du compteur selon la validité
        // Retirer toutes les classes de couleur existantes
        this.charCounterElement.classList.remove('text-gray-400', 'text-yellow-500', 'text-red-500');
        
        if (length === 0) {
            // Input vide - gris
            this.charCounterElement.classList.add('text-gray-400');
        } else if (length < this.minTagLength) {
            // Trop court (< 2) - yellow
            this.charCounterElement.classList.add('text-yellow-500');
        } else if (length <= this.maxTagLength) {
            // Longueur valide (2-20) - gris
            this.charCounterElement.classList.add('text-gray-400');
        } else {
            // Trop long (> 20) - rouge
            this.charCounterElement.classList.add('text-red-500');
        }

        // Gérer les couleurs de l'input selon la validité
        if (length === 0) {
            // Input vide - état normal
            this.tagsInput.classList.remove('border-red-300', 'border-green-300', 'bg-red-50');
            this.tagsInput.classList.add('border-gray-300');
            this.clearError();
        } else if (length > this.maxTagLength) {
            // Trop long - rouge
            this.tagsInput.classList.remove('border-green-300', 'border-gray-300');
            this.tagsInput.classList.add('border-red-300', 'bg-red-50');
        } else if (length < this.minTagLength) {
            // Trop court - neutre
            this.tagsInput.classList.remove('border-red-300', 'border-green-300', 'bg-red-50');
            this.tagsInput.classList.add('border-gray-300');
            this.clearError();
        } else {
            // Longueur valide - vert
            this.tagsInput.classList.remove('border-red-300', 'border-gray-300', 'bg-red-50');
            this.tagsInput.classList.add('border-green-300');
            this.clearError();
        }
    }

    updateTagsCounter() {
        // Vérifier que l'élément existe
        if (!this.tagsCountElement) {
            console.warn('Compteur de tags non trouvé');
            return;
        }

        // Mettre à jour le compteur de tags
        const count = this.tags.length;
        this.tagsCountElement.textContent = `${count}/${this.maxTags} tags`;

        // Changer la couleur selon le nombre de tags
        this.tagsCountElement.classList.remove('text-gray-400', 'text-yellow-500', 'text-red-400');
        
        if (count === 0) {
            this.tagsCountElement.classList.add('text-gray-400');
        } else if (count >= this.maxTags) {
            this.tagsCountElement.classList.add('text-red-400');
        } else if (count >= this.maxTags - 1) {
            this.tagsCountElement.classList.add('text-yellow-500');
        } else {
            this.tagsCountElement.classList.add('text-gray-400');
        }

        // Émettre un événement personnalisé pour notifier les autres composants
        this.emitTagsChangeEvent();
    }

    /**
     * Émet un événement personnalisé quand les tags changent
     */
    emitTagsChangeEvent() {
        const event = new CustomEvent('tagsChanged', {
            detail: {
                count: this.tags.length,
                maxTags: this.maxTags,
                tags: this.tags
            }
        });
        document.dispatchEvent(event);
    }

    addTag(name) {
        // Nettoyer le nom du tag
        name = name.trim();

        // Vérification du nombre maximum de tags
        if (this.tags.length >= this.maxTags) {
            this.showError(this.messages['max-tags']);
            return false;
        }

        // Vérification de la longueur minimale
        if (name.length < this.minTagLength) {
            this.showError(this.messages['min-length']);
            return false;
        }

        // Vérification de la longueur maximale
        if (name.length > this.maxTagLength) {
            this.showError(this.messages['max-length']);
            return false;
        }

        // Vérification des caractères autorisés (lettres, chiffres, espaces, tirets et underscores)
        const validCharPattern = /^[a-zA-Z0-9\s\-_àáâäèéêëìíîïòóôöùúûüýÿñç]+$/;
        if (!validCharPattern.test(name)) {
            this.showError(this.messages['invalid-chars']);
            return false;
        }

        // Vérifier si le tag existe déjà (insensible à la casse)
        if (this.tags.some(tag => tag.name.toLowerCase() === name.toLowerCase())) {
            this.showError(this.messages['duplicate']);
            return false;
        }

        // Créer un nouveau tag
        const newTag = {
            id: null, // Pas d'ID pour un nouveau tag
            name: name,
            color: this.getRandomColor()
        };

        this.tags.push(newTag);
        this.updateDisplay();
        this.updateHiddenField();
        this.updateInputPlaceholder();
        this.updateTagsCounter();
        this.clearError();
        return true;
    }

    removeTag(index) {
        if (index >= 0 && index < this.tags.length) {
            this.tags.splice(index, 1);
            this.updateDisplay();
            this.updateHiddenField();
            this.updateInputPlaceholder();
            this.updateTagsCounter();
            this.clearError();
        }
    }

    removeLastTag() {
        if (this.tags.length > 0) {
            this.removeTag(this.tags.length - 1);
        }
    }

    updateInputPlaceholder() {
        const remaining = this.maxTags - this.tags.length;
        if (remaining <= 0) {
            this.tagsInput.placeholder = this.messages['placeholder-max'];
            this.tagsInput.disabled = true;
        } else {
            this.tagsInput.disabled = false;
            this.tagsInput.placeholder = this.messages['placeholder-initial']
        }
    }

    updateDisplay() {
        // Vérifier si le wrapper existe déjà
        let tagsWrapper = this.tagsContainer.querySelector('.flex.flex-wrap.gap-2');
        
        if (!tagsWrapper) {
            // Créer le wrapper s'il n'existe pas
            this.tagsContainer.innerHTML = '';
            tagsWrapper = document.createElement('div');
            tagsWrapper.className = 'flex flex-wrap gap-2';
            this.tagsContainer.appendChild(tagsWrapper);
        }

        // Obtenir les éléments existants
        const existingElements = Array.from(tagsWrapper.children);
        
        // Supprimer les éléments en trop
        while (existingElements.length > this.tags.length) {
            const elementToRemove = existingElements.pop();
            elementToRemove.remove();
        }

        // Mettre à jour ou créer les éléments
        this.tags.forEach((tag, index) => {
            if (index < existingElements.length) {
                // Mettre à jour l'élément existant
                const existingElement = existingElements[index];
                const newElement = this.createTagElement(tag, index);
                existingElement.replaceWith(newElement);
            } else {
                // Créer un nouvel élément
                const tagElement = this.createTagElement(tag, index);
                tagsWrapper.appendChild(tagElement);
            }
        });
    }

    createTagElement(tag, index) {
        const tagDiv = document.createElement('div');
        
        // Générer les classes Tailwind basées sur la couleur
        let colorClasses = '';
        if (typeof tag.color === 'string') {
            // Nouveau système avec noms de couleurs Tailwind
            colorClasses = `bg-${tag.color}-100 text-${tag.color}-700 border border-${tag.color}-700`;
        } else {
            colorClasses = 'bg-gray-100 text-gray-700 border border-gray-500';
        }
        
        tagDiv.className = `tag-item inline-flex items-center px-3 py-1.5 rounded-full text-sm font-medium mr-2 mb-2 transition-all duration-200 relative group ${colorClasses}`;

        tagDiv.innerHTML = `
            <span class="truncate" title="${this.escapeHtml(tag.name)}"># ${this.escapeHtml(tag.name)}</span>
            <button type="button" class="ml-2 hover:bg-black hover:bg-opacity-10 rounded-full w-4 h-4 flex items-center justify-center transition-all duration-200 group-hover:scale-110" onclick="tagsManager.removeTag(${index})" title="Supprimer ce tag">
                <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2.5">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12"></path>
                </svg>
            </button>
        `;

        return tagDiv;
    }

    updateHiddenField() {
        this.tagsDataInput.value = JSON.stringify(this.tags);
    }

    getRandomColor() {
        return this.colors[Math.floor(Math.random() * this.colors.length)];
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    showError(message) {
        // Cacher le message d'aide
        this.helpElement.setAttribute('data-active', 'false');
        this.helpElement.classList.add('hidden');

        // Afficher le message d'erreur
        this.errorElement.setAttribute('data-active', 'true');
        this.errorElement.classList.remove('hidden');
        this.errorTextElement.textContent = message;

        // Mettre à jour le compteur de tags dans le message d'erreur
        const errorTagsCount = this.errorElement.querySelector('.text-xs');
        if (errorTagsCount) {
            const count = this.tags.length;
            errorTagsCount.textContent = `${count}/${this.maxTags} tags`;
        }

        // Ajouter la classe d'erreur à l'input
        this.tagsInput.classList.remove('border-gray-300', 'border-green-300');
        this.tagsInput.classList.add('border-red-300', 'bg-red-50');

        // Animation de secousse
        this.tagsInput.style.animation = 'shake 0.5s ease-in-out';
        setTimeout(() => {
            this.tagsInput.style.animation = '';
        }, 500);

        // Cacher l'erreur après 3 secondes pour les erreurs de validation
        if (message.includes('caractères') || message.includes('existe déjà')) {
            setTimeout(() => {
                this.clearError();
            }, 3000);
        }
    }

    clearError() {
        // Cacher le message d'erreur
        this.errorElement.setAttribute('data-active', 'false');
        this.errorElement.classList.add('hidden');
        this.errorTextElement.textContent = '';

        // Afficher le message d'aide
        this.helpElement.setAttribute('data-active', 'true');
        this.helpElement.classList.remove('hidden');

        // Supprimer les classes d'erreur
        this.tagsInput.classList.remove('border-red-300', 'bg-red-50');
    }

    /**
     * Efface tous les tags existants
     */
    clearTags() {
        this.tags = [];
        this.updateDisplay();
        this.updateHiddenField();
        this.updateInputPlaceholder();
        this.updateTagsCounter();
        this.clearError();
    }

    /**
     * Ajoute plusieurs tags d'un coup (pour l'intégration avec l'IA)
     * @param {Array} tagNames - Tableau de noms de tags à ajouter
     */
    addTags(tagNames) {
        if (!Array.isArray(tagNames)) {
            console.error('addTags attend un tableau de noms de tags');
            return;
        }

        // Effacer les tags existants d'abord
        this.clearTags();

        // Ajouter chaque tag, en s'arrêtant au maximum autorisé
        const tagsToAdd = tagNames.slice(0, this.maxTags);
        
        tagsToAdd.forEach(tagName => {
            if (typeof tagName === 'string' && tagName.trim()) {
                this.addTag(tagName.trim());
            }
        });
    }
}

// Initialiser le gestionnaire de tags quand le DOM est chargé
document.addEventListener('DOMContentLoaded', function () {
    window.tagsManager = new TagsManager();
});
