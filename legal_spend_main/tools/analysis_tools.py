"""
Analysis Tools for Legal Spend Data
Performs calculations, aggregations, and trend analysis
Using FunctionTool pattern (official ADK approach)
"""
import pandas as pd
from google.adk.tools import FunctionTool
from typing import Dict, Any
import sys
import os


def calculate_firm_totals(file_path: str) -> str:
    """
    Calculates total spend per law firm from the dataset.
    
    Args:
        file_path: Path to the data file (CSV or Parquet)
        
    Returns:
        String summary of firm totals ranked by spend
    """
    try:
        # Load data
        if file_path.endswith('.csv'):
            df = pd.read_csv(file_path)
        elif file_path.endswith('.parquet'):
            df = pd.read_parquet(file_path)
        else:
            return "❌ Error: Unsupported file type. Use CSV or Parquet."
        
        # Normalize column names
        df.columns = df.columns.str.lower().str.strip().str.replace(' ', '_')
        
        # Find firm and amount columns
        firm_col = next((col for col in df.columns if 'firm' in col.lower()), None)
        amount_col = next((col for col in df.columns if 'amount' in col.lower() or 'total' in col.lower()), None)
        
        if not firm_col or not amount_col:
            return f"❌ Error: Could not find required columns. Available: {', '.join(df.columns)}"
        
        # Calculate totals
        firm_totals = df.groupby(firm_col)[amount_col].agg(['sum', 'count', 'mean']).sort_values('sum', ascending=False)
        
        summary = []
        summary.append("=== Law Firm Spend Analysis ===\n")
        summary.append(f"Total Firms: {len(firm_totals)}")
        summary.append(f"Total Spend: ${firm_totals['sum'].sum():,.2f}\n")
        summary.append("Top 10 Law Firms by Spend:")
        
        for i, (firm, row) in enumerate(firm_totals.head(10).iterrows(), 1):
            pct = (row['sum'] / firm_totals['sum'].sum() * 100)
            summary.append(f"{i}. {firm}")
            summary.append(f"   Total: ${row['sum']:,.2f} ({pct:.1f}%)")
            summary.append(f"   Invoices: {int(row['count'])}")
            summary.append(f"   Avg: ${row['mean']:,.2f}\n")
        
        return "\n".join(summary)
        
    except Exception as e:
        return f"❌ Error calculating firm totals: {str(e)}"


def identify_cost_savings(file_path: str) -> str:
    """
    Identifies potential cost-saving opportunities in legal spend.
    
    Args:
        file_path: Path to the data file
        
    Returns:
        String summary of cost-saving recommendations
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
        
        recommendations = []
        recommendations.append("=== Cost Savings Opportunities ===\n")
        
        # 1. High-cost timekeepers on low-value tasks
        if 'rate' in df.columns and 'description' in df.columns:
            high_rate_threshold = df['rate'].quantile(0.75) if 'rate' in df.columns else 500
            doc_review_keywords = ['document review', 'doc review', 'review documents']
            
            high_cost_review = df[
                (df['rate'] > high_rate_threshold) & 
                (df['description'].str.lower().str.contains('|'.join(doc_review_keywords), na=False))
            ]
            
            if len(high_cost_review) > 0:
                potential_savings = high_cost_review['amount'].sum() * 0.4  # Assume 40% savings
                recommendations.append(f"1. High-Cost Document Review")
                recommendations.append(f"   Found {len(high_cost_review)} line items with partners/senior associates on document review")
                recommendations.append(f"   Potential Savings: ${potential_savings:,.2f}")
                recommendations.append(f"   Recommendation: Use junior associates or contract attorneys\n")
        
        # 2. Firm concentration risk
        if 'law_firm' in df.columns and 'amount' in df.columns:
            firm_totals = df.groupby('law_firm')['amount'].sum().sort_values(ascending=False)
            top_firm_pct = (firm_totals.iloc[0] / firm_totals.sum() * 100)
            
            if top_firm_pct > 50:
                recommendations.append(f"2. Firm Concentration Risk")
                recommendations.append(f"   Top firm represents {top_firm_pct:.1f}% of total spend")
                recommendations.append(f"   Recommendation: Diversify legal panel for better rates\n")
        
        # 3. Rate variance analysis
        if 'rate' in df.columns and 'timekeeper' in df.columns:
            rate_variance = df.groupby('timekeeper')['rate'].std()
            high_variance = rate_variance[rate_variance > 50].sort_values(ascending=False)
            
            if len(high_variance) > 0:
                recommendations.append(f"3. Rate Inconsistencies")
                recommendations.append(f"   Found {len(high_variance)} timekeepers with varying rates")
                recommendations.append(f"   Recommendation: Negotiate fixed rates with firms\n")
        
        # 4. Matter efficiency
        if 'matter' in df.columns and 'amount' in df.columns:
            matter_totals = df.groupby('matter')['amount'].sum().sort_values(ascending=False)
            high_cost_matters = matter_totals[matter_totals > matter_totals.quantile(0.9)]
            
            if len(high_cost_matters) > 0:
                recommendations.append(f"4. High-Cost Matters")
                recommendations.append(f"   {len(high_cost_matters)} matters in top 10% of spend")
                recommendations.append(f"   Total: ${high_cost_matters.sum():,.2f}")
                recommendations.append(f"   Recommendation: Review for scope creep or inefficiencies\n")
        
        if len(recommendations) == 1:
            recommendations.append("No specific cost-saving opportunities identified.")
            recommendations.append("Consider: rate negotiations, alternative fee arrangements, legal tech adoption")
        
        return "\n".join(recommendations)
        
    except Exception as e:
        return f"❌ Error identifying cost savings: {str(e)}"


def analyze_trends(file_path: str) -> str:
    """
    Analyzes spending trends over time.
    
    Args:
        file_path: Path to the data file
        
    Returns:
        String summary of spending trends
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
        
        if df.empty:
            return "❌ Error: No valid dates found"
        
        # Extract month/year
        df['month'] = df[date_col].dt.to_period('M')
        
        # Monthly trends
        monthly_spend = df.groupby('month')[amount_col].agg(['sum', 'count', 'mean'])
        
        summary = []
        summary.append("=== Spending Trends Analysis ===\n")
        summary.append(f"Date Range: {df[date_col].min().strftime('%Y-%m-%d')} to {df[date_col].max().strftime('%Y-%m-%d')}")
        summary.append(f"Total Months: {len(monthly_spend)}\n")
        
        summary.append("Monthly Spend Summary:")
        for month, row in monthly_spend.tail(6).iterrows():
            summary.append(f"{month}: ${row['sum']:,.2f} ({int(row['count'])} invoices, avg ${row['mean']:,.2f})")
        
        # Calculate trend
        if len(monthly_spend) >= 3:
            recent_avg = monthly_spend['sum'].tail(3).mean()
            previous_avg = monthly_spend['sum'].head(len(monthly_spend) - 3).mean()
            
            if recent_avg > previous_avg * 1.1:
                trend = "INCREASING"
                change = ((recent_avg - previous_avg) / previous_avg * 100)
                summary.append(f"\n📈 Trend: {trend} (+{change:.1f}%)")
            elif recent_avg < previous_avg * 0.9:
                trend = "DECREASING"
                change = ((previous_avg - recent_avg) / previous_avg * 100)
                summary.append(f"\n📉 Trend: {trend} (-{change:.1f}%)")
            else:
                summary.append(f"\n➡️ Trend: STABLE")
        
        return "\n".join(summary)
        
    except Exception as e:
        return f"❌ Error analyzing trends: {str(e)}"


# Create FunctionTool wrappers
CalculateFirmTotalsTool = FunctionTool(func=calculate_firm_totals)
IdentifyCostSavingsTool = FunctionTool(func=identify_cost_savings)
AnalyzeTrendsTool = FunctionTool(func=analyze_trends)


