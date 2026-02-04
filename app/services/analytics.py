
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
    async def get_cashflow_summary(db: AsyncSession, user_id: uuid.UUID) -> List[dict]:
        """
        Aggregates monthly income vs expense history (past 12 months).
        """
        # 1. Fetch Transactions (last 12 months to roughly now)
        today = date.today()
        # Fetch loosely all history or last year. For charts, usually last 12 months.
        query = select(Transaction).where(
            Transaction.user_id == user_id
        ).order_by(Transaction.transaction_date.asc())
        
        result = await db.execute(query)
        transactions = result.scalars().all()
        
        # 2. Compute Monthly Cashflow
        from app.services.data_processing import compute_monthly_cashflow
        df = compute_monthly_cashflow(transactions)
        
        # 3. Format for API
        # Expected: [{month: "2024-01", income: 5000, expense: 2000, net: 3000}, ...]
        data = []
        # If empty df, return empty list or defaults? Frontend handles empty list.
        
        # We might want to filter only last 12 months if array is huge, 
        # but for MVP returning all available history is fine or limiting in pandas.
        # Let's take tail(12)
        if not df.empty:
            df = df.tail(12)
            
        for _, row in df.iterrows():
            data.append({
                "month": row['month'],
                "income": float(row['total_income']),
                "expense": float(row['total_expense']),
                "net": float(row['net_cashflow'])
            })
            
        return data


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
                balance=Decimal(f"{row['predicted_cashflow']:.2f}"), 
                income=Decimal(0),
                expense=Decimal(0),
                # Map new fields
                predicted_balance=Decimal(f"{row['predicted_cashflow']:.2f}"),
                lower_bound=Decimal(f"{row['lower_bound']:.2f}"),
                upper_bound=Decimal(f"{row['upper_bound']:.2f}")
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
