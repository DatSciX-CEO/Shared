"""
Unit tests for ADK tools
"""
import unittest
import os
import sys
import tempfile
import pandas as pd

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from lexspend.tools.file_reader_tool import read_file
from lexspend.tools.data_analysis_tool import analyze_data, analyze_top_firms, calculate_total_spend, identify_cost_savings
from lexspend.tools.anomaly_detection_tool import detect_anomalies


class TestFileReaderTool(unittest.TestCase):
    """Test file reader tool"""
    
    def setUp(self):
        """Create temporary test CSV file"""
        self.test_data = pd.DataFrame({
            'Position Title': ['Partner', 'Associate', 'Paralegal'],
            'Units': [2.0, 5.0, 8.0],
            'Bill Rate': [950.0, 450.0, 150.0],
            'Cost': [1900.0, 2250.0, 1200.0],
            'Line Item Description': ['Case strategy', 'Document review', 'Document review'],
            'Type of Case': ['Litigation', 'Litigation', 'Litigation']
        })
        
        # Create temporary CSV file
        self.temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False)
        self.test_data.to_csv(self.temp_file.name, index=False)
        self.temp_file.close()
    
    def tearDown(self):
        """Clean up temporary file"""
        if os.path.exists(self.temp_file.name):
            os.unlink(self.temp_file.name)
    
    def test_read_csv_file(self):
        """Test reading a CSV file"""
        result = read_file(self.temp_file.name)
        self.assertIn("File loaded successfully", result)
        self.assertIn("3 rows", result)
        self.assertIn("6 columns", result)
    
    def test_read_nonexistent_file(self):
        """Test reading a non-existent file"""
        result = read_file("/nonexistent/file.csv")
        self.assertIn("Error", result)
        self.assertIn("not found", result)
    
    def test_read_unsupported_file(self):
        """Test reading an unsupported file type"""
        result = read_file("test.txt")
        self.assertIn("Unsupported file type", result)


class TestDataAnalysisTool(unittest.TestCase):
    """Test data analysis tool"""
    
    def setUp(self):
        """Create temporary test CSV file"""
        self.test_data = pd.DataFrame({
            'Position Title': ['Partner', 'Associate', 'Paralegal'],
            'Units': [2.0, 5.0, 8.0],
            'Bill Rate': [950.0, 450.0, 150.0],
            'Cost': [1900.0, 2250.0, 1200.0],
            'Line Item Description': ['Case strategy', 'Document review', 'Document review'],
            'Type of Case': ['Litigation', 'Litigation', 'Litigation'],
            'Law Firm': ['Firm A', 'Firm A', 'Firm B']
        })
        
        # Create temporary CSV file
        self.temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False)
        self.test_data.to_csv(self.temp_file.name, index=False)
        self.temp_file.close()
    
    def tearDown(self):
        """Clean up temporary file"""
        if os.path.exists(self.temp_file.name):
            os.unlink(self.temp_file.name)
    
    def test_analyze_summary(self):
        """Test summary analysis"""
        result = analyze_data(self.temp_file.name, "summary")
        self.assertIn("3 rows", result)
        self.assertIn("7 columns", result)
    
    def test_analyze_total_spend(self):
        """Test total spend calculation"""
        result = analyze_data(self.temp_file.name, "total_spend")
        self.assertIn("Total Spend", result)
        self.assertIn("5350", result)  # 1900 + 2250 + 1200
    
    def test_analyze_top_firms(self):
        """Test top firms analysis"""
        result = analyze_data(self.temp_file.name, "top_firms")
        self.assertIn("Law Firm", result)
        self.assertIn("Firm A", result)
    
    def test_analyze_cost_savings(self):
        """Test cost savings identification"""
        result = identify_cost_savings(self.test_data)
        # Should identify partner doing document review if applicable
        self.assertIsInstance(result, str)


class TestAnomalyDetectionTool(unittest.TestCase):
    """Test anomaly detection tool"""
    
    def setUp(self):
        """Create temporary test CSV file with required columns"""
        self.test_data = pd.DataFrame({
            'Position Title': ['Partner', 'Associate', 'Paralegal', 'Partner'],
            'Units': [2.0, 5.0, 8.0, 4.0],
            'Bill Rate': [950.0, 450.0, 150.0, 950.0],
            'Cost': [1900.0, 2250.0, 1200.0, 3800.0],
            'Line Item Description': [
                'Case strategy meeting',
                'Document review and analysis',
                'Document review - first pass',
                'Document review for production'  # Partner doing review - anomaly
            ],
            'Type of Case': ['Litigation', 'Litigation', 'Litigation', 'Litigation']
        })
        
        # Create temporary CSV file
        self.temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False)
        self.test_data.to_csv(self.temp_file.name, index=False)
        self.temp_file.close()
    
    def tearDown(self):
        """Clean up temporary file"""
        if os.path.exists(self.temp_file.name):
            os.unlink(self.temp_file.name)
    
    @unittest.skip("GNN model training takes too long for unit tests")
    def test_detect_anomalies(self):
        """Test anomaly detection (skipped - requires model training)"""
        # This test is skipped because GNN training takes significant time
        # In a real scenario, you'd use a pre-trained model or mock the GNN components
        result = detect_anomalies(self.temp_file.name, train_model=False)
        self.assertIn("Anomaly detection", result)


if __name__ == '__main__':
    unittest.main()

