
from pydantic import BaseModel, ConfigDict
from datetime import date, datetime
from typing import List, Optional, Dict, Any
from decimal import Decimal
from enum import Enum
import uuid

# Re-using Enums from DB schema if possible, or redefining for API boundary cleanliness
class TransactionDirection(str, Enum):
    INCOME = "income"
    EXPENSE = "expense"
    TRANSFER = "transfer"

# ==========================================
# Transactions
# ==========================================
class TransactionBase(BaseModel):
    account_id: uuid.UUID
    amount: Decimal
    direction: TransactionDirection
    description: str
    transaction_date: date
    category_primary: Optional[str] = None
    category_detailed: Optional[str] = None

class TransactionCreate(TransactionBase):
    """Schema for manual creation or single row ingestion"""
    pass

class TransactionResponse(TransactionBase):
    id: uuid.UUID
    user_id: uuid.UUID
    is_recurring: bool
    
    model_config = ConfigDict(from_attributes=True)

# ==========================================
# Forecasts
# ==========================================
class ForecastPoint(BaseModel):
    date: date
    balance: Decimal
    income: Decimal = Decimal(0)
    expense: Decimal = Decimal(0)
    # Added for frontend chart support
    predicted_balance: Decimal = Decimal(0)
    lower_bound: Decimal = Decimal(0)
    upper_bound: Decimal = Decimal(0)

class ForecastResponse(BaseModel):
    scenario_name: str
    data_points: List[ForecastPoint]

# ==========================================
# Simulation
# ==========================================
class ScenarioModificationCreate(BaseModel):
    name: str
    amount: Decimal
    start_date: date
    end_date: Optional[date] = None
    # recurring_rule: str ... kept simple for MVP

class SimulationRequest(BaseModel):
    scenario_name: str
    modifications: List[ScenarioModificationCreate]

class SimulationResult(BaseModel):
    scenario_id: uuid.UUID
    impact_summary: str
    forecast: ForecastResponse

# ==========================================
# Advice
# ==========================================
class AdviceResponse(BaseModel):
    id: uuid.UUID
    title: str
    content: str
    risk_level: str
    category: str
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)
