"""
Unit tests for GNN components
"""
import unittest
import os
import sys
import torch
import pandas as pd

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from lexspend.models.embeddings import TextEmbedder, get_embedder
from lexspend.models.graph_builder import GraphBuilder
from lexspend.models.gnn_model import GraphAutoencoder, GraphEncoder, GraphDecoder


class TestEmbeddings(unittest.TestCase):
    """Test text embeddings"""
    
    def test_embedder_initialization(self):
        """Test embedder can be initialized"""
        embedder = TextEmbedder()
        self.assertIsNotNone(embedder)
    
    def test_get_embedder_singleton(self):
        """Test get_embedder returns singleton"""
        embedder1 = get_embedder()
        embedder2 = get_embedder()
        self.assertIs(embedder1, embedder2)
    
    @unittest.skip("Requires downloading model - slow for unit tests")
    def test_embed_text(self):
        """Test embedding a single text (skipped - requires model download)"""
        embedder = TextEmbedder()
        text = "Document review and analysis"
        embedding = embedder.embed_text(text)
        self.assertEqual(len(embedding), 384)  # all-MiniLM-L6-v2 dimension


class TestGraphBuilder(unittest.TestCase):
    """Test graph builder"""
    
    def setUp(self):
        """Create test DataFrame"""
        self.test_df = pd.DataFrame({
            'Position Title': ['Partner', 'Associate', 'Paralegal'],
            'Units': [2.0, 5.0, 8.0],
            'Bill Rate': [950.0, 450.0, 150.0],
            'Cost': [1900.0, 2250.0, 1200.0],
            'Line Item Description': [
                'Case strategy meeting',
                'Document review and analysis',
                'Document review - first pass'
            ],
            'Type of Case': ['Litigation', 'Litigation', 'Contract']
        })
    
    def test_graph_builder_initialization(self):
        """Test graph builder can be initialized"""
        builder = GraphBuilder()
        self.assertIsNotNone(builder)
    
    @unittest.skip("Requires model download and graph construction - slow")
    def test_build_graph(self):
        """Test graph construction (skipped - requires model download)"""
        builder = GraphBuilder()
        graph, node_mappings = builder.build_graph(self.test_df)
        
        self.assertIsNotNone(graph)
        self.assertIn('LineItem', graph.node_types)
        self.assertIn('Timekeeper', graph.node_types)
        self.assertIn('CaseType', graph.node_types)


class TestGNNModel(unittest.TestCase):
    """Test GNN model components"""
    
    def test_graph_encoder_initialization(self):
        """Test graph encoder can be initialized"""
        encoder = GraphEncoder(input_dim=10, hidden_dim=64, embedding_dim=128)
        self.assertIsNotNone(encoder)
        self.assertEqual(encoder.input_dim, 10)
        self.assertEqual(encoder.hidden_dim, 64)
        self.assertEqual(encoder.embedding_dim, 128)
    
    def test_graph_decoder_initialization(self):
        """Test graph decoder can be initialized"""
        decoder = GraphDecoder(embedding_dim=128, hidden_dim=64, output_dim=10)
        self.assertIsNotNone(decoder)
        self.assertEqual(decoder.embedding_dim, 128)
        self.assertEqual(decoder.hidden_dim, 64)
        self.assertEqual(decoder.output_dim, 10)
    
    def test_graph_autoencoder_initialization(self):
        """Test graph autoencoder can be initialized"""
        gae = GraphAutoencoder(input_dim=10, hidden_dim=64, embedding_dim=128)
        self.assertIsNotNone(gae)
        self.assertIsNotNone(gae.encoder)
        self.assertIsNotNone(gae.decoder)


if __name__ == '__main__':
    unittest.main()

