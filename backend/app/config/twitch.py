from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache

class TwitchSettings(BaseSettings):
    client_id: str
    client_secret: str
    redirect_uri: str
    token_url: str = "https://id.twitch.tv/oauth2/token"
    validate_url: str = "https://id.twitch.tv/oauth2/validate"
    api_base_url: str = "https://api.twitch.tv/helix"
    
    # Paramètres du circuit breaker
    circuit_breaker_failure_threshold: int = 5
    circuit_breaker_reset_timeout: int = 60
    circuit_breaker_success_threshold: int = 2
    
    # Rate limiting
    rate_limit_calls: int = 800  # Nombre d'appels autorisés
    rate_limit_period: int = 60  # Période en secondes (1 minute)
    
    # Token management
    token_refresh_before_expiry: int = 3600  # Renouveler 1h avant expiration
    
    # Remplacer class Config par model_config
    model_config = SettingsConfigDict(env_prefix="TWITCH_", env_file=".env", case_sensitive=False)

@lru_cache()
def get_twitch_settings() -> TwitchSettings:
    return TwitchSettings() 