"""
Test cases for the External Common Sense Knowledge Base Interface.
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import json
import os
import tempfile

from godelOS.common_sense.external_kb_interface import ExternalCommonSenseKB_Interface


class TestExternalCommonSenseKB_Interface(unittest.TestCase):
    """Test cases for the ExternalCommonSenseKB_Interface."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.knowledge_store = Mock()
        self.cache_system = Mock()
        
        # Create a temporary directory for cache
        self.temp_dir = tempfile.TemporaryDirectory()
        self.cache_dir = self.temp_dir.name
        
        # Create the interface with mocked dependencies
        self.interface = ExternalCommonSenseKB_Interface(
            knowledge_store=self.knowledge_store,
            cache_system=self.cache_system,
            cache_dir=self.cache_dir,
            wordnet_enabled=False,  # Disable for testing
            conceptnet_enabled=False,  # Disable for testing
            offline_mode=True  # Use offline mode for testing
        )
    
    def tearDown(self):
        """Tear down test fixtures."""
        self.temp_dir.cleanup()
    
    def test_initialization(self):
        """Test initialization of the interface."""
        self.assertEqual(self.interface.knowledge_store, self.knowledge_store)
        self.assertEqual(self.interface.cache_system, self.cache_system)
        self.assertEqual(self.interface.cache_dir, self.cache_dir)
        self.assertFalse(self.interface.wordnet_enabled)
        self.assertFalse(self.interface.conceptnet_enabled)
        self.assertTrue(self.interface.offline_mode)
    
    def test_query_concept_offline_mode(self):
        """Test querying a concept in offline mode."""
        # In offline mode, should return fallback knowledge
        result = self.interface.query_concept("test_concept")
        
        self.assertEqual(result["concept"], "test_concept")
        self.assertEqual(result["relations"], [])
        self.assertEqual(result["definitions"], [])
        self.assertEqual(result["source"], ["fallback"])
    
    @patch('godelOS.common_sense.external_kb_interface.requests.get')
    def test_query_concept_with_conceptnet(self, mock_get):
        """Test querying a concept with ConceptNet enabled."""
        # Enable ConceptNet for this test
        self.interface.conceptnet_enabled = True
        self.interface.offline_mode = False
        
        # Mock the ConceptNet API response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "edges": [
                {
                    "start": {"label": "test"},
                    "rel": {"label": "IsA"},
                    "end": {"label": "concept"},
                    "weight": 0.9
                }
            ]
        }
        mock_get.return_value = mock_response
        
        # Query the concept
        result = self.interface.query_concept("test")
        
        # Check that the API was called
        mock_get.assert_called_once()
        
        # Check the result
        self.assertEqual(result["concept"], "test")
        self.assertEqual(len(result["relations"]), 1)
        self.assertEqual(result["relations"][0]["source"], "test")
        self.assertEqual(result["relations"][0]["relation"], "is_a")
        self.assertEqual(result["relations"][0]["target"], "concept")
        self.assertEqual(result["relations"][0]["weight"], 0.9)
        self.assertEqual(result["relations"][0]["source_kb"], "conceptnet")
        self.assertIn("conceptnet", result["source"])
    
    @patch('godelOS.common_sense.external_kb_interface.wn')
    def test_query_concept_with_wordnet(self, mock_wn):
        """Test querying a concept with WordNet enabled."""
        # Enable WordNet for this test
        self.interface.wordnet_enabled = True
        self.interface.offline_mode = False
        
        # Mock WordNet synsets
        mock_synset = Mock()
        mock_synset.definition.return_value = "A test definition"
        mock_synset.name.return_value = "test.n.01"
        mock_synset.hypernyms.return_value = []
        mock_synset.hyponyms.return_value = []
        mock_synset.part_meronyms.return_value = []
        mock_synset.part_holonyms.return_value = []
        
        mock_wn.synsets.return_value = [mock_synset]
        
        # Query the concept
        result = self.interface.query_concept("test")
        
        # Check that WordNet was called
        mock_wn.synsets.assert_called_once_with("test")
        
        # Check the result
        self.assertEqual(result["concept"], "test")
        self.assertEqual(len(result["definitions"]), 1)
        self.assertEqual(result["definitions"][0], "A test definition")
        self.assertIn("wordnet", result["source"])
    
    def test_query_relation(self):
        """Test querying relations between concepts."""
        # Mock query_concept to return predefined relations
        self.interface.query_concept = Mock(return_value={
            "concept": "source",
            "relations": [
                {
                    "source": "source",
                    "relation": "test_relation",
                    "target": "target",
                    "weight": 0.8,
                    "source_kb": "test"
                }
            ],
            "definitions": [],
            "source": ["test"]
        })
        
        # Query the relation
        result = self.interface.query_relation("source", "target", "test_relation")
        
        # Check the result
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["source"], "source")
        self.assertEqual(result[0]["relation"], "test_relation")
        self.assertEqual(result[0]["target"], "target")
        self.assertEqual(result[0]["weight"], 0.8)
        self.assertEqual(result[0]["source_kb"], "test")
    
    def test_get_common_sense_facts(self):
        """Test getting common sense facts about a concept."""
        # Mock query_concept to return predefined data
        self.interface.query_concept = Mock(return_value={
            "concept": "test",
            "relations": [
                {
                    "source": "test",
                    "relation": "is_a",
                    "target": "concept",
                    "weight": 0.9,
                    "source_kb": "test"
                }
            ],
            "definitions": ["A test definition"],
            "source": ["test"]
        })
        
        # Get facts
        facts = self.interface.get_common_sense_facts("test", limit=2)
        
        # Check the facts
        self.assertEqual(len(facts), 2)
        self.assertEqual(facts[0], "test is a type of concept.")
        self.assertEqual(facts[1], "test is defined as: A test definition")
    
    def test_file_based_caching(self):
        """Test file-based caching."""
        # Disable the cache system to force file-based caching
        self.interface.cache_system = None
        
        # Create test data
        test_data = {"test": "data"}
        
        # Save to cache
        self.interface._save_to_cache("test_key", test_data)
        
        # Check that the file was created
        cache_file = os.path.join(self.cache_dir, "test_key.json")
        self.assertTrue(os.path.exists(cache_file))
        
        # Get from cache
        cached_data = self.interface._get_from_cache("test_key")
        
        # Check the cached data
        self.assertEqual(cached_data, test_data)
    
    def test_caching_system(self):
        """Test caching using the cache system."""
        # Create test data
        test_data = {"test": "data"}
        
        # Mock the cache system
        self.cache_system.get.return_value = None
        
        # Save to cache
        self.interface._save_to_cache("test_key", test_data)
        
        # Check that the cache system was called
        self.cache_system.set.assert_called_once_with(
            "common_sense:test_key", test_data, ttl=self.interface.max_cache_age
        )
        
        # Mock the cache system to return the data
        self.cache_system.get.return_value = test_data
        
        # Get from cache
        cached_data = self.interface._get_from_cache("test_key")
        
        # Check that the cache system was called and the data was returned
        self.cache_system.get.assert_called_with("common_sense:test_key")
        self.assertEqual(cached_data, test_data)
    
    def test_integrate_with_knowledge_store(self):
        """Test integration with the knowledge store."""
        # Create test concept data
        concept_data = {
            "concept": "test",
            "relations": [
                {
                    "source": "test",
                    "relation": "is_a",
                    "target": "concept",
                    "weight": 0.9,
                    "source_kb": "test"
                }
            ],
            "definitions": ["A test definition"],
            "source": ["test"]
        }
        
        # Integrate with knowledge store
        self.interface._integrate_with_knowledge_store(concept_data)
        
        # Check that the knowledge store was called
        self.knowledge_store.add_entity.assert_called_with("test")
        self.knowledge_store.add_entity.assert_called_with("concept")
        self.knowledge_store.add_relation.assert_called_with("test", "is_a", "concept", confidence=0.9)
        self.knowledge_store.add_property.assert_called_with("test", "definition", "A test definition")
    
    def test_bulk_import_concepts(self):
        """Test bulk importing concepts."""
        # Mock query_concept to always succeed
        self.interface.query_concept = Mock(return_value={
            "concept": "test",
            "relations": [],
            "definitions": [],
            "source": ["test"]
        })
        
        # Bulk import concepts
        result = self.interface.bulk_import_concepts(["test1", "test2"])
        
        # Check the result
        self.assertEqual(result, {"test1": True, "test2": True})
        self.assertEqual(self.interface.query_concept.call_count, 2)
    
    def test_clear_cache(self):
        """Test clearing the cache."""
        # Create a test cache file
        cache_file = os.path.join(self.cache_dir, "concept_test.json")
        with open(cache_file, 'w') as f:
            json.dump({"test": "data"}, f)
        
        # Clear the cache for a specific concept
        self.interface.clear_cache("test")
        
        # Check that the file was removed
        self.assertFalse(os.path.exists(cache_file))
        
        # Create another test cache file
        cache_file = os.path.join(self.cache_dir, "concept_test2.json")
        with open(cache_file, 'w') as f:
            json.dump({"test": "data"}, f)
        
        # Clear all cache
        self.interface.clear_cache()
        
        # Check that the file was removed
        self.assertFalse(os.path.exists(cache_file))


if __name__ == '__main__':
    unittest.main()