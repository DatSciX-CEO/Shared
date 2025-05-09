# Base classes for database connections
from abc import ABC, abstractmethod
import pandas as pd

class BaseConnection(ABC):
    """Abstract base class for database connections."""
    def __init__(self, connection_params):
        self.connection_params = connection_params
        self.connection = None

    @abstractmethod
    def connect(self):
        """Establish a connection to the database."""
        pass

    @abstractmethod
    def disconnect(self):
        """Close the database connection."""
        pass

    @abstractmethod
    def execute_query(self, query: str) -> pd.DataFrame:
        """Execute a SQL query and return results as a pandas DataFrame."""
        pass

    @abstractmethod
    def test_connection(self) -> bool:
        """Test if the connection is alive."""
        pass

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.disconnect()

class ConnectionError(Exception):
    """Custom exception for connection errors."""
    pass

