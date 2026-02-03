
import io
import uuid
import pandas as pd
from decimal import Decimal
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, BinaryIO

from app.models.database_schema import Transaction, FinancialAccount
from app.schemas.common import TransactionDirection

REQUIRED_COLUMNS = {"date", "description", "amount"}

class IngestionService:
    
    @staticmethod
    async def process_csv_upload(
        db: AsyncSession, 
        user_id: uuid.UUID, 
        account_id: uuid.UUID, 
        file_content: bytes
    ) -> dict:
        """
        Ingests bank transactions from CSV using Pandas.
        
        Logic:
        - Validates columns (date, description, amount)
        - Normalizes types (Decimals, Dates)
        - Infers Direction (Income > 0, Expense < 0)
        - Stores raw row in JSONB for audit
        """
        
        if not file_content:
            raise ValueError("Empty file content")

        try:
            # Load into Pandas
            df = pd.read_csv(io.BytesIO(file_content))
            
            # 1. Validate Columns
            # We strip whitespace from columns to be forgiving
            df.columns = df.columns.str.strip().str.lower()
            missing = REQUIRED_COLUMNS - set(df.columns)
            if missing:
                raise ValueError(f"Missing required columns: {missing}")
            
            # 2. empty check
            if df.empty:
                raise ValueError("CSV contains no data rows")

            objects_to_add = []
            
            # 3. Iterate and Normalize
            # using itertuples for speed, but iterrows is fine for MVP volumes
            for _, row in df.iterrows():
                # Data cleanup
                try:
                    raw_date = row['date']
                    raw_desc = row['description'] 
                    raw_amount = row['amount']
                    
                    # Date Parsing (Handle common formats)
                    # pandas to_datetime is smart but we want strict python objects
                    txn_date = pd.to_datetime(raw_date).date()
                    
                    # Decimal conversion (handle currency symbols if present? MVP assumes clean #s)
                    # TODO: Add robust string cleaning (remove '$', ',')
                    amount_val = Decimal(str(raw_amount))
                    
                    # Infer Direction
                    if amount_val > 0:
                        direction = TransactionDirection.INCOME
                        clean_amount = amount_val
                    else:
                        direction = TransactionDirection.EXPENSE
                        clean_amount = abs(amount_val)
                    
                    # Store Raw Data for ML/Audit later
                    # Convert row to dict, ensure JSON serializable
                    raw_data = row.to_dict()
                    # Pandas timestamps aren't JSON serializable by default, cast to str if needed
                    # but pure read_csv usually keeps strings unless parsed. row.to_dict handles basic types.
                    
                    txn = Transaction(
                        id=uuid.uuid4(),
                        account_id=account_id,
                        user_id=user_id,
                        transaction_date=txn_date,
                        description=str(raw_desc).strip(),
                        amount=clean_amount,
                        direction=direction,
                        raw_import_data={k: str(v) for k, v in raw_data.items()} # Safest for JSONB
                    )
                    objects_to_add.append(txn)
                    
                except Exception as e:
                    # In a real app, we might log errors formatted and continue partial insert,
                    # or fail hard. For MVP, failing hard on bad data is safer integration.
                    raise ValueError(f"Row data error: {e} | Content: {row.to_dict()}")

            if objects_to_add:
                db.add_all(objects_to_add)
                await db.commit()
            
            return {
                "status": "success", 
                "rows_ingested": len(objects_to_add)
            }

        except pd.errors.EmptyDataError:
            raise ValueError("The CSV file is empty")
        except pd.errors.ParserError:
            raise ValueError("Invalid CSV format")
        except Exception as e:
            # Re-raise known ValueErrors, wrap others
            if isinstance(e, ValueError):
                raise e
            raise RuntimeError(f"Ingestion failed: {str(e)}")
