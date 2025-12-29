from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import PostgresDsn, RedisDsn, computed_field

# Será usado o Pydantic para gerenciar as configurações da aplicação e variáveis de ambiente
# usar os.getenv() diretamente é mais propenso a erros e menos flexível

class Settings(BaseSettings):
    # Informações Básicas
    PROJECT_NAME: str = "Plataform Financial Management System"
    API_V1_STR: str = "/api/v1"

    # Banco de Dados (Postgres)
    DB_USER: str
    DB_PASSWORD: str
    DB_NAME: str
    DB_HOST: str = "db" # Nome do serviço no docker-compose
    DB_PORT: int = 5432

    # Redis
    REDIS_HOST: str = "redis" # Nome do serviço no docker-compose
    REDIS_PORT: int = 6379

    # Tokens e Segurança 
    # SECRET_KEY: str

    @computed_field
    def SQLALCHEMY_DATABASE_URI(self) -> str:
        # Monta a URL de conexão automaticamente: postgresql://user:pass@host:port/db
        return str(PostgresDsn.build(
            scheme="postgresql",
            username=self.DB_USER,
            password=self.DB_PASSWORD,
            host=self.DB_HOST,
            port=self.DB_PORT,
            path=f"{self.DB_NAME}",
        ))

    @computed_field
    def CELERY_BROKER_URL(self) -> str:
        return str(RedisDsn.build(
            scheme="redis",
            host=self.REDIS_HOST,
            port=self.REDIS_PORT,
            path="0",
        ))

    @computed_field
    def CELERY_RESULT_BACKEND(self) -> str:
        return str(RedisDsn.build(
            scheme="redis",
            host=self.REDIS_HOST,
            port=self.REDIS_PORT,
            path="/1", # Usamos DB 1 para resultados, DB 0 para fila
        ))

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra="ignore"
    )

settings = Settings()