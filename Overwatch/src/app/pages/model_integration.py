# Page for Model Integration with LazyPredict
import streamlit as st
import pandas as pd
from src.core.analytics.ml import lazy_utils

# Helper to get a DataFrame from session state (e.g., loaded from EDA page)
def get_active_dataframe_for_ml(data_source_name: str = "current_eda_df") -> pd.DataFrame | None:
    return st.session_state.get(data_source_name)

def app():
    st.title("Machine Learning Model Integration")
    st.write("Automatically train and compare baseline models for classification and regression tasks using LazyPredict.")

    # --- Data Source --- 
    st.subheader("1. Data for Modeling")
    df_for_ml = get_active_dataframe_for_ml()

    if df_for_ml is None:
        st.warning("No data available for modeling. Please load data in the 	'Analytics & EDA'	 page first.")
        # Optionally, add a file uploader here as well for direct ML data input
        uploaded_file_ml = st.file_uploader("Or upload a CSV/Excel file directly for ML", type=["csv", "xlsx"], key="ml_uploader")
        if uploaded_file_ml:
            try:
                if uploaded_file_ml.name.endswith(".csv"):
                    df_for_ml = pd.read_csv(uploaded_file_ml)
                else:
                    df_for_ml = pd.read_excel(uploaded_file_ml)
                st.session_state.current_eda_df = df_for_ml # Save it for consistency
                st.success(f"Successfully loaded {uploaded_file_ml.name} for modeling.")
            except Exception as e:
                st.error(f"Error loading file: {e}")
                return
        else:
            return 

    st.write("Preview of the first 5 rows of your data:")
    st.dataframe(df_for_ml.head())

    # --- Model Configuration --- 
    st.markdown("---_---")
    st.subheader("2. Configure Modeling Task")

    columns = df_for_ml.columns.tolist()
    if not columns:
        st.error("DataFrame has no columns.")
        return

    target_column = st.selectbox("Select Target Column (Y):", options=columns, key="ml_target")
    
    problem_type = st.radio("Select Problem Type:", (	"Classification	", 	"Regression	"), key="ml_problem_type")

    # Advanced options (optional)
    with st.expander("Advanced Settings"):
        test_size = st.slider("Test Set Size (fraction):", min_value=0.1, max_value=0.5, value=0.2, step=0.05, key="ml_test_size")
        random_state = st.number_input("Random State (for reproducibility):", value=42, step=1, key="ml_random_state")

    if st.button("Run Model Comparison", key="run_lazy_predict"):
        if not target_column:
            st.error("Please select a target column.")
            return

        models_df = None
        # predictions_df = None # Predictions might be too large to display directly or less useful for initial comparison

        if problem_type == "Classification":
            st.write(f"Running LazyClassifier for target 	'{target_column}'	...")
            models_df, _ = lazy_utils.run_lazy_classifier(df_for_ml, target_column, test_size, random_state)
        elif problem_type == "Regression":
            st.write(f"Running LazyRegressor for target 	'{target_column}'	...")
            models_df, _ = lazy_utils.run_lazy_regressor(df_for_ml, target_column, test_size, random_state)
        
        if models_df is not None:
            st.markdown("---_---")
            st.subheader("3. Model Comparison Results")
            st.write(f"Top performing models for **{problem_type}** on target **{target_column}**:")
            st.dataframe(models_df)
            
            # Provide download for the results
            csv = models_df.to_csv(index=True).encode(	'utf-8	')
            st.download_button(
                label="Download Model Results as CSV",
                data=csv,
                file_name=f"lazy_{problem_type.lower()}_results_{target_column}.csv",
                mime=	'text/csv	',
            )
        else:
            st.error("Model training failed or no results were returned. Check logs or previous warnings.")

# Initialize session state for current_eda_df if not already present
if "current_eda_df" not in st.session_state:
    st.session_state.current_eda_df = None

