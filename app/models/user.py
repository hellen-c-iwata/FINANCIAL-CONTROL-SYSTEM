from sqlalchemy import Column, String, Boolean, ForeignKey, Integer
from sqlalchemy.orm import relationship
from app.models.base import TimeStampedModel


class User(TimeStampedModel):
  """
  Modelo de usuário que herda os campos de auditoria de TimeStampedModel.
  """

  __tablename__ = "users"
  
  email = Column(
    String,
    unique=True,
    nullable=False,
    index=True
  )
  
  full_name = Column(
    String,
    nullable=False
  )
  
  # Integração com Telegram (ID único do usuário no Telegram, pode ser nulo se o usuário não vinculou a conta)
  telegram_id = Column(
    String,
    unique=True,
    nullable=False,
    index=True
  )
  
  is_active = Column(
    Boolean,
    default=True,
    nullable=False
  )

  # Relacionamentos e outros campos específicos do usuário podem ser adicionados aqui
  transactions = relationship("Transaction", back_populates="owner")
  categories = relationship("Category", back_populates="owner")

class Category(TimeStampedModel):
  __tablename__ = "categories"

  name = Column(
    String,
    nullable=False
  )

  user_id = Column(
    Integer,
    ForeignKey("users.id"),
    nullable=False
  )
  is_default = Column(
    Boolean,
    default=False,
    nullable=False
  )

  owner = relationship("User", back_populates="categories")
  transactions = relationship("Transaction", back_populates="category")