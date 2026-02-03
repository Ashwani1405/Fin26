
import sys
import os
import uuid
from fastapi.testclient import TestClient

# Add current directory to path
sys.path.append(os.getcwd())

# Import app for TestClient
try:
    from app.main import app
    client = TestClient(app)
except ImportError as e:
    print(f"Error importing app: {e}")
    sys.exit(1)

def test_manual_upload(user_id_str, account_id_str):
    print(f"Testing Upload for User: {user_id_str}, Account: {account_id_str}")
    
    csv_content = b"""date,description,amount
2024-01-01,Opening Balance,5000.00
2024-01-05,Grocery Store,-150.50
2024-01-15,Paycheck,2500.00
2024-01-20,Rent Payment,-1200.00"""

    files = {"file": ("bank_statement.csv", csv_content, "text/csv")}
    
    try:
        response = client.post(
            f"/api/v1/transactions/upload-csv?user_id={user_id_str}",
            data={"account_id": account_id_str},
            files=files
        )
        
        if response.status_code == 200:
            print("\nSUCCESS: Upload Processed!")
            print(f"Response: {response.json()}")
        else:
            print(f"\nFAILURE: Status {response.status_code}")
            print(f"Detail: {response.text}")

    except Exception as e:
        print(f"EXCEPTION: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python test_upload_real.py <user_id> <account_id>")
    else:
        test_manual_upload(sys.argv[1], sys.argv[2])
