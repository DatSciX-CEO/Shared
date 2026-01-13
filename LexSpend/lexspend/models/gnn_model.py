"""
Graph Neural Network (GNN) model for anomaly detection using Graph Autoencoder
"""
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch_geometric.nn import SAGEConv, HeteroConv
from torch_geometric.data import HeteroData
from typing import Tuple, Optional
import logging

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from config import GNN_EMBEDDING_DIM, GNN_HIDDEN_DIM

logger = logging.getLogger(__name__)


class GraphEncoder(nn.Module):
    """Encoder for the Graph Autoencoder."""
    
    def __init__(self, input_dim: int, hidden_dim: int = GNN_HIDDEN_DIM, embedding_dim: int = GNN_EMBEDDING_DIM):
        super().__init__()
        self.input_dim = input_dim
        self.hidden_dim = hidden_dim
        self.embedding_dim = embedding_dim
        
        # Heterogeneous graph convolution layers
        # LineItem encoder
        self.line_item_conv1 = SAGEConv(input_dim, hidden_dim)
        self.line_item_conv2 = SAGEConv(hidden_dim, embedding_dim)
        
        # Timekeeper encoder (simple)
        self.timekeeper_conv = SAGEConv(1, hidden_dim)
        
        # CaseType encoder (simple)
        self.case_type_conv = SAGEConv(1, hidden_dim)
    
    def forward(self, x_dict: dict, edge_index_dict: dict) -> dict:
        """
        Forward pass through encoder.
        
        Args:
            x_dict: Dictionary of node features by node type
            edge_index_dict: Dictionary of edge indices by edge type
            
        Returns:
            Dictionary of node embeddings by node type
        """
        # Encode LineItem nodes
        line_item_x = x_dict['LineItem']
        
        # Aggregate from Timekeeper neighbors
        if ('Timekeeper', 'billed_on', 'LineItem') in edge_index_dict:
            timekeeper_edge_index = edge_index_dict[('Timekeeper', 'billed_on', 'LineItem')]
            # Get timekeeper features (we'll use simple aggregation)
            timekeeper_x = x_dict['Timekeeper']
            # For now, we'll process LineItem nodes directly
            # In a full implementation, we'd aggregate from neighbors
            line_item_hidden = F.relu(self.line_item_conv1(line_item_x, None))
        else:
            line_item_hidden = F.relu(self.line_item_conv1(line_item_x, None))
        
        line_item_embedding = self.line_item_conv2(line_item_hidden, None)
        
        # Encode Timekeeper nodes
        if 'Timekeeper' in x_dict:
            timekeeper_x = x_dict['Timekeeper']
            timekeeper_embedding = F.relu(self.timekeeper_conv(timekeeper_x, None))
        else:
            timekeeper_embedding = None
        
        # Encode CaseType nodes
        if 'CaseType' in x_dict:
            case_type_x = x_dict['CaseType']
            case_type_embedding = F.relu(self.case_type_conv(case_type_x, None))
        else:
            case_type_embedding = None
        
        return {
            'LineItem': line_item_embedding,
            'Timekeeper': timekeeper_embedding,
            'CaseType': case_type_embedding,
        }


class GraphDecoder(nn.Module):
    """Decoder for the Graph Autoencoder."""
    
    def __init__(self, embedding_dim: int, hidden_dim: int, output_dim: int):
        super().__init__()
        self.embedding_dim = embedding_dim
        self.hidden_dim = hidden_dim
        self.output_dim = output_dim
        
        # Decoder layers
        self.fc1 = nn.Linear(embedding_dim, hidden_dim)
        self.fc2 = nn.Linear(hidden_dim, output_dim)
    
    def forward(self, embedding: torch.Tensor) -> torch.Tensor:
        """
        Reconstruct node features from embedding.
        
        Args:
            embedding: Node embedding tensor
            
        Returns:
            Reconstructed features
        """
        hidden = F.relu(self.fc1(embedding))
        reconstructed = self.fc2(hidden)
        return reconstructed


class GraphAutoencoder(nn.Module):
    """Graph Autoencoder for unsupervised anomaly detection."""
    
    def __init__(self, input_dim: int, hidden_dim: int = GNN_HIDDEN_DIM, 
                 embedding_dim: int = GNN_EMBEDDING_DIM):
        super().__init__()
        self.input_dim = input_dim
        self.hidden_dim = hidden_dim
        self.embedding_dim = embedding_dim
        
        self.encoder = GraphEncoder(input_dim, hidden_dim, embedding_dim)
        self.decoder = GraphDecoder(embedding_dim, hidden_dim, input_dim)
    
    def forward(self, x_dict: dict, edge_index_dict: dict) -> Tuple[torch.Tensor, torch.Tensor]:
        """
        Forward pass: encode and decode.
        
        Args:
            x_dict: Dictionary of node features
            edge_index_dict: Dictionary of edge indices
            
        Returns:
            Tuple of (embeddings, reconstructed_features)
        """
        # Encode
        embeddings = self.encoder(x_dict, edge_index_dict)
        
        # Decode LineItem nodes
        line_item_embedding = embeddings['LineItem']
        reconstructed = self.decoder(line_item_embedding)
        
        return line_item_embedding, reconstructed
    
    def compute_reconstruction_error(self, original: torch.Tensor, reconstructed: torch.Tensor) -> torch.Tensor:
        """
        Compute reconstruction error (MSE) for each node.
        
        Args:
            original: Original node features
            reconstructed: Reconstructed node features
            
        Returns:
            Reconstruction error per node
        """
        # Compute MSE per node
        mse = F.mse_loss(reconstructed, original, reduction='none')
        # Sum across features to get error per node
        error_per_node = mse.sum(dim=1)
        return error_per_node


def train_gae(model: GraphAutoencoder, data: HeteroData, epochs: int = 50, 
               learning_rate: float = 0.001, device: str = 'cpu') -> GraphAutoencoder:
    """
    Train the Graph Autoencoder.
    
    Args:
        model: GraphAutoencoder model
        data: HeteroData graph
        epochs: Number of training epochs
        learning_rate: Learning rate
        device: Device to train on
        
    Returns:
        Trained model
    """
    model = model.to(device)
    optimizer = torch.optim.Adam(model.parameters(), lr=learning_rate)
    
    # Prepare data
    x_dict = {node_type: data[node_type].x.to(device) for node_type in data.node_types}
    edge_index_dict = {}
    for edge_type in data.edge_types:
        edge_index_dict[edge_type] = data[edge_type].edge_index.to(device)
    
    model.train()
    
    logger.info(f"Training GAE for {epochs} epochs...")
    for epoch in range(epochs):
        optimizer.zero_grad()
        
        # Forward pass
        _, reconstructed = model(x_dict, edge_index_dict)
        
        # Compute loss (reconstruction error)
        original = x_dict['LineItem']
        loss = F.mse_loss(reconstructed, original)
        
        # Backward pass
        loss.backward()
        optimizer.step()
        
        if (epoch + 1) % 10 == 0:
            logger.info(f"Epoch {epoch + 1}/{epochs}, Loss: {loss.item():.4f}")
    
    model.eval()
    logger.info("Training complete")
    return model


def compute_anomaly_scores(model: GraphAutoencoder, data: HeteroData, 
                          device: str = 'cpu') -> torch.Tensor:
    """
    Compute anomaly scores for all LineItem nodes.
    
    Args:
        model: Trained GraphAutoencoder model
        data: HeteroData graph
        device: Device to compute on
        
    Returns:
        Tensor of anomaly scores (one per LineItem node)
    """
    model.eval()
    model = model.to(device)
    
    # Prepare data
    x_dict = {node_type: data[node_type].x.to(device) for node_type in data.node_types}
    edge_index_dict = {}
    for edge_type in data.edge_types:
        edge_index_dict[edge_type] = data[edge_type].edge_index.to(device)
    
    with torch.no_grad():
        _, reconstructed = model(x_dict, edge_index_dict)
        original = x_dict['LineItem']
        scores = model.compute_reconstruction_error(original, reconstructed)
    
    # Normalize scores to [0, 1] range
    scores_normalized = (scores - scores.min()) / (scores.max() - scores.min() + 1e-8)
    
    return scores_normalized.cpu()

