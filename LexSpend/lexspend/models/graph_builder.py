"""
Graph construction from tabular legal spend data
"""
import pandas as pd
import numpy as np
import torch
from torch_geometric.data import HeteroData
from typing import Dict, Tuple, Optional
import logging

try:
    from .embeddings import get_embedder
except ImportError:
    # Fallback for direct execution
    import sys
    import os
    sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
    from models.embeddings import get_embedder

logger = logging.getLogger(__name__)


class GraphBuilder:
    """Builds heterogeneous graphs from legal spend tabular data."""
    
    def __init__(self):
        self.embedder = get_embedder()
    
    def build_graph(self, df: pd.DataFrame) -> Tuple[HeteroData, Dict[str, int]]:
        """
        Build a heterogeneous graph from legal spend DataFrame.
        
        Node types:
        - LineItem: One node per row (the items we want to score)
        - Timekeeper: One node per unique Position Title
        - CaseType: One node per unique Type of Case
        
        Edge types:
        - Timekeeper -> LineItem (billed_on)
        - CaseType -> LineItem (includes)
        
        Args:
            df: DataFrame with legal spend data (must have required columns)
            
        Returns:
            Tuple of (HeteroData graph, node_index_mapping dict)
        """
        logger.info("Building graph from DataFrame...")
        
        # Ensure required columns exist
        required_cols = ["Position Title", "Units", "Bill Rate", "Cost", 
                         "Line Item Description", "Type of Case"]
        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            raise ValueError(f"Missing required columns: {missing_cols}")
        
        # Create node index mappings
        line_item_indices = {idx: i for i, idx in enumerate(df.index)}
        timekeeper_names = df["Position Title"].unique()
        timekeeper_indices = {name: i for i, name in enumerate(timekeeper_names)}
        case_types = df["Type of Case"].unique()
        case_type_indices = {case_type: i for i, case_type in enumerate(case_types)}
        
        num_line_items = len(df)
        num_timekeepers = len(timekeeper_names)
        num_case_types = len(case_types)
        
        logger.info(f"Graph nodes: {num_line_items} LineItems, {num_timekeepers} Timekeepers, {num_case_types} CaseTypes")
        
        # Initialize HeteroData
        data = HeteroData()
        
        # 1. Create LineItem node features
        # Features: Units, Bill Rate, Cost, Text Embedding
        line_item_features = []
        
        # Get text embeddings for descriptions
        descriptions = df["Line Item Description"].tolist()
        text_embeddings = self.embedder.embed_batch(descriptions)
        
        for idx, row in df.iterrows():
            features = []
            # Numeric features
            features.append(float(row["Units"]) if pd.notna(row["Units"]) else 0.0)
            features.append(float(row["Bill Rate"]) if pd.notna(row["Bill Rate"]) else 0.0)
            features.append(float(row["Cost"]) if pd.notna(row["Cost"]) else 0.0)
            # Text embedding
            line_item_idx = line_item_indices[idx]
            features.extend(text_embeddings[line_item_idx].tolist())
            
            line_item_features.append(features)
        
        data['LineItem'].x = torch.tensor(line_item_features, dtype=torch.float)
        logger.info(f"LineItem features shape: {data['LineItem'].x.shape}")
        
        # 2. Create Timekeeper node features (simple one-hot or just use as structural)
        # For now, we'll use simple features (could be enhanced with timekeeper metadata)
        timekeeper_features = torch.ones(num_timekeepers, 1)  # Placeholder
        data['Timekeeper'].x = timekeeper_features
        
        # 3. Create CaseType node features
        case_type_features = torch.ones(num_case_types, 1)  # Placeholder
        data['CaseType'].x = case_type_features
        
        # 4. Create edges: Timekeeper -> LineItem
        timekeeper_edges = []
        for idx, row in df.iterrows():
            timekeeper_name = row["Position Title"]
            timekeeper_idx = timekeeper_indices[timekeeper_name]
            line_item_idx = line_item_indices[idx]
            timekeeper_edges.append([timekeeper_idx, line_item_idx])
        
        if timekeeper_edges:
            timekeeper_edge_index = torch.tensor(timekeeper_edges, dtype=torch.long).t().contiguous()
            data['Timekeeper', 'billed_on', 'LineItem'].edge_index = timekeeper_edge_index
            logger.info(f"Timekeeper->LineItem edges: {timekeeper_edge_index.shape[1]}")
        
        # 5. Create edges: CaseType -> LineItem
        case_type_edges = []
        for idx, row in df.iterrows():
            case_type = row["Type of Case"]
            case_type_idx = case_type_indices[case_type]
            line_item_idx = line_item_indices[idx]
            case_type_edges.append([case_type_idx, line_item_idx])
        
        if case_type_edges:
            case_type_edge_index = torch.tensor(case_type_edges, dtype=torch.long).t().contiguous()
            data['CaseType', 'includes', 'LineItem'].edge_index = case_type_edge_index
            logger.info(f"CaseType->LineItem edges: {case_type_edge_index.shape[1]}")
        
        # Store node index mappings for later reference
        node_mappings = {
            'line_item_indices': line_item_indices,
            'timekeeper_indices': timekeeper_indices,
            'case_type_indices': case_type_indices,
            'timekeeper_names': timekeeper_names,
            'case_types': case_types,
        }
        
        logger.info("Graph construction complete")
        return data, node_mappings

