# Example Built-in Plugin for Overwatch Command Center
import streamlit as st
from src.plugins.interface import OverwatchPlugin, PluginMetadata, AppContext

class ExampleBuiltinPlugin(OverwatchPlugin):
    """An example plugin that demonstrates basic functionality."""

    def __init__(self):
        self._app_context = None

    # In example_plugin.py
    @property
    def metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="Example Plugin",
            version="1.0.1",
            description="A simple plugin to demonstrate extensibility.",
            author="Overwatch Dev Team",
            icon="lightbulb-fill"  # Provide a Bootstrap Icon name
        )

    def initialize(self, app_context: AppContext) -> None:
        self._app_context = app_context
        # st.toast(f"Plugin 	"{self.metadata.name}	" initialized!", icon="🎉")
        # Accessing something from app_context if needed:
        # session_state = self._app_context.get("session_state")
        # if session_state:
        #     session_state.example_plugin_loaded_time = pd.Timestamp.now()
        pass

    def render_sidebar_contribution(self) -> None:
        """Adds an item to the sidebar to navigate to this plugin's page."""
        if st.sidebar.button(f"⚙️ {self.metadata.name}"):
            if self._app_context and "session_state" in self._app_context:
                self._app_context["session_state"].current_page = self.metadata.name # Trigger navigation
                # Note: The main app needs to handle routing to plugin pages based on this
            else:
                st.sidebar.warning("App context or session state not available to plugin.")

    def render_page_content(self) -> None:
        """Renders the content for this plugin's dedicated page."""
        st.title(f"{self.metadata.name} (v{self.metadata.version})")
        st.markdown(self.metadata.description)
        st.write(f"Authored by: {self.metadata.author}")
        st.markdown("---_---")
        st.write("This page demonstrates content rendered by a dynamically loaded plugin.")
        
        st.subheader("Plugin Functionality Example")
        if st.button("Show a message from plugin"):
            st.info("Hello from the Example Built-in Plugin! 👋")

        # Example: Accessing shared data (if app_context provided it)
        # if self._app_context and "shared_data" in self._app_context:
        #     st.write("Shared data from app:", self._app_context["shared_data"])

    def on_unload(self) -> None:
        # st.toast(f"Plugin 	"{self.metadata.name}	" is being unloaded.", icon="👋")
        pass

# To make this plugin discoverable, it should be placed in a directory
# that the PluginManager scans, e.g., src/plugins/builtin/

