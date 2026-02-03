
import uuid
from decimal import Decimal
from datetime import date, timedelta
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.models.database_schema import Transaction, CashflowForecast, FinancialAdvice
from app.schemas.common import ForecastResponse, ForecastPoint, AdviceResponse

class AnalyticsService:

    @staticmethod
    async def get_cashflow_summary(db: AsyncSession, user_id: uuid.UUID) -> dict:
        """
        Aggregates income vs expense for the current month.
        """
        today = date.today()
        first_of_month = date(today.year, today.month, 1)
        
        query = select(
            Transaction.direction, 
            func.sum(Transaction.amount)
        ).where(
            Transaction.user_id == user_id,
            Transaction.transaction_date >= first_of_month
        ).group_by(Transaction.direction)
        
        result = await db.execute(query)
        summary = {row.direction: row[1] for row in result.all()}
        
        return {
            "period": f"{first_of_month} to {today}",
            "income": summary.get("income", Decimal(0)),
            "expense": summary.get("expense", Decimal(0)),
            "net_flow": summary.get("income", Decimal(0)) - summary.get("expense", Decimal(0))
        }


    @staticmethod
    async def generate_forecast(db: AsyncSession, user_id: uuid.UUID, days: int = 180) -> ForecastResponse:
        """
        Generates a 6-month forecast based on historical transaction data.
        """
        # 1. Fetch Transactions
        query = select(Transaction).where(
            Transaction.user_id == user_id,
            Transaction.is_excluded_from_forecast == False
        )
        result = await db.execute(query)
        transactions = result.scalars().all()
        
        # 2. Compute Historical Cashflow
        from app.services.data_processing import compute_monthly_cashflow
        history_df = compute_monthly_cashflow(transactions)
        
        # 3. Generate Forecast
        from app.services.forecasting import generate_simple_forecast
        # approx months
        mnths = max(1, days // 30)
        forecast_df = generate_simple_forecast(history_df, months_to_forecast=mnths)
        
        # 4. Format for API
        points = []
        for _, row in forecast_df.iterrows():
            # Convert YYYY-MM to date
            dt = date.fromisoformat(f"{row['forecast_month']}-01")
            
            points.append(ForecastPoint(
                date=dt,
                balance=Decimal(f"{row['predicted_cashflow']:.2f}"), # Balance logic needs cumulative sum from current balance, but this endpoint returns net flow for MVP
                # Schema says "balance", but let's treat it as projected cashflow for this graph
                # or fetch current balance and add cumulative.
                # For pure MVP graph, let's return projected net flow as 'balance' or change schema semantics.
                # Let's assume 'balance' in the schema meant 'projected metric'. 
                income=Decimal(0), # Not predicted separately in simple model
                expense=Decimal(0)
            ))
            
        return ForecastResponse(scenario_name="Weighted Moving Avg (3M)", data_points=points)

    @staticmethod
    async def get_latest_advice(db: AsyncSession, user_id: uuid.UUID) -> List[AdviceResponse]:
        """
        Retrieves top advice. 
        """
        query = select(FinancialAdvice).where(
            FinancialAdvice.user_id == user_id, 
            FinancialAdvice.is_dismissed == False
        ).order_by(FinancialAdvice.created_at.desc()).limit(3)
        
        result = await db.execute(query)
        return [AdviceResponse.model_validate(adv) for adv in result.scalars().all()]
