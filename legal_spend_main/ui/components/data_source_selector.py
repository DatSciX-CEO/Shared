"""
Data Source Selector Component
Allows selection between CSV, Parquet, or SQL Server data sources
"""
import streamlit as st
import tempfile
import os


def render_data_source_selector():
    """
    Render data source selection UI in Streamlit sidebar.
    Updates st.session_state with data source information.
    """
    st.sidebar.subheader("📁 Data Source")
    
    # Initialize session state
    if 'data_source_type' not in st.session_state:
        st.session_state.data_source_type = None
    if 'data_file_path' not in st.session_state:
        st.session_state.data_file_path = None
    if 'data_loaded' not in st.session_state:
        st.session_state.data_loaded = False
    
    # Data source type selection
    source_type = st.sidebar.radio(
        "Select Data Source Type",
        options=["CSV File", "Parquet File", "SQL Server"],
        key="data_source_radio",
        help="Choose how to load your legal spend data"
    )
    
    st.sidebar.divider()
    
    # CSV File Upload
    if source_type == "CSV File":
        st.sidebar.caption("Upload a CSV file with legal spend data")
        uploaded_file = st.sidebar.file_uploader(
            "Choose CSV file",
            type=['csv'],
            key="csv_uploader",
            help="Upload CSV with columns: law_firm, amount, date, description"
        )
        
        if uploaded_file is not None:
            # Save to temporary file
            if st.session_state.data_file_path != uploaded_file.name:
                with tempfile.NamedTemporaryFile(delete=False, suffix='.csv', mode='wb') as tmp_file:
                    tmp_file.write(uploaded_file.getvalue())
                    tmp_path = tmp_file.name
                
                st.session_state.data_source_type = "csv"
                st.session_state.data_file_path = tmp_path
                st.session_state.data_loaded = True
                st.sidebar.success(f"✅ CSV loaded: {uploaded_file.name}")
                st.sidebar.caption(f"Path: {tmp_path}")
    
    # Parquet File Upload
    elif source_type == "Parquet File":
        st.sidebar.caption("Upload a Parquet file with legal spend data")
        uploaded_file = st.sidebar.file_uploader(
            "Choose Parquet file",
            type=['parquet'],
            key="parquet_uploader",
            help="Upload Parquet file with legal spend data"
        )
        
        if uploaded_file is not None:
            # Save to temporary file
            if st.session_state.data_file_path != uploaded_file.name:
                with tempfile.NamedTemporaryFile(delete=False, suffix='.parquet', mode='wb') as tmp_file:
                    tmp_file.write(uploaded_file.getvalue())
                    tmp_path = tmp_file.name
                
                st.session_state.data_source_type = "parquet"
                st.session_state.data_file_path = tmp_path
                st.session_state.data_loaded = True
                st.sidebar.success(f"✅ Parquet loaded: {uploaded_file.name}")
                st.sidebar.caption(f"Path: {tmp_path}")
    
    # SQL Server Connection
    elif source_type == "SQL Server":
        st.sidebar.caption("Connect to SQL Server database")
        
        with st.sidebar.expander("SQL Server Configuration", expanded=True):
            server = st.text_input("Server", value="localhost", key="sql_server")
            database = st.text_input("Database", value="LegalSpend", key="sql_database")
            
            auth_type = st.radio("Authentication", ["Windows (Trusted)", "SQL Server"], key="sql_auth")
            
            if auth_type == "SQL Server":
                username = st.text_input("Username", key="sql_username")
                password = st.text_input("Password", type="password", key="sql_password")
            
            table_name = st.text_input("Table Name", value="legal_spend", key="sql_table")
            
            if st.button("Connect to SQL Server", key="sql_connect"):
                # Store SQL connection info
                st.session_state.data_source_type = "sql"
                st.session_state.sql_config = {
                    "server": server,
                    "database": database,
                    "table_name": table_name,
                    "auth_type": auth_type
                }
                if auth_type == "SQL Server":
                    st.session_state.sql_config["username"] = username
                    st.session_state.sql_config["password"] = password
                
                st.session_state.data_loaded = True
                st.sidebar.success(f"✅ Connected to {server}/{database}")
    
    # Show current data source status
    st.sidebar.divider()
    if st.session_state.data_loaded:
        st.sidebar.info(f"📊 Data Source: {st.session_state.data_source_type.upper()}")
    else:
        st.sidebar.warning("⚠️ No data source loaded")


