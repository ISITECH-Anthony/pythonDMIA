"""
Middleware pour le logging automatique des requêtes.
"""

import logging
import time
from django.utils.deprecation import MiddlewareMixin
from django.conf import settings

logger = logging.getLogger('blog')


class RequestLoggingMiddleware(MiddlewareMixin):
    """
    Middleware pour logger les requêtes HTTP avec des informations utiles.
    """
    
    def process_request(self, request):
        """Enregistre le début du traitement de la requête."""
        request._start_time = time.time()
        
        # Log des informations de base de la requête
        user_info = f"User: {request.user.username}" if hasattr(request, 'user') and request.user.is_authenticated else "Anonymous"
        ip_address = self.get_client_ip(request)
        
        logger.debug(f"[REQUEST_START] {request.method} {request.path} | {user_info} | IP: {ip_address}")
    
    def process_response(self, request, response):
        """Enregistre la fin du traitement de la requête."""
        if hasattr(request, '_start_time'):
            duration = time.time() - request._start_time
            
            user_info = f"User: {request.user.username}" if hasattr(request, 'user') and request.user.is_authenticated else "Anonymous"
            
            # Log différent selon le code de statut
            if response.status_code >= 400:
                logger.warning(
                    f"[REQUEST_ERROR] {request.method} {request.path} | "
                    f"Status: {response.status_code} | Duration: {duration:.2f}s | {user_info}"
                )
            elif response.status_code >= 300:
                logger.info(
                    f"[REQUEST_REDIRECT] {request.method} {request.path} | "
                    f"Status: {response.status_code} | Duration: {duration:.2f}s | {user_info}"
                )
            else:
                logger.debug(
                    f"[REQUEST_SUCCESS] {request.method} {request.path} | "
                    f"Status: {response.status_code} | Duration: {duration:.2f}s | {user_info}"
                )
        
        return response
    
    def process_exception(self, request, exception):
        """Enregistre les exceptions non gérées."""
        user_info = f"User: {request.user.username}" if hasattr(request, 'user') and request.user.is_authenticated else "Anonymous"
        
        logger.error(
            f"[REQUEST_EXCEPTION] {request.method} {request.path} | "
            f"Exception: {exception.__class__.__name__}: {str(exception)} | {user_info}"
        )
        
        # Ne pas interrompre le traitement normal des exceptions
        return None
    
    def get_client_ip(self, request):
        """Récupère l'adresse IP du client."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class SecurityLoggingMiddleware(MiddlewareMixin):
    """
    Middleware pour logger les événements de sécurité.
    """
    
    def process_request(self, request):
        """Vérifie et log les tentatives suspectes."""
        
        # Log des tentatives d'accès à des URLs sensibles
        suspicious_paths = [
            '/admin/',
            '/wp-admin/',
            '/.env',
            '/config/',
            '/api/',
        ]
        
        for suspicious_path in suspicious_paths:
            if request.path.startswith(suspicious_path):
                ip_address = self.get_client_ip(request)
                user_agent = request.META.get('HTTP_USER_AGENT', 'Unknown')
                
                logger.warning(
                    f"[SECURITY_ALERT] Suspicious access attempt to {request.path} | "
                    f"IP: {ip_address} | User-Agent: {user_agent}"
                )
                break
        
        # Log des tentatives de login multiples (si c'est une vue de login)
        if request.path == '/login/' and request.method == 'POST':
            ip_address = self.get_client_ip(request)
            logger.info(f"[AUTH_ATTEMPT] Login attempt from IP: {ip_address}")
    
    def get_client_ip(self, request):
        """Récupère l'adresse IP du client."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
