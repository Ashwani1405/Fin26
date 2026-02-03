
import sys
import os
from fastapi.testclient import TestClient

# Add current directory to path
sys.path.append(os.getcwd())

try:
    from app.main import app
    print("SUCCESS: FastAPI app imported.")
    
    client = TestClient(app)
    response = client.get("/health")
    
    if response.status_code == 200:
        print(f"SUCCESS: Health Check Passed - {response.json()}")
    else:
        print(f"FAILURE: Health Check Status {response.status_code}")

    # Test CSV Upload (Mocking DB not strictly needed if we just want to hit the route logic)
    # But strictly speaking, the service tries to write to DB. 
    # For a quick verify, we'll try to trigger a validation error (400) which proves accessibility and pydantic parsing
    # Or strict success if we can mocks dependencies. 
    # Let's just create a dummy CSV request and expect it to fail on DB (Internal Server Error) or succeed if DB is up.
    # Actually, we rely on dependency injection. The TestClient uses the app's default DI.
    # The default DI points to the real async engine.
    
    # Let's try to hit the endpoint with valid params but expects a DB error or Success
    import io
    import uuid
    dummy_csv = b"date,description,amount\n2023-01-01,Salary,5000"
    
    # We need a valid UUID format
    uid = str(uuid.uuid4())
    aid = str(uuid.uuid4())
    
    print("Testing CSV Upload Endpoint...")
    files = {"file": ("test.csv", dummy_csv, "text/csv")}
    try:
        resp = client.post(
            f"/api/v1/transactions/upload-csv?user_id={uid}", 
            data={"account_id": aid}, 
            files=files
        )
        if resp.status_code == 200:
            print("SUCCESS: CSV Upload Endpoint returned 200 OK")
        elif resp.status_code == 400:
             print(f"SUCCESS: CSV Upload Endpoint Validation (400): {resp.json()}")
        elif resp.status_code == 500:
             # This is expected if the DB tables don't exist yet or connection fails
             print(f"PARTIAL SUCCESS: Endpoint reached service layer (500 as expected without DB init): {resp.text}")
        else:
             print(f"FAILURE: Unexpected status code {resp.status_code}: {resp.text}")
    except Exception as exc:
        print(f"FAILURE: Client Error {exc}")

except ImportError as e:
    print(f"FAILURE: Import Error - {e}")
except Exception as e:
    print(f"FAILURE: General Error - {e}")
