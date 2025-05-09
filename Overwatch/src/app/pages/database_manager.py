# Page for Database Management
import streamlit as st
import os
import pandas as pd
from src.core.database.credentials import CredentialManager
from src.core.database.drivers.sqlite import SQLiteConnection, ConnectionError as DBConnectionError # Renamed to avoid conflict

# Ensure data directory exists for SQLite databases
DATA_DIR = "/home/ubuntu/overwatch_command_center/data"
os.makedirs(DATA_DIR, exist_ok=True)

def app():
    st.title("Database Manager")
    st.write("Manage your database connections and explore data here.")

    cred_manager = CredentialManager()
    active_connections = st.session_state.get("active_connections", {})

    st.subheader("Manage Connections")

    # Connection Form (Simplified for now)
    with st.expander("Add New SQLite Connection"):
        with st.form("new_sqlite_connection_form"):
            conn_name = st.text_input("Connection Name (e.g., my_local_db)")
            db_filename = st.text_input("SQLite Database Filename (e.g., my_database.db)", help=f"Will be stored in {DATA_DIR}")
            submitted = st.form_submit_button("Save Connection")

            if submitted:
                if not conn_name or not db_filename:
                    st.error("Connection Name and Database Filename are required.")
                else:
                    db_path = os.path.join(DATA_DIR, db_filename)
                    conn_details = {"type": "sqlite", "database_path": db_path}
                    try:
                        cred_manager.add_credential(conn_name, conn_details)
                        st.success(f"Connection 	'{conn_name}	' saved successfully!")
                        # Touch the db file if it doesn't exist to avoid initial connection errors for new dbs
                        if not os.path.exists(db_path):
                            open(db_path, 'a').close()
                    except Exception as e:
                        st.error(f"Failed to save connection: {e}")
    
    st.markdown("---_---")
    st.subheader("Available Connections")
    saved_connections = cred_manager.list_credential_names()

    if not saved_connections:
        st.info("No saved connections. Add a new SQLite connection above.")
    else:
        conn_to_manage = st.selectbox("Select a connection to manage:", options=[""] + saved_connections)

        if conn_to_manage:
            conn_details = cred_manager.get_credential(conn_to_manage)
            st.write(f"Details for **{conn_to_manage}**:")
            st.json(conn_details) # Display connection details (excluding sensitive parts if any in future)

            col1, col2, col3 = st.columns(3)
            with col1:
                if st.button(f"Connect to 	'{conn_to_manage}	'", key=f"connect_{conn_to_manage}"):
                    if conn_details and conn_details.get("type") == "sqlite":
                        try:
                            db_conn = SQLiteConnection(conn_details)
                            db_conn.connect()
                            if db_conn.test_connection():
                                active_connections[conn_to_manage] = db_conn
                                st.session_state.active_connections = active_connections
                                st.success(f"Successfully connected to 	'{conn_to_manage}	'!")
                            else:
                                st.error(f"Failed to establish a test connection to 	'{conn_to_manage}	'.")
                                db_conn.disconnect() # Ensure cleanup
                        except DBConnectionError as e:
                            st.error(f"Connection Error for 	'{conn_to_manage}	': {e}")
                        except Exception as e:
                            st.error(f"An unexpected error occurred while connecting to 	'{conn_to_manage}	': {e}")
                    else:
                        st.error("Unsupported connection type or missing details.")
            
            with col2:
                if conn_to_manage in active_connections:
                    if st.button(f"Disconnect from 	'{conn_to_manage}	'", key=f"disconnect_{conn_to_manage}"):
                        try:
                            active_connections[conn_to_manage].disconnect()
                            del active_connections[conn_to_manage]
                            st.session_state.active_connections = active_connections
                            st.info(f"Disconnected from 	'{conn_to_manage}	'.")
                        except Exception as e:
                            st.error(f"Error disconnecting: {e}")
                else:
                    st.button(f"Disconnect from 	'{conn_to_manage}	'", key=f"disconnect_{conn_to_manage}", disabled=True)

            with col3:
                if st.button(f"Remove 	'{conn_to_manage}	'", type="primary", key=f"remove_{conn_to_manage}"):
                    if conn_to_manage in active_connections:
                        active_connections[conn_to_manage].disconnect()
                        del active_connections[conn_to_manage]
                        st.session_state.active_connections = active_connections
                    cred_manager.remove_credential(conn_to_manage)
                    st.success(f"Connection 	'{conn_to_manage}	' removed.")
                    st.experimental_rerun() # Rerun to update selectbox

            # Query Interface if connected
            if conn_to_manage in active_connections and active_connections[conn_to_manage].connection:
                st.markdown("---_---")
                st.subheader(f"Query 	'{conn_to_manage}	'")
                query = st.text_area("Enter SQL Query:", height=100, key=f"query_area_{conn_to_manage}")
                if st.button("Execute Query", key=f"execute_query_{conn_to_manage}"):
                    if query:
                        try:
                            with st.spinner("Executing query..."):
                                df_results = active_connections[conn_to_manage].execute_query(query)
                            st.dataframe(df_results)
                            if st.button("Export results to CSV", key=f"export_csv_{conn_to_manage}"):
                                csv = df_results.to_csv(index=False).encode('utf-8')
                                st.download_button(
                                    label="Download CSV",
                                    data=csv,
                                    file_name=f"{conn_to_manage}_query_results.csv",
                                    mime='text/csv',
                                )
                        except DBConnectionError as e:
                            st.error(f"Query execution failed: {e}")
                        except Exception as e:
                            st.error(f"An unexpected error occurred during query: {e}")
                    else:
                        st.warning("Please enter a query.")

    # Display active connections at the bottom
    st.sidebar.markdown("## Active Connections")
    if active_connections:
        for name in active_connections.keys():
            st.sidebar.success(f"🟢 {name}")
    else:
        st.sidebar.info("No active connections.")

# Initialize session state for active_connections if not already present
if 'active_connections' not in st.session_state:
    st.session_state.active_connections = {}

