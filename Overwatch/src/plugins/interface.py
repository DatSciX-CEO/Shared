# Plugin Interface Definitions for Overwatch Command Center
from abc import ABC, abstractmethod
from typing import Any, Dict
import streamlit as st

class PluginMetadata:
    """Holds metadata for a plugin."""
    def __init__(self, name: str, version: str, description: str, author: str, icon: str | None = None): # Add optional icon
        self.name = name
        self.version = version
        self.description = description
        self.author = author
        self.icon = icon  # Store the icon, plugins can provide it or it can be None

class OverwatchPlugin(ABC):
    """Abstract base class for all Overwatch plugins."""

    @property
    @abstractmethod
    def metadata(self) -> PluginMetadata:
        """Return metadata for the plugin."""
        pass

    @abstractmethod
    def initialize(self, app_context: Dict[str, Any]) -> None:
        """
        Called when the plugin is loaded. 
        `app_context` can provide access to shared resources or configurations if needed.
        Example: app_context.get("db_manager"), app_context.get("session_state")
        """
        pass

    @abstractmethod
    def render_sidebar_contribution(self) -> None:
        """
        Optional: Allows the plugin to add elements to the main sidebar.
        This could be a link to a plugin-specific page or a small control panel.
        Example: if st.sidebar.button(f"{self.metadata.name} Page"):
                    st.session_state.current_page_from_plugin = self.metadata.name 
        """
        pass

    @abstractmethod
    def render_page_content(self) -> None:
        """
        Optional: If the plugin contributes a full page, this method renders its content.
        This method would be called if navigation (e.g., from sidebar) directs to this plugin's page.
        Example: st.title(self.metadata.name)
                 st.write("Content for my plugin page.")
        """
        pass

    # Potentially add other methods for different types of plugin contributions,
    # e.g., adding a new data processing step, a new visualization type, etc.
    # def register_data_processor(self, name: str, function: Callable) -> None:
    #     pass

    def on_unload(self) -> None:
        """Called when the plugin is about to be unloaded (optional)."""
        pass

# Application context could be a simple dictionary or a more structured class
# For now, it can be used to pass Streamlit's session_state or other shared objects.
AppContext = Dict[str, Any]

