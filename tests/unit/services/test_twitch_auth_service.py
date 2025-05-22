import pytest
from unittest.mock import patch, AsyncMock, MagicMock
from datetime import datetime, timedelta
import httpx
from httpx import HTTPStatusError, Request, Response

from backend.app.services.twitch.auth import TwitchAuthService, TwitchError
from backend.app.models.twitch import TwitchToken
from backend.app.repositories.token_repository import TokenRepository

# Mock de TokenRepository et httpx.AsyncClient au niveau de la classe
@patch('backend.app.services.twitch.auth.TokenRepository', new_callable=MagicMock)
@patch('backend.app.services.twitch.auth.httpx.AsyncClient')
class TestTwitchAuthService:
    @pytest.mark.asyncio
    async def test_get_valid_token_from_repository_valid(self, MockAsyncClient, MockTokenRepository):
        # Arrange
        mock_repo_instance = MockTokenRepository.return_value
        mock_client_instance = MockAsyncClient.return_value
        mock_client_instance.get = AsyncMock()
        mock_client_instance.__aenter__ = AsyncMock(return_value=mock_client_instance) # Simuler le contexte async with
        mock_client_instance.__aexit__ = AsyncMock(return_value=None)

        # Configurer les méthodes asynchrones du repository mocké
        valid_expires_at = datetime.now() + timedelta(hours=1)
        mock_token_data = {
            "access_token": "valid_token",
            "expires_in": 3600,
            "token_type": "bearer",
            "expires_at": valid_expires_at.isoformat()
        }
        mock_repo_instance.get_current_token = AsyncMock(return_value=TwitchToken(**mock_token_data))
        mock_repo_instance.save_token = AsyncMock()
        mock_repo_instance.update_last_used = AsyncMock()
        mock_repo_instance.invalidate_token = AsyncMock()

        # Mock de _is_token_valid pour retourner True
        with patch.object(TwitchAuthService, '_is_token_valid', new_callable=AsyncMock) as mock_is_token_valid:
            mock_is_token_valid.return_value = True
            # Passer le mock du repository au service
            service = TwitchAuthService(token_repository=mock_repo_instance)

            # Act
            token = await service.get_valid_token()

            # Assert
            mock_repo_instance.get_current_token.assert_awaited_once()
            mock_is_token_valid.assert_awaited_once_with(mock_repo_instance.get_current_token.return_value)
            mock_repo_instance.save_token.assert_not_awaited() # On ne doit pas sauvegarder si le token est déjà valide
            assert token.access_token == "valid_token"

    @pytest.mark.asyncio
    async def test_get_valid_token_generates_new_when_none(self, MockAsyncClient, MockTokenRepository):
        # Arrange
        mock_repo_instance = MockTokenRepository.return_value
        mock_client_instance = MockAsyncClient.return_value
        mock_client_instance.get = AsyncMock()
        mock_client_instance.__aenter__ = AsyncMock(return_value=mock_client_instance) # Simuler le contexte async with
        mock_client_instance.__aexit__ = AsyncMock(return_value=None)

        # Configurer les méthodes asynchrones du repository mocké
        mock_repo_instance.get_current_token = AsyncMock(return_value=None)
        mock_repo_instance.save_token = AsyncMock()
        mock_repo_instance.update_last_used = AsyncMock()
        mock_repo_instance.invalidate_token = AsyncMock()

        # Mock de _generate_new_token pour retourner un nouveau token
        new_expires_at = datetime.now() + timedelta(hours=2)
        new_token_data = {
            "access_token": "new_token",
            "expires_in": 7200,
            "token_type": "bearer",
            "expires_at": new_expires_at.isoformat()
        }
        mock_new_token = TwitchToken(**new_token_data)

        with patch.object(TwitchAuthService, '_generate_new_token', new_callable=AsyncMock) as mock_generate_new_token:
             mock_generate_new_token.return_value = mock_new_token
             # Passer le mock du repository au service
             service = TwitchAuthService(token_repository=mock_repo_instance)

             # Act
             token = await service.get_valid_token()

             # Assert
             mock_repo_instance.get_current_token.assert_awaited_once()
             mock_generate_new_token.assert_awaited_once()
             # L'assertion pour save_token est gérée dans le test de _generate_new_token
             assert token.access_token == "new_token"

    @pytest.mark.asyncio
    async def test_get_valid_token_generates_new_when_invalid(self, MockAsyncClient, MockTokenRepository):
        # Arrange
        mock_repo_instance = MockTokenRepository.return_value
        mock_client_instance = MockAsyncClient.return_value
        mock_client_instance.get = AsyncMock()
        mock_client_instance.__aenter__ = AsyncMock(return_value=mock_client_instance) # Simuler le contexte async with
        mock_client_instance.__aexit__ = AsyncMock(return_value=None)

        # Configurer les méthodes asynchrones du repository mocké
        invalid_expires_at = datetime.now() - timedelta(hours=1)
        mock_token_data = {
            "access_token": "invalid_token",
            "expires_in": 0,
            "token_type": "bearer",
            "expires_at": invalid_expires_at.isoformat()
        }
        mock_repo_instance.get_current_token = AsyncMock(return_value=TwitchToken(**mock_token_data))
        mock_repo_instance.save_token = AsyncMock()
        mock_repo_instance.update_last_used = AsyncMock()
        mock_repo_instance.invalidate_token = AsyncMock()

        # Mock de _is_token_valid pour retourner False
        with patch.object(TwitchAuthService, '_is_token_valid', new_callable=AsyncMock) as mock_is_token_valid:
            mock_is_token_valid.return_value = False

            # Mock de _generate_new_token pour retourner un nouveau token
            new_expires_at = datetime.now() + timedelta(hours=3)
            new_token_data = {
                "access_token": "another_new_token",
                "expires_in": 10800,
                "token_type": "bearer",
                "expires_at": new_expires_at.isoformat()
            }
            mock_new_token = TwitchToken(**new_token_data)

            with patch.object(TwitchAuthService, '_generate_new_token', new_callable=AsyncMock) as mock_generate_new_token:
                 mock_generate_new_token.return_value = mock_new_token
                 # Passer le mock du repository au service
                 service = TwitchAuthService(token_repository=mock_repo_instance)

                 # Act
                 token = await service.get_valid_token()

                 # Assert
                 mock_repo_instance.get_current_token.assert_awaited_once()
                 mock_is_token_valid.assert_awaited_once_with(TwitchToken(**mock_token_data))
                 mock_generate_new_token.assert_awaited_once()
                 # L'assertion pour save_token est gérée dans le test de _generate_new_token
                 assert token.access_token == "another_new_token"

    @pytest.mark.asyncio
    async def test_get_valid_token_http_error_during_generation(self, MockAsyncClient, MockTokenRepository):
        # Arrange
        mock_repo_instance = MockTokenRepository.return_value
        mock_client_instance = MockAsyncClient.return_value
        mock_client_instance.get = AsyncMock() # Configurer get comme AsyncMock
        mock_client_instance.__aenter__ = AsyncMock(return_value=mock_client_instance) # Simuler le contexte async with
        mock_client_instance.__aexit__ = AsyncMock(return_value=None)

        # Configurer les méthodes asynchrones du repository mocké
        mock_repo_instance.get_current_token = AsyncMock(return_value=None)
        mock_repo_instance.save_token = AsyncMock()
        mock_repo_instance.update_last_used = AsyncMock()
        mock_repo_instance.invalidate_token = AsyncMock()

        # Mock de _generate_new_token pour lever une exception HTTP
        mock_response = Response(500, request=Request("POST", "http://testurl"))
        mock_exception = HTTPStatusError("HTTP error", request=Request("POST", "http://testurl"), response=mock_response)

        with patch.object(TwitchAuthService, '_generate_new_token', new_callable=AsyncMock) as mock_generate_new_token:
             mock_generate_new_token.side_effect = mock_exception
             # Passer le mock du repository au service
             service = TwitchAuthService(token_repository=mock_repo_instance)

             # Act & Assert
             with pytest.raises(TwitchError) as excinfo:
                 await service.get_valid_token()

             mock_repo_instance.get_current_token.assert_awaited_once()
             mock_generate_new_token.assert_awaited_once()
             mock_repo_instance.save_token.assert_not_awaited() # Aucun token à sauvegarder en cas d'erreur
             # Vérifier que l'exception levée est bien TwitchError avec le bon statut et détail
             assert excinfo.value.status_code == 500
             assert excinfo.value.detail == {'error': "Erreur d'authentification Twitch", 'docs_url': 'https://dev.twitch.tv/docs'}

    @pytest.mark.asyncio
    async def test__is_token_valid_is_valid_false(self, MockAsyncClient, MockTokenRepository):
        # Arrange
        mock_repo_instance = MockTokenRepository.return_value
        mock_client_instance = MockAsyncClient.return_value
        mock_client_instance.get = AsyncMock() # Configurer get comme AsyncMock
        mock_client_instance.__aenter__ = AsyncMock(return_value=mock_client_instance) # Simuler le contexte async with
        mock_client_instance.__aexit__ = AsyncMock(return_value=None)

        # Configurer les méthodes asynchrones du repository mocké
        mock_repo_instance.get_current_token = AsyncMock()
        mock_repo_instance.save_token = AsyncMock()
        mock_repo_instance.update_last_used = AsyncMock()
        mock_repo_instance.invalidate_token = AsyncMock()

        # Simuler un token marqué comme invalide
        invalid_expires_at = datetime.now() + timedelta(hours=1)
        mock_token_data = {
            "access_token": "invalid_token",
            "expires_in": 3600,
            "token_type": "bearer",
            "expires_at": invalid_expires_at.isoformat(),
            "is_valid": False # Marqué explicitement comme invalide
        }
        token = TwitchToken(**mock_token_data)

        service = TwitchAuthService(token_repository=mock_repo_instance)

        # Act
        is_valid = await service._is_token_valid(token)

        # Assert
        assert is_valid is False
        mock_client_instance.get.assert_not_awaited() # L'API Twitch ne doit pas être appelée
        mock_repo_instance.update_last_used.assert_not_awaited()
        mock_repo_instance.invalidate_token.assert_not_awaited()

    @pytest.mark.asyncio
    async def test__is_token_valid_expires_soon(self, MockAsyncClient, MockTokenRepository):
        # Arrange
        mock_repo_instance = MockTokenRepository.return_value
        mock_client_instance = MockAsyncClient.return_value
        mock_client_instance.get = AsyncMock() # Configurer get comme AsyncMock
        mock_client_instance.__aenter__ = AsyncMock(return_value=mock_client_instance) # Simuler le contexte async with
        mock_client_instance.__aexit__ = AsyncMock(return_value=None)

        # Configurer les méthodes asynchrones du repository mocké
        mock_repo_instance.get_current_token = AsyncMock()
        mock_repo_instance.save_token = AsyncMock()
        mock_repo_instance.update_last_used = AsyncMock()
        mock_repo_instance.invalidate_token = AsyncMock()

        # Simuler un token qui expire bientôt (moins que settings.token_refresh_before_expiry)
        # Nous devons mocker get_twitch_settings pour contrôler token_refresh_before_expiry
        mock_settings = MagicMock()
        # Simuler l'expiration dans 30 minutes, avec un seuil de rafraîchissement de 1 heure
        expires_at_soon = datetime.utcnow() + timedelta(minutes=30)
        mock_token_data = {
            "access_token": "soon_expiring_token",
            "expires_in": 1800,
            "token_type": "bearer",
            "expires_at": expires_at_soon.isoformat(),
            "is_valid": True
        }
        token = TwitchToken(**mock_token_data)

        with patch('backend.app.services.twitch.auth.get_twitch_settings') as mock_get_twitch_settings:
            mock_get_twitch_settings.return_value = mock_settings
            # Définir un seuil de rafraîchissement plus long que le temps restant sur le token
            mock_settings.token_refresh_before_expiry = 3600 # 1 heure en secondes

            service = TwitchAuthService(token_repository=mock_repo_instance)

            # Act
            is_valid = await service._is_token_valid(token)

            # Assert
            assert is_valid is False
            # L'API Twitch ne doit pas être appelée car le token expire bientôt
            mock_client_instance.get.assert_not_awaited()
            mock_repo_instance.update_last_used.assert_not_awaited()
            mock_repo_instance.invalidate_token.assert_not_awaited()

    @pytest.mark.asyncio
    async def test__is_token_valid_api_returns_200(self, MockAsyncClient, MockTokenRepository):
        # Arrange
        mock_repo_instance = MockTokenRepository.return_value
        mock_client_instance = MockAsyncClient.return_value
        mock_client_instance.get = AsyncMock()
        mock_client_instance.__aenter__ = AsyncMock(return_value=mock_client_instance) # Simuler le contexte async with
        mock_client_instance.__aexit__ = AsyncMock(return_value=None)

        # Configurer les méthodes asynchrones du repository mocké
        mock_repo_instance.get_current_token = AsyncMock()
        mock_repo_instance.save_token = AsyncMock()
        mock_repo_instance.update_last_used = AsyncMock()
        mock_repo_instance.invalidate_token = AsyncMock()

        # Simuler un token valide
        valid_expires_at = datetime.utcnow() + timedelta(hours=2)
        mock_token_data = {
            "access_token": "valid_token",
            "expires_in": 7200,
            "token_type": "bearer",
            "expires_at": valid_expires_at.isoformat(),
            "is_valid": True
        }
        token = TwitchToken(**mock_token_data)

        # Mock de la réponse de l'API Twitch /validate
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.raise_for_status = MagicMock()
        mock_client_instance.get.return_value = mock_response

        service = TwitchAuthService(token_repository=mock_repo_instance)

        # Act
        is_valid = await service._is_token_valid(token)

        # Assert
        assert is_valid is True
        mock_client_instance.get.assert_awaited_once() # L'API Twitch doit être appelée
        mock_repo_instance.update_last_used.assert_awaited_once_with(token)
        mock_repo_instance.invalidate_token.assert_not_awaited()
        # Vérifier les headers envoyés à l'API Twitch
        mock_client_instance.get.assert_awaited_once_with(
            service.settings.validate_url,
            headers={
                "Authorization": f"Bearer {token.access_token}",
                "Client-Id": service.settings.client_id
            }
        )

    @pytest.mark.asyncio
    async def test__is_token_valid_api_returns_non_200(self, MockAsyncClient, MockTokenRepository):
        # Arrange
        mock_repo_instance = MockTokenRepository.return_value
        mock_client_instance = MockAsyncClient.return_value
        mock_client_instance.get = AsyncMock() # Configurer get comme AsyncMock
        mock_client_instance.__aenter__ = AsyncMock(return_value=mock_client_instance) # Simuler le contexte async with
        mock_client_instance.__aexit__ = AsyncMock(return_value=None)

        # Configurer les méthodes asynchrones du repository mocké
        mock_repo_instance.get_current_token = AsyncMock()
        mock_repo_instance.save_token = AsyncMock()
        mock_repo_instance.update_last_used = AsyncMock()
        mock_repo_instance.invalidate_token = AsyncMock()

        # Simuler un token qui pourrait être invalide selon l'API (mais marqué valide localement)
        valid_expires_at = datetime.utcnow() + timedelta(hours=2)
        mock_token_data = {
            "access_token": "potentially_invalid_token",
            "expires_in": 7200,
            "token_type": "bearer",
            "expires_at": valid_expires_at.isoformat(),
            "is_valid": True # Marqué valide localement pour entrer dans la branche API call
        }
        token = TwitchToken(**mock_token_data)

        # Mock de la réponse de l'API Twitch /validate - statut non 200
        mock_response = MagicMock()
        mock_response.status_code = 401 # Par exemple, Unauthorized
        mock_response.text = "Invalid token from API"
        mock_response.raise_for_status.side_effect = httpx.HTTPStatusError("Invalid status", request=MagicMock(), response=mock_response)
        mock_client_instance.get.return_value = mock_response

        service = TwitchAuthService(token_repository=mock_repo_instance)

        # Act
        is_valid = await service._is_token_valid(token)

        # Assert
        assert is_valid is False
        mock_client_instance.get.assert_awaited_once() # L'API Twitch doit être appelée
        mock_repo_instance.update_last_used.assert_not_awaited()
        mock_repo_instance.invalidate_token.assert_awaited_once_with(token) # Le token doit être invalidé localement
        # Vérifier les headers envoyés à l'API Twitch
        mock_client_instance.get.assert_awaited_once_with(
            service.settings.validate_url,
            headers={
                "Authorization": f"Bearer {token.access_token}",
                "Client-Id": service.settings.client_id
            }
        )

    @pytest.mark.asyncio
    async def test__is_token_valid_api_http_error(self, MockAsyncClient, MockTokenRepository):
        # Arrange
        mock_repo_instance = MockTokenRepository.return_value
        mock_client_instance = MockAsyncClient.return_value
        mock_client_instance.get = AsyncMock() # Configurer get comme AsyncMock
        mock_client_instance.__aenter__ = AsyncMock(return_value=mock_client_instance) # Simuler le contexte async with
        mock_client_instance.__aexit__ = AsyncMock(return_value=None)

        # Configurer les méthodes asynchrones du repository mocké
        mock_repo_instance.get_current_token = AsyncMock()
        mock_repo_instance.save_token = AsyncMock()
        mock_repo_instance.update_last_used = AsyncMock()
        mock_repo_instance.invalidate_token = AsyncMock()

        # Simuler un token valide localement
        valid_expires_at = datetime.utcnow() + timedelta(hours=2)
        mock_token_data = {
            "access_token": "token_for_http_error",
            "expires_in": 7200,
            "token_type": "bearer",
            "expires_at": valid_expires_at.isoformat(),
            "is_valid": True
        }
        token = TwitchToken(**mock_token_data)

        # Mock de l'appel API pour lever une exception HTTP
        from httpx import ConnectError # Exemple d'erreur HTTP
        mock_exception = ConnectError("Connection failed", request=MagicMock())
        mock_client_instance.get.side_effect = mock_exception

        service = TwitchAuthService(token_repository=mock_repo_instance)

        # Act
        is_valid = await service._is_token_valid(token)

        # Assert
        assert is_valid is False
        mock_client_instance.get.assert_awaited_once() # L'API Twitch doit être appelée (et lever l'erreur)
        mock_repo_instance.update_last_used.assert_not_awaited()
        mock_repo_instance.invalidate_token.assert_not_awaited()

    @pytest.mark.asyncio
    async def test__is_token_valid_other_exception(self, MockAsyncClient, MockTokenRepository):
        # Arrange
        mock_repo_instance = MockTokenRepository.return_value
        mock_client_instance = MockAsyncClient.return_value
        mock_client_instance.get = AsyncMock() # Configurer get comme AsyncMock
        mock_client_instance.__aenter__ = AsyncMock(return_value=mock_client_instance) # Simuler le contexte async with
        mock_client_instance.__aexit__ = AsyncMock(return_value=None)

        # Configurer les méthodes asynchrones du repository mocké
        mock_repo_instance.get_current_token = AsyncMock()
        mock_repo_instance.save_token = AsyncMock()
        mock_repo_instance.update_last_used = AsyncMock()
        mock_repo_instance.invalidate_token = AsyncMock()

        # Simuler un token valide localement
        valid_expires_at = datetime.utcnow() + timedelta(hours=2)
        mock_token_data = {
            "access_token": "token_for_other_error",
            "expires_in": 7200,
            "token_type": "bearer",
            "expires_at": valid_expires_at.isoformat(),
            "is_valid": True
        }
        token = TwitchToken(**mock_token_data)

        # Mock de update_last_used pour lever une exception
        # Nous mockons ici une méthode du repository pour simuler une erreur qui n'est pas liée à l'API call
        mock_repo_instance.update_last_used = AsyncMock(side_effect=Exception("Repository error"))
        # Assurez-vous que l'appel API réussit pour atteindre cette branche
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.raise_for_status = MagicMock() # Ne lève pas d'exception pour 200
        mock_client_instance.get.return_value = mock_response

        service = TwitchAuthService(token_repository=mock_repo_instance)

        # Act
        is_valid = await service._is_token_valid(token)

        # Assert
        assert is_valid is False
        mock_client_instance.get.assert_awaited_once() # L'API Twitch doit être appelée
