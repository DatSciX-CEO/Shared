"""
Utility functions for Agent Utis MVP
Helper functions for data processing, validation, and analysis
"""

import pandas as pd
import numpy as np
import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import seaborn as sns

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def validate_data_types(df: pd.DataFrame) -> pd.DataFrame:
    """Validate and convert data types for analysis"""
    try:
        # Convert date columns
        date_columns = [col for col in df.columns if 'date' in col.lower()]
        for col in date_columns:
            df[col] = pd.to_datetime(df[col], errors='coerce')
        
        # Convert numeric columns
        numeric_columns = ['billable_hours', 'total_hours', 'hourly_rate', 'total_cost', 'utilization_rate']
        for col in numeric_columns:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        return df
    except Exception as e:
        logger.error(f"Error validating data types: {e}")
        return df

def calculate_derived_metrics(df: pd.DataFrame) -> pd.DataFrame:
    """Calculate additional metrics from base data"""
    try:
        df = df.copy()
        
        # Calculate utilization rate if not present
        if 'utilization_rate' not in df.columns and 'billable_hours' in df.columns and 'total_hours' in df.columns:
            df['utilization_rate'] = (df['billable_hours'] / df['total_hours']) * 100
        
        # Calculate cost per billable hour
        if 'total_cost' in df.columns and 'billable_hours' in df.columns:
            df['cost_per_billable_hour'] = df['total_cost'] / df['billable_hours']
        
        # Calculate efficiency ratio (billable hours / total hours)
        if 'billable_hours' in df.columns and 'total_hours' in df.columns:
            df['efficiency_ratio'] = df['billable_hours'] / df['total_hours']
        
        # Calculate revenue if hourly rate is available
        if 'billable_hours' in df.columns and 'hourly_rate' in df.columns:
            df['revenue'] = df['billable_hours'] * df['hourly_rate']
        
        return df
    except Exception as e:
        logger.error(f"Error calculating derived metrics: {e}")
        return df

def identify_outliers(df: pd.DataFrame, column: str, method: str = 'iqr') -> pd.Series:
    """Identify outliers in a numeric column"""
    try:
        if column not in df.columns or not pd.api.types.is_numeric_dtype(df[column]):
            return pd.Series([False] * len(df))
        
        if method == 'iqr':
            Q1 = df[column].quantile(0.25)
            Q3 = df[column].quantile(0.75)
            IQR = Q3 - Q1
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR
            return (df[column] < lower_bound) | (df[column] > upper_bound)
        
        elif method == 'zscore':
            z_scores = np.abs((df[column] - df[column].mean()) / df[column].std())
            return z_scores > 3
        
        return pd.Series([False] * len(df))
    except Exception as e:
        logger.error(f"Error identifying outliers: {e}")
        return pd.Series([False] * len(df))

def generate_utilization_insights(df: pd.DataFrame) -> Dict[str, Any]:
    """Generate detailed utilization insights"""
    try:
        insights = {}
        
        if 'utilization_rate' in df.columns:
            util_rates = df['utilization_rate'].dropna()
            
            insights.update({
                'mean_utilization': util_rates.mean(),
                'median_utilization': util_rates.median(),
                'std_utilization': util_rates.std(),
                'min_utilization': util_rates.min(),
                'max_utilization': util_rates.max(),
                'low_performers': len(util_rates[util_rates < 70]),
                'high_performers': len(util_rates[util_rates > 80]),
                'optimal_performers': len(util_rates[(util_rates >= 70) & (util_rates <= 80)])
            })
        
        # Role-based analysis
        if 'role' in df.columns and 'utilization_rate' in df.columns:
            role_analysis = df.groupby('role')['utilization_rate'].agg(['mean', 'count', 'std']).round(2)
            insights['role_analysis'] = role_analysis.to_dict()
        
        # Project-based analysis
        if 'project_name' in df.columns and 'utilization_rate' in df.columns:
            project_analysis = df.groupby('project_name')['utilization_rate'].agg(['mean', 'count']).round(2)
            insights['project_analysis'] = project_analysis.to_dict()
        
        return insights
    except Exception as e:
        logger.error(f"Error generating utilization insights: {e}")
        return {}

def calculate_cost_efficiency(df: pd.DataFrame) -> Dict[str, Any]:
    """Calculate cost efficiency metrics"""
    try:
        efficiency = {}
        
        if 'total_cost' in df.columns and 'billable_hours' in df.columns:
            cost_per_hour = df['total_cost'] / df['billable_hours']
            efficiency.update({
                'avg_cost_per_billable_hour': cost_per_hour.mean(),
                'median_cost_per_billable_hour': cost_per_hour.median(),
                'cost_range': {
                    'min': cost_per_hour.min(),
                    'max': cost_per_hour.max()
                }
            })
        
        if 'revenue' in df.columns and 'total_cost' in df.columns:
            profit = df['revenue'] - df['total_cost']
            profit_margin = (profit / df['revenue']) * 100
            efficiency.update({
                'total_profit': profit.sum(),
                'avg_profit_margin': profit_margin.mean(),
                'profitable_experts': len(profit[profit > 0])
            })
        
        return efficiency
    except Exception as e:
        logger.error(f"Error calculating cost efficiency: {e}")
        return {}

def prepare_time_series_data(df: pd.DataFrame, date_col: str = 'date', value_col: str = 'total_cost') -> pd.DataFrame:
    """Prepare data for time series analysis"""
    try:
        if date_col not in df.columns or value_col not in df.columns:
            return pd.DataFrame()
        
        # Convert to datetime if not already
        df[date_col] = pd.to_datetime(df[date_col])
        
        # Group by month and sum values
        monthly_data = df.groupby(df[date_col].dt.to_period('M'))[value_col].sum().reset_index()
        monthly_data[date_col] = monthly_data[date_col].dt.to_timestamp()
        
        return monthly_data
    except Exception as e:
        logger.error(f"Error preparing time series data: {e}")
        return pd.DataFrame()

def generate_recommendations(analysis_results: Dict[str, Any]) -> List[str]:
    """Generate actionable recommendations based on analysis"""
    try:
        recommendations = []
        
        # Utilization recommendations
        if 'utilization_analysis' in analysis_results:
            util_data = analysis_results['utilization_analysis']
            
            avg_util = util_data.get('avg_utilization', 0)
            if avg_util < 70:
                recommendations.append("Overall utilization is below optimal range. Consider redistributing work or reducing capacity.")
            elif avg_util > 85:
                recommendations.append("High utilization rates may lead to burnout. Consider hiring additional resources.")
            
            over_utilized = util_data.get('over_utilized', 0)
            if over_utilized > 0:
                recommendations.append(f"{over_utilized} experts are over-utilized. Monitor workload and consider rebalancing.")
        
        # Cost recommendations
        if 'spend_forecast' in analysis_results:
            spend_data = analysis_results['spend_forecast']
            trend = spend_data.get('historical_trend', 0)
            
            if trend > 0:
                recommendations.append("Spending is trending upward. Review cost management strategies.")
            elif trend < -1000:
                recommendations.append("Spending is decreasing significantly. Ensure adequate resource allocation.")
        
        # Compliance recommendations
        if 'compliance_status' in analysis_results:
            compliance_data = analysis_results['compliance_status']
            score = compliance_data.get('compliance_score', 0)
            
            if score < 75:
                recommendations.append("Compliance score is below target. Review operational procedures.")
        
        return recommendations
    except Exception as e:
        logger.error(f"Error generating recommendations: {e}")
        return ["Unable to generate recommendations due to analysis error."]

def export_results(results: Dict[str, Any], filename: str = None) -> str:
    """Export analysis results to file"""
    try:
        if filename is None:
            filename = f"agent_utis_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        import json
        
        # Convert any non-serializable objects
        serializable_results = {}
        for key, value in results.items():
            if isinstance(value, (dict, list, str, int, float, bool)) or value is None:
                serializable_results[key] = value
            else:
                serializable_results[key] = str(value)
        
        with open(filename, 'w') as f:
            json.dump(serializable_results, f, indent=2, default=str)
        
        return filename
    except Exception as e:
        logger.error(f"Error exporting results: {e}")
        return ""

def create_visualization(df: pd.DataFrame, chart_type: str = 'utilization') -> plt.Figure:
    """Create visualizations for the data"""
    try:
        fig, ax = plt.subplots(figsize=(10, 6))
        
        if chart_type == 'utilization' and 'utilization_rate' in df.columns:
            df['utilization_rate'].hist(bins=20, ax=ax, alpha=0.7)
            ax.set_xlabel('Utilization Rate (%)')
            ax.set_ylabel('Frequency')
            ax.set_title('Distribution of Utilization Rates')
            ax.axvline(70, color='r', linestyle='--', label='Min Target (70%)')
            ax.axvline(80, color='r', linestyle='--', label='Max Target (80%)')
            ax.legend()
        
        elif chart_type == 'cost_trend' and 'date' in df.columns and 'total_cost' in df.columns:
            monthly_data = prepare_time_series_data(df)
            if not monthly_data.empty:
                ax.plot(monthly_data['date'], monthly_data['total_cost'], marker='o')
                ax.set_xlabel('Date')
                ax.set_ylabel('Total Cost ($)')
                ax.set_title('Monthly Cost Trend')
                plt.xticks(rotation=45)
        
        elif chart_type == 'role_comparison' and 'role' in df.columns and 'utilization_rate' in df.columns:
            role_avg = df.groupby('role')['utilization_rate'].mean().sort_values(ascending=False)
            role_avg.plot(kind='bar', ax=ax)
            ax.set_xlabel('Role')
            ax.set_ylabel('Average Utilization Rate (%)')
            ax.set_title('Utilization by Role')
            plt.xticks(rotation=45)
        
        plt.tight_layout()
        return fig
    except Exception as e:
        logger.error(f"Error creating visualization: {e}")
        return plt.figure()

# Test queries and expected outputs for validation
TEST_QUERIES = [
    {
        "query": "What is the average utilization rate?",
        "expected_type": "numeric_summary"
    },
    {
        "query": "Which experts are over-utilized?",
        "expected_type": "expert_list"
    },
    {
        "query": "Predict next quarter spending",
        "expected_type": "forecast"
    },
    {
        "query": "What are the main compliance issues?",
        "expected_type": "compliance_report"
    },
    {
        "query": "Show me cost efficiency by role",
        "expected_type": "role_analysis"
    }
]