
from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.ext.asyncio import AsyncSession
import uuid
from pydantic import BaseModel
from decimal import Decimal
from datetime import date
from typing import Optional

from app.core.database import get_db
from app.services.analytics import AnalyticsService
from app.services.simulation_engine import SimulationEngine

router = APIRouter()

class SimulationRequest(BaseModel):
    user_id: uuid.UUID
    decision_type: str # ONE_TIME, RECURRING, EMI
    amount: Decimal
    start_date: date
    duration_months: Optional[int] = None
    description: Optional[str] = "Simulated Expense"

@router.post("/run")
async def run_simulation(
    request: SimulationRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Runs a financial simulation against the user's forecast.
    """
    # 1. Get Forecast
    # Note: effectively re-using logic from analytics
    # In a real app we might cache the forecast or have a unified call
    # For now, we regenerate it to ensure freshness.
    
    # We need the DATAFRAME, not the formatted response object from AnalyticsService.generate_forecast.
    # So we call the underlying helpers directly or refactor AnalyticsService to expose the DF.
    # Refactoring AnalyticsService is cleaner but for speed let's just use helpers.
    
    from sqlalchemy import select
    from app.models.database_schema import Transaction, FinancialAccount
    from app.services.data_processing import compute_monthly_cashflow
    from app.services.forecasting import generate_simple_forecast
    
    # Fetch Txns
    q_txn = select(Transaction).where(Transaction.user_id == request.user_id)
    res_txn = await db.execute(q_txn)
    txns = res_txn.scalars().all()
    
    # Fetch Current Balance (moved up for fallback usage)
    q_bal = select(FinancialAccount).where(FinancialAccount.user_id == request.user_id)
    res_bal = await db.execute(q_bal)
    accounts = res_bal.scalars().all()
    current_balance = sum((a.current_balance for a in accounts), Decimal(0))
    
    hist_df = compute_monthly_cashflow(txns)
    
    # NEW: Fallback Logic
    is_low_data = False
    
    # If we have less than 2 months of history, we can't do a trend
    if len(hist_df) < 2:
        is_low_data = True
        # Create dummy forecast: 12 months of 0 net cashflow (conservative)
        from dateutil.relativedelta import relativedelta
        import pandas as pd
        
        today = date.today()
        forecast_rows = []
        for i in range(12):
            next_month = today + relativedelta(months=i+1)
            forecast_rows.append({
                "forecast_month": next_month.strftime("%Y-%m"),
                "predicted_cashflow": 0.0,
                "lower_bound": 0.0,
                "upper_bound": 0.0
            })
        forecast_df = pd.DataFrame(forecast_rows)
    else:
        forecast_df = generate_simple_forecast(hist_df, months_to_forecast=12) # 1 year lookahead
    
    # Run Simulation
    result = SimulationEngine.simulate_decision(
        current_balance=current_balance,
        forecast_df=forecast_df,
        decision_type=request.decision_type,
        amount=request.amount,
        start_date=request.start_date,
        duration_months=request.duration_months
    )
    
    # Adjust Confidence if Data was Low
    if is_low_data:
        # If mathematically "Safe" (because Balance > Cost), downgrade to "Caution" due to uncertainty
        if result["recommendation"] == "Safe":
            result["recommendation"] = "Caution"
            
        result["confidence"] = 40
        result["explanation"] = "Limited historical data. Recommendation based on conservative estimates (zero future growth) + current balance. " + result["explanation"]
    
    return result
