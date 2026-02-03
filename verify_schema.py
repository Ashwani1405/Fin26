
import sys
import os

# Add current directory to path
sys.path.append(os.getcwd())

try:
    from database_schema import Base, User, FinancialAccount, Transaction, CashflowForecast, Scenario, FinancialAdvice, RiskProfile
    print("SUCCESS: All models imported corectly.")
    
    # Introspect to ensure relationships are set up (basic check)
    print(f"User table: {User.__tablename__}")
    print(f"RiskProfile table: {RiskProfile.__tablename__}")
    print(f"Account table: {FinancialAccount.__tablename__}")
    print("Schema is valid Python code.")
except ImportError as e:
    print(f"FAILURE: Import Error - {e}")
except Exception as e:
    print(f"FAILURE: General Error - {e}")
