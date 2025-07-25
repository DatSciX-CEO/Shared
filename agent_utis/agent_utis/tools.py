"""
Tools for Agent Utis - eDiscovery Utilization Analysis
Following Google ADK patterns for tool definition and integration
"""

import pandas as pd
import numpy as np
import logging
from typing import Dict, Any, Optional
import json

from google.adk.tools import AgentTool, ToolContext

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def analyze_csv_data(question: str, tool_context: ToolContext) -> str:
    """
    Analyze CSV data and provide comprehensive insights
    
    Args:
        question: The analysis question or request
        tool_context: Context containing the dataframe and state
    
    Returns:
        JSON string with analysis results
    """
    try:
        # Get dataframe from context
        df = tool_context.state.get('dataframe')
        if df is None:
            return json.dumps({"error": "No data available for analysis"})
        
        analysis = {
            "total_records": len(df),
            "columns": list(df.columns),
            "missing_data": df.isnull().sum().to_dict(),
            "data_types": {col: str(dtype) for col, dtype in df.dtypes.items()},
            "numeric_summary": {}
        }
        
        # Get date range if date columns exist
        date_cols = [col for col in df.columns if 'date' in col.lower()]
        if date_cols:
            date_col = date_cols[0]
            df[date_col] = pd.to_datetime(df[date_col], errors='coerce')
            analysis["date_range"] = {
                "start": str(df[date_col].min()),
                "end": str(df[date_col].max())
            }
        
        # Basic statistics for numeric columns
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        if len(numeric_cols) > 0:
            analysis["numeric_summary"] = df[numeric_cols].describe().to_dict()
        
        # Store results in context for other tools
        tool_context.state['data_analysis'] = analysis
        
        logger.info(f"CSV analysis completed for {len(df)} records")
        return json.dumps(analysis, default=str)
        
    except Exception as e:
        logger.error(f"Error in CSV analysis: {e}")
        return json.dumps({"error": str(e)})

async def calculate_utilization_metrics(question: str, tool_context: ToolContext) -> str:
    """
    Calculate comprehensive utilization metrics for eDiscovery experts
    
    Args:
        question: The utilization analysis question
        tool_context: Context containing the dataframe and state
    
    Returns:
        JSON string with utilization metrics
    """
    try:
        df = tool_context.state.get('dataframe')
        if df is None:
            return json.dumps({"error": "No data available for utilization analysis"})
        
        df = df.copy()
        metrics = {}
        
        # Calculate utilization rate if columns exist
        if 'billable_hours' in df.columns and 'total_hours' in df.columns:
            df['utilization_rate'] = (df['billable_hours'] / df['total_hours']) * 100
            
            metrics.update({
                "avg_utilization": float(df['utilization_rate'].mean()),
                "median_utilization": float(df['utilization_rate'].median()),
                "utilization_std": float(df['utilization_rate'].std()),
                "over_utilized": int(len(df[df['utilization_rate'] > 80])),
                "under_utilized": int(len(df[df['utilization_rate'] < 70])),
                "optimal_range": int(len(df[(df['utilization_rate'] >= 70) & (df['utilization_rate'] <= 80)])),
                "utilization_distribution": df['utilization_rate'].describe().to_dict()
            })
        
        # Calculate cost metrics if available
        if 'total_cost' in df.columns and 'billable_hours' in df.columns:
            df['cost_per_billable_hour'] = df['total_cost'] / df['billable_hours']
            metrics['avg_cost_per_hour'] = float(df['cost_per_billable_hour'].mean())
            metrics['cost_efficiency'] = df['cost_per_billable_hour'].describe().to_dict()
        
        # Role-based analysis if available
        if 'role' in df.columns and 'utilization_rate' in df.columns:
            role_metrics = df.groupby('role')['utilization_rate'].agg(['mean', 'count', 'std']).round(2)
            metrics['role_analysis'] = role_metrics.to_dict()
        
        # Store results in context
        tool_context.state['utilization_metrics'] = metrics
        
        logger.info("Utilization metrics calculated successfully")
        return json.dumps(metrics, default=str)
        
    except Exception as e:
        logger.error(f"Error calculating utilization metrics: {e}")
        return json.dumps({"error": str(e)})

async def predict_future_spend(question: str, tool_context: ToolContext) -> str:
    """
    Predict future spending using historical data and regression analysis
    
    Args:
        question: The spend prediction question
        tool_context: Context containing the dataframe and state
    
    Returns:
        JSON string with spend predictions
    """
    try:
        df = tool_context.state.get('dataframe')
        if df is None:
            return json.dumps({"error": "No data available for spend prediction"})
        
        periods = 4  # Default prediction periods
        prediction = {}
        
        if 'total_cost' in df.columns and 'date' in df.columns:
            # Prepare time series data
            df_copy = df.copy()
            df_copy['date'] = pd.to_datetime(df_copy['date'])
            monthly_spend = df_copy.groupby(df_copy['date'].dt.to_period('M'))['total_cost'].sum()
            
            if len(monthly_spend) >= 3:  # Need at least 3 data points
                # Simple linear regression using numpy
                x = np.arange(len(monthly_spend))
                y = monthly_spend.values
                
                # Fit polynomial (linear trend)
                coeffs = np.polyfit(x, y, 1)
                
                # Predict future periods
                future_x = np.arange(len(monthly_spend), len(monthly_spend) + periods)
                future_spend = np.polyval(coeffs, future_x)
                
                prediction.update({
                    "historical_trend": float(coeffs[0]),  # slope
                    "current_baseline": float(coeffs[1]),  # intercept
                    "predicted_monthly_spend": [float(x) for x in future_spend],
                    "total_predicted": float(sum(future_spend)),
                    "confidence_level": "Medium" if len(monthly_spend) >= 6 else "Low",
                    "data_points_used": len(monthly_spend),
                    "historical_monthly_avg": float(monthly_spend.mean())
                })
            else:
                prediction["error"] = "Insufficient data for prediction (need at least 3 months)"
        else:
            prediction["error"] = "Missing required columns for spend prediction"
        
        # Store results in context
        tool_context.state['spend_prediction'] = prediction
        
        logger.info("Spend prediction completed")
        return json.dumps(prediction, default=str)
        
    except Exception as e:
        logger.error(f"Error in spend prediction: {e}")
        return json.dumps({"error": str(e)})

async def check_compliance_metrics(question: str, tool_context: ToolContext) -> str:
    """
    Check operational metrics against industry compliance benchmarks
    
    Args:
        question: The compliance check question
        tool_context: Context containing analysis results
    
    Returns:
        JSON string with compliance report
    """
    try:
        # Get previous analysis results from context
        data_analysis = tool_context.state.get('data_analysis', {})
        utilization_metrics = tool_context.state.get('utilization_metrics', {})
        
        # Combine metrics for compliance analysis
        combined_metrics = {**data_analysis, **utilization_metrics}
        
        compliance_report = {
            "compliance_score": 0,
            "max_score": 100,
            "issues": [],
            "recommendations": [],
            "benchmarks_met": []
        }
        
        # Check utilization compliance (25 points)
        if "avg_utilization" in combined_metrics:
            avg_util = combined_metrics["avg_utilization"]
            if 70 <= avg_util <= 80:
                compliance_report["compliance_score"] += 25
                compliance_report["benchmarks_met"].append("Optimal utilization range achieved")
            elif avg_util < 70:
                compliance_report["issues"].append(f"Average utilization ({avg_util:.1f}%) below optimal range (70-80%)")
                compliance_report["recommendations"].append("Consider workload redistribution or capacity reduction")
            else:
                compliance_report["issues"].append(f"Average utilization ({avg_util:.1f}%) above optimal range (70-80%)")
                compliance_report["recommendations"].append("Risk of burnout - consider additional resources")
        
        # Check for over-utilization risks (25 points)
        if "over_utilized" in combined_metrics:
            over_util_count = combined_metrics["over_utilized"]
            if over_util_count == 0:
                compliance_report["compliance_score"] += 25
                compliance_report["benchmarks_met"].append("No over-utilization detected")
            else:
                compliance_report["issues"].append(f"{over_util_count} experts are over-utilized (>80%)")
                compliance_report["recommendations"].append("Redistribute workload to prevent expert burnout")
        
        # Check cost efficiency (25 points)
        if "avg_cost_per_hour" in combined_metrics:
            cost_per_hour = combined_metrics["avg_cost_per_hour"]
            # Industry benchmark: reasonable cost per hour
            if cost_per_hour < 200:  # Reasonable threshold
                compliance_report["compliance_score"] += 25
                compliance_report["benchmarks_met"].append("Cost efficiency within acceptable range")
            else:
                compliance_report["issues"].append(f"High average cost per hour (${cost_per_hour:.2f})")
                compliance_report["recommendations"].append("Review pricing strategy and operational efficiency")
        
        # Check data quality (25 points)
        total_records = combined_metrics.get("total_records", 0)
        if total_records > 10:
            compliance_report["compliance_score"] += 25
            compliance_report["benchmarks_met"].append("Sufficient data volume for analysis")
        else:
            compliance_report["issues"].append("Limited data volume may affect analysis reliability")
            compliance_report["recommendations"].append("Increase data collection frequency for better insights")
        
        # Calculate final percentage
        compliance_report["compliance_percentage"] = (compliance_report["compliance_score"] / compliance_report["max_score"]) * 100
        
        # Store results in context
        tool_context.state['compliance_report'] = compliance_report
        
        logger.info("Compliance check completed")
        return json.dumps(compliance_report, default=str)
        
    except Exception as e:
        logger.error(f"Error in compliance check: {e}")
        return json.dumps({"error": str(e)})

# Tool definitions for agent registration
TOOLS = [
    {
        "name": "analyze_csv_data",
        "description": "Analyze CSV data and provide comprehensive data insights for eDiscovery utilization",
        "function": analyze_csv_data
    },
    {
        "name": "calculate_utilization_metrics", 
        "description": "Calculate utilization rates, efficiency metrics, and cost analysis for legal experts",
        "function": calculate_utilization_metrics
    },
    {
        "name": "predict_future_spend",
        "description": "Forecast future spending using historical data and regression analysis",
        "function": predict_future_spend
    },
    {
        "name": "check_compliance_metrics",
        "description": "Check operational metrics against legal industry compliance benchmarks",
        "function": check_compliance_metrics
    }
]