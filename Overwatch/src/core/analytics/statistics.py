# Basic Statistics Functions for EDA
import pandas as pd
import numpy as np

def get_descriptive_stats(df: pd.DataFrame) -> pd.DataFrame | None:
    """Calculates descriptive statistics for a DataFrame."""
    if not isinstance(df, pd.DataFrame):
        # st.error("Input must be a pandas DataFrame.")
        return None
    try:
        return df.describe(include=	"all	")
    except Exception as e:
        # st.error(f"Error calculating descriptive statistics: {e}")
        return None

def get_data_types(df: pd.DataFrame) -> pd.DataFrame | None:
    """Gets the data types of columns in a DataFrame."""
    if not isinstance(df, pd.DataFrame):
        return None
    try:
        return df.dtypes.to_frame(	"Data Type	")
    except Exception as e:
        return None

def get_missing_values(df: pd.DataFrame) -> pd.DataFrame | None:
    """Calculates missing values for each column in a DataFrame."""
    if not isinstance(df, pd.DataFrame):
        return None
    try:
        missing_counts = df.isnull().sum()
        missing_percentages = (df.isnull().sum() / len(df)) * 100
        missing_df = pd.DataFrame({
            	"Missing Values	": missing_counts,
            	"% Missing	": missing_percentages
        })
        return missing_df[missing_df[	"Missing Values	"] > 0].sort_values(by=	"% Missing	", ascending=False)
    except Exception as e:
        return None

def get_unique_value_counts(df: pd.DataFrame, column: str) -> pd.DataFrame | None:
    """Gets unique value counts for a specific column."""
    if not isinstance(df, pd.DataFrame) or column not in df.columns:
        return None
    try:
        return df[column].value_counts().to_frame(	"Count	")
    except Exception as e:
        return None


# Add more statistics functions as needed, e.g., correlation, skewness, kurtosis

def get_correlation_matrix(df: pd.DataFrame, method: str = 	"pearson	") -> pd.DataFrame | None:
    """Calculates the correlation matrix for numerical columns in a DataFrame."""
    if not isinstance(df, pd.DataFrame):
        return None
    try:
        numerical_df = df.select_dtypes(include=np.number)
        if numerical_df.empty:
            # st.warning("No numerical columns found for correlation analysis.")
            return None
        return numerical_df.corr(method=method)
    except Exception as e:
        # st.error(f"Error calculating correlation matrix: {e}")
        return None

