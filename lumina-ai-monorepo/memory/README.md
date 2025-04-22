# Advanced Memory System

This module provides a sophisticated memory system for Lumina AI, enabling enhanced context management, knowledge retention, and information retrieval.

## Components

### 1. Neural Context Compression

Compresses conversation context while preserving semantic meaning, reducing token usage while maintaining critical information.

- `compression/neural_compression.py`: Core compression algorithms
- `compression/autoencoder.py`: Neural autoencoder for semantic compression
- `compression/pca.py`: PCA-based compression for lightweight applications
- `compression/factory.py`: Factory for creating compression instances
- `compression/base.py`: Base classes and interfaces

### 2. Hierarchical Memory Management

Organizes memories into topics and hierarchical structures for efficient storage and retrieval.

- `hierarchical/topic_management.py`: Topic identification and management
- `hierarchical/memory.py`: Hierarchical memory organization

### 3. Cross-Session Memory

Enables persistent memory across user sessions, providing long-term knowledge retention.

- `cross_session/persistent_memory.py`: Cross-session memory storage and retrieval

### 4. Memory Retrieval Optimization

Provides sophisticated retrieval mechanisms to access the most relevant memories.

- `retrieval/memory_retrieval.py`: Advanced retrieval algorithms

### 5. Vector Storage

Efficient storage and retrieval of vector embeddings for semantic search.

- `vector/store.py`: Vector storage interface
- `vector/enhanced_store.py`: Enhanced vector storage with additional capabilities
- `vector/provider_factory.py`: Factory for creating vector store providers
- `vector/providers/base.py`: Base provider interface
- `vector/providers/inmemory.py`: In-memory vector storage
- `vector/providers/pinecone.py`: Pinecone vector database integration
- `vector/providers/weaviate.py`: Weaviate vector database integration

### 6. Integration

Connects the memory system with other Lumina AI components.

- `integration/memory_integration.py`: Integration with learning, collaboration, and UI

## Usage

```python
from memory.integration.memory_integration import memory_integration

# Store a memory
memory_integration.store_memory(
    user_id="user123",
    key="japan_trip",
    value="Japan is a beautiful country with rich culture and history.",
    memory_type="travel",
    importance=0.9
)

# Retrieve memories by context
context = "I'm planning to visit Japan next month."
memories = memory_integration.retrieve_by_context("user123", context, limit=5)

# Compress conversation context
compressed = memory_integration.compress_context(long_context, compression_ratio=0.3)

# Get topics for a user
topics = memory_integration.get_topics_for_user("user123")

# Get memories for UI display
ui_data = memory_integration.get_memory_for_ui("user123", current_context)
```

## Testing

Run the test suite:

```bash
python -m memory.tests.test_memory_system
```

## Integration with Other Components

The memory system integrates with:

1. **Learning System**: Shares memories for knowledge acquisition
2. **Collaboration System**: Enables memory sharing in collaborative environments
3. **UI Components**: Provides memory visualization and interaction

## Performance Considerations

- Use appropriate compression ratios based on context importance
- Consider memory lifecycle management for long-term storage
- Use vector database providers for large-scale deployments
