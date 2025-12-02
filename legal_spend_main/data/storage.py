"""
SQLite Storage for Analysis Results
Stores analysis sessions and results for later retrieval
"""
import sqlite3
import pandas as pd
from typing import Optional, List, Dict, Any
from datetime import datetime
import sys
import os

# Import config
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from config import RESULTS_DB_PATH


class ResultsStorage:
    """Manages SQLite storage for analysis results."""
    
    def __init__(self, db_path: str = RESULTS_DB_PATH):
        """
        Initialize storage.
        
        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        self._init_database()
    
    def _init_database(self):
        """Initialize database schema."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create analysis sessions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS analysis_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT UNIQUE,
                data_source TEXT,
                data_source_type TEXT,
                analysis_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                total_records INTEGER,
                total_spend REAL,
                notes TEXT
            )
        """)
        
        # Create analysis results table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS analysis_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT,
                result_type TEXT,
                result_data TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (session_id) REFERENCES analysis_sessions(session_id)
            )
        """)
        
        # Create agent interactions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS agent_interactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT,
                agent_name TEXT,
                user_query TEXT,
                agent_response TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (session_id) REFERENCES analysis_sessions(session_id)
            )
        """)
        
        conn.commit()
        conn.close()
    
    def create_session(self, session_id: str, data_source: str, 
                      data_source_type: str, total_records: int,
                      total_spend: float = 0.0, notes: str = "") -> bool:
        """
        Create a new analysis session.
        
        Args:
            session_id: Unique session identifier
            data_source: Path or connection string to data source
            data_source_type: Type of data source (csv, parquet, sql)
            total_records: Number of records in dataset
            total_spend: Total spend amount
            notes: Optional notes
            
        Returns:
            True if successful
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO analysis_sessions 
                (session_id, data_source, data_source_type, total_records, total_spend, notes)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (session_id, data_source, data_source_type, total_records, total_spend, notes))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error creating session: {e}")
            return False
    
    def save_result(self, session_id: str, result_type: str, result_data: str) -> bool:
        """
        Save an analysis result.
        
        Args:
            session_id: Session identifier
            result_type: Type of result (e.g., 'firm_totals', 'anomalies', 'forecast')
            result_data: Result data as JSON string
            
        Returns:
            True if successful
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO analysis_results (session_id, result_type, result_data)
                VALUES (?, ?, ?)
            """, (session_id, result_type, result_data))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error saving result: {e}")
            return False
    
    def log_interaction(self, session_id: str, agent_name: str, 
                       user_query: str, agent_response: str) -> bool:
        """
        Log an agent interaction.
        
        Args:
            session_id: Session identifier
            agent_name: Name of the agent
            user_query: User's query
            agent_response: Agent's response
            
        Returns:
            True if successful
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO agent_interactions 
                (session_id, agent_name, user_query, agent_response)
                VALUES (?, ?, ?, ?)
            """, (session_id, agent_name, user_query, agent_response))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error logging interaction: {e}")
            return False
    
    def get_recent_sessions(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get recent analysis sessions.
        
        Args:
            limit: Maximum number of sessions to return
            
        Returns:
            List of session dictionaries
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT session_id, data_source, data_source_type, 
                   analysis_date, total_records, total_spend
            FROM analysis_sessions
            ORDER BY analysis_date DESC
            LIMIT ?
        """, (limit,))
        
        columns = [desc[0] for desc in cursor.description]
        results = [dict(zip(columns, row)) for row in cursor.fetchall()]
        
        conn.close()
        return results
    
    def get_session_results(self, session_id: str) -> List[Dict[str, Any]]:
        """
        Get all results for a session.
        
        Args:
            session_id: Session identifier
            
        Returns:
            List of result dictionaries
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT result_type, result_data, created_at
            FROM analysis_results
            WHERE session_id = ?
            ORDER BY created_at DESC
        """, (session_id,))
        
        columns = [desc[0] for desc in cursor.description]
        results = [dict(zip(columns, row)) for row in cursor.fetchall()]
        
        conn.close()
        return results


