import pytest
from unittest.mock import patch, MagicMock
import os
import importlib
import sys

def test_config_init_module():
    """Test direct import of the config package initialization to increase coverage."""
    with patch('os.getenv', return_value="test") as mock_getenv, \
         patch('backend.app.config.TestSettings') as MockTestSettings:
        
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
                old_module = sys.modules['backend.app.config']
            
            import backend.app.config
            importlib.reload(backend.app.config)
            
            # Restaurer après le test
            if 'old_module' in locals():
                sys.modules['backend.app.config'] = old_module
        
        # Vérifier que la classe correcte a été utilisée
        MockTestSettings.assert_called_once()

def test_config_get_settings():
    """Test la fonction get_settings dans config/__init__.py"""
    # Tester avec environnement dev (par défaut)
    with patch('os.getenv', return_value="dev") as mock_getenv, \
         patch('backend.app.config.DevSettings') as MockDevSettings:
        
        # Importer la fonction
        from backend.app.config import get_settings
        
        # Appeler la fonction
        settings = get_settings()
        
        # Vérifier que la bonne classe a été utilisée
        MockDevSettings.assert_called_once()
    
    # Tester avec environnement prod
    with patch('os.getenv', return_value="prod") as mock_getenv, \
         patch('backend.app.config.ProdSettings') as MockProdSettings:
        
        # Réimporter la fonction
        importlib.reload(sys.modules['backend.app.config'])
        from backend.app.config import get_settings
        
        # Appeler la fonction
        settings = get_settings()
        
        # Vérifier que la bonne classe a été utilisée
        MockProdSettings.assert_called_once() 