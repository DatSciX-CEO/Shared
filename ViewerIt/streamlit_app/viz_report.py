"""
ViewerIt Streamlit Visualization Dashboard
Embedded visualization for data comparison results
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
import sys

# Configure Streamlit for embedding
st.set_page_config(
    page_title="ViewerIt Visualizer",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Custom CSS for Cyberpunk theme
st.markdown("""
<style>
    /* Main background */
    .stApp {
        background-color: #0a0a0f;
        color: #e0e0e0;
    }
    
    /* Headers */
    h1, h2, h3, h4, h5, h6 {
        color: #00f5ff !important;
        font-family: 'Orbitron', monospace !important;
        text-shadow: 0 0 10px rgba(0, 245, 255, 0.5);
    }
    
    /* Text */
    p, span, label {
        color: #e0e0e0;
        font-family: 'Rajdhani', sans-serif;
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: #12121a;
        border-right: 1px solid #2a2a3a;
    }
    
    /* Metrics */
    [data-testid="stMetricValue"] {
        color: #00f5ff !important;
        font-family: 'Orbitron', monospace !important;
        text-shadow: 0 0 10px rgba(0, 245, 255, 0.5);
    }
    
    [data-testid="stMetricLabel"] {
        color: #888899 !important;
    }
    
    /* Cards */
    [data-testid="stExpander"] {
        background-color: #12121a;
        border: 1px solid #2a2a3a;
        border-radius: 8px;
    }
    
    /* Dataframes */
    .stDataFrame {
        background-color: #12121a;
        border: 1px solid #2a2a3a;
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: transparent;
    }
    
    .stTabs [data-baseweb="tab"] {
        background-color: #12121a;
        border: 1px solid #2a2a3a;
        color: #888899;
        border-radius: 8px;
        padding: 10px 20px;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: #00f5ff20;
        border-color: #00f5ff;
        color: #00f5ff;
    }
    
    /* Buttons */
    .stButton button {
        background: linear-gradient(90deg, #00f5ff, #ff00ff);
        color: #0a0a0f;
        border: none;
        font-weight: bold;
        text-transform: uppercase;
        letter-spacing: 2px;
    }
    
    .stButton button:hover {
        box-shadow: 0 0 20px rgba(0, 245, 255, 0.5);
    }
    
    /* Select boxes */
    .stSelectbox [data-baseweb="select"] {
        background-color: #12121a;
        border-color: #2a2a3a;
    }
    
    /* Progress bar */
    .stProgress > div > div {
        background: linear-gradient(90deg, #00f5ff, #ff00ff);
    }
    
    /* Hide Streamlit branding for embedding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Plotly chart backgrounds */
    .js-plotly-plot .plotly .bg {
        fill: #0a0a0f !important;
    }
</style>
""", unsafe_allow_html=True)

# Load fonts
st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=Orbitron:wght@400;500;600;700&family=Rajdhani:wght@400;500;600;700&display=swap" rel="stylesheet">
""", unsafe_allow_html=True)


def load_data(session_id: str, filename: str) -> pd.DataFrame:
    """Load data from the backend uploads directory."""
    # Path to backend uploads
    backend_path = Path(__file__).parent.parent / "backend" / "uploads" / session_id / filename
    
    if not backend_path.exists():
        st.error(f"File not found: {filename}")
        return pd.DataFrame()
    
    ext = backend_path.suffix.lower()
    
    try:
        if ext == ".csv":
            return pd.read_csv(backend_path)
        elif ext in (".xlsx", ".xls"):
            return pd.read_excel(backend_path)
        elif ext == ".parquet":
            return pd.read_parquet(backend_path)
        elif ext == ".json":
            return pd.read_json(backend_path)
        else:
            # Try CSV with different delimiters
            for delimiter in ["\x14", "|", "\t", ","]:
                try:
                    df = pd.read_csv(backend_path, delimiter=delimiter)
                    if len(df.columns) > 1:
                        return df
                except:
                    continue
            return pd.read_csv(backend_path)
    except Exception as e:
        st.error(f"Error loading {filename}: {e}")
        return pd.DataFrame()


def create_plotly_theme():
    """Create consistent Plotly theme for cyberpunk aesthetic."""
    return dict(
        template="plotly_dark",
        paper_bgcolor="#0a0a0f",
        plot_bgcolor="#0a0a0f",
        font=dict(family="Rajdhani, sans-serif", color="#e0e0e0"),
        colorway=["#00f5ff", "#ff00ff", "#f0ff00", "#39ff14", "#ff6600"],
    )


def main():
    # Get query parameters
    query_params = st.query_params
    session_id = query_params.get("session_id", "")
    file1 = query_params.get("file1", "")
    file2 = query_params.get("file2", "")
    
    st.title("📊 Data Visualization Dashboard")
    
    if not session_id or not file1 or not file2:
        st.warning("No data loaded. Please run a comparison from the main application.")
        st.info("This dashboard is designed to be embedded in the ViewerIt React application.")
        return
    
    # Load dataframes
    with st.spinner("Loading data..."):
        df1 = load_data(session_id, file1)
        df2 = load_data(session_id, file2)
    
    if df1.empty or df2.empty:
        st.error("Could not load one or both files.")
        return
    
    # Create tabs
    tab1, tab2, tab3, tab4 = st.tabs(["📈 Overview", "🔍 Column Analysis", "📊 Distribution", "🎯 Differences"])
    
    with tab1:
        st.subheader("Dataset Overview")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown(f"### {file1}")
            c1, c2, c3 = st.columns(3)
            c1.metric("Rows", f"{len(df1):,}")
            c2.metric("Columns", len(df1.columns))
            c3.metric("Memory", f"{df1.memory_usage(deep=True).sum() / 1024 / 1024:.2f} MB")
            
            st.markdown("**Data Types:**")
            dtype_counts = df1.dtypes.value_counts()
            fig = px.pie(
                values=dtype_counts.values, 
                names=[str(t) for t in dtype_counts.index],
                hole=0.4,
            )
            fig.update_layout(**create_plotly_theme())
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.markdown(f"### {file2}")
            c1, c2, c3 = st.columns(3)
            c1.metric("Rows", f"{len(df2):,}")
            c2.metric("Columns", len(df2.columns))
            c3.metric("Memory", f"{df2.memory_usage(deep=True).sum() / 1024 / 1024:.2f} MB")
            
            st.markdown("**Data Types:**")
            dtype_counts = df2.dtypes.value_counts()
            fig = px.pie(
                values=dtype_counts.values, 
                names=[str(t) for t in dtype_counts.index],
                hole=0.4,
            )
            fig.update_layout(**create_plotly_theme())
            st.plotly_chart(fig, use_container_width=True)
        
        # Column comparison
        st.subheader("Column Comparison")
        cols1 = set(df1.columns)
        cols2 = set(df2.columns)
        common = cols1 & cols2
        only_in_1 = cols1 - cols2
        only_in_2 = cols2 - cols1
        
        c1, c2, c3 = st.columns(3)
        c1.metric("Common Columns", len(common))
        c2.metric(f"Only in {file1}", len(only_in_1))
        c3.metric(f"Only in {file2}", len(only_in_2))
        
        if only_in_1:
            with st.expander(f"Columns only in {file1}"):
                st.write(", ".join(sorted(only_in_1)))
        
        if only_in_2:
            with st.expander(f"Columns only in {file2}"):
                st.write(", ".join(sorted(only_in_2)))
    
    with tab2:
        st.subheader("Column-by-Column Analysis")
        
        # Select column
        common_cols = sorted(list(cols1 & cols2))
        if common_cols:
            selected_col = st.selectbox("Select a column to analyze:", common_cols)
            
            if selected_col:
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown(f"**{file1}**")
                    st.write(f"Unique values: {df1[selected_col].nunique()}")
                    st.write(f"Null values: {df1[selected_col].isnull().sum()}")
                    
                    if df1[selected_col].dtype in ['int64', 'float64']:
                        st.dataframe(df1[selected_col].describe())
                    else:
                        st.write("Top values:")
                        st.dataframe(df1[selected_col].value_counts().head(10))
                
                with col2:
                    st.markdown(f"**{file2}**")
                    st.write(f"Unique values: {df2[selected_col].nunique()}")
                    st.write(f"Null values: {df2[selected_col].isnull().sum()}")
                    
                    if df2[selected_col].dtype in ['int64', 'float64']:
                        st.dataframe(df2[selected_col].describe())
                    else:
                        st.write("Top values:")
                        st.dataframe(df2[selected_col].value_counts().head(10))
        else:
            st.warning("No common columns found between the datasets.")
    
    with tab3:
        st.subheader("Value Distributions")
        
        numeric_cols_1 = df1.select_dtypes(include=['number']).columns.tolist()
        numeric_cols_2 = df2.select_dtypes(include=['number']).columns.tolist()
        common_numeric = list(set(numeric_cols_1) & set(numeric_cols_2))
        
        if common_numeric:
            dist_col = st.selectbox("Select numeric column:", common_numeric)
            
            if dist_col:
                fig = go.Figure()
                fig.add_trace(go.Histogram(
                    x=df1[dist_col], 
                    name=file1, 
                    opacity=0.7,
                    marker_color="#00f5ff"
                ))
                fig.add_trace(go.Histogram(
                    x=df2[dist_col], 
                    name=file2, 
                    opacity=0.7,
                    marker_color="#ff00ff"
                ))
                fig.update_layout(
                    barmode='overlay',
                    title=f"Distribution of {dist_col}",
                    **create_plotly_theme()
                )
                st.plotly_chart(fig, use_container_width=True)
                
                # Box plot
                fig2 = go.Figure()
                fig2.add_trace(go.Box(y=df1[dist_col], name=file1, marker_color="#00f5ff"))
                fig2.add_trace(go.Box(y=df2[dist_col], name=file2, marker_color="#ff00ff"))
                fig2.update_layout(
                    title=f"Box Plot: {dist_col}",
                    **create_plotly_theme()
                )
                st.plotly_chart(fig2, use_container_width=True)
        else:
            st.info("No common numeric columns found for distribution analysis.")
    
    with tab4:
        st.subheader("Data Differences")
        
        # Null value comparison
        st.markdown("### Null Value Comparison")
        null_data = []
        for col in common:
            null_data.append({
                "Column": col,
                f"Nulls in {file1}": df1[col].isnull().sum(),
                f"Nulls in {file2}": df2[col].isnull().sum(),
                "Difference": abs(df1[col].isnull().sum() - df2[col].isnull().sum())
            })
        
        null_df = pd.DataFrame(null_data)
        null_df = null_df[null_df["Difference"] > 0].sort_values("Difference", ascending=False)
        
        if not null_df.empty:
            fig = px.bar(
                null_df.head(20),
                x="Column",
                y=[f"Nulls in {file1}", f"Nulls in {file2}"],
                barmode="group",
                title="Columns with Different Null Counts"
            )
            fig.update_layout(**create_plotly_theme())
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.success("No difference in null value counts between datasets.")
        
        # Row count comparison
        st.markdown("### Summary Statistics")
        summary_data = {
            "Metric": ["Total Rows", "Total Columns", "Common Columns", "Unique Columns"],
            file1: [len(df1), len(df1.columns), len(common), len(only_in_1)],
            file2: [len(df2), len(df2.columns), len(common), len(only_in_2)],
        }
        summary_df = pd.DataFrame(summary_data)
        st.dataframe(summary_df, use_container_width=True, hide_index=True)


if __name__ == "__main__":
    main()

