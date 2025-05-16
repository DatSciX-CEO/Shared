# src/plugins/builtin/example_plugin.py
import streamlit as st
from src.plugins.interface import OverwatchPlugin, PluginMetadata, AppContext
# import pandas as pd # If you use pandas in your plugin

class ExampleBuiltinPlugin(OverwatchPlugin):
    """An example plugin that demonstrates basic functionality."""

    def __init__(self):
        self._app_context: AppContext | None = None # Initialize with type hint

    @property
    def metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="Example Plugin",
            version="1.0.2", # Updated version
            description="A simple plugin to demonstrate extensibility and navigation.",
            author="Overwatch Dev Team",
            icon="💡"  # Using an emoji as an icon example
        )

    def initialize(self, app_context: AppContext) -> None:
        self._app_context = app_context
        # Example: Store something in session state if needed during initialization
        # if self._app_context and "session_state" in self._app_context:
        #     self._app_context["session_state"][f"{self.metadata.name}_initialized_time"] = pd.Timestamp.now()
        # st.toast(f"Plugin '{self.metadata.name}' initialized!", icon=self.metadata.icon)


    def render_sidebar_contribution(self) -> None:
        """Adds an item to the sidebar to navigate to this plugin's page via the Plugin Viewer."""
        if self._app_context is None or "session_state" not in self._app_context:
            st.sidebar.warning(f"App context not available to {self.metadata.name}. Cannot create sidebar button.")
            return

        button_label = f"{self.metadata.icon} {self.metadata.name}"
        
        if st.sidebar.button(button_label, key=f"plugin_btn_{self.metadata.name.replace(' ', '_')}"):
            self._app_context["session_state"].active_plugin_for_viewer = self.metadata.name
            
            # Navigate to the dedicated plugin viewer page
            # Ensure the target path matches the filename in your src/app/pages/ directory
            plugin_viewer_page_path = "pages/4_🧩_Plugins.py" # Or whatever you named it
            try:
                st.switch_page(plugin_viewer_page_path)
            except Exception as e:
                st.error(f"Navigation to plugin page failed: {e}. Ensure '{plugin_viewer_page_path}' exists.")
                # Fallback or further error handling
                # st.experimental_rerun() 

    def render_page_content(self) -> None:
        """Renders the content for this plugin's dedicated page."""
        # This content will be displayed by '4_🧩_Plugins.py' when this plugin is active.
        # st.title(f"{self.metadata.icon} {self.metadata.name} (v{self.metadata.version})") # Title is now handled by viewer
        st.markdown(f"### Welcome to the {self.metadata.name}!")
        st.write(f"This page demonstrates content rendered by the dynamically loaded **{self.metadata.name}**.")
        st.markdown(f"_{self.metadata.description}_")
        st.write(f"Authored by: {self.metadata.author}")
        
        st.markdown("---")
        st.subheader("Plugin Functionality Example")
        
        if 'plugin_button_clicks' not in st.session_state:
            st.session_state.plugin_button_clicks = 0

        if st.button("Show a message from plugin", key=f"msg_btn_{self.metadata.name.replace(' ', '_')}"):
            st.session_state.plugin_button_clicks += 1
            st.info(f"Hello from the Example Built-in Plugin! 👋 (Button clicked {st.session_state.plugin_button_clicks} times)")

        # Example: Accessing shared data (if app_context provided it during init)
        # if self._app_context and "shared_data" in self._app_context["session_state"]:
        #     st.write("Shared data from app session state:", self._app_context["session_state"]["shared_data"])
        # else:
        #     st.caption("No 'shared_data' found in app context session state for this plugin.")

    def on_unload(self) -> None:
        # Cleanup actions if any
        # st.toast(f"Plugin '{self.metadata.name}' is being unloaded.", icon="👋")
        if self._app_context and "session_state" in self._app_context:
            # Example: Clean up session state specific to this plugin
            # self._app_context["session_state"].pop(f"{self.metadata.name}_initialized_time", None)
            # self._app_context["session_state"].pop(f"{self.metadata.name}_button_clicks", None)
            pass
