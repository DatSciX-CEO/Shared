# # Main application logic for Overwatch Command Center
# import streamlit as st
# from streamlit_option_menu import option_menu # Import for enhanced navigation
# import os
# import sys

# # Determine the project root directory
# APP_DIR = os.path.dirname(os.path.abspath(__file__))
# SRC_ROOT_DIR = os.path.dirname(APP_DIR)
# PROJECT_ROOT_DIR = os.path.dirname(SRC_ROOT_DIR)

# if PROJECT_ROOT_DIR not in sys.path:
#     sys.path.insert(0, PROJECT_ROOT_DIR)

# # Import page modules and plugin components
# from src.app.pages import home
# from src.app.pages import database_manager
# from src.app.pages import analytics
# from src.app.pages import model_integration
# from src.plugins.manager import PluginManager, AppContext
# from src.plugins.interface import OverwatchPlugin # For type hinting

# # --- App Configuration ---
# st.set_page_config(
#     page_title="Overwatch Command Center",
#     page_icon="🌠",  # Space/galaxy themed icon
#     layout="wide",
#     initial_sidebar_state="expanded",
#     menu_items={
#         'About': "# Overwatch Command Center\nModular. Extensible. Powerful. 🌌"
#     }
# )

# # --- Initialize Session State ---
# def initialize_session_state():
#     if "active_connections" not in st.session_state:
#         st.session_state.active_connections = {}
#     if "last_query_result" not in st.session_state:
#         st.session_state.last_query_result = None
#     if "current_eda_df" not in st.session_state:
#         st.session_state.current_eda_df = None
#     # current_page will be managed by streamlit-option-menu's return value,
#     # but we still use st.session_state.current_page to store the active selection.
#     if "current_page" not in st.session_state:
#         st.session_state.current_page = "Home"
#     if "plugin_manager" not in st.session_state:
#         app_context: AppContext = {"session_state": st.session_state}
#         st.session_state.plugin_manager = PluginManager(app_context=app_context)
#         st.session_state.plugin_manager.load_plugins()
#     # 'loaded_plugins_pages' session state key seems unused, can be omitted if not needed.

# # --- Main Application ---
# def main():
#     initialize_session_state()

#     plugin_manager: PluginManager = st.session_state.plugin_manager
#     loaded_plugins: list[OverwatchPlugin] = plugin_manager.get_all_plugins()

#     # --- Thematic Sidebar Title ---
#     # Fetch theme's primary color for the title, with a fallback
#     THEME_PRIMARY_COLOR_FOR_TITLE = st.get_option("theme.primaryColor") or "#00F2EA" # Default to Teal
#     st.sidebar.markdown(
#         f"<h1 style='text-align: center; color: {THEME_PRIMARY_COLOR_FOR_TITLE};'>🛰️ Overwatch</h1>",
#         unsafe_allow_html=True
#     )
#     st.sidebar.markdown("---")

#     # --- Page Definitions ---
#     # Core Pages with recommended Bootstrap Icons
#     core_page_definitions = {
#         "Home": {"module": home, "icon": "house-door-fill"},
#         "Database Manager": {"module": database_manager, "icon": "database-fill-gear"},
#         "Analytics & EDA": {"module": analytics, "icon": "graph-up-arrow"},
#         "Model Integration": {"module": model_integration, "icon": "cpu-fill"},
#     }

#     # Plugin Pages
#     plugin_page_definitions = {}
#     for plugin in loaded_plugins:
#         if hasattr(plugin, 'render_page_content'):
#             # Use getattr to safely access an 'icon' attribute from plugin.metadata, with a default
#             plugin_icon = getattr(plugin.metadata, "icon", "box-fill") # Default icon if not specified
#             plugin_page_definitions[plugin.metadata.name] = {"module": plugin, "icon": plugin_icon}

#     # Combine page titles and icons for the menu
#     page_titles = list(core_page_definitions.keys()) + list(plugin_page_definitions.keys())
#     page_icons = [details["icon"] for details in core_page_definitions.values()] + \
#                  [details["icon"] for details in plugin_page_definitions.values()]

#     # Determine default index for option_menu
#     current_page_selection = st.session_state.get("current_page", "Home")
#     try:
#         default_menu_index = page_titles.index(current_page_selection)
#     except ValueError:
#         default_menu_index = 0 # Default to Home if current_page_selection isn't valid

#     # --- Sidebar Navigation Menu ---
#     # Fetch theme colors for option_menu styles with fallbacks
#     # These fallbacks should match your desired Miami theme if config.toml is not read
#     THEME_PRIMARY_COLOR = st.get_option("theme.primaryColor") or "#00F2EA"
#     THEME_SECONDARY_BG_COLOR = st.get_option("theme.secondaryBackgroundColor") or "#1C002E"
#     THEME_BACKGROUND_COLOR = st.get_option("theme.backgroundColor") or "#0A001A" # For selected nav link text contrast
#     # Define a hover color, can be a distinct color or derived (e.g., slightly darker/lighter)
#     HOVER_COLOR = "#2E0045" # Example: A slightly different shade of purple for hover

#     with st.sidebar:
#         selected_page_name = option_menu(
#             menu_title="Navigation",
#             options=page_titles,
#             icons=page_icons,
#             menu_icon="rocket-takeoff-fill", # Thematic icon for the menu itself
#             default_index=default_menu_index,
#             orientation="vertical",
#             styles={
#                 "container": {"padding": "5px !important", "background-color": THEME_SECONDARY_BG_COLOR},
#                 "icon": {"color": THEME_PRIMARY_COLOR, "font-size": "20px"},
#                 "nav-link": {
#                     "font-size": "16px",
#                     "text-align": "left",
#                     "margin":"0px",
#                     "--hover-color": HOVER_COLOR # Custom property used by option-menu for hover
#                 },
#                 "nav-link-selected": {
#                     "background-color": THEME_PRIMARY_COLOR,
#                     "color": THEME_BACKGROUND_COLOR # Text color for selected item for contrast
#                 },
#             }
#         )

#     # Update session state with the selected page
#     st.session_state.current_page = selected_page_name
#     page_to_render = selected_page_name

#     # --- Page Rendering Logic ---
#     with st.spinner(f"Launching {page_to_render}... 🌠"):
#         page_rendered_successfully = False
#         if page_to_render in core_page_definitions:
#             core_page_definitions[page_to_render]["module"].app()
#             page_rendered_successfully = True
#         elif page_to_render in plugin_page_definitions:
#             plugin_module_instance = plugin_page_definitions[page_to_render]["module"]
#             try:
#                 plugin_module_instance.render_page_content()
#                 page_rendered_successfully = True
#             except Exception as e:
#                 st.error(f"Error rendering page content for plugin '{page_to_render}': {e}")
#                 # Optionally, redirect to home or display a less disruptive error message
#                 # st.session_state.current_page = "Home"
#                 # st.experimental_rerun() # Trigger a rerun to go to home

#         if not page_rendered_successfully:
#             st.error(f"Page '{page_to_render}' could not be rendered. Returning to Home.")
#             st.session_state.current_page = "Home" # Reset to home
#             # st.experimental_rerun() # Use rerun to force reload to home page
#             home.app() # Directly render home as a fallback


#     # --- Plugin Sidebar Contributions (Additional Controls) ---
#     st.sidebar.markdown("---")
#     st.sidebar.subheader("Plugin Controls")
#     plugins_with_sidebar_contributions = False
#     for plugin in loaded_plugins:
#         if hasattr(plugin, 'render_sidebar_contribution'):
#             try:
#                 # Consider logic here: should contributions always show, or only for active plugin?
#                 # For now, all plugins with the method will attempt to render their sidebar part.
#                 plugin.render_sidebar_contribution()
#                 plugins_with_sidebar_contributions = True
#             except Exception as e:
#                 st.sidebar.error(f"Error in plugin '{plugin.metadata.name}' sidebar: {e}")

#     if not loaded_plugins or not plugins_with_sidebar_contributions:
#         st.sidebar.info("No additional plugin controls.")

#     # --- Footer Info ---
#     st.sidebar.markdown("---")
#     st.sidebar.info(
#         "Overwatch Command Center v0.1.0\n"
#         "Modular & Extensible ✨"
#     )

# if __name__ == "__main__":
#     main()



# src/app/main.py
import streamlit as st
import os
import sys
from datetime import datetime # For the placeholder time

# --- Path Setup (CRITICAL: Corrected for proper module resolution) ---
# This setup assumes main.py is in a directory like 'src/app/'
# The directory that needs to be on sys.path for "from src.xxx" to work is the PARENT of 'src'.

APP_SCRIPT_PATH = os.path.abspath(__file__)       # Full path to this main.py script
APP_DIR = os.path.dirname(APP_SCRIPT_PATH)        # Directory of main.py (e.g., /path/to/project/src/app)
SRC_ROOT_DIR = os.path.dirname(APP_DIR)           # Parent of app_dir (e.g., /path/to/project/src)
PROJECT_ROOT_DIR = os.path.dirname(SRC_ROOT_DIR)  # Parent of src_dir (e.g., /path/to/project, this is Overwatch/)

# Add PROJECT_ROOT_DIR to sys.path so that imports like "from src.plugins..." work correctly.
# This ensures that Python can find the 'src' module from the project's root.
if PROJECT_ROOT_DIR not in sys.path:
    sys.path.insert(0, PROJECT_ROOT_DIR)
    # For debugging path issues, you can print to stderr (visible in the console where Streamlit runs)
    # print(f"DEBUG (main.py): Added {PROJECT_ROOT_DIR} to sys.path", file=sys.stderr)


# --- Import Application Modules ---
# Attempt to import essential modules. Errors here will stop the app.
try:
    from src.plugins.manager import PluginManager, AppContext
    from src.plugins.interface import OverwatchPlugin # For type hinting
except ImportError as e:
    # Display a prominent error message in the Streamlit app if imports fail.
    st.error(f"Fatal Error: Failed to import core modules (PluginManager, OverwatchPlugin, AppContext).")
    st.error(f"This usually indicates a problem with your Python environment or PYTHONPATH setup, even after path adjustments.")
    st.error(f"Details: {e}") # Show the specific ImportError
    st.error(f"Current sys.path: {sys.path}") # Display current sys.path for debugging
    st.error(f"PROJECT_ROOT_DIR that was added to sys.path: {PROJECT_ROOT_DIR}")
    st.stop() # Stop execution if essential modules can't be loaded.

# --- Application Configuration (Called only ONCE) ---
# This should be the first Streamlit command in your script.
st.set_page_config(
    page_title="Overwatch Command Center",
    page_icon="🌠",  # Emoji icon for the browser tab
    layout="wide",   # Use the full width of the page
    initial_sidebar_state="expanded", # Ensures sidebar is open by default
    menu_items={
        'Get Help': 'https://www.example.com/help', # Replace with your actual help URL
        'Report a bug': "https://www.example.com/bug", # Replace with your actual bug report URL
        'About': "# Overwatch Command Center\nModular. Extensible. Powerful. 🌌" # Markdown for the About section
    }
)

# --- Initialize Shared Session State (Centralized) ---
def initialize_global_session_state():
    """
    Initializes global session state variables if they don't exist.
    This function is called once when main.py runs.
    Individual pages in the 'pages/' directory will inherit this session state.
    """
    # For database connections
    if "active_connections" not in st.session_state:
        st.session_state.active_connections = {}
    if "last_query_result" not in st.session_state:
        st.session_state.last_query_result = None

    # For data passed to EDA/ML pages
    if "current_eda_df" not in st.session_state:
        st.session_state.current_eda_df = None

    # For plugin management: stores the name of the plugin to be viewed by the plugin viewer page
    if "active_plugin_for_viewer" not in st.session_state:
        st.session_state.active_plugin_for_viewer = None

    # Initialize Plugin Manager
    if "plugin_manager" not in st.session_state:
        try:
            # Create the application context that plugins might use (e.g., to access session_state)
            app_context: AppContext = {"session_state": st.session_state}
            st.session_state.plugin_manager = PluginManager(app_context=app_context)
            st.session_state.plugin_manager.load_plugins() # Discover and load all plugins
            # st.toast("Plugin system initialized!", icon="🔌") # Optional user feedback
        except Exception as e:
            st.error(f"Critical Error: Could not initialize or load plugins via PluginManager: {e}")
            st.exception(e) # Show full traceback for debugging in the app
            st.session_state.plugin_manager = None # Ensure it's None if initialization failed
    
    # Placeholder for any other global state, like an application initialization timestamp
    if 'app_init_time' not in st.session_state:
        st.session_state.app_init_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# --- Define Common Sidebar Elements ---
def build_common_sidebar():
    """
    Builds common sidebar elements like the application title, plugin controls, and footer.
    These elements will appear on every page navigated to via the `pages/` directory.
    """
    # Thematic Sidebar Title - uses theme color if available, otherwise a fallback.
    THEME_PRIMARY_COLOR_FOR_TITLE = st.get_option("theme.primaryColor") or "#00F2EA" # Default to a teal color
    st.sidebar.markdown(
        f"<h1 style='text-align: center; color: {THEME_PRIMARY_COLOR_FOR_TITLE};'>🛰️ Overwatch</h1>",
        unsafe_allow_html=True
    )
    st.sidebar.markdown("---") # Visual separator

    # Streamlit automatically adds links to pages from the 'pages/' directory here in the sidebar.

    # --- Plugin Sidebar Contributions ---
    st.sidebar.markdown("## Plugin Controls") # Section title for plugin buttons

    # Check if plugin_manager was successfully initialized and is available
    if "plugin_manager" in st.session_state and st.session_state.plugin_manager is not None:
        plugin_manager: PluginManager = st.session_state.plugin_manager
        loaded_plugins: list[OverwatchPlugin] = plugin_manager.get_all_plugins()
        plugins_with_sidebar_contributions = False

        if loaded_plugins:
            for plugin in loaded_plugins:
                # Check if the plugin has the method to render sidebar contributions
                if hasattr(plugin, 'render_sidebar_contribution'):
                    try:
                        # Ensure plugin has access to app_context if it needs to set session_state.
                        # This is a safeguard; ideally, plugins are initialized with app_context.
                        if not hasattr(plugin, '_app_context') or plugin._app_context is None:
                             if hasattr(plugin_manager, 'app_context'): # Check if plugin_manager has app_context
                                 plugin._app_context = plugin_manager.app_context

                        plugin.render_sidebar_contribution() # Call the plugin's method
                        plugins_with_sidebar_contributions = True
                    except Exception as e:
                        st.sidebar.error(f"Error in '{plugin.metadata.name}' sidebar contribution: {e}", icon="⚠️")
                        # st.sidebar.exception(e) # Uncomment for more detailed error in sidebar during development
        
        if not loaded_plugins:
            st.sidebar.info("No plugins loaded.")
        elif not plugins_with_sidebar_contributions:
            st.sidebar.info("No plugin-specific controls available in the sidebar.")
    else:
        st.sidebar.warning("Plugin manager is not available. Plugin controls cannot be displayed.", icon="⚙️")

    # --- Footer Info (Appears on all pages in the sidebar) ---
    st.sidebar.markdown("---") # Visual separator
    st.sidebar.info(
        f"Overwatch Command Center v0.1.0\n"
        f"© {datetime.now().year} - Modular & Extensible ✨"
    )
    # Displaying the application initialization time from session state
    st.sidebar.caption(f"Initialized: {st.session_state.get('app_init_time', 'N/A')}")

# --- Main Execution Block ---
# This code runs when `streamlit run src/app/main.py` is executed.
if __name__ == "__main__":
    # Initialize global session state variables. This is crucial and should run first.
    initialize_global_session_state()
    
    # Build the common sidebar elements. These will appear on every page.
    build_common_sidebar()
    
    # Content for main.py itself (if accessed directly):
    # In a multipage app using the `pages/` directory, Streamlit typically defaults to
    # showing the first page from that directory (e.g., a file named 0_Home.py).
    # The content here in `main.py` will only be shown if a user somehow navigates
    # directly to `main.py` without a page from the `pages/` directory being selected,
    # or if there are no files in the `pages/` directory.
    st.markdown(
        """
        ### 🚀 Overwatch Command Center Initialized!

        Please select a module from the navigation panel on the left.
        
        If you're seeing this, the main application script (`main.py`) has run. 
        Streamlit should typically display your 'Home' page or another selected page from the `pages/` directory.
        """
    )
    # For debugging path issues further if they persist:
    # You can uncomment these lines during development to see path information directly in the app.
    # with st.expander("Path Debug Information (from main.py)"):
    #     st.write(f"**PROJECT_ROOT_DIR (should contain 'src'):** `{PROJECT_ROOT_DIR}`")
    #     st.write(f"**SRC_ROOT_DIR (should be 'src'):** `{SRC_ROOT_DIR}`")
    #     st.write(f"**APP_DIR (should be 'src/app'):** `{APP_DIR}`")
    #     st.write(f"**sys.path:**")
    #     st.json(sys.path) # Displays the sys.path list as JSON
