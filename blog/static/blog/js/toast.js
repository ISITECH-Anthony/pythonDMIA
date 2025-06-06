/**
 * Système de Toast Épuré pour BlogHub
 * Avec barre de progression et gestion du hover
 */

class ToastManager {
    constructor() {
        this.container = null;
        this.toasts = new Map();
        this.createContainer();
    }

    createContainer() {
        if (document.getElementById('toast-container')) return;
        
        this.container = document.createElement('div');
        this.container.id = 'toast-container';
        this.container.className = 'toast-container';
        document.body.appendChild(this.container);
    }

    show(message, type = 'info', options = {}) {
        const {
            duration = 5000,
            persistent = false,
            allowHtml = false
        } = options;

        const toastId = Date.now() + Math.random();
        const toast = this.createToast(message, type, toastId, { persistent, allowHtml, duration });
        
        // Insérer en PREMIÈRE position (en haut)
        this.container.insertBefore(toast, this.container.firstChild);
        
        // Stocker la référence
        this.toasts.set(toastId, {
            element: toast,
            persistent,
            duration,
            timer: null,
            isPaused: false,
            remainingTime: duration
        });

        // Animation d'entrée
        requestAnimationFrame(() => {
            toast.classList.add('toast-show');
        });

        // Configurer l'auto-suppression si non persistant
        if (!persistent) {
            this.startAutoRemoval(toastId);
        }

        return toastId;
    }

    createToast(message, type, toastId, options) {
        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;
        toast.setAttribute('data-toast-id', toastId);

        // Structure du toast avec icône
        toast.innerHTML = `
            <div class="toast-content">
                <div class="toast-icon"></div>
                <div class="toast-message">${options.allowHtml ? message : this.escapeHtml(message)}</div>
                <button class="toast-close" aria-label="Fermer">
                    ×
                </button>
            </div>
            ${!options.persistent ? '<div class="toast-progress"><div class="toast-progress-bar"></div></div>' : ''}
        `;

        // Événement de fermeture
        const closeButton = toast.querySelector('.toast-close');
        closeButton.addEventListener('click', () => {
            this.remove(toastId);
        });

        // Événements hover pour pause/resume
        if (!options.persistent) {
            toast.addEventListener('mouseenter', () => this.pauseToast(toastId));
            toast.addEventListener('mouseleave', () => this.resumeToast(toastId));
        }

        return toast;
    }

    startAutoRemoval(toastId) {
        const toastData = this.toasts.get(toastId);
        if (!toastData || toastData.persistent) return;

        // Démarrer l'animation de la barre de progression
        this.startProgressBar(toastId);

        // Timer pour la suppression
        toastData.timer = setTimeout(() => {
            this.remove(toastId);
        }, toastData.duration);
    }

    startProgressBar(toastId) {
        const toastData = this.toasts.get(toastId);
        if (!toastData) return;

        const progressBar = toastData.element.querySelector('.toast-progress-bar');
        if (!progressBar) return;

        // Reset et démarrer l'animation
        progressBar.style.width = '100%';
        progressBar.style.transition = `width ${toastData.duration}ms linear`;
        
        requestAnimationFrame(() => {
            progressBar.style.width = '0%';
        });
    }

    pauseToast(toastId) {
        const toastData = this.toasts.get(toastId);
        if (!toastData || toastData.isPaused) return;

        toastData.isPaused = true;
        
        // Arrêter le timer
        if (toastData.timer) {
            clearTimeout(toastData.timer);
            toastData.timer = null;
        }

        // Pausser la barre de progression
        const progressBar = toastData.element.querySelector('.toast-progress-bar');
        if (progressBar) {
            const computedStyle = window.getComputedStyle(progressBar);
            const currentWidth = computedStyle.width;
            progressBar.style.transition = 'none';
            progressBar.style.width = currentWidth;
            
            // Calculer le temps restant basé sur la largeur
            const parentWidth = progressBar.parentElement.offsetWidth;
            const percentage = parseInt(currentWidth) / parentWidth;
            toastData.remainingTime = toastData.duration * percentage;
        }
    }

    resumeToast(toastId) {
        const toastData = this.toasts.get(toastId);
        if (!toastData || !toastData.isPaused) return;

        toastData.isPaused = false;

        // Redémarrer le timer avec le temps restant
        toastData.timer = setTimeout(() => {
            this.remove(toastId);
        }, toastData.remainingTime);

        // Reprendre l'animation de la barre de progression
        const progressBar = toastData.element.querySelector('.toast-progress-bar');
        if (progressBar) {
            progressBar.style.transition = `width ${toastData.remainingTime}ms linear`;
            progressBar.style.width = '0%';
        }
    }

    remove(toastId) {
        const toastData = this.toasts.get(toastId);
        if (!toastData) return;

        const toast = toastData.element;

        // Nettoyer les timers
        if (toastData.timer) {
            clearTimeout(toastData.timer);
        }

        // Animation de sortie
        toast.classList.add('toast-hide');

        setTimeout(() => {
            if (toast.parentNode) {
                toast.parentNode.removeChild(toast);
            }
            this.toasts.delete(toastId);
        }, 300);
    }

    // Méthodes utilitaires
    escapeHtml(text) {
        const map = {
            '&': '&amp;',
            '<': '&lt;',
            '>': '&gt;',
            '"': '&quot;',
            "'": '&#039;'
        };
        return text.replace(/[&<>"']/g, function(m) { return map[m]; });
    }

    // Méthodes raccourcis pour différents types
    success(message, options = {}) {
        return this.show(message, 'success', { ...options, duration: 1500 });
    }

    error(message, options = {}) {
        return this.show(message, 'error', { ...options, duration: 5000 });
    }

    warning(message, options = {}) {
        return this.show(message, 'warning', { ...options, duration: 1500 });
    }

    info(message, options = {}) {
        return this.show(message, 'info', { ...options, duration: 1500 });
    }

    // Toast permanent
    permanent(message, type = 'info') {
        return this.show(message, type, { persistent: true });
    }

    // Supprimer tous les toasts
    clear() {
        this.toasts.forEach((_, toastId) => {
            this.remove(toastId);
        });
    }
}

// Initialiser le gestionnaire global
const toastManager = new ToastManager();

// Exposer globalement pour utilisation facile
window.toast = toastManager;

// Fonction de compatibilité simplifiée
window.showToast = function(message, type = 'info', options = {}) {
    if (typeof options === 'number') {
        options = { duration: options };
    }
    return toastManager.show(message, type, options);
};
