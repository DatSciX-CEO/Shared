"""
SQLite storage for analysis results
"""
import sqlite3
import pandas as pd
from typing import Optional, List, Dict, Any
import logging
from datetime import datetime

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from config import DB_PATH

logger = logging.getLogger(__name__)


class ResultsStorage:
    """Manages SQLite storage for analysis results."""
    
    def __init__(self, db_path: str = DB_PATH):
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
        
        # Create results table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS analysis_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                file_path TEXT,
                analysis_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                line_item_index INTEGER,
                review_score REAL,
                original_data TEXT,
                metadata TEXT
            )
        """)
        
        # Create analysis sessions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS analysis_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                file_path TEXT,
                analysis_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                total_items INTEGER,
                high_risk_items INTEGER,
                notes TEXT
            )
        """)
        
        conn.commit()
        conn.close()
        logger.info(f"Database initialized at {self.db_path}")
    
    def save_results(self, file_path: str, df: pd.DataFrame, scores: pd.Series, 
                    metadata: Optional[Dict[str, Any]] = None) -> int:
        """
        Save analysis results to database.
        
        Args:
            file_path: Path to source file
            df: Original DataFrame
            scores: Series of anomaly scores (indexed by DataFrame index)
            metadata: Optional metadata dictionary
            
        Returns:
            Session ID
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create analysis session
        high_risk = (scores > 0.7).sum() if len(scores) > 0 else 0
        cursor.execute("""
            INSERT INTO analysis_sessions (file_path, total_items, high_risk_items, notes)
            VALUES (?, ?, ?, ?)
        """, (file_path, len(df), high_risk, str(metadata) if metadata else None))
        
        session_id = cursor.lastrowid
        
        # Insert results
        for idx, score in scores.items():
            # Get original row data as JSON string
            row_data = df.loc[idx].to_dict()
            import json
            original_data = json.dumps(row_data)
            
            cursor.execute("""
                INSERT INTO analysis_results 
                (file_path, line_item_index, review_score, original_data, metadata)
                VALUES (?, ?, ?, ?, ?)
            """, (file_path, int(idx), float(score), original_data, 
                  json.dumps(metadata) if metadata else None))
        
        conn.commit()
        conn.close()
        logger.info(f"Saved {len(scores)} results to database (session {session_id})")
        return session_id
    
    def load_results(self, session_id: Optional[int] = None) -> pd.DataFrame:
        """
        Load analysis results from database.
        
        Args:
            session_id: Optional session ID to load specific session
            
        Returns:
            DataFrame with results
        """
        conn = sqlite3.connect(self.db_path)
        
        if session_id:
            query = """
                SELECT * FROM analysis_results 
                WHERE file_path IN (
                    SELECT file_path FROM analysis_sessions WHERE id = ?
                )
                ORDER BY review_score DESC
            """
            df = pd.read_sql_query(query, conn, params=(session_id,))
        else:
            # Load most recent session
            query = """
                SELECT r.* FROM analysis_results r
                JOIN analysis_sessions s ON r.file_path = s.file_path
                WHERE s.id = (SELECT MAX(id) FROM analysis_sessions)
                ORDER BY r.review_score DESC
            """
            df = pd.read_sql_query(query, conn)
        
        conn.close()
        return df
    
    def get_recent_sessions(self, limit: int = 10) -> pd.DataFrame:
        """
        Get recent analysis sessions.
        
        Args:
            limit: Maximum number of sessions to return
            
        Returns:
            DataFrame with session information
        """
        conn = sqlite3.connect(self.db_path)
        query = """
            SELECT * FROM analysis_sessions 
            ORDER BY analysis_date DESC 
            LIMIT ?
        """
        df = pd.read_sql_query(query, conn, params=(limit,))
        conn.close()
        return df

