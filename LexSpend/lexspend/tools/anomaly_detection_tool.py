"""
Anomaly Detection Tool for ADK - Uses GNN to detect document review anomalies
Using FunctionTool pattern (official ADK approach)
"""
import pandas as pd
import torch
from typing import Dict, Any, Optional
import logging
from google.adk.tools import FunctionTool

from ..models.graph_builder import GraphBuilder
from ..models.gnn_model import GraphAutoencoder, train_gae, compute_anomaly_scores
from ..data.storage import ResultsStorage
from ..data.preprocessing import prepare_data_for_analysis

# Import config
try:
    import sys
    import os
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(current_dir)))
    if project_root not in sys.path:
        sys.path.insert(0, project_root)
    from config import GNN_EPOCHS, GNN_LEARNING_RATE, GNN_EMBEDDING_DIM, GNN_HIDDEN_DIM
except ImportError:
    # Fallback defaults
    GNN_EPOCHS = 50
    GNN_LEARNING_RATE = 0.001
    GNN_EMBEDDING_DIM = 128
    GNN_HIDDEN_DIM = 64

logger = logging.getLogger(__name__)


def detect_anomalies(file_path: str, train_model: bool = True) -> str:
    """
    Run anomaly detection on legal spend data using Graph Neural Networks.

    Args:
        file_path: Path to CSV or Excel file with legal spend data
        train_model: Whether to train the model (True) or use pre-trained (False)

    Returns:
        String summary of results including high-risk items
    """
    try:
        # Load and validate data
        success, message, df = prepare_data_for_analysis(file_path)
        if not success:
            return f"Error: {message}"
        
        logger.info(f"Processing {len(df)} line items for anomaly detection")
        
        # Build graph
        graph_builder = GraphBuilder()
        graph, node_mappings = graph_builder.build_graph(df)
        
        # Get input dimension from LineItem features
        input_dim = graph['LineItem'].x.shape[1]
        
        # Initialize model
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        model = GraphAutoencoder(
            input_dim=input_dim,
            hidden_dim=GNN_HIDDEN_DIM,
            embedding_dim=GNN_EMBEDDING_DIM
        )
        
        # Train model
        if train_model:
            model = train_gae(
                model, graph, 
                epochs=GNN_EPOCHS,
                learning_rate=GNN_LEARNING_RATE,
                device=device
            )
        
        # Compute anomaly scores
        scores = compute_anomaly_scores(model, graph, device=device)
        
        # Convert scores to pandas Series with original DataFrame index
        score_series = pd.Series(scores.numpy(), index=df.index)
        
        # Save results
        storage = ResultsStorage()
        session_id = storage.save_results(file_path, df, score_series)
        
        # Generate summary
        summary = []
        summary.append(f"Anomaly detection complete for {len(df)} line items")
        summary.append(f"Results saved to database (session {session_id})")
        summary.append(f"\nReview Score Statistics:")
        summary.append(f"  Mean: {score_series.mean():.4f}")
        summary.append(f"  Median: {score_series.median():.4f}")
        summary.append(f"  Max: {score_series.max():.4f}")
        summary.append(f"  Min: {score_series.min():.4f}")
        
        # High-risk items (score > 0.7)
        high_risk = score_series[score_series > 0.7]
        summary.append(f"\nHigh-risk items (score > 0.7): {len(high_risk)}")
        
        if len(high_risk) > 0:
            summary.append("\nTop 10 highest-risk items:")
            top_risk = high_risk.nlargest(10)
            for idx, score in top_risk.items():
                row = df.loc[idx]
                desc = row.get("Line Item Description", "N/A")[:50]
                pos = row.get("Position Title", "N/A")
                cost = row.get("Cost", "N/A")
                summary.append(f"  Score {score:.4f}: {desc}... ({pos}, Cost: ${cost})")
        
        return "\n".join(summary)
        
    except Exception as e:
        logger.error(f"Error in anomaly detection: {e}", exc_info=True)
        return f"Error during anomaly detection: {type(e).__name__}: {str(e)}"


# Create FunctionTool wrapper
# FunctionTool uses the function name and docstring automatically for description
AnomalyDetectionTool = FunctionTool(func=detect_anomalies)
