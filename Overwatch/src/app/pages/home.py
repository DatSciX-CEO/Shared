# src/app/pages/0_🏠_Home.py
import streamlit as st
import os
import sys

# --- Robust Path Setup for Page-Specific Execution ---
# Ensures that when this page script is run by Streamlit,
# it can find modules in your 'src' directory.
PAGE_SCRIPT_PATH = os.path.abspath(__file__)
PAGE_DIR = os.path.dirname(PAGE_SCRIPT_PATH)      # Directory of this page (e.g., /path/to/project/src/app/pages)
APP_DIR = os.path.dirname(PAGE_DIR)              # Directory of the app (e.g., /path/to/project/src/app)
SRC_ROOT_DIR = os.path.dirname(APP_DIR)          # Root of 'src' (e.g., /path/to/project/src)
PROJECT_ROOT_DIR = os.path.dirname(SRC_ROOT_DIR) # Project root (e.g., /path/to/project)

# Add PROJECT_ROOT_DIR to sys.path so 'from src.core...' or 'from src.plugins...' works
if PROJECT_ROOT_DIR not in sys.path:
    sys.path.insert(0, PROJECT_ROOT_DIR)
    # For debugging:
    # print(f"DEBUG (Home Page): Added {PROJECT_ROOT_DIR} to sys.path", file=sys.stderr)

# --- Attempt to Import Any Necessary Project Modules (if this page needs them) ---
# Example: If the home page needs to display info from the plugin manager
# try:
#     from src.plugins.manager import PluginManager # Assuming PluginManager is needed
# except ImportError as e:
#     st.error(f"Error importing modules in 0_🏠_Home.py: {e}")
#     st.stop()

# --- Main Function to Render the Home Page Content ---
def display_home_page_content():
    st.title("🏠 Welcome to Overwatch Command Center!")
    st.subheader("Your Unified Hub for Data Operations, Analytics, and Extensibility 🌌")
    st.markdown("---")

    st.markdown(
        """
        Overwatch is designed to be a modular and extensible platform providing seamless integration for:

        - **🗄️ Universal Database Connectivity**: Securely manage and query your databases.
        - **📊 Comprehensive Analytics & EDA**: Upload data, explore, and visualize insights.
        - **🤖 Machine Learning Integration**: Quickly train and compare baseline models.
        - **🔌 Dynamic Plugin Support**: Extend capabilities with custom plugins.

        Use the navigation panel on the left to explore the different modules.
        """
    )

    st.markdown("---")
    st.header("🚀 Quick Navigation")
    st.write("While the sidebar provides full navigation, here are some key areas:")

    cols = st.columns(3)
    with cols[0]:
        st.subheader("Database")
        st.image("https://placehold.co/300x200/7F00FF/FFFFFF?text=Databases&font=raleway", use_column_width=True) # Purple
        st.write("Connect to databases, manage credentials, and execute SQL queries.")
        if st.button("Go to Database Manager", key="home_db_btn"):
            st.switch_page("pages/2_🗄️_Database_Manager.py") # Ensure filename matches

    with cols[1]:
        st.subheader("Analytics")
        st.image("https://placehold.co/300x200/00F2EA/FFFFFF?text=Analytics&font=raleway", use_column_width=True) # Teal
        st.write("Perform EDA, visualize data, and uncover statistical insights.")
        if st.button("Go to Analytics & EDA", key="home_analytics_btn"):
            st.switch_page("pages/1_📊_Analytics.py") # Ensure filename matches
            
    with cols[2]:
        st.subheader("ML Models")
        st.image("https://placehold.co/300x200/FF69B4/FFFFFF?text=ML+Models&font=raleway", use_column_width=True) # Pink
        st.write("Integrate machine learning models and compare their performance.")
        if st.button("Go to Model Integration", key="home_ml_btn"):
            st.switch_page("pages/3_🤖_Model_Integration.py") # Ensure filename matches

    st.markdown("---")
    st.info("✨ Explore, extend, and empower your data workflows with Overwatch!")

    # Example: Displaying some info from session_state if needed
    # if "plugin_manager" in st.session_state and st.session_state.plugin_manager:
    #     plugin_manager = st.session_state.plugin_manager
    #     num_plugins = len(plugin_manager.get_all_plugins())
    #     st.sidebar.success(f"{num_plugins} plugins loaded.") # Example of using sidebar from a page

# --- Ensure the page rendering function is called when this script is run ---
if __name__ == "__main__":
    # Any specific initializations for this page can go here,
    # though most global state should be in main.py's initialize_global_session_state
    
    # Call the function that builds the Streamlit UI for this page
    display_home_page_content()
