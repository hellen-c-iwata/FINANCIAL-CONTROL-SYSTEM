import enum
from xmlrpc.client import Boolean
from sqlalchemy import Column, String, Numeric, Date, ForeignKey, Enum, Integer
from sqlalchemy.orm import relationship
from app.models.base import TimeStampedModel

class TransactionType(str, enum.Enum):
    INCOME = "income" # RECEITA
    EXPENSE = "expense" # DESPESA
    INVESTMENT = "investment" # INVESTIMENTO

class Transaction(TimeStampedModel):
  __tablename__ = "transactions"

  description = Column(
    String,
    nullable=False
  )

  amount = Column(
    Numeric(10, 2),
    nullable=False
  )

  type = Column(
    Enum(TransactionType),
    nullable=False
  )

  date = Column(
    Date,
    nullable=False
  )

  is_paid = Column(
    Boolean,
    default=False,
    nullable=False
  )
  
  user_id = Column(
    Integer,
    ForeignKey("users.id"),
    nullable=False
  )

  category_id = Column(
    Integer,
    ForeignKey("categories.id"),
    nullable=False
  )

  owner = relationship("User", back_populates="transactions")
  category = relationship("Category", back_populates="transactions")