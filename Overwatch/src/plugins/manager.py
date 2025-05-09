# Plugin Manager for Overwatch Command Center
import importlib
import os
import sys
import inspect
from typing import Dict, List, Type
import streamlit as st # For logging/displaying plugin info, if needed directly here

from src.plugins.interface import OverwatchPlugin, AppContext, PluginMetadata

# Define paths for plugins
BUILTIN_PLUGIN_DIR = os.path.join(os.path.dirname(__file__), "builtin")
EXTERNAL_PLUGIN_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "plugins_ext") # As per Overwatch.txt structure

class PluginManager:
    def __init__(self, app_context: AppContext):
        self.app_context = app_context
        self.loaded_plugins: Dict[str, OverwatchPlugin] = {}
        self._ensure_plugin_dirs_exist()

    def _ensure_plugin_dirs_exist(self):
        os.makedirs(BUILTIN_PLUGIN_DIR, exist_ok=True)
        os.makedirs(EXTERNAL_PLUGIN_DIR, exist_ok=True)

    def discover_plugins(self) -> List[Type[OverwatchPlugin]]:
        """Discovers plugin classes from specified directories."""
        discovered_plugin_classes: List[Type[OverwatchPlugin]] = []
        plugin_paths = [BUILTIN_PLUGIN_DIR, EXTERNAL_PLUGIN_DIR]

        for plugin_dir in plugin_paths:
            if not os.path.isdir(plugin_dir):
                # st.warning(f"Plugin directory not found: {plugin_dir}")
                continue

            # Add plugin directory to sys.path to allow direct imports
            if plugin_dir not in sys.path:
                sys.path.insert(0, plugin_dir)

            for item_name in os.listdir(plugin_dir):
                item_path = os.path.join(plugin_dir, item_name)
                module_name = None

                if os.path.isfile(item_path) and item_name.endswith(".py") and item_name != "__init__.py":
                    module_name = item_name[:-3]
                elif os.path.isdir(item_path) and os.path.exists(os.path.join(item_path, "__init__.py")):
                    # This is a package-based plugin
                    module_name = item_name

                if module_name:
                    try:
                        module = importlib.import_module(module_name)
                        for name, obj in inspect.getmembers(module):
                            if inspect.isclass(obj) and issubclass(obj, OverwatchPlugin) and obj is not OverwatchPlugin:
                                if obj not in discovered_plugin_classes: # Avoid duplicates
                                    discovered_plugin_classes.append(obj)
                                    # print(f"Discovered plugin class: {obj.__name__} from {module_name}") # Debug
                    except ImportError as e:
                        st.error(f"Error importing plugin module '{module_name}' from '{plugin_dir}': {e}") # Corrected
                    except Exception as e:
                        st.error(f"Unexpected error discovering plugin '{module_name}' from '{plugin_dir}': {e}") # Corrected

            # Clean up sys.path if added
            # if plugin_dir in sys.path and plugin_dir != BUILTIN_PLUGIN_DIR: # Keep builtin path for now
            #     sys.path.remove(plugin_dir)

        return discovered_plugin_classes

    def load_plugins(self):
        """Loads all discovered plugins."""
        plugin_classes = self.discover_plugins()
        for plugin_class in plugin_classes:
            try:
                plugin_instance = plugin_class() # Instantiate the plugin
                plugin_metadata = plugin_instance.metadata # Access metadata property
                if plugin_metadata.name in self.loaded_plugins:
                    st.warning(f"Plugin with name '{plugin_metadata.name}' already loaded. Skipping duplicate.") # Corrected
                    continue

                plugin_instance.initialize(self.app_context)
                self.loaded_plugins[plugin_metadata.name] = plugin_instance
                st.success(f"Successfully loaded plugin: {plugin_metadata.name} v{plugin_metadata.version}")
            except Exception as e:
                st.error(f"Error loading plugin {plugin_class.__name__}: {e}")

    def get_plugin(self, name: str) -> OverwatchPlugin | None:
        """Gets a loaded plugin by name."""
        return self.loaded_plugins.get(name)

    def get_all_plugins(self) -> List[OverwatchPlugin]:
        """Returns a list of all loaded plugin instances."""
        return list(self.loaded_plugins.values())

    def unload_plugin(self, name: str):
        """Unloads a specific plugin."""
        plugin = self.loaded_plugins.pop(name, None)
        if plugin:
            try:
                plugin.on_unload()
                st.info(f"Plugin '{name}' unloaded.") # Corrected
            except Exception as e:
                st.error(f"Error during unload of plugin {name}: {e}")

    def unload_all_plugins(self):
        """Unloads all currently loaded plugins."""
        for name in list(self.loaded_plugins.keys()): # Iterate over a copy of keys
            self.unload_plugin(name)

# Example of how AppContext might be structured or used:
# app_context = {
#     "session_state": st.session_state,
#     "db_manager": my_db_manager_instance, # if plugins need DB access
#     "config": my_app_config
# }

# For testing purposes (run this file directly)
if __name__ == "__main__":
    # Create dummy app_context for testing
    class MockSessionState(dict):
        pass

    if "session_state" not in globals(): # Simple check if running in streamlit context
        mock_session = MockSessionState()
        app_context_test: AppContext = {"session_state": mock_session}
    else:
        app_context_test: AppContext = {"session_state": st.session_state}

    # Create a dummy plugin for testing in plugins_ext or builtin
    # Example: /home/ubuntu/overwatch_command_center/src/plugins/builtin/my_test_plugin.py
    # Contents of my_test_plugin.py:
    # from src.plugins.interface import OverwatchPlugin, PluginMetadata, AppContext
    # import streamlit as st
    # class MyTestPlugin(OverwatchPlugin):
    #     @property
    #     def metadata(self) -> PluginMetadata:
    #         return PluginMetadata(name="Test Plugin", version="0.1", description="A test plugin.", author="Test Author")
    #     def initialize(self, app_context: AppContext):
    #         st.write(f"Test Plugin Initialized! App context keys: {list(app_context.keys())}")
    #     def render_sidebar_contribution(self):
    #         if st.sidebar.button("Test Plugin Page"):
    #             self.app_context["session_state"].current_page_from_plugin = self.metadata.name
    #     def render_page_content(self):
    #         st.title(self.metadata.name)
    #         st.write("This is the content from the Test Plugin.")

    print(f"Looking for plugins in: {BUILTIN_PLUGIN_DIR} and {EXTERNAL_PLUGIN_DIR}")
    manager = PluginManager(app_context=app_context_test)
    manager.load_plugins()

    print("\nLoaded plugins:")
    for name, plugin_obj in manager.loaded_plugins.items():
        print(f"- {name}: {plugin_obj.metadata.description}")

    # This test won't show Streamlit UI elements unless run via `streamlit run manager.py`
    # To test UI contributions, you would integrate this into the main Streamlit app.