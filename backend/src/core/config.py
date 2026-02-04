from pydantic import BaseModel
import os


class Settings(BaseModel):
    app_name: str = "Questionnaire Agent API"
    environment: str = os.getenv("ENVIRONMENT", "development")
    cors_origins: list[str] = [
        origin.strip()
        for origin in os.getenv("CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173").split(",")
        if origin.strip()
    ]
    config_watch_interval: int = int(os.getenv("CONFIG_WATCH_INTERVAL", "300"))
    database_url: str = os.getenv("DATABASE_URL", "postgresql+psycopg://postgres:postgres@db:5432/makeball")
    chroma_path: str = os.getenv("CHROMA_PATH", "./.chroma")
    worker_broker_url: str = os.getenv("WORKER_BROKER_URL", "redis://redis:6379/0")
    worker_result_backend: str = os.getenv("WORKER_RESULT_BACKEND", "redis://redis:6379/1")
    storage_path: str = os.getenv("STORAGE_PATH", "./storage")
    embedding_model_name: str = os.getenv("EMBEDDING_MODEL_NAME", "sentence-transformers/all-MiniLM-L6-v2")
    embeddings_backend: str = os.getenv("EMBEDDINGS_BACKEND", "sentence_transformers")
    embeddings_device: str = os.getenv("EMBEDDINGS_DEVICE", "cpu")
    coarse_chunk_size: int = int(os.getenv("COARSE_CHUNK_SIZE", "1800"))
    coarse_chunk_overlap: int = int(os.getenv("COARSE_CHUNK_OVERLAP", "200"))
    citation_chunk_size: int = int(os.getenv("CITATION_CHUNK_SIZE", "800"))
    citation_chunk_overlap: int = int(os.getenv("CITATION_CHUNK_OVERLAP", "120"))
    questionnaire_output_path: str = os.getenv("QUESTIONNAIRE_OUTPUT_PATH", "./storage/questionnaires")
    llm_model_name: str = os.getenv("LLM_MODEL_NAME", "mistralai/Mistral-7B-Instruct-v0.2")
    llm_max_tokens: int = int(os.getenv("LLM_MAX_TOKENS", "512"))
    llm_backend: str = os.getenv("LLM_BACKEND", "transformers")
    llm_device: str = os.getenv("LLM_DEVICE", "cpu")
    llm_torch_dtype: str = os.getenv("LLM_TORCH_DTYPE", "float32")
    llm_local_files_only: bool = os.getenv("LLM_LOCAL_FILES_ONLY", "false").lower() in ("1", "true", "yes")
    coarse_top_k: int = int(os.getenv("COARSE_TOP_K", "6"))
    coarse_fetch_k: int = int(os.getenv("COARSE_FETCH_K", "12"))
    citation_top_k: int = int(os.getenv("CITATION_TOP_K", "6"))


settings = Settings()
