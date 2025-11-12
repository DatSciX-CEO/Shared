"""
Results Table Component for LexSpend - Displays anomaly detection results
"""
import streamlit as st
import pandas as pd
from typing import Optional
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from lexspend.data.storage import ResultsStorage


def display_anomaly_results(session_id: Optional[int] = None, threshold: float = 0.7):
    """
    Display anomaly detection results with filtering and sorting.
    
    Args:
        session_id: Optional session ID to load specific session (None for most recent)
        threshold: Threshold for filtering high-risk items (0-1)
    """
    storage = ResultsStorage()
    
    # Load results
    try:
        results_df = storage.load_results(session_id)
        
        if results_df.empty:
            st.warning("No anomaly detection results found. Run anomaly detection first.")
            return
        
        # Parse review_score if it's a string
        if 'review_score' in results_df.columns:
            results_df['review_score'] = pd.to_numeric(results_df['review_score'], errors='coerce')
        
        st.subheader("📊 Anomaly Detection Results")
        
        # Statistics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Items", len(results_df))
        with col2:
            high_risk_count = len(results_df[results_df['review_score'] > threshold])
            st.metric("High-Risk Items", high_risk_count, delta=f"Score > {threshold}")
        with col3:
            st.metric("Mean Score", f"{results_df['review_score'].mean():.4f}")
        with col4:
            st.metric("Max Score", f"{results_df['review_score'].max():.4f}")
        
        st.markdown("---")
        
        # Threshold slider
        threshold = st.slider(
            "Review Score Threshold",
            min_value=0.0,
            max_value=1.0,
            value=threshold,
            step=0.05,
            help="Items with scores above this threshold are considered high-risk"
        )
        
        # Filter by threshold
        filtered_df = results_df[results_df['review_score'] >= threshold].copy()
        
        if len(filtered_df) == 0:
            st.info(f"No items found with review score >= {threshold}")
            return
        
        # Sort options
        sort_by = st.selectbox(
            "Sort by",
            options=["review_score", "line_item_index"],
            index=0,
            format_func=lambda x: "Review Score (High to Low)" if x == "review_score" else "Line Item Index"
        )
        
        ascending = sort_by != "review_score"
        filtered_df = filtered_df.sort_values(by=sort_by, ascending=ascending)
        
        # Display table
        st.subheader(f"High-Risk Items (Score >= {threshold})")
        
        # Prepare display columns
        display_columns = ['line_item_index', 'review_score']
        
        # Try to parse original_data if it exists
        if 'original_data' in filtered_df.columns:
            try:
                import json
                # Parse JSON strings in original_data
                parsed_data = []
                for idx, row in filtered_df.iterrows():
                    try:
                        data = json.loads(row['original_data'])
                        parsed_data.append(data)
                    except:
                        parsed_data.append({})
                
                # Create DataFrame from parsed data
                parsed_df = pd.DataFrame(parsed_data)
                
                # Merge with scores
                display_df = filtered_df[['line_item_index', 'review_score']].copy()
                for col in parsed_df.columns:
                    if col not in display_df.columns:
                        display_df[col] = [row.get(col, 'N/A') for row in parsed_data]
                
                # Reorder columns to show score first, then original data
                score_col = display_df.pop('review_score')
                display_df.insert(0, 'review_score', score_col)
                
            except Exception as e:
                st.warning(f"Could not parse original data: {e}")
                display_df = filtered_df[display_columns]
        else:
            display_df = filtered_df[display_columns]
        
        # Display the table
        st.dataframe(
            display_df,
            use_container_width=True,
            height=400
        )
        
        # Export button
        if st.button("📥 Export Filtered Results"):
            csv = display_df.to_csv(index=False)
            st.download_button(
                label="Download CSV",
                data=csv,
                file_name=f"anomaly_results_threshold_{threshold:.2f}.csv",
                mime="text/csv"
            )
        
        # Show top 10 highest risk items
        st.markdown("---")
        st.subheader("🔴 Top 10 Highest-Risk Items")
        top_10 = filtered_df.nlargest(10, 'review_score')
        
        for idx, row in top_10.iterrows():
            with st.expander(f"Score: {row['review_score']:.4f} - Line Item {row['line_item_index']}"):
                if 'original_data' in row:
                    try:
                        import json
                        data = json.loads(row['original_data'])
                        st.json(data)
                    except:
                        st.text(str(row['original_data']))
                else:
                    st.text(str(row.to_dict()))
    
    except Exception as e:
        st.error(f"Error loading results: {type(e).__name__}: {str(e)}")


def display_recent_sessions():
    """
    Display recent analysis sessions.
    """
    storage = ResultsStorage()
    
    try:
        sessions_df = storage.get_recent_sessions(limit=10)
        
        if sessions_df.empty:
            st.info("No analysis sessions found.")
            return
        
        st.subheader("📋 Recent Analysis Sessions")
        
        # Display sessions table
        st.dataframe(
            sessions_df,
            use_container_width=True,
            column_config={
                "analysis_date": st.column_config.DatetimeColumn("Analysis Date"),
                "total_items": st.column_config.NumberColumn("Total Items"),
                "high_risk_items": st.column_config.NumberColumn("High-Risk Items"),
            }
        )
        
        # Allow selection
        if len(sessions_df) > 0:
            selected_session = st.selectbox(
                "Select session to view",
                options=sessions_df['id'].tolist(),
                format_func=lambda x: f"Session {x} - {sessions_df[sessions_df['id']==x]['file_path'].iloc[0]}"
            )
            return selected_session
    
    except Exception as e:
        st.error(f"Error loading sessions: {type(e).__name__}: {str(e)}")
    
    return None

