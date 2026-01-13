"""
Data Analysis Tool for ADK - Performs various analysis operations on legal spend data
Using FunctionTool pattern (official ADK approach)
"""
import pandas as pd
from typing import Dict, Any
from google.adk.tools import FunctionTool


def analyze_data(file_path: str, analysis_type: str = "summary") -> str:
    """
    Performs analysis on legal spend data.

    Args:
        file_path: Path to CSV or Excel file with legal spend data
        analysis_type: Type of analysis to perform. Options:
            - "summary": Basic summary statistics
            - "top_firms": Top law firms by spend
            - "total_spend": Total spend calculation
            - "cost_savings": Identify cost savings opportunities
            - "trends": Analyze spending trends over time

    Returns:
        Analysis results as a string
    """
    try:
        # Load data
        if file_path.endswith('.csv'):
            df = pd.read_csv(file_path)
        elif file_path.endswith(('.xls', '.xlsx')):
            df = pd.read_excel(file_path)
        else:
            return f"Error: Unsupported file type. Expected CSV or Excel file."
        
        if analysis_type == "summary":
            return f"Data summary: {len(df)} rows, {len(df.columns)} columns. Columns: {', '.join(df.columns.tolist())}"
        elif analysis_type == "top_firms":
            # Try to find law firm column
            firm_col = None
            for col in df.columns:
                if 'firm' in col.lower() or 'law' in col.lower():
                    firm_col = col
                    break
            if firm_col and "Cost" in df.columns:
                result_df = analyze_top_firms(df, firm_col, top_n=5)
                return result_df.to_string()
            else:
                return "Could not find law firm column in data."
        elif analysis_type == "total_spend":
            if "Cost" in df.columns:
                result = calculate_total_spend(df)
                return f"Total Spend: ${result['total_spend']:,.2f}\nAverage per item: ${result['average_cost_per_item']:,.2f}\nTotal items: {result['total_line_items']}"
            else:
                return "Could not find Cost column in data."
        elif analysis_type == "cost_savings":
            return identify_cost_savings(df)
        elif analysis_type == "trends":
            return "Trend analysis: Use the data to identify spending patterns over time if date columns are available."
        else:
            return f"Unknown analysis type: {analysis_type}. Available types: summary, top_firms, total_spend, cost_savings, trends"
    except Exception as e:
        return f"Error performing analysis: {type(e).__name__}: {str(e)}"


def analyze_top_firms(df: pd.DataFrame, firm_column: str = "Law Firm", top_n: int = 5) -> pd.DataFrame:
    """
    Analyze top law firms by spend.
    
    Args:
        df: DataFrame with legal spend data
        firm_column: Name of column containing law firm names
        top_n: Number of top firms to return
        
    Returns:
        DataFrame with top firms and their total spend
    """
    if firm_column not in df.columns:
        # Try to find a similar column
        possible_columns = [col for col in df.columns if 'firm' in col.lower() or 'law' in col.lower()]
        if possible_columns:
            firm_column = possible_columns[0]
        else:
            return pd.DataFrame({"Error": ["No law firm column found"]})
    
    if "Cost" not in df.columns:
        return pd.DataFrame({"Error": ["No Cost column found"]})
    
    firm_totals = df.groupby(firm_column)["Cost"].sum().sort_values(ascending=False).head(top_n)
    result = pd.DataFrame({
        "Law Firm": firm_totals.index,
        "Total Spend": firm_totals.values
    })
    return result


def calculate_total_spend(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Calculate total spend and related metrics.
    
    Args:
        df: DataFrame with legal spend data
        
    Returns:
        Dictionary with total spend and metrics
    """
    if "Cost" not in df.columns:
        return {"error": "No Cost column found"}
    
    total_spend = df["Cost"].sum()
    avg_cost = df["Cost"].mean()
    median_cost = df["Cost"].median()
    total_items = len(df)
    
    # Calculate total hours if available
    total_hours = None
    if "Units" in df.columns or "Hours" in df.columns:
        hours_col = "Units" if "Units" in df.columns else "Hours"
        total_hours = df[hours_col].sum()
    
    return {
        "total_spend": float(total_spend),
        "average_cost_per_item": float(avg_cost),
        "median_cost_per_item": float(median_cost),
        "total_line_items": int(total_items),
        "total_hours": float(total_hours) if total_hours is not None else None,
    }


def identify_cost_savings(df: pd.DataFrame) -> str:
    """
    Identify potential cost savings opportunities.
    
    Args:
        df: DataFrame with legal spend data
        
    Returns:
        String with cost savings recommendations
    """
    recommendations = []
    
    # Check for high-cost document review by partners
    if "Position Title" in df.columns and "Line Item Description" in df.columns:
        partner_review = df[
            (df["Position Title"].str.contains("Partner", case=False, na=False)) &
            (df["Line Item Description"].str.contains("review|document", case=False, na=False))
        ]
        if len(partner_review) > 0:
            partner_cost = partner_review["Cost"].sum()
            recommendations.append(
                f"Found {len(partner_review)} line items where Partners are billing for document review. "
                f"Total cost: ${partner_cost:,.2f}. Consider using lower-cost timekeepers for review work."
            )
    
    # Check for unusually high rates
    if "Bill Rate" in df.columns:
        avg_rate = df["Bill Rate"].mean()
        high_rate_items = df[df["Bill Rate"] > avg_rate * 2]
        if len(high_rate_items) > 0:
            recommendations.append(
                f"Found {len(high_rate_items)} line items with rates more than 2x the average. "
                f"Review these for rate negotiation opportunities."
            )
    
    # Check for duplicate or similar line items
    if "Line Item Description" in df.columns:
        duplicate_descriptions = df["Line Item Description"].value_counts()
        duplicates = duplicate_descriptions[duplicate_descriptions > 10]
        if len(duplicates) > 0:
            recommendations.append(
                f"Found {len(duplicates)} frequently repeated line item descriptions. "
                f"Consider consolidating or standardizing these activities."
            )
    
    if not recommendations:
        return "No obvious cost savings opportunities identified. Data appears to be within normal ranges."
    
    return "\n\n".join(recommendations)


# Create FunctionTool wrapper
# FunctionTool uses the function name and docstring automatically for description
DataAnalysisTool = FunctionTool(func=analyze_data)
