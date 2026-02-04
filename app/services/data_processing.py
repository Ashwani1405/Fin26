
import pandas as pd
from typing import List
from decimal import Decimal
from app.models.database_schema import Transaction, TransactionDirection

def compute_monthly_cashflow(transactions: List[Transaction]) -> pd.DataFrame:
    """
    Computes monthly cashflow (Income, Expense, Net) from a list of transactions.
    
    Args:
        transactions: List of SQLAlchemy Transaction objects.
        
    Returns:
        pd.DataFrame with columns: ['month', 'total_income', 'total_expense', 'net_cashflow']
        Sorted by month ascending.
    """
    if not transactions:
        return pd.DataFrame(columns=["month", "total_income", "total_expense", "net_cashflow"])

    # 1. Convert ORM objects to structured list for Pandas
    data = []
    for t in transactions:
        # Filter out Transfers for P&L view? 
        # Requirement implies Income/Expense focus. We'll skip transfers for strict cashflow (or keep separate).
        # For now, let's ignore TRANSFER type for the Net, or treat based on sign if provided.
        # But our Schema implies direction explicitly.
        
        # Normalize direction
        # Handle cases where it is an Enum object, a string, or a string repo of Enum (TransactionDirection.INCOME)
        raw_dir = t.direction
        if hasattr(raw_dir, 'value'):
            d_val = raw_dir.value
        else:
            d_val = str(raw_dir)
            # Fallback if it stringified as Class.MEMBER
            if "." in d_val: 
                d_val = d_val.split(".")[-1]
        
        d_val = d_val.lower()
        
        # Filter transfers
        if d_val == "transfer":
            continue
            
        data.append({
            "date": t.transaction_date,
            "amount": float(t.amount), 
            "direction": d_val 
        })
    
    if not data:
        return pd.DataFrame(columns=["month", "total_income", "total_expense", "net_cashflow"])

    df = pd.DataFrame(data)
    
    # 2. Pre-processing
    df['date'] = pd.to_datetime(df['date'])
    df['month'] = df['date'].dt.to_period('M').astype(str) # Format: YYYY-MM
    
    # 3. Vectorized Calculation
    # Masks (compare against string values)
    is_income = df['direction'] == "income"
    is_expense = df['direction'] == "expense"
    
    # We aggregate by Month
    # We can do this by creating separate columns first or grouping
    
    df['income_amt'] = df.loc[is_income, 'amount'].fillna(0)
    df['expense_amt'] = df.loc[is_expense, 'amount'].fillna(0)
    
    grouped = df.groupby('month')[['income_amt', 'expense_amt']].sum().reset_index()
    
    # 4. Finalizing
    grouped = grouped.rename(columns={
        'income_amt': 'total_income',
        'expense_amt': 'total_expense'
    })
    
    grouped['net_cashflow'] = grouped['total_income'] - grouped['total_expense']
    
    # DEBUG: Print final df
    print("DEBUG: Final Cashflow DF:\n", grouped)
    print("DEBUG: Sample direction:", df['direction'].unique() if not df.empty else "Empty")
    
    return grouped.sort_values('month')

# Example Usage (not run on import)
if __name__ == "__main__":
    # Mock Objects
    from datetime import date
    mock_txns = [
        Transaction(transaction_date=date(2024, 1, 15), amount=Decimal("5000"), direction=TransactionDirection.INCOME),
        Transaction(transaction_date=date(2024, 1, 20), amount=Decimal("150"), direction=TransactionDirection.EXPENSE),
        Transaction(transaction_date=date(2024, 2, 1), amount=Decimal("3000"), direction=TransactionDirection.INCOME),
    ]
    
    result = compute_monthly_cashflow(mock_txns)
    print(result)
