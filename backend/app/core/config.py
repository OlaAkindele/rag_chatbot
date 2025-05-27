from pydantic_settings import BaseSettings
from pydantic import ConfigDict


# configuration to enable env to be read 
class Settings(BaseSettings):
    # tell it to read from “.env”
    model_config = ConfigDict(env_file=".env")

    neo4j_uri:      str
    neo4j_username: str
    neo4j_password: str
    openai_api_key: str
    openai_model:   str

settings = Settings()


