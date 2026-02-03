
from decimal import Decimal
from typing import List, Dict, Optional
from datetime import date
from dateutil.relativedelta import relativedelta
import pandas as pd

class SimulationEngine:
    
    @staticmethod
    def simulate_decision(
        current_balance: Decimal,
        forecast_df: pd.DataFrame,
        decision_type: str, # ONE_TIME, RECURRING, EMI
        amount: Decimal,
        start_date: date,
        duration_months: Optional[int] = None
    ) -> dict:
        """
        Simulates a financial decision against a forecast.
        
        Args:
            current_balance: Starting cash on hand.
            forecast_df: DataFrame from generate_simple_forecast (cols: forecast_month, predicted_cashflow)
            decision_type: "ONE_TIME" | "RECURRING" | "EMI"
            amount: Cost of decision (Positive value treated as expense)
            start_date: When the decision starts.
            duration_months: For EMI only.
            
        Returns:
            Dict with recommendation, confidence, explanation, and impact stats.
        """
        if forecast_df.empty:
            return {"error": "No forecast data available"}

        # 1. Prepare Simulation DataFrame
        # We work on copies to stay pure
        sim_df = forecast_df.copy()
        sim_df['simulated_cashflow'] = sim_df['predicted_cashflow']
        
        # 2. Apply Decision Logic
        impact_amt = float(amount)
        start_month_str = start_date.strftime("%Y-%m")
        
        months_affected_count = 0
        
        for idx, row in sim_df.iterrows():
            row_date = date.fromisoformat(f"{row['forecast_month']}-01")
            row_month_str = row['forecast_month']
            
            # Skip past months if start_date is in future
            # Simplified logic: compare YYYY-MM strings or dates
            if row_date < date(start_date.year, start_date.month, 1):
                continue

            apply_impact = False
            
            if decision_type == "ONE_TIME":
                if row_month_str == start_month_str:
                    apply_impact = True
                    
            elif decision_type == "RECURRING":
                apply_impact = True # Applies to all future months in forecast
                
            elif decision_type == "EMI":
                # Check if within duration
                # Calculate months diff
                diff = (row_date.year - start_date.year) * 12 + (row_date.month - start_date.month)
                if 0 <= diff < (duration_months or 0):
                    apply_impact = True
            
            if apply_impact:
                # Subtract expense (assuming amount is cost)
                sim_df.at[idx, 'simulated_cashflow'] -= impact_amt
                months_affected_count += 1

        # 3. Calculate Projected Balances
        # We need to run a cumulative sum starting from current balance
        # But wait, 'predicted_cashflow' is Net Flow (Income - Expense).
        # So Balance[t] = Balance[t-1] + NetFlow[t]
        
        # Initialize
        running_balance = float(current_balance)
        sim_df['projected_balance'] = 0.0
        
        # Apply iteratively
        lowest_balance = float('inf')
        
        for idx, row in sim_df.iterrows():
            flow = row['simulated_cashflow']
            running_balance += flow
            sim_df.at[idx, 'projected_balance'] = running_balance
            if running_balance < lowest_balance:
                lowest_balance = running_balance

        # 4. Generate Recommendation
        # Thresholds
        safety_buffer = 1000.0 # Hardcoded MVP heuristic. Should be dynamic (e.g. 1 month expenses)
        
        if lowest_balance < 0:
            rec = "Avoid"
            confidence = 95
            explanation = f"This decision leads to negative balance (${lowest_balance:,.2f}) in future months."
        elif lowest_balance < safety_buffer:
            rec = "Caution"
            confidence = 80
            explanation = f"Balance remains positive but dips below safety buffer (${safety_buffer}). Lowest: ${lowest_balance:,.2f}."
        else:
            rec = "Safe"
            confidence = 90
            explanation = f"Your balance stays healthy (min ${lowest_balance:,.2f}) throughout the period."

        return {
            "recommendation": rec,
            "confidence": confidence,
            "explanation": explanation,
            "projected_impact": {
                "lowest_balance": round(lowest_balance, 2),
                "months_affected": months_affected_count,
                "total_cost": round(impact_amt * months_affected_count, 2)
            }
        }
