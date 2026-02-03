
import pandas as pd
from app.services.forecasting import generate_simple_forecast

def test_forecast():
    print("Testing Forecast Logic...")
    
    # Case 1: Rich History
    data_rich = {
        "month": ["2023-10", "2023-11", "2023-12", "2024-01"],
        "net_cashflow": [1000, 1200, 800, 1500]
    }
    df_rich = pd.DataFrame(data_rich)
    
    forecast = generate_simple_forecast(df_rich, months_to_forecast=3)
    
    print("\nHistory:")
    print(df_rich)
    print("\nForecast (Rich Data):")
    print(forecast)
    
    # Assertions
    # Baseline: (1200*0.3) + (800*0.3) + (1500*0.4) = 360 + 240 + 600 = 1200
    assert len(forecast) == 3
    first_pred = forecast.iloc[0]['predicted_cashflow']
    assert first_pred == 1200.0, f"Expected 1200, got {first_pred}"
    assert forecast.iloc[0]['forecast_month'] == "2024-02"

    # Case 2: Sparse History
    data_sparse = {
        "month": ["2024-01"],
        "net_cashflow": [500]
    }
    df_sparse = pd.DataFrame(data_sparse)
    forecast_sparse = generate_simple_forecast(df_sparse)
    print("\nForecast (Sparse Data):")
    print(forecast_sparse.head(1))
    
    assert forecast_sparse.iloc[0]['predicted_cashflow'] == 500.0
    
    print("\nSUCCESS: Forecast Logic Verified")

if __name__ == "__main__":
    test_forecast()
