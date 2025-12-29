from datetime import datetime
from sqlalchemy import Column, Integer, DateTime
from app.core.database import Base

class TimeStampedModel(Base):
  """
  Classe abstrata que adiciona campos de auditoria (created_at, updated_at)
  automaticamente a todas as tabelas que herdarem dela.
  """
  __abstract__ = True

  id = Column(
    Integer,
    primary_key=True,
    autoincrement=True,
    nullable=False,
    unique=True,
    index=True,
    )
  
  created_at = Column(
    DateTime,
    default=datetime.astimezone.utcnow,
    nullable=False)
  
  updated_at = Column(
    DateTime,
    default=datetime.astimezone.utcnow,
    onupdate=datetime.astimezone.utcnow,
    nullable=False)