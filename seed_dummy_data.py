
import asyncio
import uuid
from decimal import Decimal
from app.core.database import engine, AsyncSessionLocal
from app.models.database_schema import User, FinancialAccount, AccountType

async def seed():
    async with AsyncSessionLocal() as session:
        # Create Dummy User
        user_id = uuid.uuid4()
        user = User(
            id=user_id,
            email=f"dummy_{user_id}@example.com",
            full_name="Test User"
        )
        
        # Create Dummy Account
        account_id = uuid.uuid4()
        account = FinancialAccount(
            id=account_id,
            user_id=user_id,
            institution_name="Demo Bank",
            account_name="Checking 001",
            account_type=AccountType.CHECKING,
            current_balance=Decimal("1500.00")
        )
        
        session.add(user)
        session.add(account)
        await session.commit()
        
        print("\n" + "="*50)
        print("SEED DATA CREATED SUCCESSFULLY")
        print("="*50)
        print(f"User ID:    {user_id}")
        print(f"Account ID: {account_id}")
        print("="*50)
        print("\nRun the verified CSV upload test with:")
        print(f"python test_upload_real.py --user_id {user_id} --account_id {account_id}")

if __name__ == "__main__":
    asyncio.run(seed())
