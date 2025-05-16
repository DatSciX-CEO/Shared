# src/app/pages/4_🧩_Plugins.py 
# (Choose a suitable number and emoji, e.g., 9_🧩_Plugins.py if you have many core pages)
import streamlit as st

# Optional: Consistent page config if not inheriting from main.py's config
# st.set_page_config(layout="wide") 

st.header("🧩 Plugin Content Viewer")
st.markdown("---")

# Retrieve the plugin manager and the name of the plugin to display from session state
if "plugin_manager" not in st.session_state or st.session_state.plugin_manager is None:
    st.error("Plugin manager not initialized. This indicates an issue with the main application setup.")
    st.warning("Please ensure you have run the main application first or try returning to the Home page.")
    if st.button("Go to Home"):
        # Ensure the path to your home page file is correct
        st.switch_page("pages/0_🏠_Home.py") 
    st.stop()

plugin_manager = st.session_state.plugin_manager
active_plugin_name = st.session_state.get("active_plugin_for_viewer")

if active_plugin_name:
    plugin = plugin_manager.get_plugin(active_plugin_name)
    if plugin:
        # Display plugin metadata
        plugin_icon = plugin.metadata.icon or "⚙️" # Default icon if plugin doesn't provide one
        st.subheader(f"{plugin_icon} {plugin.metadata.name}", anchor=False)
        st.caption(f"Version {plugin.metadata.version} by {plugin.metadata.author}")
        st.markdown(f"> {plugin.metadata.description}")
        st.markdown("---")
        
        # Render the plugin's main content
        try:
            plugin.render_page_content()
        except Exception as e:
            st.error(f"Error rendering content for plugin '{plugin.metadata.name}': {e}")
            st.exception(e) # Shows full traceback for debugging
    else:
        st.error(f"Could not load plugin: '{active_plugin_name}'. It might have been unloaded or an error occurred.")
        st.info("Please select a valid plugin from the 'Plugin Controls' section in the sidebar.")
else:
    st.info("Select a plugin from the 'Plugin Controls' section in the sidebar to view its content here.")
    st.caption("This page is dedicated to displaying content from loaded plugins.")

    # Optionally, list available plugins that can render content
    loaded_plugins = plugin_manager.get_all_plugins()
    content_plugins = [p for p in loaded_plugins if hasattr(p, 'render_page_content')]
    if content_plugins:
        st.markdown("#### Available Plugins with Pages:")
        for p in content_plugins:
            if st.button(f"View {p.metadata.name}", key=f"quick_view_{p.metadata.name}"):
                st.session_state.active_plugin_for_viewer = p.metadata.name
                st.experimental_rerun() # Rerun to display the newly selected plugin
    else:
        st.write("No plugins with displayable pages are currently loaded.")

