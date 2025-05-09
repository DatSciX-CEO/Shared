# Machine Learning Components using LazyPredict
import streamlit as st
import pandas as pd
from lazypredict.Supervised import LazyClassifier, LazyRegressor
from sklearn.model_selection import train_test_split

# Helper to get a DataFrame from session state (e.g., loaded from EDA page)
def get_active_dataframe_for_ml(data_source_name: str = "current_eda_df") -> pd.DataFrame | None:
    return st.session_state.get(data_source_name)

def run_lazy_classifier(df: pd.DataFrame, target_column: str, test_size: float = 0.2, random_state: int = 42):
    """Runs LazyClassifier on the given DataFrame."""
    if not isinstance(df, pd.DataFrame) or target_column not in df.columns:
        st.error("Invalid DataFrame or target column specified for classification.")
        return None, None

    y = df[target_column]
    X = df.drop(columns=[target_column])

    # Ensure target is suitable for classification (e.g., not too many unique values if it's numeric)
    if pd.api.types.is_numeric_dtype(y) and y.nunique() > 30: # Heuristic
        st.warning(f"Target column '{target_column}' is numeric with {y.nunique()} unique values. Consider if regression is more appropriate or if binning is needed for classification.")
        # Forcing to int if it looks like it could be categorical integers
        if y.nunique() < 100 and (y.apply(float.is_integer).all() or y.dtype == "int64" or y.dtype == "int32") :
             y = y.astype(int)
        else:
            st.error("Target column seems continuous. LazyClassifier is for classification tasks.")
            return None,None
    elif not pd.api.types.is_numeric_dtype(y):
        # Attempt to encode if categorical string
        try:
            y = y.astype("category").cat.codes # Cleaned up spaces in "category"
        except Exception as e:
            st.error(f"Could not encode target column '{target_column}' for classification: {e}") # Corrected f-string
            return None, None

    # Handle categorical features in X by one-hot encoding (simplistic approach)
    # More sophisticated preprocessing might be needed (e.g., for high cardinality features)
    try:
        X_processed = pd.get_dummies(X, drop_first=True)
    except Exception as e:
        st.error(f"Error during one-hot encoding of features: {e}")
        return None, None

    X_train, X_test, y_train, y_test = train_test_split(X_processed, y, test_size=test_size, random_state=random_state)

    clf = LazyClassifier(verbose=0, ignore_warnings=True, custom_metric=None)
    try:
        with st.spinner("Running LazyClassifier... This may take a while."):
            models, predictions = clf.fit(X_train, X_test, y_train, y_test)
        return models, predictions
    except Exception as e:
        st.error(f"Error running LazyClassifier: {e}")
        return None, None

def run_lazy_regressor(df: pd.DataFrame, target_column: str, test_size: float = 0.2, random_state: int = 42):
    """Runs LazyRegressor on the given DataFrame."""
    if not isinstance(df, pd.DataFrame) or target_column not in df.columns:
        st.error("Invalid DataFrame or target column specified for regression.")
        return None, None

    y = df[target_column]
    X = df.drop(columns=[target_column])

    if not pd.api.types.is_numeric_dtype(y):
        st.error(f"Target column '{target_column}' must be numeric for regression.") # Corrected f-string
        return None, None

    try:
        X_processed = pd.get_dummies(X, drop_first=True)
    except Exception as e:
        st.error(f"Error during one-hot encoding of features: {e}")
        return None, None

    X_train, X_test, y_train, y_test = train_test_split(X_processed, y, test_size=test_size, random_state=random_state)

    reg = LazyRegressor(verbose=0, ignore_warnings=True, custom_metric=None)
    try:
        with st.spinner("Running LazyRegressor... This may take a while."):
            models, predictions = reg.fit(X_train, X_test, y_train, y_test)
        return models, predictions
    except Exception as e:
        st.error(f"Error running LazyRegressor: {e}")
        return None, None