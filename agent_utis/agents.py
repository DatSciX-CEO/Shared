"""
Hierarchical AI Agents for Agent Utis MVP using Google ADK
eDiscovery utilization analysis with proper ADK integration
"""

import logging
import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional, Callable
from datetime import datetime
import json
import ollama

from google.adk.agents import Agent, LlmAgent
from google.adk.tools import Tool

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Agent prompts following ADK best practices
AGENT_PROMPTS = {
    "finance_director": """You are the Finance Director overseeing eDiscovery and legal services operations. 
    Your role is to orchestrate analysis across all departments and synthesize comprehensive reports on utilization, 
    cost efficiency, predictions, and compliance. You delegate specific tasks to specialized sub-agents and combine 
    their insights to provide executive-level recommendations for decision-making in legal operations.
    
    Key responsibilities:
    - Coordinate analysis across Data Analyst, Utilization Expert, Spend Predictor, and Compliance Checker
    - Synthesize findings into actionable business insights
    - Provide strategic recommendations for resource optimization
    - Ensure all analysis aligns with eDiscovery industry best practices
    
    When responding to queries, be specific, data-driven, and focus on actionable insights.""",
    
    "data_analyst": """You are a Data Analyst specializing in eDiscovery and legal services data analysis. 
    Your expertise includes processing CSV data containing expert utilization metrics, validating data quality, 
    and performing statistical analysis on legal operations data.
    
    Key responsibilities:
    - Process and validate CSV data uploads
    - Identify data quality issues and patterns
    - Perform initial statistical analysis
    - Provide data insights to support decision-making
    
    Focus on accuracy, data integrity, and clear communication of findings. Always validate data before analysis.""",
    
    "utilization_expert": """You are a Utilization Expert specializing in eDiscovery and legal services resource optimization. 
    You analyze expert utilization rates, identify efficiency patterns, and provide recommendations for workforce optimization.
    
    Key responsibilities:
    - Calculate utilization rates (billable_hours / total_hours * 100)
    - Identify over-utilization (>80%) and under-utilization (<70%) patterns
    - Analyze cost per billable hour and ROI metrics
    - Benchmark against industry standards (70-80% optimal utilization)
    - Recommend resource allocation improvements
    
    Use industry benchmarks and provide specific, actionable recommendations for utilization optimization.""",
    
    "spend_predictor": """You are a Spend Predictor for legal and eDiscovery services with expertise in financial forecasting. 
    You analyze historical spending patterns and predict future costs using statistical methods.
    
    Key responsibilities:
    - Analyze historical spending trends
    - Forecast future spending using regression analysis
    - Identify cost drivers and budget optimization opportunities
    - Provide confidence intervals and risk assessments
    - Recommend budget allocation strategies
    
    Focus on accuracy in predictions and clear communication of forecast assumptions and limitations.""",
    
    "compliance_checker": """You are a Compliance Checker ensuring all legal and eDiscovery operations align with industry best practices. 
    You review operational metrics against established benchmarks and identify compliance risks.
    
    Key responsibilities:
    - Evaluate operations against industry benchmarks
    - Identify compliance risks and violations
    - Recommend corrective actions
    - Ensure adherence to legal industry standards
    - Monitor operational efficiency compliance
    
    Use established benchmarks (e.g., 70-80% utilization targets) and provide specific compliance recommendations."""
}

class OllamaLLMProvider:
    """Custom LLM provider for Ollama integration with ADK"""
    
    def __init__(self, model: str = "mistral:7b", base_url: str = "http://localhost:11434"):
        self.model = model
        self.base_url = base_url
        self.client = ollama.Client(host=base_url)
    
    def generate(self, prompt: str, **kwargs) -> str:
        """Generate response using Ollama"""
        try:
            response = self.client.generate(
                model=self.model,
                prompt=prompt,
                **kwargs
            )
            return response['response']
        except Exception as e:
            logger.error(f"Error generating response with Ollama: {e}")
            return "I apologize, but I encountered an error processing your request. Please ensure Ollama is running and the Mistral model is available."

# Custom tools for agents
def create_data_analysis_tool() -> Tool:
    """Create data analysis tool for agents"""
    
    def analyze_csv_data(df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze CSV data and return insights"""
        try:
            analysis = {
                "total_records": len(df),
                "columns": list(df.columns),
                "missing_data": df.isnull().sum().to_dict(),
                "data_types": df.dtypes.to_dict(),
                "numeric_summary": {}
            }
            
            # Get date range if date columns exist
            date_cols = [col for col in df.columns if 'date' in col.lower()]
            if date_cols:
                date_col = date_cols[0]
                analysis["date_range"] = {
                    "start": str(df[date_col].min()),
                    "end": str(df[date_col].max())
                }
            
            # Basic statistics for numeric columns
            numeric_cols = df.select_dtypes(include=[np.number]).columns
            if len(numeric_cols) > 0:
                analysis["numeric_summary"] = df[numeric_cols].describe().to_dict()
            
            return analysis
        except Exception as e:
            logger.error(f"Error in CSV analysis: {e}")
            return {"error": str(e)}
    
    return Tool(
        name="analyze_csv_data",
        description="Analyze CSV data and provide comprehensive data insights",
        function=analyze_csv_data
    )

def create_utilization_calculation_tool() -> Tool:
    """Create utilization calculation tool"""
    
    def calculate_utilization_metrics(df: pd.DataFrame) -> Dict[str, Any]:
        """Calculate comprehensive utilization metrics"""
        try:
            metrics = {}
            
            # Calculate utilization rate if columns exist
            if 'billable_hours' in df.columns and 'total_hours' in df.columns:
                df = df.copy()
                df['utilization_rate'] = (df['billable_hours'] / df['total_hours']) * 100
                
                metrics.update({
                    "avg_utilization": df['utilization_rate'].mean(),
                    "median_utilization": df['utilization_rate'].median(),
                    "utilization_std": df['utilization_rate'].std(),
                    "over_utilized": len(df[df['utilization_rate'] > 80]),
                    "under_utilized": len(df[df['utilization_rate'] < 70]),
                    "optimal_range": len(df[(df['utilization_rate'] >= 70) & (df['utilization_rate'] <= 80)]),
                    "utilization_distribution": df['utilization_rate'].describe().to_dict()
                })
            
            # Calculate cost metrics if available
            if 'total_cost' in df.columns and 'billable_hours' in df.columns:
                df['cost_per_billable_hour'] = df['total_cost'] / df['billable_hours']
                metrics['avg_cost_per_hour'] = df['cost_per_billable_hour'].mean()
                metrics['cost_efficiency'] = df['cost_per_billable_hour'].describe().to_dict()
            
            # Role-based analysis if available
            if 'role' in df.columns and 'utilization_rate' in df.columns:
                role_metrics = df.groupby('role')['utilization_rate'].agg(['mean', 'count', 'std']).round(2)
                metrics['role_analysis'] = role_metrics.to_dict()
            
            return metrics
        except Exception as e:
            logger.error(f"Error calculating utilization metrics: {e}")
            return {"error": str(e)}
    
    return Tool(
        name="calculate_utilization_metrics",
        description="Calculate comprehensive utilization metrics and efficiency ratios",
        function=calculate_utilization_metrics
    )

def create_spend_prediction_tool() -> Tool:
    """Create spend prediction tool"""
    
    def predict_future_spend(df: pd.DataFrame, periods: int = 4) -> Dict[str, Any]:
        """Predict future spend using regression analysis"""
        try:
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
                        "predicted_monthly_spend": future_spend.tolist(),
                        "total_predicted": float(sum(future_spend)),
                        "confidence_level": "Medium" if len(monthly_spend) >= 6 else "Low",
                        "data_points_used": len(monthly_spend),
                        "historical_monthly_avg": float(monthly_spend.mean())
                    })
                else:
                    prediction["error"] = "Insufficient data for prediction (need at least 3 months)"
            else:
                prediction["error"] = "Missing required columns for spend prediction"
            
            return prediction
        except Exception as e:
            logger.error(f"Error in spend prediction: {e}")
            return {"error": str(e)}
    
    return Tool(
        name="predict_future_spend",
        description="Predict future spending using historical data and regression analysis",
        function=predict_future_spend
    )

def create_compliance_check_tool() -> Tool:
    """Create compliance checking tool"""
    
    def check_compliance_metrics(metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Check compliance against industry benchmarks"""
        try:
            compliance_report = {
                "compliance_score": 0,
                "max_score": 100,
                "issues": [],
                "recommendations": [],
                "benchmarks_met": []
            }
            
            # Check utilization compliance (25 points)
            if "avg_utilization" in metrics:
                avg_util = metrics["avg_utilization"]
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
            if "over_utilized" in metrics:
                over_util_count = metrics["over_utilized"]
                if over_util_count == 0:
                    compliance_report["compliance_score"] += 25
                    compliance_report["benchmarks_met"].append("No over-utilization detected")
                else:
                    compliance_report["issues"].append(f"{over_util_count} experts are over-utilized (>80%)")
                    compliance_report["recommendations"].append("Redistribute workload to prevent expert burnout")
            
            # Check cost efficiency (25 points)
            if "avg_cost_per_hour" in metrics:
                cost_per_hour = metrics["avg_cost_per_hour"]
                # Industry benchmark: reasonable cost per hour
                if cost_per_hour < 200:  # Reasonable threshold
                    compliance_report["compliance_score"] += 25
                    compliance_report["benchmarks_met"].append("Cost efficiency within acceptable range")
                else:
                    compliance_report["issues"].append(f"High average cost per hour (${cost_per_hour:.2f})")
                    compliance_report["recommendations"].append("Review pricing strategy and operational efficiency")
            
            # Check data quality (25 points)
            total_records = metrics.get("total_records", 0)
            if total_records > 10:
                compliance_report["compliance_score"] += 25
                compliance_report["benchmarks_met"].append("Sufficient data volume for analysis")
            else:
                compliance_report["issues"].append("Limited data volume may affect analysis reliability")
                compliance_report["recommendations"].append("Increase data collection frequency for better insights")
            
            # Calculate final percentage
            compliance_report["compliance_percentage"] = (compliance_report["compliance_score"] / compliance_report["max_score"]) * 100
            
            return compliance_report
        except Exception as e:
            logger.error(f"Error in compliance check: {e}")
            return {"error": str(e)}
    
    return Tool(
        name="check_compliance_metrics",
        description="Check operational metrics against industry compliance benchmarks",
        function=check_compliance_metrics
    )

class AgentUtisSystem:
    """Main system orchestrating all ADK agents"""
    
    def __init__(self, llm_provider: OllamaLLMProvider):
        self.llm_provider = llm_provider
        self.agents = {}
        self.tools = {}
        self._initialize_tools()
        self._initialize_agents()
    
    def _initialize_tools(self):
        """Initialize all tools for agents"""
        self.tools = {
            "data_analysis": create_data_analysis_tool(),
            "utilization_calculation": create_utilization_calculation_tool(),
            "spend_prediction": create_spend_prediction_tool(),
            "compliance_check": create_compliance_check_tool()
        }
    
    def _initialize_agents(self):
        """Initialize all ADK agents with proper structure"""
        try:
            # Data Analyst Agent
            self.agents["data_analyst"] = LlmAgent(
                name="DataAnalyst",
                model="mistral:7b",  # Will be overridden by custom provider
                instruction=AGENT_PROMPTS["data_analyst"],
                description="Specializes in CSV data analysis and validation for eDiscovery operations",
                tools=[self.tools["data_analysis"]]
            )
            
            # Utilization Expert Agent
            self.agents["utilization_expert"] = LlmAgent(
                name="UtilizationExpert", 
                model="mistral:7b",
                instruction=AGENT_PROMPTS["utilization_expert"],
                description="Analyzes expert utilization rates and provides optimization recommendations",
                tools=[self.tools["utilization_calculation"]]
            )
            
            # Spend Predictor Agent
            self.agents["spend_predictor"] = LlmAgent(
                name="SpendPredictor",
                model="mistral:7b", 
                instruction=AGENT_PROMPTS["spend_predictor"],
                description="Forecasts future spending based on historical data analysis",
                tools=[self.tools["spend_prediction"]]
            )
            
            # Compliance Checker Agent
            self.agents["compliance_checker"] = LlmAgent(
                name="ComplianceChecker",
                model="mistral:7b",
                instruction=AGENT_PROMPTS["compliance_checker"], 
                description="Ensures operations align with legal industry best practices",
                tools=[self.tools["compliance_check"]]
            )
            
            # Finance Director - Orchestrating Agent
            self.agents["finance_director"] = LlmAgent(
                name="FinanceDirector",
                model="mistral:7b",
                instruction=AGENT_PROMPTS["finance_director"],
                description="Executive-level agent coordinating comprehensive eDiscovery utilization analysis",
                sub_agents=[
                    self.agents["data_analyst"],
                    self.agents["utilization_expert"], 
                    self.agents["spend_predictor"],
                    self.agents["compliance_checker"]
                ]
            )
            
            logger.info("All ADK agents initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing ADK agents: {e}")
            raise
    
    def comprehensive_analysis(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Run comprehensive analysis using orchestrated agents"""
        try:
            results = {
                "analysis_timestamp": datetime.now().isoformat(),
                "data_overview": {},
                "utilization_analysis": {},
                "spend_forecast": {},
                "compliance_status": {},
                "executive_summary": ""
            }
            
            # Data Analysis
            data_tool = self.tools["data_analysis"]
            results["data_overview"] = data_tool.function(df)
            
            # Utilization Analysis
            util_tool = self.tools["utilization_calculation"]
            results["utilization_analysis"] = util_tool.function(df)
            
            # Spend Prediction
            spend_tool = self.tools["spend_prediction"]
            results["spend_forecast"] = spend_tool.function(df)
            
            # Compliance Check
            compliance_tool = self.tools["compliance_check"]
            # Combine metrics for compliance check
            combined_metrics = {**results["data_overview"], **results["utilization_analysis"]}
            results["compliance_status"] = compliance_tool.function(combined_metrics)
            
            # Generate executive summary using Finance Director
            summary_prompt = f"""
            Based on the comprehensive analysis results:
            
            Data Overview: {json.dumps(results['data_overview'], default=str)}
            Utilization Analysis: {json.dumps(results['utilization_analysis'], default=str)}
            Spend Forecast: {json.dumps(results['spend_forecast'], default=str)}
            Compliance Status: {json.dumps(results['compliance_status'], default=str)}
            
            Provide a comprehensive executive summary with key findings and strategic recommendations for eDiscovery operations management.
            """
            
            results["executive_summary"] = self.llm_provider.generate(summary_prompt)
            
            return results
            
        except Exception as e:
            logger.error(f"Error in comprehensive analysis: {e}")
            return {"error": str(e)}
    
    def answer_query(self, query: str, df: pd.DataFrame, context: Dict[str, Any] = None) -> str:
        """Answer specific queries using the Finance Director agent"""
        try:
            # Get analysis context if not provided
            if context is None:
                context = self.comprehensive_analysis(df)
            
            # Prepare context for the query
            context_str = json.dumps(context, default=str, indent=2)
            
            query_prompt = f"""
            {AGENT_PROMPTS['finance_director']}
            
            Based on this comprehensive analysis of the eDiscovery utilization data:
            {context_str}
            
            User Query: {query}
            
            Provide a specific, data-driven response with actionable insights and recommendations.
            """
            
            return self.llm_provider.generate(query_prompt)
            
        except Exception as e:
            logger.error(f"Error answering query: {e}")
            return "I apologize, but I encountered an error processing your query. Please ensure the data is properly loaded and try again."
    
    def get_agent(self, agent_name: str) -> Optional[LlmAgent]:
        """Get specific agent by name"""
        return self.agents.get(agent_name)
    
    def list_agents(self) -> List[str]:
        """List all available agents"""
        return list(self.agents.keys())

# Factory function for easy initialization
def create_agent_system(model: str = "mistral:7b", ollama_host: str = "http://localhost:11434") -> AgentUtisSystem:
    """Create and initialize the complete agent system"""
    try:
        llm_provider = OllamaLLMProvider(model=model, base_url=ollama_host)
        return AgentUtisSystem(llm_provider)
    except Exception as e:
        logger.error(f"Error creating agent system: {e}")
        raise

# Example usage
if __name__ == "__main__":
    # Initialize the system
    agent_system = create_agent_system()
    
    # Example usage with sample data
    sample_data = pd.DataFrame({
        'expert_name': ['John Doe', 'Jane Smith', 'Bob Johnson'],
        'billable_hours': [140, 160, 60],
        'total_hours': [160, 200, 100],
        'total_cost': [14000, 16000, 6000],
        'date': ['2024-01-01', '2024-01-01', '2024-01-01']
    })
    
    # Run comprehensive analysis
    results = agent_system.comprehensive_analysis(sample_data)
    print("Analysis Results:", json.dumps(results, indent=2, default=str))
    
    # Answer a query
    response = agent_system.answer_query("What are the main utilization insights?", sample_data, results)
    print("Query Response:", response)