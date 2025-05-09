# Main application logic for Overwatch Command Center
import streamlit as st
from streamlit_option_menu import option_menu # Import for enhanced navigation
import os
import sys

# Determine the project root directory
APP_DIR = os.path.dirname(os.path.abspath(__file__))
SRC_ROOT_DIR = os.path.dirname(APP_DIR)
PROJECT_ROOT_DIR = os.path.dirname(SRC_ROOT_DIR)

if PROJECT_ROOT_DIR not in sys.path:
    sys.path.insert(0, PROJECT_ROOT_DIR)

# Import page modules and plugin components
from src.app.pages import home
from src.app.pages import database_manager
from src.app.pages import analytics
from src.app.pages import model_integration
from src.plugins.manager import PluginManager, AppContext
from src.plugins.interface import OverwatchPlugin # For type hinting

# --- App Configuration ---
st.set_page_config(
    page_title="Overwatch Command Center",
    page_icon="🌠",  # Space/galaxy themed icon
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'About': "# Overwatch Command Center\nModular. Extensible. Powerful. 🌌"
    }
)

# --- Initialize Session State ---
def initialize_session_state():
    if "active_connections" not in st.session_state:
        st.session_state.active_connections = {}
    if "last_query_result" not in st.session_state:
        st.session_state.last_query_result = None
    if "current_eda_df" not in st.session_state:
        st.session_state.current_eda_df = None
    # current_page will be managed by streamlit-option-menu's return value,
    # but we still use st.session_state.current_page to store the active selection.
    if "current_page" not in st.session_state:
        st.session_state.current_page = "Home"
    if "plugin_manager" not in st.session_state:
        app_context: AppContext = {"session_state": st.session_state}
        st.session_state.plugin_manager = PluginManager(app_context=app_context)
        st.session_state.plugin_manager.load_plugins()
    # 'loaded_plugins_pages' session state key seems unused, can be omitted if not needed.

# --- Main Application ---
def main():
    initialize_session_state()

    plugin_manager: PluginManager = st.session_state.plugin_manager
    loaded_plugins: list[OverwatchPlugin] = plugin_manager.get_all_plugins()

    # --- Thematic Sidebar Title ---
    # Fetch theme's primary color for the title, with a fallback
    THEME_PRIMARY_COLOR_FOR_TITLE = st.get_option("theme.primaryColor") or "#00F2EA" # Default to Teal
    st.sidebar.markdown(
        f"<h1 style='text-align: center; color: {THEME_PRIMARY_COLOR_FOR_TITLE};'>🛰️ Overwatch</h1>",
        unsafe_allow_html=True
    )
    st.sidebar.markdown("---")

    # --- Page Definitions ---
    # Core Pages with recommended Bootstrap Icons
    core_page_definitions = {
        "Home": {"module": home, "icon": "house-door-fill"},
        "Database Manager": {"module": database_manager, "icon": "database-fill-gear"},
        "Analytics & EDA": {"module": analytics, "icon": "graph-up-arrow"},
        "Model Integration": {"module": model_integration, "icon": "cpu-fill"},
    }

    # Plugin Pages
    plugin_page_definitions = {}
    for plugin in loaded_plugins:
        if hasattr(plugin, 'render_page_content'):
            # Use getattr to safely access an 'icon' attribute from plugin.metadata, with a default
            plugin_icon = getattr(plugin.metadata, "icon", "box-fill") # Default icon if not specified
            plugin_page_definitions[plugin.metadata.name] = {"module": plugin, "icon": plugin_icon}

    # Combine page titles and icons for the menu
    page_titles = list(core_page_definitions.keys()) + list(plugin_page_definitions.keys())
    page_icons = [details["icon"] for details in core_page_definitions.values()] + \
                 [details["icon"] for details in plugin_page_definitions.values()]

    # Determine default index for option_menu
    current_page_selection = st.session_state.get("current_page", "Home")
    try:
        default_menu_index = page_titles.index(current_page_selection)
    except ValueError:
        default_menu_index = 0 # Default to Home if current_page_selection isn't valid

    # --- Sidebar Navigation Menu ---
    # Fetch theme colors for option_menu styles with fallbacks
    # These fallbacks should match your desired Miami theme if config.toml is not read
    THEME_PRIMARY_COLOR = st.get_option("theme.primaryColor") or "#00F2EA"
    THEME_SECONDARY_BG_COLOR = st.get_option("theme.secondaryBackgroundColor") or "#1C002E"
    THEME_BACKGROUND_COLOR = st.get_option("theme.backgroundColor") or "#0A001A" # For selected nav link text contrast
    # Define a hover color, can be a distinct color or derived (e.g., slightly darker/lighter)
    HOVER_COLOR = "#2E0045" # Example: A slightly different shade of purple for hover

    with st.sidebar:
        selected_page_name = option_menu(
            menu_title="Navigation",
            options=page_titles,
            icons=page_icons,
            menu_icon="rocket-takeoff-fill", # Thematic icon for the menu itself
            default_index=default_menu_index,
            orientation="vertical",
            styles={
                "container": {"padding": "5px !important", "background-color": THEME_SECONDARY_BG_COLOR},
                "icon": {"color": THEME_PRIMARY_COLOR, "font-size": "20px"},
                "nav-link": {
                    "font-size": "16px",
                    "text-align": "left",
                    "margin":"0px",
                    "--hover-color": HOVER_COLOR # Custom property used by option-menu for hover
                },
                "nav-link-selected": {
                    "background-color": THEME_PRIMARY_COLOR,
                    "color": THEME_BACKGROUND_COLOR # Text color for selected item for contrast
                },
            }
        )

    # Update session state with the selected page
    st.session_state.current_page = selected_page_name
    page_to_render = selected_page_name

    # --- Page Rendering Logic ---
    with st.spinner(f"Launching {page_to_render}... 🌠"):
        page_rendered_successfully = False
        if page_to_render in core_page_definitions:
            core_page_definitions[page_to_render]["module"].app()
            page_rendered_successfully = True
        elif page_to_render in plugin_page_definitions:
            plugin_module_instance = plugin_page_definitions[page_to_render]["module"]
            try:
                plugin_module_instance.render_page_content()
                page_rendered_successfully = True
            except Exception as e:
                st.error(f"Error rendering page content for plugin '{page_to_render}': {e}")
                # Optionally, redirect to home or display a less disruptive error message
                # st.session_state.current_page = "Home"
                # st.experimental_rerun() # Trigger a rerun to go to home

        if not page_rendered_successfully:
            st.error(f"Page '{page_to_render}' could not be rendered. Returning to Home.")
            st.session_state.current_page = "Home" # Reset to home
            # st.experimental_rerun() # Use rerun to force reload to home page
            home.app() # Directly render home as a fallback


    # --- Plugin Sidebar Contributions (Additional Controls) ---
    st.sidebar.markdown("---")
    st.sidebar.subheader("Plugin Controls")
    plugins_with_sidebar_contributions = False
    for plugin in loaded_plugins:
        if hasattr(plugin, 'render_sidebar_contribution'):
            try:
                # Consider logic here: should contributions always show, or only for active plugin?
                # For now, all plugins with the method will attempt to render their sidebar part.
                plugin.render_sidebar_contribution()
                plugins_with_sidebar_contributions = True
            except Exception as e:
                st.sidebar.error(f"Error in plugin '{plugin.metadata.name}' sidebar: {e}")

    if not loaded_plugins or not plugins_with_sidebar_contributions:
        st.sidebar.info("No additional plugin controls.")

    # --- Footer Info ---
    st.sidebar.markdown("---")
    st.sidebar.info(
        "Overwatch Command Center v0.1.0\n"
        "Modular & Extensible ✨"
    )

if __name__ == "__main__":
    main()