# Basic Visualization Wrappers for EDA using Streamlit's built-in charts and Matplotlib/Seaborn if needed
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

def plot_histogram(df: pd.DataFrame, column: str, bins: int = 10):
    """Plots a histogram for a specified column using Matplotlib and displays in Streamlit."""
    if not isinstance(df, pd.DataFrame) or column not in df.columns:
        st.error("Invalid DataFrame or column specified.")
        return
    if not pd.api.types.is_numeric_dtype(df[column]):
        st.warning(f"Column 	'{column}	' is not numeric. Cannot plot histogram.")
        return
    try:
        fig, ax = plt.subplots()
        # sns.histplot(df[column], kde=True, ax=ax, bins=bins) # Using seaborn for a slightly nicer look
        df[column].plot(kind=	'hist	', ax=ax, bins=bins, edgecolor=	'black	')
        ax.set_title(f"Histogram of {column}")
        ax.set_xlabel(column)
        ax.set_ylabel("Frequency")
        st.pyplot(fig)
    except Exception as e:
        st.error(f"Error plotting histogram for {column}: {e}")

def plot_boxplot(df: pd.DataFrame, column: str):
    """Plots a boxplot for a specified column using Matplotlib and displays in Streamlit."""
    if not isinstance(df, pd.DataFrame) or column not in df.columns:
        st.error("Invalid DataFrame or column specified.")
        return
    if not pd.api.types.is_numeric_dtype(df[column]):
        st.warning(f"Column 	'{column}	' is not numeric. Cannot plot boxplot.")
        return
    try:
        fig, ax = plt.subplots()
        # sns.boxplot(y=df[column], ax=ax)
        df[[column]].plot(kind=	'box	', ax=ax, vert=False) # Horizontal boxplot
        ax.set_title(f"Boxplot of {column}")
        # ax.set_ylabel(column) # Not needed for horizontal
        st.pyplot(fig)
    except Exception as e:
        st.error(f"Error plotting boxplot for {column}: {e}")

def plot_scatterplot(df: pd.DataFrame, x_column: str, y_column: str):
    """Plots a scatterplot for two specified columns using Matplotlib and displays in Streamlit."""
    if not isinstance(df, pd.DataFrame) or x_column not in df.columns or y_column not in df.columns:
        st.error("Invalid DataFrame or columns specified.")
        return
    if not pd.api.types.is_numeric_dtype(df[x_column]) or not pd.api.types.is_numeric_dtype(df[y_column]):
        st.warning(f"Both 	'{x_column}	' and 	'{y_column}	' must be numeric to plot a scatterplot.")
        return
    try:
        fig, ax = plt.subplots()
        # sns.scatterplot(x=df[x_column], y=df[y_column], ax=ax)
        df.plot(kind=	'scatter	', x=x_column, y=y_column, ax=ax)
        ax.set_title(f"Scatterplot of {y_column} vs {x_column}")
        ax.set_xlabel(x_column)
        ax.set_ylabel(y_column)
        st.pyplot(fig)
    except Exception as e:
        st.error(f"Error plotting scatterplot for {x_column} vs {y_column}: {e}")

def plot_correlation_heatmap(df: pd.DataFrame, method: str = 	"pearson	"):
    """Plots a correlation heatmap for numerical columns in a DataFrame."""
    if not isinstance(df, pd.DataFrame):
        st.error("Input must be a pandas DataFrame.")
        return
    try:
        numerical_df = df.select_dtypes(include=np.number)
        if numerical_df.empty:
            st.warning("No numerical columns found for correlation heatmap.")
            return
        corr_matrix = numerical_df.corr(method=method)
        fig, ax = plt.subplots(figsize=(10, 8))
        sns.heatmap(corr_matrix, annot=True, fmt=".2f", cmap=	'coolwarm	', ax=ax)
        ax.set_title(f"Correlation Heatmap (Method: {method.capitalize()})")
        st.pyplot(fig)
    except Exception as e:
        st.error(f"Error plotting correlation heatmap: {e}")


# Add more visualization functions as needed, e.g., bar charts for categorical data, line plots for time series

def plot_barchart(df: pd.DataFrame, column: str):
    """Plots a bar chart for a specified categorical column."""
    if not isinstance(df, pd.DataFrame) or column not in df.columns:
        st.error("Invalid DataFrame or column specified.")
        return
    if pd.api.types.is_numeric_dtype(df[column]) and df[column].nunique() > 20: # Heuristic for too many unique numeric values
        st.warning(f"Column 	'{column}	' is numeric with many unique values. Consider binning or using a histogram.")
        # return # Or allow it if user insists
    try:
        counts = df[column].value_counts()
        if counts.empty:
            st.warning(f"No data to plot for column 	'{column}	'.")
            return
        
        fig, ax = plt.subplots()
        # counts.plot(kind=	'bar	', ax=ax)
        sns.barplot(x=counts.index, y=counts.values, ax=ax)
        ax.set_title(f"Bar Chart of {column}")
        ax.set_xlabel(column)
        ax.set_ylabel("Count")
        plt.xticks(rotation=45, ha=	'right	')
        plt.tight_layout()
        st.pyplot(fig)
    except Exception as e:
        st.error(f"Error plotting bar chart for {column}: {e}")

# Placeholder for using Streamlit's native charts if preferred for simplicity
# e.g., st.bar_chart, st.line_chart, st.area_chart

