import logging
import sys

def setup_logging():
    # Configuration du handler pour stdout
    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setLevel(logging.DEBUG)
    
    # Format personnalisé
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    stdout_handler.setFormatter(formatter)
    
    # Configuration du logger root
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)
    
    # Supprime les handlers existants pour éviter les doublons
    root_logger.handlers = []
    root_logger.addHandler(stdout_handler)
    
    # Configuration spécifique pour nos loggers
    for logger_name in ['backend.app.services.twitch_service', 'backend.app.routers.auth']:
        logger = logging.getLogger(logger_name)
        logger.setLevel(logging.DEBUG) 