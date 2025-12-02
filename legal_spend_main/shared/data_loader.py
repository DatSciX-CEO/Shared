"""
Universal Data Loader
Reusable data loading functions for CSV, Parquet, and SQL Server
Can be imported by other applications for integration
"""
import pandas as pd
from typing import Tuple, Optional, Dict, Any
import sys
import os

# Import data utilities
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from data.sql_connector import SQLServerConnector
from data.data_validator import validate_legal_spend_data


class UniversalDataLoader:
    """
    Universal data loader supporting multiple data sources.
    Handles CSV, Parquet, and SQL Server data with validation.
    """
    
    def __init__(self):
        """Initialize the data loader."""
        self.data = None
        self.source_type = None
        self.source_path = None
    
    def load_csv(self, file_path: str, validate: bool = True) -> Tuple[bool, str, Optional[pd.DataFrame]]:
        """
        Load data from CSV file.
        
        Args:
            file_path: Path to CSV file
            validate: Whether to validate data (default: True)
            
        Returns:
            Tuple of (success, message, dataframe)
        """
        try:
            df = pd.read_csv(file_path)
            
            if validate:
                success, message, df = validate_legal_spend_data(df)
                if not success:
                    return False, message, None
            
            self.data = df
            self.source_type = "csv"
            self.source_path = file_path
            
            return True, f"✅ CSV loaded: {len(df)} rows", df
            
        except Exception as e:
            return False, f"❌ Error loading CSV: {str(e)}", None
    
    def load_parquet(self, file_path: str, validate: bool = True) -> Tuple[bool, str, Optional[pd.DataFrame]]:
        """
        Load data from Parquet file.
        
        Args:
            file_path: Path to Parquet file
            validate: Whether to validate data (default: True)
            
        Returns:
            Tuple of (success, message, dataframe)
        """
        try:
            df = pd.read_parquet(file_path)
            
            if validate:
                success, message, df = validate_legal_spend_data(df)
                if not success:
                    return False, message, None
            
            self.data = df
            self.source_type = "parquet"
            self.source_path = file_path
            
            return True, f"✅ Parquet loaded: {len(df)} rows", df
            
        except Exception as e:
            return False, f"❌ Error loading Parquet: {str(e)}", None
    
    def load_sql_server(
        self,
        query: Optional[str] = None,
        table_name: Optional[str] = None,
        config: Optional[Dict[str, Any]] = None,
        validate: bool = True
    ) -> Tuple[bool, str, Optional[pd.DataFrame]]:
        """
        Load data from SQL Server.
        
        Args:
            query: SQL query to execute (optional)
            table_name: Table name to read (optional)
            config: SQL Server configuration dict (optional)
            validate: Whether to validate data (default: True)
            
        Returns:
            Tuple of (success, message, dataframe)
        """
        try:
            if not query and not table_name:
                return False, "❌ Must provide either query or table_name", None
            
            connector = SQLServerConnector(config)
            
            if not connector.connect():
                return False, "❌ Failed to connect to SQL Server", None
            
            if query:
                df = connector.execute_query(query)
            else:
                df = connector.execute_query(f"SELECT * FROM {table_name}")
            
            connector.disconnect()
            
            if validate:
                success, message, df = validate_legal_spend_data(df)
                if not success:
                    return False, message, None
            
            self.data = df
            self.source_type = "sql"
            self.source_path = f"SQL: {table_name or 'custom query'}"
            
            return True, f"✅ SQL Server data loaded: {len(df)} rows", df
            
        except Exception as e:
            return False, f"❌ Error loading SQL Server data: {str(e)}", None
    
    def get_summary(self) -> Dict[str, Any]:
        """
        Get summary of loaded data.
        
        Returns:
            Dict with data summary information
        """
        if self.data is None:
            return {"loaded": False, "message": "No data loaded"}
        
        return {
            "loaded": True,
            "source_type": self.source_type,
            "source_path": self.source_path,
            "rows": len(self.data),
            "columns": len(self.data.columns),
            "column_names": self.data.columns.tolist(),
            "total_spend": self.data['amount'].sum() if 'amount' in self.data.columns else None,
            "date_range": {
                "min": self.data['date'].min() if 'date' in self.data.columns else None,
                "max": self.data['date'].max() if 'date' in self.data.columns else None,
            } if 'date' in self.data.columns else None,
        }
    
    def get_data(self) -> Optional[pd.DataFrame]:
        """
        Get the loaded DataFrame.
        
        Returns:
            pandas DataFrame or None if no data loaded
        """
        return self.data


