"""
Main Agent for Agent Utis - eDiscovery Utilization Analysis
Following Google ADK patterns for agent definition and orchestration
"""

import os
import pandas as pd
from typing import Dict, Any, Optional
import logging

from google.adk.agents import Agent
from google.adk.tools import ToolContext

from .tools import TOOLS
from ..sub_agents.data_analyst import create_data_analyst_agent
from ..sub_agents.utilization_expert import create_utilization_expert_agent
from ..sub_agents.spend_predictor import create_spend_predictor_agent
from ..sub_agents.compliance_checker import create_compliance_checker_agent

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def setup_before_agent_call(tool_context: ToolContext) -> None:
    """
    Setup function called before agent interactions
    Prepares the context with necessary configurations
    """
    # Initialize any required context state
    if not hasattr(tool_context, 'state'):
        tool_context.state = {}
    
    logger.info("Agent context initialized successfully")

def create_finance_director_agent(dataframe: Optional[pd.DataFrame] = None) -> Agent:
    """
    Create and configure the Finance Director agent with sub-agents and tools
    
    Args:
        dataframe: Optional pandas DataFrame to store in context
    
    Returns:
        Configured Agent instance
    """
    
    # Get model from environment or use default
    model = os.getenv("AGENT_MODEL", "gemini-2.0-flash-exp")
    
    # Main agent instruction
    instruction = """You are the Finance Director overseeing eDiscovery and legal services operations. 
    Your role is to orchestrate analysis across all departments and synthesize comprehensive reports on utilization, 
    cost efficiency, predictions, and compliance. You delegate specific tasks to specialized sub-agents and combine 
    their insights to provide executive-level recommendations for decision-making in legal operations.
    
    Key responsibilities:
    - Coordinate analysis across Data Analyst, Utilization Expert, Spend Predictor, and Compliance Checker
    - Synthesize findings into actionable business insights
    - Provide strategic recommendations for resource optimization
    - Ensure all analysis aligns with eDiscovery industry best practices
    
    When responding to queries, be specific, data-driven, and focus on actionable insights.
    Always consider the context of eDiscovery operations and legal industry standards.
    
    Available tools for analysis:
    - analyze_csv_data: For comprehensive data analysis and validation
    - calculate_utilization_metrics: For expert utilization and efficiency analysis
    - predict_future_spend: For financial forecasting and budget planning
    - check_compliance_metrics: For industry compliance and benchmark analysis
    
    Use these tools to provide thorough analysis and recommendations."""
    
    # Global instruction for all interactions
    global_instruction = """You are an expert in eDiscovery utilization analysis. 
    Provide accurate, data-driven insights with specific recommendations for legal operations optimization."""
    
    # Create sub-agents
    sub_agents = [
        create_data_analyst_agent(),
        create_utilization_expert_agent(),
        create_spend_predictor_agent(),
        create_compliance_checker_agent()
    ]
    
    # Create the main agent
    agent = Agent(
        name="FinanceDirector",
        model=model,
        instruction=instruction,
        global_instruction=global_instruction,
        sub_agents=sub_agents,
        tools=TOOLS,
        before_agent_call=setup_before_agent_call,
        generation_config={
            "temperature": 0.1,  # Low temperature for consistent analysis
            "top_p": 0.9,
            "top_k": 40,
            "max_output_tokens": 2048
        }
    )
    
    logger.info("Finance Director agent created with 4 sub-agents and 4 tools")
    return agent

class AgentUtisSystem:
    """
    Main system for managing Agent Utis operations
    """
    
    def __init__(self, dataframe: Optional[pd.DataFrame] = None):
        self.dataframe = dataframe
        self.agent = create_finance_director_agent(dataframe)
        self.tool_context = ToolContext()
        
        # Store dataframe in context if provided
        if dataframe is not None:
            self.tool_context.state = {'dataframe': dataframe}
        else:
            self.tool_context.state = {}
    
    def set_dataframe(self, df: pd.DataFrame) -> None:
        """Set or update the dataframe for analysis"""
        self.dataframe = df
        self.tool_context.state['dataframe'] = df
        logger.info(f"Dataframe updated with {len(df)} records")
    
    async def comprehensive_analysis(self, df: Optional[pd.DataFrame] = None) -> Dict[str, Any]:
        """
        Run comprehensive analysis using all available tools
        
        Args:
            df: Optional dataframe to analyze
        
        Returns:
            Dictionary containing all analysis results
        """
        try:
            # Update dataframe if provided
            if df is not None:
                self.set_dataframe(df)
            
            if self.dataframe is None:
                return {"error": "No dataframe available for analysis"}
            
            results = {
                "analysis_timestamp": pd.Timestamp.now().isoformat(),
                "data_overview": {},
                "utilization_analysis": {},
                "spend_forecast": {},
                "compliance_status": {},
                "executive_summary": ""
            }
            
            # Run data analysis
            data_result = await self.agent.tools[0]["function"]("Analyze the CSV data", self.tool_context)
            results["data_overview"] = data_result
            
            # Run utilization analysis
            util_result = await self.agent.tools[1]["function"]("Calculate utilization metrics", self.tool_context)
            results["utilization_analysis"] = util_result
            
            # Run spend prediction
            spend_result = await self.agent.tools[2]["function"]("Predict future spending", self.tool_context)
            results["spend_forecast"] = spend_result
            
            # Run compliance check
            compliance_result = await self.agent.tools[3]["function"]("Check compliance metrics", self.tool_context)
            results["compliance_status"] = compliance_result
            
            # Generate executive summary using the main agent
            summary_prompt = f"""
            Based on the comprehensive analysis results:
            
            Data Overview: {data_result}
            Utilization Analysis: {util_result}
            Spend Forecast: {spend_result}
            Compliance Status: {compliance_result}
            
            Provide a comprehensive executive summary with key findings and strategic recommendations for eDiscovery operations management.
            """
            
            # Note: In a full implementation, you would use agent.run_async() here
            # For now, we'll use a placeholder
            results["executive_summary"] = "Executive summary would be generated using the Finance Director agent"
            
            return results
            
        except Exception as e:
            logger.error(f"Error in comprehensive analysis: {e}")
            return {"error": str(e)}
    
    async def answer_query(self, query: str, context: Optional[Dict[str, Any]] = None) -> str:
        """
        Answer specific queries using the Finance Director agent
        
        Args:
            query: User query about the data
            context: Optional analysis context
        
        Returns:
            Agent response to the query
        """
        try:
            if self.dataframe is None:
                return "No data available for analysis. Please upload a CSV file first."
            
            # In a full implementation, you would use agent.run_async() with the query
            # For now, we'll provide a structured response based on available context
            
            response = f"""
            Based on the available eDiscovery utilization data with {len(self.dataframe)} records:
            
            Query: {query}
            
            [This would be processed by the Finance Director agent using the available tools and sub-agents]
            
            The agent would analyze your specific question and provide data-driven insights with actionable recommendations.
            """
            
            return response
            
        except Exception as e:
            logger.error(f"Error answering query: {e}")
            return "I apologize, but I encountered an error processing your query."
    
    def get_agent_info(self) -> Dict[str, Any]:
        """Get information about the agent system"""
        return {
            "main_agent": self.agent.name,
            "sub_agents": [sub_agent.name for sub_agent in self.agent.sub_agents] if self.agent.sub_agents else [],
            "tools": [tool["name"] for tool in self.agent.tools] if self.agent.tools else [],
            "model": self.agent.model,
            "data_loaded": self.dataframe is not None,
            "data_records": len(self.dataframe) if self.dataframe is not None else 0
        }

# Factory function for easy initialization
def create_agent_system(dataframe: Optional[pd.DataFrame] = None) -> AgentUtisSystem:
    """
    Create and initialize the complete Agent Utis system
    
    Args:
        dataframe: Optional pandas DataFrame for analysis
    
    Returns:
        Configured AgentUtisSystem instance
    """
    try:
        return AgentUtisSystem(dataframe)
    except Exception as e:
        logger.error(f"Error creating agent system: {e}")
        raise