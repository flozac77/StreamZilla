import pytest
from unittest.mock import patch, MagicMock
import os
import importlib
import sys

def test_config_init_module():
    """Test direct import of the config package initialization to increase coverage."""
    with patch('os.getenv', return_value="test") as mock_getenv, \
         patch('backend.app.config.test.TestSettings') as MockTestSettings:
        
        # Simuler l'instance de TestSettings
        mock_instance = MagicMock()
        MockTestSettings.return_value = mock_instance
        
        # Configurer les attributs nécessaires
        mock_instance.TWITCH_REDIRECT_URI = "http://test.com/callback"
        mock_instance.TWITCH_CLIENT_ID = "test_id"
        mock_instance.MONGODB_URL = "mongodb://test:27017"
        mock_instance.MONGODB_DB_NAME = "test_db"
        mock_instance.REDIS_URL = "redis://test:6379"
        
        # Désactiver les prints dans le module
        with patch('builtins.print'):
            # Recharger le module
            if 'backend.app.config' in sys.modules:
                del sys.modules['backend.app.config']
            
            import backend.app.config
            importlib.reload(backend.app.config)
            
            # Vérifier que la classe correcte a été utilisée
            assert MockTestSettings.call_count == 2  # Une fois pour get_settings() et une fois pour settings

def test_config_get_settings():
    """Test la fonction get_settings dans config/__init__.py"""
    # Tester avec environnement dev (par défaut)
    with patch('os.getenv', return_value="dev") as mock_getenv, \
         patch('backend.app.config.dev.DevSettings') as MockDevSettings:
        
        # Réimporter le module
        if 'backend.app.config' in sys.modules:
            del sys.modules['backend.app.config']
        
        import backend.app.config
        importlib.reload(backend.app.config)
        
        # Appeler la fonction
        settings = backend.app.config.get_settings()
        
        # Vérifier que la bonne classe a été utilisée
        assert MockDevSettings.call_count == 3  # Une fois pour l'import, une fois pour le rechargement, et une fois pour l'appel explicite
    
    # Tester avec environnement prod
    with patch('os.getenv', return_value="prod") as mock_getenv, \
         patch('backend.app.config.prod.ProdSettings') as MockProdSettings:
        
        # Réimporter le module
        if 'backend.app.config' in sys.modules:
            del sys.modules['backend.app.config']
        
        import backend.app.config
        importlib.reload(backend.app.config)
        
        # Appeler la fonction
        settings = backend.app.config.get_settings()
        
        # Vérifier que la bonne classe a été utilisée
        assert MockProdSettings.call_count == 3  # Une fois pour l'import, une fois pour le rechargement, et une fois pour l'appel explicite 