import streamlit as st

def app():
    st.title("Welcome to Overwatch Command Center")
    st.write("This is the central hub for your data operations.")
    st.write("Navigate using the sidebar to access different modules.")

    st.header("Quick Access")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Go to Database Manager"):
            # This is a conceptual navigation, actual navigation is handled by sidebar radio in main.py
            # For a more direct navigation, would need to manage session state or use a different navigation pattern
            st.info("Please use the sidebar to navigate to Database Manager.") 
    with col2:
        if st.button("Go to Analytics & EDA"):
            st.info("Please use the sidebar to navigate to Analytics & EDA.")

    st.markdown("---_---")
    st.subheader("About Overwatch")
    st.markdown("""
    Overwatch is designed to be a modular and extensible platform for:
    - Universal Database Connectivity
    - Comprehensive Analytics & EDA
    - Machine Learning Model Integration
    - Workflow Automation
    - Custom Plugin Support
    """)

