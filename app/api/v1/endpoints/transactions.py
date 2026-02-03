
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
import uuid

from app.core.database import get_db
from app.services.ingestion import IngestionService

router = APIRouter()

@router.post("/upload-csv")
async def upload_transactions(
    user_id: uuid.UUID = Query(..., description="The user to attach transactions to"),
    account_id: uuid.UUID = Form(..., description="The bank account ID these transactions belong to"),
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db)
):
    """
    Ingests a CSV of bank transactions.
    Required Columns: date, description, amount
    """
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Only CSV files allowed")
        
    content = await file.read()
    
    if len(content) == 0:
        raise HTTPException(status_code=400, detail="Empty file")

    try:
        result = await IngestionService.process_csv_upload(db, user_id, account_id, content)
        return result
    except ValueError as e:
        # Validation Errors (Missing columns, bad format)
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        # Unexpected Server Errors
        raise HTTPException(status_code=500, detail=f"Internal Processing Error: {str(e)}")
