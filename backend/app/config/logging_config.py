import logging
import sys

def setup_logging():
    # Configuration du handler de base
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(
        logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
    )

    # Configuration du logger root
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.WARNING)  # Niveau global WARNING
    root_logger.addHandler(handler)

    # Configuration spécifique pour nos loggers
    twitch_loggers = [
        logging.getLogger("backend.app.services.twitch"),
        logging.getLogger("backend.app.services.twitch_service"),
        logging.getLogger("backend.app.services.twitch.auth")
    ]

    for logger in twitch_loggers:
        logger.setLevel(logging.WARNING)  # Force le niveau WARNING pour Twitch
        if not logger.handlers:
            logger.addHandler(handler)
        logger.propagate = True  # Permet la propagation vers le logger root

    # Configuration spécifique pour nos loggers
    for logger_name in ['backend.app.routers.auth']:
        logger = logging.getLogger(logger_name)
        logger.setLevel(logging.DEBUG) 