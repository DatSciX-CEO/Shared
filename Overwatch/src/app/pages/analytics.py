# Page for Analytics & EDA
import streamlit as st
import pandas as pd
from src.core.analytics import statistics
from src.core.analytics import visualization

# Helper to get a DataFrame from session state (e.g., loaded from DB or uploaded)
def get_active_dataframe(data_source_name: str = "current_df") -> pd.DataFrame | None:
    return st.session_state.get(data_source_name)

# Helper to set a DataFrame in session state
def set_active_dataframe(df: pd.DataFrame, data_source_name: str = "current_df"):
    st.session_state[data_source_name] = df

def app():
    st.title("Analytics & Exploratory Data Analysis (EDA)")

    # --- Data Source Selection --- 
    st.subheader("1. Select or Upload Data")
    
    # Option 1: Use data from an active DB connection (simplified)
    # This would typically involve selecting a table after connecting to a DB
    # For now, let's assume a DataFrame might be in session_state from the DB page or direct upload
    active_connections = st.session_state.get("active_connections", {})
    db_options = list(active_connections.keys())
    
    # Option 2: Upload a CSV/Excel file
    uploaded_file = st.file_uploader("Upload a CSV or Excel file", type=["csv", "xlsx"])

    df_to_analyze = None
    df_source_name = "" # To display the source of the DataFrame

    if uploaded_file is not None:
        try:
            if uploaded_file.name.endswith(".csv"):
                df_upload = pd.read_csv(uploaded_file)
            else:
                df_upload = pd.read_excel(uploaded_file)
            set_active_dataframe(df_upload, "uploaded_df")
            df_to_analyze = df_upload
            df_source_name = f"Uploaded File: {uploaded_file.name}"
            st.success(f"Successfully loaded {uploaded_file.name}")
        except Exception as e:
            st.error(f"Error loading file: {e}")
            return
    else:
        # Allow selecting a previously loaded/queried DataFrame (e.g., from DB page)
        # This part needs more robust handling of how DataFrames are passed between pages
        # For now, we just check if a "last_query_result" exists in session state
        if "last_query_result" in st.session_state and isinstance(st.session_state.last_query_result, pd.DataFrame):
            if st.button("Use Last Query Result for Analysis"):
                df_to_analyze = st.session_state.last_query_result
                set_active_dataframe(df_to_analyze, "current_eda_df") # Use a specific key for EDA df
                df_source_name = "Last Database Query Result"
        elif "current_eda_df" in st.session_state:
             df_to_analyze = st.session_state.current_eda_df
             df_source_name = "Previously Loaded Data for EDA"

    if df_to_analyze is None:
        st.info("Please upload a file or ensure a DataFrame is available from a database query to begin analysis.")
        return

    st.markdown(f"**Analyzing Data Source:** `{df_source_name}`")
    st.dataframe(df_to_analyze.head())

    # --- EDA Operations --- 
    st.markdown("---_---")
    st.subheader("2. Exploratory Data Analysis")

    eda_operations = [
        "Show Descriptive Statistics", 
        "Show Data Types", 
        "Show Missing Values", 
        "Show Correlation Matrix",
        "Plot Histogram", 
        "Plot Boxplot", 
        "Plot Scatterplot",
        "Plot Bar Chart"
    ]
    selected_operation = st.selectbox("Choose an EDA operation:", options=eda_operations)

    if selected_operation == "Show Descriptive Statistics":
        stats_df = statistics.get_descriptive_stats(df_to_analyze)
        if stats_df is not None:
            st.write("Descriptive Statistics:")
            st.dataframe(stats_df)
        else:
            st.error("Could not generate descriptive statistics.")

    elif selected_operation == "Show Data Types":
        types_df = statistics.get_data_types(df_to_analyze)
        if types_df is not None:
            st.write("Data Types:")
            st.dataframe(types_df)
        else:
            st.error("Could not retrieve data types.")

    elif selected_operation == "Show Missing Values":
        missing_df = statistics.get_missing_values(df_to_analyze)
        if missing_df is not None and not missing_df.empty:
            st.write("Missing Values:")
            st.dataframe(missing_df)
        elif missing_df is not None and missing_df.empty:
            st.success("No missing values found.")
        else:
            st.error("Could not calculate missing values.")
            
    elif selected_operation == "Show Correlation Matrix":
        st.write("Correlation Matrix (Pearson):")
        corr_df = statistics.get_correlation_matrix(df_to_analyze)
        if corr_df is not None:
            st.dataframe(corr_df)
            visualization.plot_correlation_heatmap(df_to_analyze)
        else:
            st.warning("Could not generate correlation matrix. Ensure there are numerical columns.")

    # Visualization plots
    elif selected_operation in ["Plot Histogram", "Plot Boxplot", "Plot Scatterplot", "Plot Bar Chart"]:
        columns = df_to_analyze.columns.tolist()
        if not columns:
            st.warning("No columns found in the DataFrame.")
            return

        if selected_operation == "Plot Histogram":
            hist_col = st.selectbox("Select column for Histogram:", options=columns, key="hist_col")
            if hist_col:
                bins = st.slider("Number of bins:", min_value=5, max_value=100, value=20, key="hist_bins")
                visualization.plot_histogram(df_to_analyze, hist_col, bins)
        
        elif selected_operation == "Plot Boxplot":
            box_col = st.selectbox("Select column for Boxplot:", options=columns, key="box_col")
            if box_col:
                visualization.plot_boxplot(df_to_analyze, box_col)

        elif selected_operation == "Plot Scatterplot":
            scatter_x = st.selectbox("Select X-axis column:", options=columns, key="scatter_x")
            scatter_y = st.selectbox("Select Y-axis column:", options=columns, key="scatter_y")
            if scatter_x and scatter_y:
                visualization.plot_scatterplot(df_to_analyze, scatter_x, scatter_y)
        
        elif selected_operation == "Plot Bar Chart":
            bar_col = st.selectbox("Select column for Bar Chart (Categorical Recommended):", options=columns, key="bar_col")
            if bar_col:
                visualization.plot_barchart(df_to_analyze, bar_col)

# Add a placeholder for session state if it doesn't exist, for direct running of this page
if "active_connections" not in st.session_state:
    st.session_state.active_connections = {}
if "last_query_result" not in st.session_state:
    st.session_state.last_query_result = None # Or an empty DataFrame
if "current_eda_df" not in st.session_state:
    st.session_state.current_eda_df = None

