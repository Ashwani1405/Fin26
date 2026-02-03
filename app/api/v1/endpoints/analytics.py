
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
import uuid
from typing import List

from app.core.database import get_db
from app.services.analytics import AnalyticsService
from app.schemas.common import ForecastResponse, AdviceResponse

router = APIRouter()

@router.get("/cashflow/{user_id}")
async def get_cashflow(user_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    return await AnalyticsService.get_cashflow_summary(db, user_id)

@router.get("/forecast/{user_id}", response_model=ForecastResponse)
async def get_forecast(user_id: uuid.UUID, days: int = 30, db: AsyncSession = Depends(get_db)):
    return await AnalyticsService.generate_forecast(db, user_id, days)

@router.get("/advice/{user_id}", response_model=List[AdviceResponse])
async def get_advice(user_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    return await AnalyticsService.get_latest_advice(db, user_id)
