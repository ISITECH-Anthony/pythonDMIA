def get_client_ip(request):
    """
    Obtient l'adresse IP réelle du client en tenant compte des proxies
    """
    # Gérer le cas où request n'a pas d'attribut META
    if not hasattr(request, 'META'):
        return 'unknown'
    
    # Ordre de priorité pour récupérer l'IP
    headers_to_check = [
        'HTTP_X_FORWARDED_FOR',
        'HTTP_X_REAL_IP',
        'HTTP_X_FORWARDED',
        'HTTP_X_CLUSTER_CLIENT_IP',
        'HTTP_FORWARDED_FOR',
        'HTTP_FORWARDED',
        'REMOTE_ADDR'
    ]
    
    for header in headers_to_check:
        ip = request.META.get(header)
        if ip:
            # Pour HTTP_X_FORWARDED_FOR, prendre la première IP (celle du client)
            if header == 'HTTP_X_FORWARDED_FOR':
                ip = ip.split(',')[0].strip()
            else:
                ip = ip.strip()
            
            # Vérifier que l'IP n'est pas vide après nettoyage
            if ip:
                return ip
    
    # Si aucune IP n'est trouvée, retourner 'unknown'
    return 'unknown'
