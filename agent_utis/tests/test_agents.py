"""
Unit tests for Agent Utis agents
"""

import unittest
import pandas as pd
import numpy as np
from unittest.mock import Mock, patch
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents import DataAnalyst, UtilizationExpert, SpendPredictor, ComplianceChecker, FinanceDirector, OllamaLLMProvider

class TestOllamaLLMProvider(unittest.TestCase):
    
    @patch('agents.ollama.Client')
    def test_generate_success(self, mock_client):
        mock_instance = Mock()
        mock_instance.generate.return_value = {'response': 'Test response'}
        mock_client.return_value = mock_instance
        
        provider = OllamaLLMProvider()
        result = provider.generate("Test prompt")
        
        self.assertEqual(result, "Test response")
        mock_instance.generate.assert_called_once()

    @patch('agents.ollama.Client')
    def test_generate_error(self, mock_client):
        mock_instance = Mock()
        mock_instance.generate.side_effect = Exception("Connection error")
        mock_client.return_value = mock_instance
        
        provider = OllamaLLMProvider()
        result = provider.generate("Test prompt")
        
        self.assertIn("error", result.lower())

class TestDataAnalyst(unittest.TestCase):
    
    def setUp(self):
        self.mock_llm = Mock()
        self.mock_llm.generate.return_value = "Test analysis insight"
        self.analyst = DataAnalyst(self.mock_llm)
        
        # Sample test data
        self.test_df = pd.DataFrame({
            'expert_name': ['John Doe', 'Jane Smith'],
            'billable_hours': [100, 150],
            'total_hours': [120, 180],
            'date': ['2024-01-01', '2024-01-02']
        })
    
    def test_analyze_csv_success(self):
        result = self.analyst.analyze_csv(self.test_df)
        
        self.assertIsInstance(result, dict)
        self.assertEqual(result['total_records'], 2)
        self.assertIn('columns', result)
        self.assertIn('llm_insight', result)
    
    def test_analyze_csv_error(self):
        # Test with invalid data
        invalid_df = "not a dataframe"
        result = self.analyst.analyze_csv(invalid_df)
        
        self.assertIn('error', result)

class TestUtilizationExpert(unittest.TestCase):
    
    def setUp(self):
        self.mock_llm = Mock()
        self.mock_llm.generate.return_value = "Test utilization analysis"
        self.expert = UtilizationExpert(self.mock_llm)
        
        self.test_df = pd.DataFrame({
            'expert_name': ['John Doe', 'Jane Smith', 'Bob Johnson'],
            'billable_hours': [100, 150, 60],
            'total_hours': [120, 180, 100],
            'total_cost': [12000, 18000, 6000]
        })
    
    def test_calculate_utilization_metrics(self):
        result = self.expert.calculate_utilization_metrics(self.test_df)
        
        self.assertIsInstance(result, dict)
        self.assertIn('avg_utilization', result)
        self.assertIn('over_utilized', result)
        self.assertIn('under_utilized', result)
        self.assertIn('expert_analysis', result)
        
        # Test calculations
        expected_avg = ((100/120 + 150/180 + 60/100) / 3) * 100
        self.assertAlmostEqual(result['avg_utilization'], expected_avg, places=1)

class TestSpendPredictor(unittest.TestCase):
    
    def setUp(self):
        self.mock_llm = Mock()
        self.mock_llm.generate.return_value = "Test spend prediction"
        self.predictor = SpendPredictor(self.mock_llm)
        
        self.test_df = pd.DataFrame({
            'total_cost': [10000, 15000, 12000, 18000],
            'date': ['2024-01-01', '2024-02-01', '2024-03-01', '2024-04-01']
        })
    
    def test_predict_spend_success(self):
        result = self.predictor.predict_spend(self.test_df)
        
        self.assertIsInstance(result, dict)
        self.assertIn('predicted_monthly_spend', result)
        self.assertIn('predictive_analysis', result)
    
    def test_predict_spend_insufficient_data(self):
        small_df = pd.DataFrame({
            'total_cost': [10000],
            'date': ['2024-01-01']
        })
        
        result = self.predictor.predict_spend(small_df)
        
        # Should handle gracefully with insufficient data
        self.assertIsInstance(result, dict)

class TestComplianceChecker(unittest.TestCase):
    
    def setUp(self):
        self.mock_llm = Mock()
        self.mock_llm.generate.return_value = "Test compliance analysis"
        self.checker = ComplianceChecker(self.mock_llm)
    
    def test_check_compliance(self):
        test_metrics = {
            'avg_utilization': 75.0,
            'over_utilized': 2,
            'under_utilized': 1
        }
        
        result = self.checker.check_compliance(test_metrics)
        
        self.assertIsInstance(result, dict)
        self.assertIn('compliance_score', result)
        self.assertIn('issues', result)
        self.assertIn('recommendations', result)
        self.assertIn('compliance_analysis', result)

class TestFinanceDirector(unittest.TestCase):
    
    def setUp(self):
        self.mock_llm = Mock()
        self.mock_llm.generate.return_value = "Test director analysis"
        self.director = FinanceDirector(self.mock_llm)
        
        self.test_df = pd.DataFrame({
            'expert_name': ['John Doe', 'Jane Smith'],
            'billable_hours': [100, 150],
            'total_hours': [120, 180],
            'total_cost': [12000, 18000],
            'date': ['2024-01-01', '2024-02-01']
        })
    
    def test_comprehensive_analysis(self):
        result = self.director.comprehensive_analysis(self.test_df)
        
        self.assertIsInstance(result, dict)
        self.assertIn('data_overview', result)
        self.assertIn('utilization_analysis', result)
        self.assertIn('spend_forecast', result)
        self.assertIn('compliance_status', result)
        self.assertIn('executive_summary', result)
        self.assertIn('generated_at', result)
    
    def test_answer_query(self):
        query = "What is the average utilization rate?"
        result = self.director.answer_query(query, self.test_df)
        
        self.assertIsInstance(result, str)
        self.assertTrue(len(result) > 0)

class TestIntegration(unittest.TestCase):
    
    def test_end_to_end_workflow(self):
        """Test complete workflow with all agents"""
        
        # Create test data
        test_df = pd.DataFrame({
            'expert_name': ['Expert1', 'Expert2', 'Expert3'],
            'billable_hours': [140, 160, 50],
            'total_hours': [160, 200, 100],
            'total_cost': [14000, 16000, 5000],
            'date': ['2024-01-01', '2024-01-01', '2024-01-01']
        })
        
        # Mock LLM provider
        mock_llm = Mock()
        mock_llm.generate.return_value = "Mock analysis result"
        
        # Create Finance Director
        director = FinanceDirector(mock_llm)
        
        # Run comprehensive analysis
        result = director.comprehensive_analysis(test_df)
        
        # Verify structure
        self.assertIn('data_overview', result)
        self.assertIn('utilization_analysis', result)
        self.assertIn('spend_forecast', result)
        self.assertIn('compliance_status', result)
        self.assertIn('executive_summary', result)
        
        # Verify utilization calculations
        util_analysis = result['utilization_analysis']
        expected_rates = [87.5, 80.0, 50.0]  # (140/160, 160/200, 50/100) * 100
        expected_avg = sum(expected_rates) / len(expected_rates)
        
        self.assertAlmostEqual(util_analysis['avg_utilization'], expected_avg, places=1)
        self.assertEqual(util_analysis['over_utilized'], 1)  # Expert1 > 80%
        self.assertEqual(util_analysis['under_utilized'], 1)  # Expert3 < 70%

if __name__ == '__main__':
    unittest.main()