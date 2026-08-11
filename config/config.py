from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str
    ENVIRONMENT: str = "development"

    embedding_model: str
    embedding_model_api_key: str
    embedding_dimensions: int
    base_url: str
    llm: str
    llm_api_key: str
    min_credible_chunks: int
    similarity_threshold: float
    answer_context_count: int
    

    class Config:
        env_file = ".env" 
        env_file_encoding = "utf-8"


settings = Settings()