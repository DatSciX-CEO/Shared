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
from google.adk.llms.litellm import LiteLLM

from .tools import TOOLS
from ..sub_agents.data_analyst import create_data_analyst_agent
from ..sub_agents.utilization_expert import create_utilization_expert_agent
from ..sub_agents.spend_predictor import create_spend_predictor_agent
from ..sub_agents.compliance_checker import create_compliance_checker_agent

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def setup_before_agent_call(tool_context: ToolContext) -> None:
    \"\"\"
    Setup function called before agent interactions
    Prepares the context with necessary configurations
    \"\"\"\n    # Initialize any required context state
    if not hasattr(tool_context, \'state\'):
        tool_context.state = {}
    
    logger.info(\"Agent context initialized successfully\")

def create_finance_director_agent(dataframe: Optional[pd.DataFrame] = None) -> Agent:
    \"\"\"\n    Create and configure the Finance Director agent with sub-agents and tools
    
    Args:
        dataframe: Optional pandas DataFrame to store in context
    
    Returns:
        Configured Agent instance
    \"\"\"\n    
    # Get model from environment or use default
    model_name = os.getenv(\"AGENT_MODEL\", \"ollama/mistral:7b\") # Changed to Ollama format
    
    # Configure LiteLLM for Ollama
    llm = LiteLLM(model=model_name, api_base=os.getenv(\"OLLAMA_API_BASE\", \"http://localhost:11434\"))
    
    # Main agent instruction
    instruction = \"\"\"You are the Finance Director overseeing eDiscovery and legal services operations. 
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
    
    Use these tools to provide thorough analysis and recommendations.\"\"\"\n    
    # Global instruction for all interactions
    global_instruction = \"\"\"You are an expert in eDiscovery utilization analysis. 
    Provide accurate, data-driven insights with specific recommendations for legal operations optimization.\"\"\"\n    
    # Create sub-agents
    sub_agents = [
        create_data_analyst_agent(),
        create_utilization_expert_agent(),
        create_spend_predictor_agent(),
        create_compliance_checker_agent()
    ]
    
    # Create the main agent
    agent = Agent(
        name=\"FinanceDirector\",
        llm=llm, # Use LiteLLM instance
        instruction=instruction,
        global_instruction=global_instruction,
        sub_agents=sub_agents,
        tools=TOOLS,
        before_agent_call=setup_before_agent_call,
        generation_config={
            \"temperature\": 0.1,  # Low temperature for consistent analysis
            \"top_p\": 0.9,
            \"top_k\": 40,
            \"max_output_tokens\": 2048
        }
    )
    
    logger.info(\"Finance Director agent created with 4 sub-agents and 4 tools\")
    return agent

class AgentUtisSystem:
    \"\"\"\n    Main system for managing Agent Utis operations
    \"\"\"\n    
    def __init__(self, dataframe: Optional[pd.DataFrame] = None):
        self.dataframe = dataframe
        self.agent = create_finance_director_agent(dataframe)
        self.tool_context = ToolContext()
        
        # Store dataframe in context if provided
        if dataframe is not None:
            self.tool_context.state = {\'dataframe\': dataframe}
        else:
            self.tool_context.state = {}
    
    def set_dataframe(self, df: pd.DataFrame) -> None:
        \"\"\"Set or update the dataframe for analysis\"\"\"\n        self.dataframe = df
        self.tool_context.state[\'dataframe\'] = df
        logger.info(f\"Dataframe updated with {len(df)} records\")
    
    async def comprehensive_analysis(self, df: Optional[pd.DataFrame] = None) -> Dict[str, Any]:
        \"\"\"\n        Run comprehensive analysis using all available tools
        
        Args:
            df: Optional dataframe to analyze
        
        Returns:
            Dictionary containing all analysis results
        \"\"\"\n        try:
            # Update dataframe if provided
            if df is not None:
                self.set_dataframe(df)
            
            if self.dataframe is None:
                return {\"error\": \"No dataframe available for analysis\"}
            
            # The Finance Director agent will orchestrate the analysis
            # by calling the appropriate tools and sub-agents.
            # We provide a prompt that encourages it to use all relevant tools.
            analysis_prompt = \"\"\"Perform a comprehensive analysis of the provided eDiscovery utilization data. \
            This should include data overview, utilization metrics, spend prediction, and compliance checks. \
            Synthesize all findings into a detailed executive summary with actionable recommendations.\"\"\"
            
            # Run the agent with the comprehensive analysis prompt
            response = await self.agent.run_async(
                prompt=analysis_prompt,
                tool_context=self.tool_context
            )
            
            # The response from agent.run_async() will contain the synthesized results
            # You might need to parse this response based on how the Finance Director agent
            # is instructed to format its output. For now, we'll return the raw response.
            
            # In a real scenario, you'd likely have the Finance Director agent
            # output a structured JSON or a well-formatted string that can be parsed.
            # For this MVP, we'll assume the agent's response is the executive summary.
            
            results = {
                \"analysis_timestamp\": pd.Timestamp.now().isoformat(),
                \"executive_summary\": response.text # Assuming the agent's final response is the summary
            }
            
            # If the agent was designed to output structured data, you would parse it here.
            # For example, if it outputs JSON:
            # try:
            #     parsed_response = json.loads(response.text)
            #     results.update(parsed_response)
            # except json.JSONDecodeError:
            #     logger.warning(\"Agent response was not valid JSON.\")
            
            return results
            
        except Exception as e:
            logger.error(f\"Error in comprehensive analysis: {e}\")
            return {\"error\": str(e)}
    
    async def answer_query(self, query: str, context: Optional[Dict[str, Any]] = None) -> str:
        \"\"\"\n        Answer specific queries using the Finance Director agent
        
        Args:
            query: User query about the data
            context: Optional analysis context
        
        Returns:
            Agent response to the query
        \"\"\"\n        try:
            if self.dataframe is None:
                return \"No data available for analysis. Please upload a CSV file first.\"\n            
            # The Finance Director agent will answer the query using its tools and sub-agents
            response = await self.agent.run_async(
                prompt=query,
                tool_context=self.tool_context
            )
            
            return response.text # Return the agent's text response
            
        except Exception as e:
            logger.error(f\"Error answering query: {e}\")
            return \"I apologize, but I encountered an error processing your query.\"\n    
    def get_agent_info(self) -> Dict[str, Any]:
        \"\"\"\n        Get information about the agent system
        \"\"\"\n        return {
            \"main_agent\": self.agent.name,
            \"sub_agents\": [sub_agent.name for sub_agent in self.agent.sub_agents] if self.agent.sub_agents else [],
            \"tools\": [tool.name for tool in self.agent.tools] if self.agent.tools else [], # Access .name attribute
            \"model\": self.agent.llm.model, # Access model from llm object
            \"data_loaded\": self.dataframe is not None,
            \"data_records\": len(self.dataframe) if self.dataframe is not None else 0
        }

# Factory function for easy initialization
def create_agent_system(dataframe: Optional[pd.DataFrame] = None) -> AgentUtisSystem:
    \"\"\"\n    Create and initialize the complete Agent Utis system
    
    Args:
        dataframe: Optional pandas DataFrame for analysis
    
    Returns:
        Configured AgentUtisSystem instance
    \"\"\"\n    try:
        return AgentUtisSystem(dataframe)
    except Exception as e:
        logger.error(f\"Error creating agent system: {e}\")
        raise