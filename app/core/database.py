# Arquivo para definir a configuração do banco de dados e a conexão com o banco de dados "Engine" do SQLAlchemy.

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.config import settings

# MOTOR DE CONEXÃO COM O BANCO DE DADOS
# pool_pre_ping=True ajuda a evitar erros de conexão ociosas
engine = create_engine(
  settings.SQLALCHEMY_DATABASE_URI,
  pool_pre_ping=True
)

# SESSÃO DO BANCO DE DADOS
# cada requisição terá sua própria sessão
SessionLocal = sessionmaker(
  autocommit=False,
  autoflush=False,
  bind=engine
)

# BASE DECLARATIVA
# classe base para todos os MODELS (tabelas) herdarem
Base = declarative_base()

# Dependency Injection: Função para o FastAPI usar nas rotas
def get_db():
  db = SessionLocal()
  try:
    yield db
  finally:
    db.close()
