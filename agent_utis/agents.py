"""
Hierarchical AI Agents for Agent Utis MVP
Local eDiscovery utilization analysis using Ollama
"""

import logging
import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional, Callable
from datetime import datetime
import json
import ollama
from dataclasses import dataclass
from enum import Enum

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AgentRole(Enum):
    FINANCE_DIRECTOR = "finance_director"
    DATA_ANALYST = "data_analyst"
    UTILIZATION_EXPERT = "utilization_expert"
    SPEND_PREDICTOR = "spend_predictor"
    COMPLIANCE_CHECKER = "compliance_checker"

# Agent prompts
AGENT_PROMPTS = {
    AgentRole.FINANCE_DIRECTOR: """You are the Finance Director overseeing eDiscovery and legal services operations. 
    Your role is to orchestrate analysis across all departments and synthesize comprehensive reports on utilization, 
    cost efficiency, predictions, and compliance. You delegate specific tasks to specialized sub-agents and combine 
    their insights to provide executive-level recommendations for decision-making in legal operations.
    
    Key responsibilities:
    - Coordinate analysis across Data Analyst, Utilization Expert, Spend Predictor, and Compliance Checker
    - Synthesize findings into actionable business insights
    - Provide strategic recommendations for resource optimization
    - Ensure all analysis aligns with eDiscovery industry best practices
    
    When responding to queries, be specific, data-driven, and focus on actionable insights.""",
    
    AgentRole.DATA_ANALYST: """You are a Data Analyst specializing in eDiscovery and legal services data analysis. 
    Your expertise includes processing CSV data containing expert utilization metrics, validating data quality, 
    and performing statistical analysis on legal operations data.
    
    Focus on accuracy, data integrity, and clear communication of findings. Always validate data before analysis.""",
    
    AgentRole.UTILIZATION_EXPERT: """You are a Utilization Expert specializing in eDiscovery and legal services resource optimization. 
    You analyze expert utilization rates, identify efficiency patterns, and provide recommendations for workforce optimization.
    
    Key metrics:
    - Calculate utilization rates (billable_hours / total_hours * 100)
    - Identify over-utilization (>80%) and under-utilization (<70%) patterns
    - Benchmark against industry standards (70-80% optimal utilization)""",
    
    AgentRole.SPEND_PREDICTOR: """You are a Spend Predictor for legal and eDiscovery services with expertise in financial forecasting. 
    You analyze historical spending patterns and predict future costs using statistical methods.
    
    Focus on accuracy in predictions and clear communication of forecast assumptions and limitations.""",
    
    AgentRole.COMPLIANCE_CHECKER: """You are a Compliance Checker ensuring all legal and eDiscovery operations align with industry best practices. 
    You review operational metrics against established benchmarks and identify compliance risks.
    
    Use established benchmarks (e.g., 70-80% utilization targets) and provide specific compliance recommendations."""
}

@dataclass
class Tool:
    """Tool definition for agents"""
    name: str
    description: str
    function: Callable
    
class BaseAgent:
    """Base agent class with Ollama integration"""
    
    def __init__(self, role: AgentRole, model: str = "mistral:7b", base_url: str = "http://localhost:11434"):
        self.role = role
        self.model = model
        self.prompt = AGENT_PROMPTS[role]
        self.client = ollama.Client(host=base_url)
        
    def generate_response(self, prompt: str, context: Dict[str, Any] = None) -> str:
        """Generate response using Ollama"""
        try:
            full_prompt = f"{self.prompt}\n\n"
            if context:
                full_prompt += f"Context: {json.dumps(context, default=str)}\n\n"
            full_prompt += f"Query: {prompt}\n\nResponse:"
            
            response = self.client.generate(
                model=self.model,
                prompt=full_prompt,
                options={
                    "temperature": 0.7,
                    "top_p": 0.9,
                    "num_predict": 2048
                }
            )
            return response['response']
        except Exception as e:
            logger.error(f"Error generating response with Ollama: {e}")
            return f"Error: Unable to generate response. Please ensure Ollama is running with {self.model} model."

class DataAnalyst(BaseAgent):
    """Data Analyst agent with CSV processing capabilities"""
    
    def __init__(self, model: str = "mistral:7b"):
        super().__init__(AgentRole.DATA_ANALYST, model)
        
    def analyze_csv(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze CSV data and return insights"""
        try:
            analysis = {
                "total_records": len(df),
                "columns": list(df.columns),
                "missing_data": df.isnull().sum().to_dict(),
                "data_types": {col: str(dtype) for col, dtype in df.dtypes.items()},
                "numeric_summary": {}
            }
            
            # Date range analysis
            date_cols = [col for col in df.columns if 'date' in col.lower()]
            if date_cols:
                date_col = date_cols[0]
                df[date_col] = pd.to_datetime(df[date_col], errors='coerce')
                analysis["date_range"] = {
                    "start": str(df[date_col].min()),
                    "end": str(df[date_col].max())
                }
            
            # Numeric statistics
            numeric_cols = df.select_dtypes(include=[np.number]).columns
            if len(numeric_cols) > 0:
                analysis["numeric_summary"] = df[numeric_cols].describe().to_dict()
            
            # Get LLM insights
            analysis["insights"] = self.generate_response(
                f"Analyze this data overview and provide key insights: {json.dumps(analysis, default=str)}"
            )
            
            return analysis
        except Exception as e:
            logger.error(f"Error in CSV analysis: {e}")
            return {"error": str(e)}

class UtilizationExpert(BaseAgent):
    """Utilization Expert agent"""
    
    def __init__(self, model: str = "mistral:7b"):
        super().__init__(AgentRole.UTILIZATION_EXPERT, model)
        
    def calculate_metrics(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Calculate utilization metrics"""
        try:
            metrics = {}
            
            if 'billable_hours' in df.columns and 'total_hours' in df.columns:
                df = df.copy()
                df['utilization_rate'] = (df['billable_hours'] / df['total_hours']) * 100
                
                metrics.update({
                    "avg_utilization": float(df['utilization_rate'].mean()),
                    "median_utilization": float(df['utilization_rate'].median()),
                    "over_utilized": int(len(df[df['utilization_rate'] > 80])),
                    "under_utilized": int(len(df[df['utilization_rate'] < 70])),
                    "optimal_range": int(len(df[(df['utilization_rate'] >= 70) & (df['utilization_rate'] <= 80)]))
                })
                
                # Role-based analysis
                if 'role' in df.columns:
                    role_metrics = df.groupby('role')['utilization_rate'].agg(['mean', 'count']).round(2)
                    metrics['role_analysis'] = role_metrics.to_dict()
            
            # Get expert analysis
            metrics["expert_analysis"] = self.generate_response(
                f"Analyze these utilization metrics and provide recommendations: {json.dumps(metrics, default=str)}"
            )
            
            return metrics
        except Exception as e:
            logger.error(f"Error calculating utilization metrics: {e}")
            return {"error": str(e)}

class SpendPredictor(BaseAgent):
    """Spend Predictor agent"""
    
    def __init__(self, model: str = "mistral:7b"):
        super().__init__(AgentRole.SPEND_PREDICTOR, model)
        
    def predict_spend(self, df: pd.DataFrame, periods: int = 4) -> Dict[str, Any]:
        """Predict future spending"""
        try:
            prediction = {}
            
            if 'total_cost' in df.columns and 'date' in df.columns:
                df_copy = df.copy()
                df_copy['date'] = pd.to_datetime(df_copy['date'])
                monthly_spend = df_copy.groupby(df_copy['date'].dt.to_period('M'))['total_cost'].sum()
                
                if len(monthly_spend) >= 3:
                    # Linear regression
                    x = np.arange(len(monthly_spend))
                    y = monthly_spend.values
                    coeffs = np.polyfit(x, y, 1)
                    
                    # Predict future
                    future_x = np.arange(len(monthly_spend), len(monthly_spend) + periods)
                    future_spend = np.polyval(coeffs, future_x)
                    
                    prediction.update({
                        "historical_trend": float(coeffs[0]),
                        "predicted_monthly_spend": [float(x) for x in future_spend],
                        "total_predicted": float(sum(future_spend)),
                        "confidence_level": "Medium" if len(monthly_spend) >= 6 else "Low"
                    })
                    
                    # Get predictive insights
                    prediction["analysis"] = self.generate_response(
                        f"Analyze this spending forecast and provide insights: {json.dumps(prediction, default=str)}"
                    )
                else:
                    prediction["error"] = "Insufficient data for prediction"
            else:
                prediction["error"] = "Missing required columns"
            
            return prediction
        except Exception as e:
            logger.error(f"Error in spend prediction: {e}")
            return {"error": str(e)}

class ComplianceChecker(BaseAgent):
    """Compliance Checker agent"""
    
    def __init__(self, model: str = "mistral:7b"):
        super().__init__(AgentRole.COMPLIANCE_CHECKER, model)
        
    def check_compliance(self, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Check compliance against benchmarks"""
        try:
            report = {
                "compliance_score": 0,
                "max_score": 100,
                "issues": [],
                "recommendations": []
            }
            
            # Check utilization compliance
            if "avg_utilization" in metrics:
                avg_util = metrics["avg_utilization"]
                if 70 <= avg_util <= 80:
                    report["compliance_score"] += 25
                elif avg_util < 70:
                    report["issues"].append(f"Average utilization ({avg_util:.1f}%) below optimal range")
                    report["recommendations"].append("Consider workload redistribution")
                else:
                    report["issues"].append(f"Average utilization ({avg_util:.1f}%) above optimal range")
                    report["recommendations"].append("Risk of burnout - consider additional resources")
            
            # Check over-utilization
            if "over_utilized" in metrics and metrics["over_utilized"] == 0:
                report["compliance_score"] += 25
            else:
                report["issues"].append(f"{metrics.get('over_utilized', 0)} experts are over-utilized")
            
            # Calculate percentage
            report["compliance_percentage"] = (report["compliance_score"] / report["max_score"]) * 100
            
            # Get compliance analysis
            report["analysis"] = self.generate_response(
                f"Analyze this compliance report and provide recommendations: {json.dumps(report, default=str)}"
            )
            
            return report
        except Exception as e:
            logger.error(f"Error in compliance check: {e}")
            return {"error": str(e)}

class FinanceDirector(BaseAgent):
    """Finance Director orchestrating agent"""
    
    def __init__(self, model: str = "mistral:7b"):
        super().__init__(AgentRole.FINANCE_DIRECTOR, model)
        self.data_analyst = DataAnalyst(model)
        self.utilization_expert = UtilizationExpert(model)
        self.spend_predictor = SpendPredictor(model)
        self.compliance_checker = ComplianceChecker(model)
        
    def comprehensive_analysis(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Run comprehensive analysis using all sub-agents"""
        try:
            results = {
                "analysis_timestamp": datetime.now().isoformat(),
                "data_overview": self.data_analyst.analyze_csv(df),
                "utilization_analysis": self.utilization_expert.calculate_metrics(df),
                "spend_forecast": self.spend_predictor.predict_spend(df),
                "compliance_status": {},
                "executive_summary": ""
            }
            
            # Compliance check using utilization metrics
            results["compliance_status"] = self.compliance_checker.check_compliance(
                results["utilization_analysis"]
            )
            
            # Generate executive summary
            summary_context = {
                "data_records": len(df),
                "avg_utilization": results["utilization_analysis"].get("avg_utilization", "N/A"),
                "compliance_score": results["compliance_status"].get("compliance_percentage", "N/A"),
                "spend_trend": results["spend_forecast"].get("historical_trend", "N/A")
            }
            
            results["executive_summary"] = self.generate_response(
                "Provide an executive summary of the analysis results",
                context=summary_context
            )
            
            return results
        except Exception as e:
            logger.error(f"Error in comprehensive analysis: {e}")
            return {"error": str(e)}
    
    def answer_query(self, query: str, df: pd.DataFrame, context: Dict[str, Any] = None) -> str:
        """Answer specific queries"""
        try:
            if context is None:
                context = self.comprehensive_analysis(df)
            
            return self.generate_response(query, context=context)
        except Exception as e:
            logger.error(f"Error answering query: {e}")
            return "I apologize, but I encountered an error processing your query."

# Factory function
def create_agent_system(model: str = "mistral:7b", ollama_host: str = "http://localhost:11434") -> FinanceDirector:
    """Create and initialize the complete agent system"""
    try:
        # Test Ollama connection
        client = ollama.Client(host=ollama_host)
        client.list()  # Test connection
        
        return FinanceDirector(model=model)
    except Exception as e:
        logger.error(f"Error creating agent system: {e}")
        raise Exception(f"Failed to connect to Ollama at {ollama_host}. Ensure Ollama is running and {model} is available.")