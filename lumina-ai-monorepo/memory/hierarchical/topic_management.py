"""
Hierarchical memory management module for the Advanced Memory System.

This module provides functionality for organizing memory items into a semantic
hierarchy for better retrieval and context management.
"""

import logging
import numpy as np
from typing import Dict, List, Optional, Any, Union, Tuple
import uuid
from sklearn.cluster import AgglomerativeClustering
from sklearn.metrics.pairwise import cosine_similarity
import torch
from transformers import AutoTokenizer, AutoModel

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class TopicNode:
    """
    Represents a node in the topic hierarchy.
    
    Each node corresponds to a topic and can have parent and child topics,
    forming a hierarchical structure.
    """
    
    def __init__(self, name: str, description: str = "", embedding: Optional[np.ndarray] = None):
        """
        Initialize a topic node.
        
        Args:
            name: Name of the topic
            description: Description of the topic
            embedding: Vector embedding representing the topic's semantic meaning
        """
        self.id = str(uuid.uuid4())
        self.name = name
        self.description = description
        self.embedding = embedding
        self.parent = None
        self.children = []
        self.memory_items = []
        self.importance_score = 0.5  # Default importance
        self.created_at = None
        self.updated_at = None
    
    def add_child(self, child: 'TopicNode') -> None:
        """
        Add a child topic to this topic.
        
        Args:
            child: The child topic to add
        """
        if child not in self.children:
            self.children.append(child)
            child.parent = self
    
    def remove_child(self, child: 'TopicNode') -> None:
        """
        Remove a child topic from this topic.
        
        Args:
            child: The child topic to remove
        """
        if child in self.children:
            self.children.remove(child)
            child.parent = None
    
    def add_memory_item(self, memory_item: Dict[str, Any]) -> None:
        """
        Add a memory item to this topic.
        
        Args:
            memory_item: The memory item to add
        """
        self.memory_items.append(memory_item)
    
    def get_path_from_root(self) -> List['TopicNode']:
        """
        Get the path from the root topic to this topic.
        
        Returns:
            List of topics from root to this topic
        """
        path = []
        current = self
        while current:
            path.insert(0, current)
            current = current.parent
        return path
    
    def get_all_descendants(self) -> List['TopicNode']:
        """
        Get all descendant topics of this topic.
        
        Returns:
            List of all descendant topics
        """
        descendants = []
        for child in self.children:
            descendants.append(child)
            descendants.extend(child.get_all_descendants())
        return descendants
    
    def to_dict(self, include_children: bool = True) -> Dict[str, Any]:
        """
        Convert the topic node to a dictionary representation.
        
        Args:
            include_children: Whether to include child topics in the dictionary
            
        Returns:
            Dictionary representation of the topic node
        """
        result = {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "importance_score": self.importance_score,
            "memory_item_count": len(self.memory_items),
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }
        
        if include_children:
            result["children"] = [child.to_dict() for child in self.children]
        
        return result


class EmbeddingModel:
    """
    Model for generating embeddings for text.
    
    This class uses transformer models to generate vector embeddings
    that capture the semantic meaning of text.
    """
    
    def __init__(self, model_name: str = "sentence-transformers/all-mpnet-base-v2"):
        """
        Initialize the embedding model.
        
        Args:
            model_name: Name of the pre-trained model to use for embeddings
        """
        logger.info(f"Initializing EmbeddingModel with model: {model_name}")
        self.model_name = model_name
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        logger.info(f"Using device: {self.device}")
        
        # Load tokenizer and model
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModel.from_pretrained(model_name).to(self.device)
        
        logger.info("EmbeddingModel initialized successfully")
    
    def get_embedding(self, text: str) -> np.ndarray:
        """
        Generate an embedding for the input text.
        
        Args:
            text: Input text to embed
            
        Returns:
            Vector embedding of the text
        """
        # Tokenize and prepare input
        inputs = self.tokenizer(text, return_tensors="pt", padding=True, truncation=True, max_length=512).to(self.device)
        
        # Generate embeddings
        with torch.no_grad():
            outputs = self.model(**inputs)
        
        # Use mean pooling to get a single vector for the text
        attention_mask = inputs["attention_mask"]
        token_embeddings = outputs.last_hidden_state
        input_mask_expanded = attention_mask.unsqueeze(-1).expand(token_embeddings.size()).float()
        sum_embeddings = torch.sum(token_embeddings * input_mask_expanded, 1)
        sum_mask = torch.clamp(input_mask_expanded.sum(1), min=1e-9)
        mean_embeddings = sum_embeddings / sum_mask
        
        # Convert to numpy array
        embedding = mean_embeddings.cpu().numpy()[0]
        
        return embedding


class TopicClustering:
    """
    Clusters memory items into topics based on semantic similarity.
    
    This class uses clustering algorithms to group similar memory items
    into topics and organize them hierarchically.
    """
    
    def __init__(self, embedding_model: EmbeddingModel):
        """
        Initialize the topic clustering.
        
        Args:
            embedding_model: Model for generating text embeddings
        """
        logger.info("Initializing TopicClustering")
        self.embedding_model = embedding_model
    
    def cluster_items(self, items: List[Dict[str, Any]], max_topics: int = 10, threshold: float = 0.5) -> List[TopicNode]:
        """
        Cluster memory items into topics.
        
        Args:
            items: List of memory items to cluster
            max_topics: Maximum number of topics to create
            threshold: Similarity threshold for clustering
            
        Returns:
            List of topic nodes
        """
        logger.info(f"Clustering {len(items)} items into max {max_topics} topics")
        
        if not items:
            logger.warning("No items to cluster")
            return []
        
        # Generate embeddings for all items
        embeddings = []
        for item in items:
            content = item.get("content", "")
            embedding = self.embedding_model.get_embedding(content)
            embeddings.append(embedding)
        
        embeddings_array = np.array(embeddings)
        
        # Perform hierarchical clustering
        n_clusters = min(max_topics, len(items))
        clustering = AgglomerativeClustering(
            n_clusters=n_clusters,
            metric="cosine",
            linkage="average"
        )
        
        cluster_labels = clustering.fit_predict(embeddings_array)
        
        # Group items by cluster
        clusters = {}
        for i, label in enumerate(cluster_labels):
            if label not in clusters:
                clusters[label] = []
            clusters[label].append((items[i], embeddings[i]))
        
        # Create topic nodes for each cluster
        topics = []
        for label, cluster_items in clusters.items():
            # Calculate cluster centroid
            cluster_embeddings = np.array([emb for _, emb in cluster_items])
            centroid = np.mean(cluster_embeddings, axis=0)
            
            # Generate topic name and description
            topic_name = self._generate_topic_name(cluster_items)
            topic_description = self._generate_topic_description(cluster_items)
            
            # Create topic node
            topic = TopicNode(name=topic_name, description=topic_description, embedding=centroid)
            
            # Add memory items to topic
            for item, _ in cluster_items:
                topic.add_memory_item(item)
            
            topics.append(topic)
        
        logger.info(f"Created {len(topics)} topics")
        return topics
    
    def organize_hierarchy(self, topics: List[TopicNode], max_depth: int = 3) -> TopicNode:
        """
        Organize topics into a hierarchical structure.
        
        Args:
            topics: List of topic nodes to organize
            max_depth: Maximum depth of the hierarchy
            
        Returns:
            Root topic node of the hierarchy
        """
        logger.info(f"Organizing {len(topics)} topics into hierarchy with max depth {max_depth}")
        
        if not topics:
            logger.warning("No topics to organize")
            root = TopicNode(name="Root", description="Root topic")
            return root
        
        # Create root topic
        root = TopicNode(name="Root", description="Root topic")
        
        if len(topics) == 1:
            # Only one topic, make it a child of root
            root.add_child(topics[0])
            return root
        
        # Get embeddings for all topics
        topic_embeddings = np.array([topic.embedding for topic in topics])
        
        # Calculate similarity matrix
        similarity_matrix = cosine_similarity(topic_embeddings)
        
        # Create hierarchy using agglomerative clustering
        for depth in range(max_depth):
            if depth == 0:
                # First level: add all topics as children of root
                for topic in topics:
                    root.add_child(topic)
            else:
                # Subsequent levels: cluster similar topics
                n_clusters = max(2, len(topics) // (2 ** depth))
                clustering = AgglomerativeClustering(
                    n_clusters=n_clusters,
                    affinity="precomputed",
                    linkage="average",
                    metric="precomputed"
                )
                
                # Convert similarity to distance
                distance_matrix = 1 - similarity_matrix
                cluster_labels = clustering.fit_predict(distance_matrix)
                
                # Group topics by cluster
                clusters = {}
                for i, label in enumerate(cluster_labels):
                    if label not in clusters:
                        clusters[label] = []
                    clusters[label].append(topics[i])
                
                # Create parent topics for each cluster
                for label, cluster_topics in clusters.items():
                    if len(cluster_topics) <= 1:
                        continue
                    
                    # Calculate cluster centroid
                    cluster_embeddings = np.array([topic.embedding for topic in cluster_topics])
                    centroid = np.mean(cluster_embeddings, axis=0)
                    
                    # Generate parent topic name and description
                    parent_name = self._generate_parent_topic_name(cluster_topics)
                    parent_description = self._generate_parent_topic_description(cluster_topics)
                    
                    # Create parent topic
                    parent_topic = TopicNode(name=parent_name, description=parent_description, embedding=centroid)
                    
                    # Add cluster topics as children of parent topic
                    for topic in cluster_topics:
                        if topic.parent:
                            topic.parent.remove_child(topic)
                        parent_topic.add_child(topic)
                    
                    # Add parent topic to root
                    root.add_child(parent_topic)
        
        logger.info(f"Created hierarchy with root topic and {len(root.children)} top-level topics")
        return root
    
    def _generate_topic_name(self, cluster_items: List[Tuple[Dict[str, Any], np.ndarray]]) -> str:
        """
        Generate a name for a topic based on its items.
        
        Args:
            cluster_items: List of (item, embedding) tuples in the cluster
            
        Returns:
            Generated topic name
        """
        # This is a placeholder implementation
        # In a production system, this would use more sophisticated NLP techniques
        
        # Extract words from all items
        all_words = []
        for item, _ in cluster_items:
            content = item.get("content", "")
            words = content.split()
            all_words.extend([word.lower() for word in words if len(word) > 3])
        
        # Count word frequencies
        word_counts = {}
        for word in all_words:
            word_counts[word] = word_counts.get(word, 0) + 1
        
        # Get most frequent words
        sorted_words = sorted(word_counts.items(), key=lambda x: x[1], reverse=True)
        top_words = [word for word, _ in sorted_words[:3]]
        
        if top_words:
            return " ".join(top_words).title()
        else:
            return f"Topic {str(uuid.uuid4())[:8]}"
    
    def _generate_topic_description(self, cluster_items: List[Tuple[Dict[str, Any], np.ndarray]]) -> str:
        """
        Generate a description for a topic based on its items.
        
        Args:
            cluster_items: List of (item, embedding) tuples in the cluster
            
        Returns:
            Generated topic description
        """
        # This is a placeholder implementation
        # In a production system, this would use more sophisticated NLP techniques
        
        # Use the first few items as the description
        descriptions = []
        for item, _ in cluster_items[:3]:
            content = item.get("content", "")
            # Take the first sentence or first 100 characters
            description = content.split(".")[0] if "." in content else content[:100]
            descriptions.append(description)
        
        return " | ".join(descriptions)
    
    def _generate_parent_topic_name(self, topics: List[TopicNode]) -> str:
        """
        Generate a name for a parent topic based on its child topics.
        
        Args:
            topics: List of child topics
            
        Returns:
            Generated parent topic name
        """
        # This is a placeholder implementation
        # In a production system, this would use more sophisticated NLP techniques
        
        # Use common words from child topic names
        all_words = []
        for topic in topics:
            words = topic.name.split()
            all_words.extend([word.lower() for word in words if len(word) > 3])
        
        # Count word frequencies
        word_counts = {}
        for word in all_words:
            word_counts[word] = word_counts.get(word, 0) + 1
        
        # Get most frequent words
        sorted_words = sorted(word_counts.items(), key=lambda x: x[1], reverse=True)
        top_words = [word for word, _ in sorted_words[:2]]
        
        if top_words:
            return " ".join(top_words).title()
        else:
            return f"Group {str(uuid.uuid4())[:8]}"
    
    def _generate_parent_topic_description(self, topics: List[TopicNode]) -> str:
        """
        Generate a description for a parent topic based on its child topics.
        
        Args:
            topics: List of child topics
            
        Returns:
            Generated parent topic description
        """
        # This is a placeholder implementation
        # In a production system, this would use more sophisticated NLP techniques
        
        # Use child topic names as the description
        topic_names = [topic.name for topic in topics[:5]]
        return "Group containing: " + ", ".join(topic_names)


class TopicManager:
    """
    Manages the topic hierarchy and provides operations for working with topics.
    
    This class provides functionality for creating, updating, and navigating
    the topic hierarchy, as well as associating memory items with topics.
    """
    
    def __init__(self, embedding_model: Optional[EmbeddingModel] = None):
        """
        Initialize the topic manager.
        
        Args:
            embedding_model: Model for generating text embeddings
        """
        logger.info("Initializing TopicManager")
        self.embedding_model = embedding_model or EmbeddingModel()
        self.topic_clustering = TopicClustering(self.embedding_model)
        self.root_topic = TopicNode(name="Root", description="Root topic")
        self.topics_by_id = {self.root_topic.id: self.root_topic}
    
    def create_topic(self, name: str, description: str = "", parent_id: Optional[str] = None) -> TopicNode:
        """
        Create a new topic.
        
        Args:
            name: Name of the topic
            description: Description of the topic
            parent_id: ID of the parent topic (None for root)
            
        Returns:
            The created topic node
        """
        logger.info(f"Creating topic: {name}")
        
        # Generate embedding for the topic
        embedding = self.embedding_model.get_embedding(name + " " + description)
        
        # Create topic node
        topic = TopicNode(name=name, description=description, embedding=embedding)
        
        # Add to topics dictionary
        self.topics_by_id[topic.id] = topic
        
        # Add to parent
        if parent_id:
            parent = self.topics_by_id.get(parent_id)
            if parent:
                parent.add_child(topic)
            else:
                logger.warning(f"Parent topic with ID {parent_id} not found, adding to root")
                self.root_topic.add_child(topic)
        else:
            self.root_topic.add_child(topic)
        
        return topic
    
    def get_topic(self, topic_id: str) -> Optional[TopicNode]:
        """
        Get a topic by ID.
        
        Args:
            topic_id: ID of the topic to get
            
        Returns:
            The topic node if found, None otherwise
        """
        return self.topics_by_id.get(topic_id)
    
    def update_topic(self, topic_id: str, name: Optional[str] = None, description: Optional[str] = None) -> Optional[TopicNode]:
        """
        Update a topic.
        
        Args:
            topic_id: ID of the topic to update
            name: New name for the topic (None to keep current)
            description: New description for the topic (None to keep current)
            
        Returns:
            The updated topic node if found, None otherwise
        """
        topic = self.topics_by_id.get(topic_id)
        if not topic:
            logger.warning(f"Topic with ID {topic_id} not found")
            return None
        
        logger.info(f"Updating topic: {topic.name}")
        
        if name:
            topic.name = name
        
        if description:
            topic.description = description
        
        if name or description:
            # Update embedding
            embedding_text = topic.name + " " + topic.description
            topic.embedding = self.embedding_model.get_embedding(embedding_text)
        
        return topic
    
    def delete_topic(self, topic_id: str) -> bool:
        """
        Delete a topic.
        
        Args:
            topic_id: ID of the topic to delete
            
        Returns:
            True if the topic was deleted, False otherwise
        """
        topic = self.topics_by_id.get(topic_id)
        if not topic:
            logger.warning(f"Topic with ID {topic_id} not found")
            return False
        
        logger.info(f"Deleting topic: {topic.name}")
        
        # Remove from parent
        if topic.parent:
            topic.parent.remove_child(topic)
        
        # Move children to parent
        parent = topic.parent or self.root_topic
        for child in topic.children[:]:  # Copy to avoid modification during iteration
            topic.remove_child(child)
            parent.add_child(child)
        
        # Remove from topics dictionary
        del self.topics_by_id[topic_id]
        
        return True
    
    def move_topic(self, topic_id: str, new_parent_id: str) -> bool:
        """
        Move a topic to a new parent.
        
        Args:
            topic_id: ID of the topic to move
            new_parent_id: ID of the new parent topic
            
        Returns:
            True if the topic was moved, False otherwise
        """
        topic = self.topics_by_id.get(topic_id)
        new_parent = self.topics_by_id.get(new_parent_id)
        
        if not topic:
            logger.warning(f"Topic with ID {topic_id} not found")
            return False
        
        if not new_parent:
            logger.warning(f"New parent topic with ID {new_parent_id} not found")
            return False
        
        logger.info(f"Moving topic {topic.name} to parent {new_parent.name}")
        
        # Check for circular reference
        current = new_parent
        while current:
            if current.id == topic_id:
                logger.warning(f"Cannot move topic {topic.name} to {new_parent.name}: would create circular reference")
                return False
            current = current.parent
        
        # Remove from current parent
        if topic.parent:
            topic.parent.remove_child(topic)
        
        # Add to new parent
        new_parent.add_child(topic)
        
        return True
    
    def add_memory_item_to_topic(self, topic_id: str, memory_item: Dict[str, Any]) -> bool:
        """
        Add a memory item to a topic.
        
        Args:
            topic_id: ID of the topic to add the memory item to
            memory_item: The memory item to add
            
        Returns:
            True if the memory item was added, False otherwise
        """
        topic = self.topics_by_id.get(topic_id)
        if not topic:
            logger.warning(f"Topic with ID {topic_id} not found")
            return False
        
        logger.info(f"Adding memory item to topic: {topic.name}")
        topic.add_memory_item(memory_item)
        return True
    
    def find_best_topic_for_item(self, memory_item: Dict[str, Any]) -> Optional[TopicNode]:
        """
        Find the best matching topic for a memory item.
        
        Args:
            memory_item: The memory item to find a topic for
            
        Returns:
            The best matching topic node if found, None otherwise
        """
        content = memory_item.get("content", "")
        if not content:
            logger.warning("Memory item has no content")
            return None
        
        logger.info("Finding best topic for memory item")
        
        # Generate embedding for the memory item
        item_embedding = self.embedding_model.get_embedding(content)
        
        # Find the most similar topic
        best_topic = None
        best_similarity = -1
        
        for topic_id, topic in self.topics_by_id.items():
            if topic.embedding is None:
                continue
            
            # Calculate similarity
            similarity = cosine_similarity([item_embedding], [topic.embedding])[0][0]
            
            if similarity > best_similarity:
                best_similarity = similarity
                best_topic = topic
        
        # Check if similarity is high enough
        if best_similarity < 0.5:
            logger.info("No sufficiently similar topic found")
            return None
        
        logger.info(f"Found best topic: {best_topic.name} with similarity {best_similarity:.2f}")
        return best_topic
    
    def organize_items_into_topics(self, items: List[Dict[str, Any]], max_topics: int = 10) -> TopicNode:
        """
        Organize memory items into a topic hierarchy.
        
        Args:
            items: List of memory items to organize
            max_topics: Maximum number of topics to create
            
        Returns:
            Root topic node of the created hierarchy
        """
        logger.info(f"Organizing {len(items)} items into topics")
        
        # Cluster items into topics
        topics = self.topic_clustering.cluster_items(items, max_topics=max_topics)
        
        # Organize topics into hierarchy
        root = self.topic_clustering.organize_hierarchy(topics)
        
        # Update internal state
        self.root_topic = root
        self.topics_by_id = {root.id: root}
        
        # Add all topics to the dictionary
        def add_topics_recursive(topic):
            self.topics_by_id[topic.id] = topic
            for child in topic.children:
                add_topics_recursive(child)
        
        for child in root.children:
            add_topics_recursive(child)
        
        logger.info(f"Created topic hierarchy with {len(self.topics_by_id)} topics")
        return root
    
    def get_topic_hierarchy(self) -> Dict[str, Any]:
        """
        Get the complete topic hierarchy.
        
        Returns:
            Dictionary representation of the topic hierarchy
        """
        return self.root_topic.to_dict()
    
    def search_topics(self, query: str, limit: int = 5) -> List[TopicNode]:
        """
        Search for topics matching the query.
        
        Args:
            query: Search query
            limit: Maximum number of results to return
            
        Returns:
            List of matching topic nodes
        """
        logger.info(f"Searching topics with query: {query}")
        
        if not query:
            return []
        
        # Generate embedding for the query
        query_embedding = self.embedding_model.get_embedding(query)
        
        # Calculate similarity with all topics
        topic_similarities = []
        for topic_id, topic in self.topics_by_id.items():
            if topic.embedding is None:
                continue
            
            # Calculate similarity
            similarity = cosine_similarity([query_embedding], [topic.embedding])[0][0]
            topic_similarities.append((topic, similarity))
        
        # Sort by similarity
        topic_similarities.sort(key=lambda x: x[1], reverse=True)
        
        # Return top results
        results = [topic for topic, _ in topic_similarities[:limit]]
        logger.info(f"Found {len(results)} matching topics")
        
        return results
