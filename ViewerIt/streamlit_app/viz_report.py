"""
ViewerIt Streamlit Visualization Dashboard
Enhanced with multi-file comparison, schema analysis, and quality checking
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from pathlib import Path

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
        elif ext == ".tsv":
            return pd.read_csv(backend_path, sep='\t')
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


def render_overview_tab(dataframes: dict[str, pd.DataFrame]):
    """Render dataset overview tab."""
    st.subheader("Dataset Overview")
    
    cols = st.columns(len(dataframes))
    
    for idx, (filename, df) in enumerate(dataframes.items()):
        with cols[idx]:
            st.markdown(f"### {filename}")
            c1, c2, c3 = st.columns(3)
            c1.metric("Rows", f"{len(df):,}")
            c2.metric("Columns", len(df.columns))
            c3.metric("Memory", f"{df.memory_usage(deep=True).sum() / 1024 / 1024:.2f} MB")
            
            st.markdown("**Data Types:**")
            dtype_counts = df.dtypes.value_counts()
            fig = px.pie(
                values=dtype_counts.values, 
                names=[str(t) for t in dtype_counts.index],
                hole=0.4,
            )
            fig.update_layout(**create_plotly_theme(), showlegend=True, height=200)
            st.plotly_chart(fig, use_container_width=True)
    
    # Column comparison
    st.subheader("Column Comparison Across Files")
    
    all_cols = set()
    col_presence = {}
    for filename, df in dataframes.items():
        cols_set = set(df.columns)
        all_cols.update(cols_set)
        col_presence[filename] = cols_set
    
    # Build presence matrix
    presence_data = []
    for col in sorted(all_cols):
        row = {"Column": col}
        for filename in dataframes.keys():
            row[filename] = "✓" if col in col_presence[filename] else "✗"
        presence_data.append(row)
    
    presence_df = pd.DataFrame(presence_data)
    st.dataframe(presence_df, use_container_width=True, hide_index=True)


def render_column_analysis_tab(dataframes: dict[str, pd.DataFrame]):
    """Render column-by-column analysis tab."""
    st.subheader("Column-by-Column Analysis")
    
    # Find common columns
    common_cols = set(list(dataframes.values())[0].columns)
    for df in dataframes.values():
        common_cols &= set(df.columns)
    
    common_cols = sorted(list(common_cols))
    
    if common_cols:
        selected_col = st.selectbox("Select a column to analyze:", common_cols)
        
        if selected_col:
            cols = st.columns(len(dataframes))
            
            for idx, (filename, df) in enumerate(dataframes.items()):
                with cols[idx]:
                    st.markdown(f"**{filename}**")
                    st.write(f"Unique values: {df[selected_col].nunique()}")
                    st.write(f"Null values: {df[selected_col].isnull().sum()}")
                    
                    if df[selected_col].dtype in ['int64', 'float64']:
                        st.dataframe(df[selected_col].describe())
                    else:
                        st.write("Top values:")
                        st.dataframe(df[selected_col].value_counts().head(10))
    else:
        st.warning("No common columns found between the datasets.")


def render_distribution_tab(dataframes: dict[str, pd.DataFrame]):
    """Render value distribution tab."""
    st.subheader("Value Distributions")
    
    # Find common numeric columns
    common_numeric = None
    for df in dataframes.values():
        numeric_cols = set(df.select_dtypes(include=['number']).columns)
        if common_numeric is None:
            common_numeric = numeric_cols
        else:
            common_numeric &= numeric_cols
    
    common_numeric = sorted(list(common_numeric)) if common_numeric else []
    
    if common_numeric:
        dist_col = st.selectbox("Select numeric column:", common_numeric)
        
        if dist_col:
            # Histogram overlay
            fig = go.Figure()
            colors = ["#00f5ff", "#ff00ff", "#f0ff00", "#39ff14", "#ff6600"]
            
            for idx, (filename, df) in enumerate(dataframes.items()):
                color = colors[idx % len(colors)]
                fig.add_trace(go.Histogram(
                    x=df[dist_col], 
                    name=filename, 
                    opacity=0.6,
                    marker_color=color
                ))
            
            fig.update_layout(
                barmode='overlay',
                title=f"Distribution of {dist_col}",
                **create_plotly_theme()
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # Box plot comparison
            fig2 = go.Figure()
            for idx, (filename, df) in enumerate(dataframes.items()):
                color = colors[idx % len(colors)]
                fig2.add_trace(go.Box(
                    y=df[dist_col], 
                    name=filename, 
                    marker_color=color
                ))
            
            fig2.update_layout(
                title=f"Box Plot: {dist_col}",
                **create_plotly_theme()
            )
            st.plotly_chart(fig2, use_container_width=True)
    else:
        st.info("No common numeric columns found for distribution analysis.")


def render_differences_tab(dataframes: dict[str, pd.DataFrame]):
    """Render data differences tab."""
    st.subheader("Data Differences")
    
    # Find common columns
    common_cols = set(list(dataframes.values())[0].columns)
    for df in dataframes.values():
        common_cols &= set(df.columns)
    
    if len(common_cols) == 0:
        st.warning("No common columns to compare.")
        return
    
    # Null value comparison
    st.markdown("### Null Value Comparison")
    null_data = []
    for col in common_cols:
        row = {"Column": col}
        for filename, df in dataframes.items():
            row[f"Nulls in {filename}"] = df[col].isnull().sum()
        null_data.append(row)
    
    null_df = pd.DataFrame(null_data)
    
    # Find columns with different null counts
    diff_cols = []
    for _, row in null_df.iterrows():
        null_counts = [v for k, v in row.items() if k.startswith("Nulls")]
        if len(set(null_counts)) > 1:
            diff_cols.append(row["Column"])
    
    if diff_cols:
        filtered_null_df = null_df[null_df["Column"].isin(diff_cols)]
        
        # Bar chart for null differences
        fig = go.Figure()
        colors = ["#00f5ff", "#ff00ff", "#f0ff00", "#39ff14", "#ff6600"]
        
        for idx, filename in enumerate(dataframes.keys()):
            col_name = f"Nulls in {filename}"
            fig.add_trace(go.Bar(
                x=filtered_null_df["Column"],
                y=filtered_null_df[col_name],
                name=filename,
                marker_color=colors[idx % len(colors)]
            ))
        
        fig.update_layout(
            barmode="group",
            title="Columns with Different Null Counts",
            **create_plotly_theme()
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.success("No difference in null value counts between datasets.")
    
    # Summary statistics
    st.markdown("### Summary Statistics")
    summary_data = {"Metric": ["Total Rows", "Total Columns", "Common Columns"]}
    for filename, df in dataframes.items():
        summary_data[filename] = [len(df), len(df.columns), len(common_cols)]
    
    summary_df = pd.DataFrame(summary_data)
    st.dataframe(summary_df, use_container_width=True, hide_index=True)


def render_venn_tab(dataframes: dict[str, pd.DataFrame], join_col: str):
    """Render Venn diagram for record overlap (2-3 files only)."""
    st.subheader("Record Overlap (Venn Diagram)")
    
    if len(dataframes) > 3:
        st.warning("Venn diagram is only available for 2-3 files.")
        return
    
    if not join_col:
        st.warning("Select a join column to see record overlap.")
        return
    
    # Get unique keys from each file
    keys_by_file = {}
    for filename, df in dataframes.items():
        if join_col in df.columns:
            keys_by_file[filename] = set(df[join_col].dropna().astype(str))
    
    if len(keys_by_file) < 2:
        st.warning(f"Column '{join_col}' not found in all files.")
        return
    
    filenames = list(keys_by_file.keys())
    
    if len(filenames) == 2:
        # Two-set Venn
        set_a = keys_by_file[filenames[0]]
        set_b = keys_by_file[filenames[1]]
        
        only_a = len(set_a - set_b)
        only_b = len(set_b - set_a)
        both = len(set_a & set_b)
        
        fig = go.Figure()
        
        # Create circles using scatter traces
        import numpy as np
        theta = np.linspace(0, 2*np.pi, 100)
        
        # Circle A
        x_a = 0.7 * np.cos(theta) - 0.3
        y_a = 0.7 * np.sin(theta)
        fig.add_trace(go.Scatter(x=x_a, y=y_a, mode='lines', 
                                 line=dict(color='#00f5ff', width=3),
                                 fill='toself', fillcolor='rgba(0,245,255,0.2)',
                                 name=filenames[0]))
        
        # Circle B
        x_b = 0.7 * np.cos(theta) + 0.3
        y_b = 0.7 * np.sin(theta)
        fig.add_trace(go.Scatter(x=x_b, y=y_b, mode='lines',
                                 line=dict(color='#ff00ff', width=3),
                                 fill='toself', fillcolor='rgba(255,0,255,0.2)',
                                 name=filenames[1]))
        
        # Add annotations
        fig.add_annotation(x=-0.6, y=0, text=f"{only_a}", font=dict(size=20, color='#00f5ff'))
        fig.add_annotation(x=0, y=0, text=f"{both}", font=dict(size=20, color='#39ff14'))
        fig.add_annotation(x=0.6, y=0, text=f"{only_b}", font=dict(size=20, color='#ff00ff'))
        
        fig.update_layout(
            showlegend=True,
            **create_plotly_theme(),
            xaxis=dict(showgrid=False, showticklabels=False, zeroline=False),
            yaxis=dict(showgrid=False, showticklabels=False, zeroline=False, scaleanchor='x'),
            title="Record Overlap"
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Show numbers
        col1, col2, col3 = st.columns(3)
        col1.metric(f"Only in {filenames[0]}", only_a)
        col2.metric("In Both", both)
        col3.metric(f"Only in {filenames[1]}", only_b)
    
    else:  # 3 files
        st.info("3-file Venn diagram coming soon. Showing overlap statistics:")
        
        sets = [keys_by_file[f] for f in filenames]
        
        all_three = sets[0] & sets[1] & sets[2]
        ab_only = (sets[0] & sets[1]) - sets[2]
        ac_only = (sets[0] & sets[2]) - sets[1]
        bc_only = (sets[1] & sets[2]) - sets[0]
        a_only = sets[0] - sets[1] - sets[2]
        b_only = sets[1] - sets[0] - sets[2]
        c_only = sets[2] - sets[0] - sets[1]
        
        overlap_data = {
            "Overlap": [
                "All three files",
                f"{filenames[0]} & {filenames[1]} only",
                f"{filenames[0]} & {filenames[2]} only",
                f"{filenames[1]} & {filenames[2]} only",
                f"{filenames[0]} only",
                f"{filenames[1]} only",
                f"{filenames[2]} only",
            ],
            "Count": [
                len(all_three), len(ab_only), len(ac_only), len(bc_only),
                len(a_only), len(b_only), len(c_only)
            ]
        }
        
        st.dataframe(pd.DataFrame(overlap_data), use_container_width=True, hide_index=True)


def render_quality_tab(dataframes: dict[str, pd.DataFrame]):
    """Render data quality overview tab."""
    st.subheader("Data Quality Overview")
    
    quality_data = []
    
    for filename, df in dataframes.items():
        total_cells = len(df) * len(df.columns)
        null_cells = df.isnull().sum().sum()
        completeness = (1 - null_cells / total_cells) * 100 if total_cells > 0 else 100
        duplicates = df.duplicated().sum()
        
        quality_data.append({
            "File": filename,
            "Rows": len(df),
            "Columns": len(df.columns),
            "Completeness %": round(completeness, 2),
            "Duplicate Rows": duplicates,
            "Memory (MB)": round(df.memory_usage(deep=True).sum() / 1024 / 1024, 2),
        })
    
    quality_df = pd.DataFrame(quality_data)
    st.dataframe(quality_df, use_container_width=True, hide_index=True)
    
    # Completeness comparison chart
    fig = px.bar(
        quality_df,
        x="File",
        y="Completeness %",
        color="File",
        color_discrete_sequence=["#00f5ff", "#ff00ff", "#f0ff00", "#39ff14", "#ff6600"],
        title="Data Completeness by File"
    )
    fig.update_layout(**create_plotly_theme())
    st.plotly_chart(fig, use_container_width=True)


def main():
    # Get query parameters
    query_params = st.query_params
    session_id = query_params.get("session_id", "")
    
    # Support multiple files
    file_params = []
    for key in query_params:
        if key.startswith("file"):
            file_params.append(query_params.get(key))
    
    # Fallback to file1, file2 format
    if not file_params:
        file1 = query_params.get("file1", "")
        file2 = query_params.get("file2", "")
        if file1:
            file_params.append(file1)
        if file2:
            file_params.append(file2)
    
    st.title("📊 Data Visualization Dashboard")
    
    if not session_id or not file_params:
        st.warning("No data loaded. Please run a comparison from the main application.")
        st.info("This dashboard is designed to be embedded in the ViewerIt React application.")
        return
    
    # Load all dataframes
    dataframes = {}
    with st.spinner("Loading data..."):
        for filename in file_params:
            if filename:
                df = load_data(session_id, filename)
                if not df.empty:
                    dataframes[filename] = df
    
    if len(dataframes) == 0:
        st.error("Could not load any files.")
        return
    
    if len(dataframes) == 1:
        st.info(f"Loaded 1 file: {list(dataframes.keys())[0]}")
    else:
        st.success(f"Loaded {len(dataframes)} files for comparison")
    
    # Find common columns for join selection
    common_cols = set(list(dataframes.values())[0].columns) if dataframes else set()
    for df in dataframes.values():
        common_cols &= set(df.columns)
    
    # Join column selector in sidebar
    join_col = ""
    if common_cols:
        join_col = st.selectbox("Join Column (for overlap analysis):", [""] + sorted(list(common_cols)))
    
    # Create tabs
    tab_names = ["📈 Overview", "🔍 Column Analysis", "📊 Distribution", "🎯 Differences", "📉 Quality"]
    if len(dataframes) <= 3 and join_col:
        tab_names.append("🔮 Venn Diagram")
    
    tabs = st.tabs(tab_names)
    
    with tabs[0]:
        render_overview_tab(dataframes)
    
    with tabs[1]:
        render_column_analysis_tab(dataframes)
    
    with tabs[2]:
        render_distribution_tab(dataframes)
    
    with tabs[3]:
        render_differences_tab(dataframes)
    
    with tabs[4]:
        render_quality_tab(dataframes)
    
    if len(tabs) > 5:
        with tabs[5]:
            render_venn_tab(dataframes, join_col)


if __name__ == "__main__":
    main()
