
import pandas as pd
from decimal import Decimal
from datetime import date
from app.services.simulation_engine import SimulationEngine

def test_simulation():
    print("Testing Simulation Engine...")
    
    # Mock Forecast (Healthy Cashflow: +500/month)
    forecast_data = {
        "forecast_month": ["2024-03", "2024-04", "2024-05", "2024-06"],
        "predicted_cashflow": [500.0, 500.0, 500.0, 500.0]
    }
    df = pd.DataFrame(forecast_data)
    current_bal = Decimal(2000) # Starting with 2k
    
    print(f"\nScenario 1: Buy fancy laptop ($2500 one-time)")
    # Should dip to negative in month 1: 2000 + 500 - 2500 = 0? No wait.
    # Start: 2000. 
    # Month 1 (+500 - 2500) = Net -2000. End Bal = 0.
    # Actually logic: running_bal += flow.
    # Flow = 500 - 2500 = -2000.
    # Bal = 2000 + (-2000) = 0.
    
    # If laptop is 3000:
    # Flow = 500 - 3000 = -2500. 
    # Bal = 2000 - 2500 = -500. -> Avoid.
    
    res1 = SimulationEngine.simulate_decision(
        current_balance=current_bal,
        forecast_df=df,
        decision_type="ONE_TIME",
        amount=Decimal(3000),
        start_date=date(2024, 3, 15)
    )
    print("Result:", res1)
    assert res1['recommendation'] == "Avoid", "Should avoid bankruptcy"
    
    print(f"\nScenario 2: Netflix Subscription ($20 recurring)")
    # Impact is small. Balances should grow.
    res2 = SimulationEngine.simulate_decision(
        current_balance=current_bal,
        forecast_df=df,
        decision_type="RECURRING",
        amount=Decimal(20),
        start_date=date(2024, 3, 1)
    )
    print("Result:", res2)
    assert res2['recommendation'] == "Safe", "Should be safe"
    
    print(f"\nScenario 3: Big EMI ($1000/month for 4 months)")
    # Month 1: 2000 + (500 - 1000) = 1500
    # Month 2: 1500 + (500 - 1000) = 1000 (Hit Safety Buffer 1000?)
    # Month 3: 1000 + (500 - 1000) = 500 (Caution)
    # Month 4: 500 + (500 - 1000) = 0 (Caution/Avoid)
    
    res3 = SimulationEngine.simulate_decision(
        current_balance=current_bal,
        forecast_df=df,
        decision_type="EMI",
        amount=Decimal(1000),
        start_date=date(2024, 3, 1),
        duration_months=4
    )
    print("Result:", res3)
    assert res3['recommendation'] != "Safe", "Should warn about depleting savings"

    print("\nSUCCESS: Simulation Logic Verified")

if __name__ == "__main__":
    test_simulation()
