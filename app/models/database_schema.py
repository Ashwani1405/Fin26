
import uuid
import datetime
from decimal import Decimal
from enum import Enum
from typing import List, Optional

from sqlalchemy import (
    Column, Integer, String, Boolean, DateTime, Date, 
    ForeignKey, Numeric, Text, Index, UniqueConstraint, JSON, Uuid
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.sql import func

# ==================================================================================
# Base Configuration
# ==================================================================================

class Base(DeclarativeBase):
    pass

class TimestampMixin:
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

# ==================================================================================
# Enums
# ==================================================================================

class CurrencyCode(str, Enum):
    USD = "USD"
    EUR = "EUR"
    GBP = "GBP"
    CAD = "CAD"

class AccountType(str, Enum):
    CHECKING = "checking"
    SAVINGS = "savings"
    CREDIT = "credit"
    INVESTMENT = "investment"
    LOAN = "loan"

class TransactionDirection(str, Enum):
    INCOME = "income"
    EXPENSE = "expense"
    TRANSFER = "transfer"

class RiskScoreLevel(str, Enum):
    VERY_LOW_RISK = "very_low"
    LOW_RISK = "low"
    MODERATE_RISK = "moderate"
    HIGH_RISK = "high"
    CRITICAL_RISK = "critical"

class ModelType(str, Enum):
    FORECASTING = "forecasting"
    CLASSIFICATION = "classification"
    RECOMMENDATION = "recommendation"
    RISK_ASSESSMENT = "risk_assessment"

# ==================================================================================
# Core Identity & Banking
# ==================================================================================

class User(Base, TimestampMixin):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    full_name: Mapped[str] = mapped_column(String(255), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    
    preferences: Mapped[dict] = mapped_column(JSON, default=dict)

    accounts: Mapped[List["FinancialAccount"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    scenarios: Mapped[List["Scenario"]] = relationship(back_populates="user")
    alerts: Mapped[List["FinancialAdvice"]] = relationship(back_populates="user")
    risk_profiles: Mapped[List["RiskProfile"]] = relationship(back_populates="user")

    def __repr__(self):
        return f"<User {self.email}>"


class FinancialAccount(Base, TimestampMixin):
    __tablename__ = "financial_accounts"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    
    institution_name: Mapped[str] = mapped_column(String(255), nullable=False)
    account_name: Mapped[str] = mapped_column(String(255), nullable=False)
    account_type: Mapped[AccountType] = mapped_column(String(50), nullable=False) 
    
    current_balance: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False, default=0)
    currency: Mapped[str] = mapped_column(String(3), default="USD")
    
    provider_metadata: Mapped[dict] = mapped_column(JSON, default=dict)
    last_synced_at: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True), nullable=True)

    user: Mapped["User"] = relationship(back_populates="accounts")
    transactions: Mapped[List["Transaction"]] = relationship(back_populates="account")

    def __repr__(self):
        return f"<Account {self.account_name} ({self.institution_name})>"


class Transaction(Base, TimestampMixin):
    __tablename__ = "transactions"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    account_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("financial_accounts.id"), nullable=False, index=True)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    
    amount: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False)
    direction: Mapped[TransactionDirection] = mapped_column(String(20), nullable=False, default=TransactionDirection.EXPENSE)
    
    currency: Mapped[str] = mapped_column(String(3), default="USD")
    description: Mapped[str] = mapped_column(Text, nullable=False)
    merchant_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, index=True)
    
    transaction_date: Mapped[datetime.date] = mapped_column(Date, nullable=False, index=True)
    posted_date: Mapped[Optional[datetime.date]] = mapped_column(Date, nullable=True)

    category_primary: Mapped[Optional[str]] = mapped_column(String(100), index=True)
    category_detailed: Mapped[Optional[str]] = mapped_column(String(100))
    tags: Mapped[list] = mapped_column(JSON, default=list) # SQLite doesn't have ARRAY
    
    is_recurring: Mapped[bool] = mapped_column(Boolean, default=False)
    recurring_frequency: Mapped[Optional[str]] = mapped_column(String(50))
    
    is_excluded_from_forecast: Mapped[bool] = mapped_column(Boolean, default=False)
    
    raw_import_data: Mapped[dict] = mapped_column(JSON, default=dict)

    account: Mapped["FinancialAccount"] = relationship(back_populates="transactions")

    __table_args__ = (
        Index('idx_transactions_user_date', 'user_id', 'transaction_date'),
    )


class MLModel(Base, TimestampMixin):
    __tablename__ = "ml_models"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    version: Mapped[str] = mapped_column(String(50), nullable=False)
    model_type: Mapped[ModelType] = mapped_column(String(50), nullable=False)
    is_active_production: Mapped[bool] = mapped_column(Boolean, default=False)
    
    parameters: Mapped[dict] = mapped_column(JSON, default=dict)
    training_metrics: Mapped[dict] = mapped_column(JSON, default=dict)
    
    training_data_hash: Mapped[Optional[str]] = mapped_column(String(255))
    code_commit_sha: Mapped[Optional[str]] = mapped_column(String(40))
    artifact_path: Mapped[str] = mapped_column(String(500))

    __table_args__ = (
        UniqueConstraint('name', 'version', name='uq_model_version'),
    )

class CashflowForecast(Base, TimestampMixin):
    __tablename__ = "cashflow_forecasts"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    
    generated_by_model_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("ml_models.id"), nullable=True)
    scenario_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("scenarios.id"), nullable=True)

    forecast_date: Mapped[datetime.date] = mapped_column(Date, nullable=False)
    projected_balance: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False)
    projected_income: Mapped[Decimal] = mapped_column(Numeric(18, 4), default=0)
    projected_expense: Mapped[Decimal] = mapped_column(Numeric(18, 4), default=0)
    
    confidence_interval_lower: Mapped[Optional[Decimal]] = mapped_column(Numeric(18, 4))
    confidence_interval_upper: Mapped[Optional[Decimal]] = mapped_column(Numeric(18, 4))

    __table_args__ = (
        Index('idx_forecast_user_scenario_date', 'user_id', 'scenario_id', 'forecast_date'),
    )


class Scenario(Base, TimestampMixin):
    __tablename__ = "scenarios"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    is_baseline: Mapped[bool] = mapped_column(Boolean, default=False)

    modifications: Mapped[List["ScenarioModification"]] = relationship(back_populates="scenario", cascade="all, delete-orphan")
    user: Mapped["User"] = relationship(back_populates="scenarios")


class ScenarioModification(Base, TimestampMixin):
    __tablename__ = "scenario_modifications"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    scenario_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("scenarios.id"), nullable=False)
    
    name: Mapped[str] = mapped_column(String(255))
    modification_type: Mapped[str] = mapped_column(String(50))
    
    amount: Mapped[Decimal] = mapped_column(Numeric(18, 4))
    start_date: Mapped[datetime.date] = mapped_column(Date, nullable=False)
    end_date: Mapped[Optional[datetime.date]] = mapped_column(Date, nullable=True)
    
    recurrence_rule: Mapped[Optional[str]] = mapped_column(String(100))
    parameters: Mapped[dict] = mapped_column(JSON, default=dict)

    scenario: Mapped["Scenario"] = relationship(back_populates="modifications")


class RiskProfile(Base, TimestampMixin):
    __tablename__ = "risk_profiles"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    generated_by_model_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("ml_models.id"), nullable=True)

    assessment_date: Mapped[datetime.date] = mapped_column(Date, nullable=False, default=datetime.date.today)
    overall_risk_score: Mapped[int] = mapped_column(Integer)
    risk_level: Mapped[RiskScoreLevel] = mapped_column(String(50))
    
    risk_factors: Mapped[dict] = mapped_column(JSON, default=dict)

    user: Mapped["User"] = relationship(back_populates="risk_profiles")


class FinancialAdvice(Base, TimestampMixin):
    __tablename__ = "financial_advice"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    generated_by_model_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("ml_models.id"), nullable=True)

    title: Mapped[str] = mapped_column(String(255), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    
    risk_level: Mapped[str] = mapped_column(String(50), default="medium")
    category: Mapped[str] = mapped_column(String(100))
    
    is_dismissed: Mapped[bool] = mapped_column(Boolean, default=False)
    dismissed_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(timezone=True))
    
    is_pinned: Mapped[bool] = mapped_column(Boolean, default=False)
    viewed_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(timezone=True))

    related_transaction_ids: Mapped[list] = mapped_column(JSON, default=list)

    user: Mapped["User"] = relationship(back_populates="alerts")
