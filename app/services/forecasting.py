
import pandas as pd
import numpy as np
from typing import List, Optional
from datetime import date, timedelta
from dateutil.relativedelta import relativedelta

def generate_simple_forecast(
    history_df: pd.DataFrame, 
    months_to_forecast: int = 6
) -> pd.DataFrame:
    """
    Generates a generic MVP forecast based on historical cashflow.
    
    Algorithm:
    1. Weighted Moving Average of last 3 months (30%, 30%, 40%).
    2. Fallback to Global Average if < 3 months data.
    3. Uncertainty: Fixed +/- 20% band.
    
    Args:
        history_df: DataFrame with ['month', 'net_cashflow']
        
    Returns:
        DataFrame with ['forecast_month', 'predicted_cashflow', 'lower_bound', 'upper_bound']
    """
    if history_df.empty or 'net_cashflow' not in history_df.columns:
         return pd.DataFrame()

    # Ensure sorted
    df = history_df.sort_values('month').copy()
    
    # 1. Determine Baseline
    values = df['net_cashflow'].values
    
    if len(values) >= 3:
        # Simple weighted average of last 3
        # Giving slight weight to most recent
        baseline = (values[-3] * 0.3) + (values[-2] * 0.3) + (values[-1] * 0.4)
    else:
        # Not enough data, use global mean
        baseline = np.mean(values)
        
    # 2. Project Forward
    # Get last actual month
    last_month_str = df['month'].iloc[-1]
    last_date = date.fromisoformat(f"{last_month_str}-01")
    
    forecast_rows = []
    
    for i in range(1, months_to_forecast + 1):
        next_date = last_date + relativedelta(months=i)
        next_month_str = next_date.strftime("%Y-%m")
        
        # In a real model, we'd apply a trend or seasonality here.
        # For MVP, flat line projection is often safer than wild polynomial fits.
        prediction = float(baseline)
        
        # Uncertainty (20%)
        # TODO: Calculate std dev of history for dynamic bounds
        uncertainty = abs(prediction) * 0.2
        
        forecast_rows.append({
            "forecast_month": next_month_str,
            "predicted_cashflow": round(prediction, 2),
            "lower_bound": round(prediction - uncertainty, 2),
            "upper_bound": round(prediction + uncertainty, 2)
        })
        
    return pd.DataFrame(forecast_rows)
