import os
from pydantic import BaseSettings, ConfigDict
from dotenv import load_dotenv

load_dotenv()

client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")

class Settings(BaseSettings):
    CLIENT_ID: str
    CLIENT_SECRET: str
    # ... you can add other variables (ex. REDIRECT_URI)

    model_config = ConfigDict(env_file=".env")

settings = Settings()
