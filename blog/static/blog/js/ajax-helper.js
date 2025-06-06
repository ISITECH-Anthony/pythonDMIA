/**
 * Utilitaires AJAX pour BlogHub
 * Centralise la gestion CSRF et les requêtes AJAX
 */

class AjaxHelper {
    constructor() {
        this.csrfToken = null;
        this.initCsrfToken();
    }

    /**
     * Initialise le token CSRF une seule fois
     */
    initCsrfToken() {
        // Essayer de récupérer depuis la meta tag
        const metaTag = document.querySelector('meta[name="csrf-token"]');
        if (metaTag) {
            this.csrfToken = metaTag.getAttribute('content');
        } else {
            // Fallback: essayer de récupérer depuis les cookies
            this.csrfToken = this.getCookie('csrftoken');
        }
        
        if (!this.csrfToken) {
            console.warn('CSRF token non trouvé. Les requêtes AJAX pourraient échouer.');
        }
    }

    /**
     * Récupère un cookie par nom
     */
    getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    /**
     * Retourne les headers par défaut avec CSRF
     */
    getDefaultHeaders() {
        return {
            'Content-Type': 'application/json',
            'X-CSRFToken': this.csrfToken,
        };
    }

    /**
     * Effectue une requête POST avec gestion d'erreur intégrée
     */
    async post(url, data = {}, options = {}) {
        const config = {
            method: 'POST',
            headers: this.getDefaultHeaders(),
            body: JSON.stringify(data),
            ...options
        };

        try {
            const response = await fetch(url, config);
            const responseData = await response.json();

            if (!response.ok) {
                throw new Error(responseData.error || `Erreur ${response.status}`);
            }

            return responseData;
        } catch (error) {
            console.error('Erreur AJAX:', error);
            throw error;
        }
    }

    /**
     * Effectue une requête GET
     */
    async get(url, options = {}) {
        const config = {
            method: 'GET',
            headers: {
                'X-CSRFToken': this.csrfToken,
            },
            ...options
        };

        try {
            const response = await fetch(url, config);
            const responseData = await response.json();

            if (!response.ok) {
                throw new Error(responseData.error || `Erreur ${response.status}`);
            }

            return responseData;
        } catch (error) {
            console.error('Erreur AJAX:', error);
            throw error;
        }
    }

    /**
     * Wrapper pour les actions qui requièrent une authentification
     */
    async authenticatedRequest(url, data = {}, options = {}) {
        try {
            return await this.post(url, data, options);
        } catch (error) {
            if (error.message.includes('403') || error.message.includes('401')) {
                if (window.toast) {
                    window.toast.warning('Vous devez être connecté pour effectuer cette action');
                }
                // Optionnel: rediriger vers la page de connexion
                // window.location.href = '/auth/login/';
            } else {
                if (window.toast) {
                    window.toast.error('Erreur lors de la requête: ' + error.message);
                }
            }
            throw error;
        }
    }
}

// Instance globale
const ajaxHelper = new AjaxHelper();

// Exposer globalement pour faciliter l'utilisation
window.ajaxHelper = ajaxHelper;

// Fonctions de convenance pour compatibilité
window.postRequest = (url, data, options) => ajaxHelper.post(url, data, options);
window.getRequest = (url, options) => ajaxHelper.get(url, options);
window.authenticatedPost = (url, data, options) => ajaxHelper.authenticatedRequest(url, data, options);
