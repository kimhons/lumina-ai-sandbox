"""
Test module for the Advanced Memory System.

This module provides comprehensive tests for all components of the
Advanced Memory System, including neural compression, hierarchical memory,
cross-session memory, retrieval optimization, and integration with other
Lumina AI components.
"""

import unittest
import logging
import json
import time
from datetime import datetime, timedelta
import numpy as np
from typing import Dict, List, Any, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Import memory system components
from memory.compression.neural_compression import ContextCompressor
from memory.hierarchical.topic_management import TopicManager
from memory.cross_session.persistent_memory import CrossSessionMemory, MemoryItem, UserMemoryStore
from memory.retrieval.memory_retrieval import (
    MemoryRetrievalOptimizer, 
    EmbeddingProvider, 
    ContextAnalyzer, 
    RelevanceScorer, 
    MemoryRetriever
)
from memory.integration.memory_integration import MemorySystemIntegration

class TestContextCompression(unittest.TestCase):
    """Test cases for neural context compression."""
    
    def setUp(self):
        """Set up test environment."""
        self.embedding_provider = EmbeddingProvider()
        self.compressor = ContextCompressor(self.embedding_provider)
        
        # Sample conversation context
        self.context = """
        User: I'm planning a trip to Japan next month. Can you recommend some places to visit?
        Assistant: Japan is a wonderful destination! Some popular places to visit include Tokyo, Kyoto, Osaka, and Hiroshima. Tokyo is known for its modern technology and bustling city life, while Kyoto offers traditional temples and gardens. Osaka is famous for its food culture, and Hiroshima has important historical sites. When will you be traveling and how long is your trip?
        User: I'll be there for two weeks in May. I'm interested in both traditional culture and modern attractions. I also love food!
        Assistant: Two weeks in May is perfect for Japan! The weather should be pleasant and you'll have time to explore multiple regions. For traditional culture, I recommend spending at least 3-4 days in Kyoto visiting temples like Kinkaku-ji (Golden Pavilion) and Fushimi Inari Shrine. For modern attractions, Tokyo offers districts like Shibuya, Akihabara, and Shinjuku. For food experiences, don't miss the street food in Osaka's Dotonbori area and the seafood markets in Tokyo. Would you like a sample itinerary?
        User: Yes, a sample itinerary would be great. I'd also like to know about transportation options between cities.
        """
    
    def test_compression_ratio(self):
        """Test that compression achieves the target ratio."""
        target_ratio = 0.5
        compressed = self.compressor.compress(self.context, target_ratio)
        
        # Check that compression reduced the length
        self.assertLess(len(compressed), len(self.context))
        
        # Check that the compression ratio is approximately as requested
        actual_ratio = len(compressed) / len(self.context)
        self.assertLess(actual_ratio, target_ratio + 0.2)  # Allow some flexibility
    
    def test_semantic_preservation(self):
        """Test that compression preserves key semantic information."""
        compressed = self.compressor.compress(self.context, 0.5)
        
        # Check that key information is preserved
        key_terms = ["Japan", "Tokyo", "Kyoto", "May", "two weeks", "itinerary"]
        for term in key_terms:
            self.assertIn(term, compressed)
    
    def test_different_compression_ratios(self):
        """Test compression with different ratios."""
        ratios = [0.3, 0.5, 0.7]
        
        previous_length = len(self.context)
        for ratio in ratios:
            compressed = self.compressor.compress(self.context, ratio)
            current_length = len(compressed)
            
            # Check that higher ratios result in less compression
            self.assertLess(current_length, previous_length)
            previous_length = current_length


class TestTopicManagement(unittest.TestCase):
    """Test cases for hierarchical memory management."""
    
    def setUp(self):
        """Set up test environment."""
        self.embedding_provider = EmbeddingProvider()
        self.topic_manager = TopicManager(self.embedding_provider)
        
        # Sample user and memories
        self.user_id = "test_user_123"
        self.memories = [
            {
                "key": "japan_trip_1",
                "value": "Japan is a wonderful destination with beautiful temples in Kyoto.",
                "memory_type": "travel",
                "importance_score": 0.8
            },
            {
                "key": "japan_trip_2",
                "value": "Tokyo offers modern technology and bustling city life.",
                "memory_type": "travel",
                "importance_score": 0.7
            },
            {
                "key": "python_tip_1",
                "value": "Python list comprehensions are a concise way to create lists.",
                "memory_type": "coding",
                "importance_score": 0.9
            },
            {
                "key": "python_tip_2",
                "value": "Use virtual environments to manage Python dependencies.",
                "memory_type": "coding",
                "importance_score": 0.8
            },
            {
                "key": "recipe_1",
                "value": "Sushi rice should be short-grain and seasoned with rice vinegar.",
                "memory_type": "cooking",
                "importance_score": 0.6
            }
        ]
        
        # Add memories to topic manager
        for memory in self.memories:
            memory_item = MemoryItem(
                key=memory["key"],
                value=memory["value"],
                user_id=self.user_id,
                memory_type=memory["memory_type"],
                importance_score=memory["importance_score"]
            )
            self.topic_manager.assign_memory_to_topics(self.user_id, memory_item)
    
    def test_topic_creation(self):
        """Test that topics are created correctly."""
        topics = self.topic_manager.get_topics_for_user(self.user_id)
        
        # Check that topics were created
        self.assertGreater(len(topics), 0)
        
        # Check that topic names are meaningful
        topic_names = [topic["name"] for topic in topics]
        self.assertTrue(any("travel" in name.lower() for name in topic_names) or 
                       any("japan" in name.lower() for name in topic_names))
        self.assertTrue(any("coding" in name.lower() for name in topic_names) or 
                       any("python" in name.lower() for name in topic_names))
    
    def test_memory_assignment(self):
        """Test that memories are assigned to appropriate topics."""
        topics = self.topic_manager.get_topics_for_user(self.user_id)
        
        for topic in topics:
            memories = self.topic_manager.get_memories_by_topic(self.user_id, topic["id"])
            
            # Check that each topic has at least one memory
            self.assertGreater(len(memories), 0)
            
            # Check that memories in the topic are related
            if "travel" in topic["name"].lower() or "japan" in topic["name"].lower():
                self.assertTrue(any("japan" in memory["value"].lower() for memory in memories))
            elif "coding" in topic["name"].lower() or "python" in topic["name"].lower():
                self.assertTrue(any("python" in memory["value"].lower() for memory in memories))
    
    def test_topic_similarity(self):
        """Test that similar memories are grouped in the same topic."""
        # Add a new memory similar to existing ones
        new_memory = MemoryItem(
            key="japan_trip_3",
            value="Kyoto has many traditional temples and beautiful gardens.",
            user_id=self.user_id,
            memory_type="travel",
            importance_score=0.75
        )
        self.topic_manager.assign_memory_to_topics(self.user_id, new_memory)
        
        # Find the topic containing Japan memories
        topics = self.topic_manager.get_topics_for_user(self.user_id)
        japan_topic = None
        for topic in topics:
            memories = self.topic_manager.get_memories_by_topic(self.user_id, topic["id"])
            if any("japan" in memory["value"].lower() for memory in memories):
                japan_topic = topic
                break
        
        self.assertIsNotNone(japan_topic)
        
        # Check that the new memory is in the same topic
        memories = self.topic_manager.get_memories_by_topic(self.user_id, japan_topic["id"])
        self.assertTrue(any(memory["key"] == "japan_trip_3" for memory in memories))


class TestCrossSessionMemory(unittest.TestCase):
    """Test cases for cross-session memory."""
    
    def setUp(self):
        """Set up test environment."""
        self.cross_session_memory = CrossSessionMemory()
        
        # Sample user
        self.user_id = "test_user_456"
    
    def test_memory_storage_and_retrieval(self):
        """Test storing and retrieving memory items."""
        # Store a memory item
        memory = self.cross_session_memory.store(
            user_id=self.user_id,
            key="test_memory_1",
            value="This is a test memory item.",
            memory_type="test",
            importance_score=0.7
        )
        
        # Check that the memory was stored correctly
        self.assertEqual(memory["key"], "test_memory_1")
        self.assertEqual(memory["value"], "This is a test memory item.")
        self.assertEqual(memory["user_id"], self.user_id)
        
        # Retrieve the memory
        retrieved = self.cross_session_memory.retrieve(self.user_id, "test_memory_1")
        
        # Check that the retrieved memory matches
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved["key"], "test_memory_1")
        self.assertEqual(retrieved["value"], "This is a test memory item.")
    
    def test_memory_update(self):
        """Test updating memory items."""
        # Store a memory item
        self.cross_session_memory.store(
            user_id=self.user_id,
            key="test_memory_2",
            value="Original value.",
            memory_type="test",
            importance_score=0.6
        )
        
        # Update the memory
        updated = self.cross_session_memory.update(
            user_id=self.user_id,
            key="test_memory_2",
            value="Updated value."
        )
        
        # Check that the update was successful
        self.assertTrue(updated)
        
        # Retrieve the updated memory
        retrieved = self.cross_session_memory.retrieve(self.user_id, "test_memory_2")
        
        # Check that the value was updated
        self.assertEqual(retrieved["value"], "Updated value.")
    
    def test_memory_expiration(self):
        """Test that memories expire correctly."""
        # Store a memory with a short TTL
        self.cross_session_memory.store(
            user_id=self.user_id,
            key="expiring_memory",
            value="This memory will expire soon.",
            memory_type="test",
            importance_score=0.5,
            ttl_seconds=1  # Expire after 1 second
        )
        
        # Verify it exists initially
        initial = self.cross_session_memory.retrieve(self.user_id, "expiring_memory")
        self.assertIsNotNone(initial)
        
        # Wait for expiration
        time.sleep(1.5)
        
        # Verify it's gone after expiration
        expired = self.cross_session_memory.retrieve(self.user_id, "expiring_memory")
        self.assertIsNone(expired)
    
    def test_user_memory_store(self):
        """Test user memory store functionality."""
        # Create a user memory store
        store = UserMemoryStore(self.user_id)
        
        # Add some memories
        for i in range(5):
            item = MemoryItem(
                key=f"memory_{i}",
                value=f"Memory value {i}",
                user_id=self.user_id,
                memory_type="test",
                importance_score=0.5 + i * 0.1
            )
            store.add_item(item)
        
        # Check store size
        self.assertEqual(len(store.get_all_items()), 5)
        
        # Check getting by importance
        important = store.get_important_items(3)
        self.assertEqual(len(important), 3)
        self.assertEqual(important[0].key, "memory_4")  # Highest importance
        
        # Check getting recent items
        recent = store.get_recent_items(2)
        self.assertEqual(len(recent), 2)
        self.assertEqual(recent[0].key, "memory_4")  # Most recent


class TestMemoryRetrieval(unittest.TestCase):
    """Test cases for memory retrieval optimization."""
    
    def setUp(self):
        """Set up test environment."""
        self.embedding_provider = EmbeddingProvider()
        self.context_analyzer = ContextAnalyzer(self.embedding_provider)
        self.relevance_scorer = RelevanceScorer(self.embedding_provider)
        self.memory_retriever = MemoryRetriever(
            context_analyzer=self.context_analyzer,
            relevance_scorer=self.relevance_scorer,
            embedding_provider=self.embedding_provider
        )
        self.retrieval_optimizer = MemoryRetrievalOptimizer(
            memory_retriever=self.memory_retriever,
            embedding_provider=self.embedding_provider
        )
        
        # Sample memory store
        self.memory_store = {}
        
        # Add sample memories
        memories = [
            {
                "key": "japan_info",
                "value": "Japan is an island country in East Asia with a rich cultural heritage.",
                "memory_type": "general",
                "importance_score": 0.7
            },
            {
                "key": "tokyo_info",
                "value": "Tokyo is the capital of Japan and a bustling metropolis with modern technology.",
                "memory_type": "travel",
                "importance_score": 0.8
            },
            {
                "key": "python_info",
                "value": "Python is a high-level programming language known for its readability and versatility.",
                "memory_type": "coding",
                "importance_score": 0.9
            },
            {
                "key": "recipe_info",
                "value": "Sushi is a traditional Japanese dish featuring vinegared rice and various toppings.",
                "memory_type": "cooking",
                "importance_score": 0.6
            }
        ]
        
        for memory in memories:
            # Generate embedding
            embedding = self.embedding_provider.get_embedding(memory["value"])
            
            # Add to memory store
            self.memory_store[memory["key"]] = {
                "id": memory["key"],
                "key": memory["key"],
                "value": memory["value"],
                "memory_type": memory["memory_type"],
                "importance_score": memory["importance_score"],
                "embedding": embedding,
                "created_at": datetime.now() - timedelta(days=1),
                "updated_at": datetime.now() - timedelta(hours=12),
                "last_accessed": datetime.now() - timedelta(hours=6),
                "access_count": 5
            }
    
    def test_context_analysis(self):
        """Test context analysis functionality."""
        context = "I'm planning a trip to Japan and Tokyo. Can you tell me about Japanese cuisine?"
        
        analysis = self.context_analyzer.analyze_context(context)
        
        # Check that key terms were extracted
        self.assertIn("japan", analysis["key_terms"])
        self.assertIn("tokyo", analysis["key_terms"])
        
        # Check that entities were extracted
        self.assertIn("Japan", analysis["entities"])
        self.assertIn("Tokyo", analysis["entities"])
        
        # Check that embedding was generated
        self.assertIsNotNone(analysis["embedding"])
        self.assertGreater(len(analysis["embedding"]), 0)
    
    def test_semantic_search(self):
        """Test semantic search functionality."""
        query = "Tell me about Japan and its capital city."
        
        results = self.memory_retriever.retrieve_by_semantic_search(
            self.memory_store, query, limit=2)
        
        # Check that results were returned
        self.assertEqual(len(results), 2)
        
        # Check that the most relevant results were returned
        result_keys = [item["key"] for item, _ in results]
        self.assertIn("japan_info", result_keys)
        self.assertIn("tokyo_info", result_keys)
    
    def test_context_retrieval(self):
        """Test context-based retrieval functionality."""
        context = "I'm interested in Japanese food and culture."
        
        results = self.memory_retriever.retrieve_by_context(
            self.memory_store, context, limit=2)
        
        # Check that results were returned
        self.assertEqual(len(results), 2)
        
        # Check that relevant results were returned
        result_keys = [item["key"] for item, _ in results]
        self.assertTrue("japan_info" in result_keys or "recipe_info" in result_keys)
    
    def test_hybrid_search(self):
        """Test hybrid search functionality."""
        context = "I'm learning about different countries."
        query = "Tell me about Japan and its cuisine."
        
        results = self.memory_retriever.retrieve_by_hybrid_search(
            self.memory_store, context, query, limit=2)
        
        # Check that results were returned
        self.assertEqual(len(results), 2)
        
        # Check that relevant results were returned
        result_keys = [item["key"] for item, _ in results]
        self.assertTrue("japan_info" in result_keys or "recipe_info" in result_keys)
    
    def test_retrieval_optimization(self):
        """Test retrieval optimization functionality."""
        context = "I'm planning my vacation."
        query = "What can you tell me about Japan?"
        
        results = self.retrieval_optimizer.optimize_retrieval_strategy(
            self.memory_store, context, query, limit=2)
        
        # Check that results were returned
        self.assertEqual(len(results), 2)
        
        # Check that relevant results were returned
        result_keys = [item["key"] for item, _ in results]
        self.assertIn("japan_info", result_keys)
    
    def test_diverse_retrieval(self):
        """Test diversity-aware retrieval functionality."""
        context = "Tell me about Japan."
        
        # First without diversity
        regular_results = self.retrieval_optimizer.retrieve_memories(
            self.memory_store, context, limit=2, strategy="context")
        
        # Then with diversity
        diverse_results = self.retrieval_optimizer.retrieve_and_rank(
            self.memory_store, context, limit=2, diversity_factor=0.5)
        
        # Check that results were returned
        self.assertEqual(len(diverse_results), 2)
        
        # Check that diverse results cover different aspects
        diverse_types = set(item.get("memory_type") for item in diverse_results)
        self.assertGreater(len(diverse_types), 1)


class TestMemoryIntegration(unittest.TestCase):
    """Test cases for memory system integration."""
    
    def setUp(self):
        """Set up test environment."""
        self.memory_integration = MemorySystemIntegration()
        
        # Sample user
        self.user_id = "test_user_789"
    
    def test_store_and_retrieve(self):
        """Test storing and retrieving memories through integration."""
        # Store a memory
        memory = self.memory_integration.store_memory(
            user_id=self.user_id,
            key="integration_test_1",
            value="This is a test of the memory integration.",
            memory_type="test",
            importance=0.8
        )
        
        # Check that the memory was stored correctly
        self.assertEqual(memory["key"], "integration_test_1")
        self.assertEqual(memory["value"], "This is a test of the memory integration.")
        
        # Retrieve the memory
        retrieved = self.memory_integration.retrieve_memory(self.user_id, "integration_test_1")
        
        # Check that the retrieved memory matches
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved["key"], "integration_test_1")
        self.assertEqual(retrieved["value"], "This is a test of the memory integration.")
    
    def test_context_retrieval_integration(self):
        """Test context-based retrieval through integration."""
        # Store some memories
        self.memory_integration.store_memory(
            user_id=self.user_id,
            key="japan_memory",
            value="Japan is a beautiful country with rich culture and history.",
            memory_type="travel",
            importance=0.9
        )
        
        self.memory_integration.store_memory(
            user_id=self.user_id,
            key="python_memory",
            value="Python is a versatile programming language used in many fields.",
            memory_type="coding",
            importance=0.8
        )
        
        # Retrieve by context
        context = "I'm planning to visit Japan next month."
        memories = self.memory_integration.retrieve_by_context(self.user_id, context, limit=1)
        
        # Check that relevant memories were retrieved
        self.assertEqual(len(memories), 1)
        self.assertEqual(memories[0]["key"], "japan_memory")
    
    def test_context_compression_integration(self):
        """Test context compression through integration."""
        context = """
        User: Can you tell me about the history of Japan?
        Assistant: Japan has a rich history dating back thousands of years. The earliest known civilization in Japan is the Jomon period, which began around 14,500 BCE. Later came the Yayoi period, when rice cultivation was introduced from the Asian mainland. The first unified state in Japan was established in the 4th century CE under the Yamato dynasty. Throughout its history, Japan has gone through periods of isolation and openness to foreign influence. The Meiji Restoration in 1868 marked Japan's rapid modernization and emergence as a world power. After World War II, Japan experienced remarkable economic growth and is now known for its technological innovation, rich cultural traditions, and unique blend of ancient customs and modern lifestyle.
        User: That's interesting. What about Japanese cuisine?
        """
        
        compressed = self.memory_integration.compress_context(context, compression_ratio=0.3)
        
        # Check that compression worked
        self.assertLess(len(compressed), len(context))
        
        # Check that key information is preserved
        key_terms = ["Japan", "history", "cuisine"]
        for term in key_terms:
            self.assertIn(term, compressed)
    
    def test_topic_management_integration(self):
        """Test topic management through integration."""
        # Store memories that should form topics
        for i in range(3):
            self.memory_integration.store_memory(
                user_id=self.user_id,
                key=f"travel_memory_{i}",
                value=f"Travel memory {i} about exploring different countries and cultures.",
                memory_type="travel",
                importance=0.7 + i * 0.1
            )
        
        for i in range(3):
            self.memory_integration.store_memory(
                user_id=self.user_id,
                key=f"coding_memory_{i}",
                value=f"Coding memory {i} about programming languages and software development.",
                memory_type="coding",
                importance=0.7 + i * 0.1
            )
        
        # Get topics
        topics = self.memory_integration.get_topics_for_user(self.user_id)
        
        # Check that topics were created
        self.assertGreater(len(topics), 0)
        
        # Check that memories can be retrieved by topic
        if topics:
            topic_id = topics[0]["id"]
            memories = self.memory_integration.get_memories_by_topic(self.user_id, topic_id)
            self.assertGreater(len(memories), 0)
    
    def test_ui_integration(self):
        """Test UI integration functionality."""
        # Store some memories
        self.memory_integration.store_memory(
            user_id=self.user_id,
            key="ui_test_memory_1",
            value="This is a memory for testing UI integration.",
            memory_type="test",
            importance=0.8
        )
        
        # Get memory for UI
        context = "Testing UI integration."
        ui_data = self.memory_integration.get_memory_for_ui(self.user_id, context)
        
        # Check that UI data was returned
        self.assertIn("recent_memories", ui_data)
        self.assertIn("relevant_memories", ui_data)
        self.assertIn("topics", ui_data)


def run_tests():
    """Run all test cases."""
    logger.info("Running Advanced Memory System tests...")
    
    # Create test suite
    suite = unittest.TestSuite()
    
    # Add test cases
    suite.addTest(unittest.makeSuite(TestContextCompression))
    suite.addTest(unittest.makeSuite(TestTopicManagement))
    suite.addTest(unittest.makeSuite(TestCrossSessionMemory))
    suite.addTest(unittest.makeSuite(TestMemoryRetrieval))
    suite.addTest(unittest.makeSuite(TestMemoryIntegration))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Log results
    logger.info(f"Tests run: {result.testsRun}")
    logger.info(f"Errors: {len(result.errors)}")
    logger.info(f"Failures: {len(result.failures)}")
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    exit(0 if success else 1)
