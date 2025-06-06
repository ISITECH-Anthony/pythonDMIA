"""
Tests pour les fonctions utilitaires.
"""
from django.test import TestCase, RequestFactory
from django.contrib.auth import get_user_model
from blog.utils import get_client_ip

User = get_user_model()


class UtilsTest(TestCase):
    """Tests pour les fonctions utilitaires."""

    def setUp(self):
        """Configuration initiale pour chaque test."""
        self.factory = RequestFactory()

    def test_get_client_ip_with_x_forwarded_for(self):
        """Test de récupération de l'IP avec X-Forwarded-For."""
        request = self.factory.get('/')
        request.META['HTTP_X_FORWARDED_FOR'] = '192.168.1.1, 10.0.0.1, 172.16.0.1'
        
        ip = get_client_ip(request)
        self.assertEqual(ip, '192.168.1.1')

    def test_get_client_ip_with_x_real_ip(self):
        """Test de récupération de l'IP avec X-Real-IP."""
        request = self.factory.get('/')
        request.META['HTTP_X_REAL_IP'] = '203.0.113.1'
        
        ip = get_client_ip(request)
        self.assertEqual(ip, '203.0.113.1')

    def test_get_client_ip_with_remote_addr(self):
        """Test de récupération de l'IP avec REMOTE_ADDR."""
        request = self.factory.get('/')
        request.META['REMOTE_ADDR'] = '198.51.100.1'
        
        ip = get_client_ip(request)
        self.assertEqual(ip, '198.51.100.1')

    def test_get_client_ip_priority_order(self):
        """Test de l'ordre de priorité des en-têtes IP."""
        request = self.factory.get('/')
        request.META['HTTP_X_FORWARDED_FOR'] = '192.168.1.1'
        request.META['HTTP_X_REAL_IP'] = '203.0.113.1'
        request.META['REMOTE_ADDR'] = '198.51.100.1'
        
        # X-Forwarded-For doit avoir la priorité
        ip = get_client_ip(request)
        self.assertEqual(ip, '192.168.1.1')

    def test_get_client_ip_x_real_ip_fallback(self):
        """Test de fallback vers X-Real-IP."""
        request = self.factory.get('/')
        request.META['HTTP_X_REAL_IP'] = '203.0.113.1'
        request.META['REMOTE_ADDR'] = '198.51.100.1'
        
        # X-Real-IP doit être utilisé quand X-Forwarded-For n'est pas présent
        ip = get_client_ip(request)
        self.assertEqual(ip, '203.0.113.1')

    def test_get_client_ip_remote_addr_fallback(self):
        """Test de fallback vers REMOTE_ADDR."""
        request = self.factory.get('/')
        request.META['REMOTE_ADDR'] = '198.51.100.1'
        
        # REMOTE_ADDR doit être utilisé en dernier recours
        ip = get_client_ip(request)
        self.assertEqual(ip, '198.51.100.1')

    def test_get_client_ip_no_headers(self):
        """Test sans aucun en-tête IP."""
        request = self.factory.get('/')
        # Supprimer même REMOTE_ADDR pour tester le cas vraiment sans aucune IP
        del request.META['REMOTE_ADDR']
        
        ip = get_client_ip(request)
        self.assertEqual(ip, 'unknown')

    def test_get_client_ip_empty_x_forwarded_for(self):
        """Test avec X-Forwarded-For vide."""
        request = self.factory.get('/')
        request.META['HTTP_X_FORWARDED_FOR'] = ''
        request.META['HTTP_X_REAL_IP'] = '203.0.113.1'
        
        # Doit fallback vers X-Real-IP
        ip = get_client_ip(request)
        self.assertEqual(ip, '203.0.113.1')

    def test_get_client_ip_empty_x_real_ip(self):
        """Test avec X-Real-IP vide."""
        request = self.factory.get('/')
        request.META['HTTP_X_REAL_IP'] = ''
        request.META['REMOTE_ADDR'] = '198.51.100.1'
        
        # Doit fallback vers REMOTE_ADDR
        ip = get_client_ip(request)
        self.assertEqual(ip, '198.51.100.1')

    def test_get_client_ip_whitespace_stripping(self):
        """Test de suppression des espaces."""
        request = self.factory.get('/')
        request.META['HTTP_X_FORWARDED_FOR'] = '  192.168.1.1  , 10.0.0.1  '
        
        ip = get_client_ip(request)
        self.assertEqual(ip, '192.168.1.1')

    def test_get_client_ip_multiple_forwarded_ips(self):
        """Test avec plusieurs IPs dans X-Forwarded-For."""
        request = self.factory.get('/')
        request.META['HTTP_X_FORWARDED_FOR'] = '192.168.1.1,10.0.0.1,172.16.0.1'
        
        # Doit retourner la première IP (client original)
        ip = get_client_ip(request)
        self.assertEqual(ip, '192.168.1.1')

    def test_get_client_ip_single_forwarded_ip(self):
        """Test avec une seule IP dans X-Forwarded-For."""
        request = self.factory.get('/')
        request.META['HTTP_X_FORWARDED_FOR'] = '192.168.1.1'
        
        ip = get_client_ip(request)
        self.assertEqual(ip, '192.168.1.1')

    def test_get_client_ip_ipv6_address(self):
        """Test avec une adresse IPv6."""
        request = self.factory.get('/')
        request.META['HTTP_X_FORWARDED_FOR'] = '2001:db8::1'
        
        ip = get_client_ip(request)
        self.assertEqual(ip, '2001:db8::1')

    def test_get_client_ip_mixed_ipv4_ipv6(self):
        """Test avec mélange d'adresses IPv4 et IPv6."""
        request = self.factory.get('/')
        request.META['HTTP_X_FORWARDED_FOR'] = '2001:db8::1, 192.168.1.1'
        
        # Doit retourner la première IP
        ip = get_client_ip(request)
        self.assertEqual(ip, '2001:db8::1')

    def test_get_client_ip_localhost_addresses(self):
        """Test avec des adresses localhost."""
        request = self.factory.get('/')
        request.META['HTTP_X_FORWARDED_FOR'] = '127.0.0.1'
        
        ip = get_client_ip(request)
        self.assertEqual(ip, '127.0.0.1')

    def test_get_client_ip_private_addresses(self):
        """Test avec des adresses privées."""
        test_cases = [
            '192.168.1.1',    # Réseau privé classe C
            '10.0.0.1',       # Réseau privé classe A
            '172.16.0.1',     # Réseau privé classe B
        ]
        
        for private_ip in test_cases:
            with self.subTest(ip=private_ip):
                request = self.factory.get('/')
                request.META['HTTP_X_FORWARDED_FOR'] = private_ip
                
                ip = get_client_ip(request)
                self.assertEqual(ip, private_ip)

    def test_get_client_ip_case_insensitive_headers(self):
        """Test que les en-têtes sont traités de manière insensible à la casse."""
        request = self.factory.get('/')
        # Django normalise automatiquement les en-têtes HTTP
        request.META['HTTP_X_FORWARDED_FOR'] = '192.168.1.1'
        
        ip = get_client_ip(request)
        self.assertEqual(ip, '192.168.1.1')

    def test_get_client_ip_malformed_forwarded_for(self):
        """Test avec un en-tête X-Forwarded-For malformé."""
        request = self.factory.get('/')
        request.META['HTTP_X_FORWARDED_FOR'] = 'not-an-ip-address'
        request.META['HTTP_X_REAL_IP'] = '203.0.113.1'
        
        # Même si X-Forwarded-For est malformé, on le retourne tel quel
        # Le filtrage/validation des IPs peut être fait à un niveau supérieur
        ip = get_client_ip(request)
        self.assertEqual(ip, 'not-an-ip-address')

    def test_get_client_ip_request_without_meta(self):
        """Test avec une requête sans attribut META."""
        class MockRequest:
            pass
        
        request = MockRequest()
        
        ip = get_client_ip(request)
        self.assertEqual(ip, 'unknown')
