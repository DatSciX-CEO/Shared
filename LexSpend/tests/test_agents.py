"""
Unit tests for ADK agents
"""
import unittest
import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from lexspend.agent import lexspend_agent, root_agent
from lexspend.agents.analysis_agent import analysis_agent
from lexspend.agents.ediscovery_agent import ediscovery_agent
from lexspend.agents.anomaly_agent import anomaly_agent


class TestAgents(unittest.TestCase):
    """Test ADK agents"""
    
    def test_root_agent_exists(self):
        """Test that root_agent is defined"""
        self.assertIsNotNone(root_agent)
        self.assertEqual(root_agent.name, "lexspend_agent")
    
    def test_lexspend_agent_has_tools(self):
        """Test that main agent has tools"""
        self.assertIsNotNone(lexspend_agent.tools)
        self.assertGreater(len(lexspend_agent.tools), 0)
    
    def test_analysis_agent_exists(self):
        """Test that analysis agent is defined"""
        self.assertIsNotNone(analysis_agent)
        self.assertEqual(analysis_agent.name, "analysis_agent")
    
    def test_ediscovery_agent_exists(self):
        """Test that eDiscovery agent is defined"""
        self.assertIsNotNone(ediscovery_agent)
        self.assertEqual(ediscovery_agent.name, "ediscovery_agent")
    
    def test_anomaly_agent_exists(self):
        """Test that anomaly agent is defined"""
        self.assertIsNotNone(anomaly_agent)
        self.assertEqual(anomaly_agent.name, "anomaly_agent")
    
    def test_agents_have_models(self):
        """Test that all agents have models configured"""
        self.assertIsNotNone(lexspend_agent.model)
        self.assertIsNotNone(analysis_agent.model)
        self.assertIsNotNone(ediscovery_agent.model)
        self.assertIsNotNone(anomaly_agent.model)


if __name__ == '__main__':
    unittest.main()

