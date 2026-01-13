"""
Forecasting Tools
Predicts future legal spend based on historical data
Using FunctionTool pattern (official ADK approach)
"""
import pandas as pd
import numpy as np
from google.adk.tools import FunctionTool
from datetime import datetime, timedelta
import sys
import os


def forecast_spend(file_path: str, months_ahead: int = 3) -> str:
    """
    Forecasts future legal spend based on historical trends.
    
    Args:
        file_path: Path to the data file
        months_ahead: Number of months to forecast (default: 3)
        
    Returns:
        String summary of spend forecast
    """
    try:
        # Load data
        if file_path.endswith('.csv'):
            df = pd.read_csv(file_path)
        elif file_path.endswith('.parquet'):
            df = pd.read_parquet(file_path)
        else:
            return "❌ Error: Unsupported file type"
        
        # Normalize column names
        df.columns = df.columns.str.lower().str.strip().str.replace(' ', '_')
        
        # Find date and amount columns
        date_col = next((col for col in df.columns if 'date' in col.lower()), None)
        amount_col = next((col for col in df.columns if 'amount' in col.lower()), None)
        
        if not date_col or not amount_col:
            return "❌ Error: Could not find date or amount columns"
        
        # Convert date column
        df[date_col] = pd.to_datetime(df[date_col], errors='coerce')
        df = df.dropna(subset=[date_col])
        
        if df.empty or len(df) < 3:
            return "❌ Error: Insufficient data for forecasting (need at least 3 months)"
        
        # Extract month/year and aggregate
        df['month'] = df[date_col].dt.to_period('M')
        monthly_spend = df.groupby('month')[amount_col].sum().sort_index()
        
        if len(monthly_spend) < 3:
            return "❌ Error: Need at least 3 months of data for forecasting"
        
        # Simple linear regression for trend
        x = np.arange(len(monthly_spend))
        y = monthly_spend.values
        
        # Calculate trend line
        z = np.polyfit(x, y, 1)
        p = np.poly1d(z)
        
        # Generate forecast
        forecast_x = np.arange(len(monthly_spend), len(monthly_spend) + months_ahead)
        forecast_y = p(forecast_x)
        
        # Calculate confidence interval (simple approach)
        residuals = y - p(x)
        std_error = np.std(residuals)
        
        summary = []
        summary.append("=== Legal Spend Forecast ===\n")
        summary.append(f"Historical Period: {monthly_spend.index[0]} to {monthly_spend.index[-1]}")
        summary.append(f"Months of Data: {len(monthly_spend)}")
        summary.append(f"Average Monthly Spend: ${monthly_spend.mean():,.2f}\n")
        
        # Trend analysis
        if z[0] > 0:
            summary.append(f"📈 Trend: INCREASING (${z[0]:,.2f}/month)")
        elif z[0] < 0:
            summary.append(f"📉 Trend: DECREASING (${abs(z[0]):,.2f}/month)")
        else:
            summary.append(f"➡️ Trend: STABLE")
        
        summary.append(f"\nForecast for Next {months_ahead} Months:")
        
        # Generate future month labels
        last_month = monthly_spend.index[-1].to_timestamp()
        total_forecast = 0
        
        for i, forecast_val in enumerate(forecast_y, 1):
            future_month = (last_month + pd.DateOffset(months=i)).strftime('%Y-%m')
            lower_bound = max(0, forecast_val - (1.96 * std_error))
            upper_bound = forecast_val + (1.96 * std_error)
            
            summary.append(f"\n{future_month}:")
            summary.append(f"  Forecast: ${forecast_val:,.2f}")
            summary.append(f"  Range: ${lower_bound:,.2f} - ${upper_bound:,.2f}")
            total_forecast += forecast_val
        
        summary.append(f"\n=== Summary ===")
        summary.append(f"Total Forecast ({months_ahead} months): ${total_forecast:,.2f}")
        summary.append(f"Average Forecast per Month: ${total_forecast/months_ahead:,.2f}")
        
        # Budget recommendation
        recommended_budget = total_forecast * 1.1  # Add 10% buffer
        summary.append(f"\n💡 Recommended Budget (with 10% buffer): ${recommended_budget:,.2f}")
        
        # Seasonality note
        if len(monthly_spend) >= 12:
            summary.append(f"\n📊 Note: Consider seasonal patterns in your planning")
        
        return "\n".join(summary)
        
    except Exception as e:
        return f"❌ Error forecasting spend: {str(e)}"


# Create FunctionTool wrapper
ForecastSpendTool = FunctionTool(func=forecast_spend)


