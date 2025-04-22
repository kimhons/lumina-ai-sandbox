"""
Memory retrieval optimization module for the Advanced Memory System.

This module provides functionality for optimizing memory retrieval through
context-aware search, semantic similarity, and relevance ranking.
"""

import logging
import numpy as np
from typing import Dict, List, Optional, Any, Union, Tuple, Callable
import heapq
from sklearn.metrics.pairwise import cosine_similarity
import torch
from transformers import AutoTokenizer, AutoModel

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class EmbeddingProvider:
    """
    Provides vector embeddings for text using transformer models.
    
    This class is responsible for generating semantic vector representations
    of text that can be used for similarity comparisons and retrieval.
    """
    
    def __init__(self, model_name: str = "sentence-transformers/all-mpnet-base-v2"):
        """
        Initialize the embedding provider.
        
        Args:
            model_name: Name of the pre-trained model to use for embeddings
        """
        logger.info(f"Initializing EmbeddingProvider with model: {model_name}")
        self.model_name = model_name
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        logger.info(f"Using device: {self.device}")
        
        # Load tokenizer and model
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModel.from_pretrained(model_name).to(self.device)
        
        logger.info("EmbeddingProvider initialized successfully")
    
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
    
    def get_embeddings(self, texts: List[str]) -> np.ndarray:
        """
        Generate embeddings for multiple texts.
        
        Args:
            texts: List of input texts to embed
            
        Returns:
            Array of vector embeddings for the texts
        """
        if not texts:
            return np.array([])
        
        # Tokenize and prepare input
        inputs = self.tokenizer(texts, return_tensors="pt", padding=True, truncation=True, max_length=512).to(self.device)
        
        # Generate embeddings
        with torch.no_grad():
            outputs = self.model(**inputs)
        
        # Use mean pooling to get a single vector for each text
        attention_mask = inputs["attention_mask"]
        token_embeddings = outputs.last_hidden_state
        input_mask_expanded = attention_mask.unsqueeze(-1).expand(token_embeddings.size()).float()
        sum_embeddings = torch.sum(token_embeddings * input_mask_expanded, 1)
        sum_mask = torch.clamp(input_mask_expanded.sum(1), min=1e-9)
        mean_embeddings = sum_embeddings / sum_mask
        
        # Convert to numpy array
        embeddings = mean_embeddings.cpu().numpy()
        
        return embeddings


class ContextAnalyzer:
    """
    Analyzes conversation context to extract key information.
    
    This class is responsible for analyzing the current conversation context
    to extract key information that can be used for memory retrieval.
    """
    
    def __init__(self, embedding_provider: Optional[EmbeddingProvider] = None):
        """
        Initialize the context analyzer.
        
        Args:
            embedding_provider: Provider for generating text embeddings
        """
        logger.info("Initializing ContextAnalyzer")
        self.embedding_provider = embedding_provider or EmbeddingProvider()
    
    def extract_key_terms(self, context: str, max_terms: int = 10) -> List[str]:
        """
        Extract key terms from the conversation context.
        
        Args:
            context: The conversation context
            max_terms: Maximum number of key terms to extract
            
        Returns:
            List of key terms extracted from the context
        """
        # This is a simplified implementation
        # In a production system, this would use more sophisticated NLP techniques
        
        # Tokenize and clean
        words = context.lower().split()
        
        # Remove common stop words
        stop_words = {"the", "a", "an", "and", "or", "but", "is", "are", "was", "were", 
                     "in", "on", "at", "to", "for", "with", "by", "about", "of", "from"}
        words = [word for word in words if word not in stop_words and len(word) > 3]
        
        # Count word frequencies
        word_counts = {}
        for word in words:
            word_counts[word] = word_counts.get(word, 0) + 1
        
        # Get most frequent words
        sorted_words = sorted(word_counts.items(), key=lambda x: x[1], reverse=True)
        key_terms = [word for word, _ in sorted_words[:max_terms]]
        
        logger.info(f"Extracted {len(key_terms)} key terms from context")
        return key_terms
    
    def extract_entities(self, context: str) -> List[str]:
        """
        Extract named entities from the conversation context.
        
        Args:
            context: The conversation context
            
        Returns:
            List of named entities extracted from the context
        """
        # This is a placeholder implementation
        # In a production system, this would use a proper NER model
        
        # For now, just return capitalized words as a simple approximation
        words = context.split()
        entities = [word for word in words if word and word[0].isupper()]
        
        # Remove duplicates
        entities = list(set(entities))
        
        logger.info(f"Extracted {len(entities)} entities from context")
        return entities
    
    def get_context_embedding(self, context: str) -> np.ndarray:
        """
        Generate an embedding for the conversation context.
        
        Args:
            context: The conversation context
            
        Returns:
            Vector embedding of the context
        """
        return self.embedding_provider.get_embedding(context)
    
    def analyze_context(self, context: str) -> Dict[str, Any]:
        """
        Perform a comprehensive analysis of the conversation context.
        
        Args:
            context: The conversation context
            
        Returns:
            Dictionary containing analysis results
        """
        logger.info("Analyzing conversation context")
        
        # Extract key information
        key_terms = self.extract_key_terms(context)
        entities = self.extract_entities(context)
        embedding = self.get_context_embedding(context)
        
        # Prepare result
        result = {
            "key_terms": key_terms,
            "entities": entities,
            "embedding": embedding,
            "context_length": len(context),
            "term_count": len(key_terms),
            "entity_count": len(entities)
        }
        
        logger.info("Context analysis complete")
        return result


class RelevanceScorer:
    """
    Scores the relevance of memory items to the current context.
    
    This class is responsible for determining how relevant a memory item
    is to the current conversation context, using various scoring methods.
    """
    
    def __init__(self, embedding_provider: Optional[EmbeddingProvider] = None):
        """
        Initialize the relevance scorer.
        
        Args:
            embedding_provider: Provider for generating text embeddings
        """
        logger.info("Initializing RelevanceScorer")
        self.embedding_provider = embedding_provider or EmbeddingProvider()
    
    def score_semantic_similarity(self, context_embedding: np.ndarray, memory_embedding: np.ndarray) -> float:
        """
        Score the semantic similarity between context and memory.
        
        Args:
            context_embedding: Embedding of the conversation context
            memory_embedding: Embedding of the memory item
            
        Returns:
            Similarity score between 0 and 1
        """
        # Calculate cosine similarity
        similarity = cosine_similarity([context_embedding], [memory_embedding])[0][0]
        
        # Ensure the score is between 0 and 1
        similarity = max(0.0, min(1.0, similarity))
        
        return similarity
    
    def score_term_overlap(self, context_terms: List[str], memory_value: str) -> float:
        """
        Score the overlap between context terms and memory content.
        
        Args:
            context_terms: Key terms from the conversation context
            memory_value: Content of the memory item
            
        Returns:
            Overlap score between 0 and 1
        """
        if not context_terms:
            return 0.0
        
        # Convert memory value to lowercase for case-insensitive matching
        memory_lower = memory_value.lower()
        
        # Count how many context terms appear in the memory
        matches = sum(1 for term in context_terms if term.lower() in memory_lower)
        
        # Calculate overlap score
        score = matches / len(context_terms)
        
        return score
    
    def score_recency(self, last_accessed_time, current_time) -> float:
        """
        Score the recency of a memory item.
        
        Args:
            last_accessed_time: When the memory was last accessed
            current_time: Current time
            
        Returns:
            Recency score between 0 and 1 (higher for more recent)
        """
        # Calculate time difference in seconds
        time_diff = (current_time - last_accessed_time).total_seconds()
        
        # Apply decay function (exponential decay)
        # Half-life of 1 day (86400 seconds)
        half_life = 86400
        decay_factor = 0.5 ** (time_diff / half_life)
        
        return decay_factor
    
    def score_importance(self, importance_score: float) -> float:
        """
        Score based on the importance of a memory item.
        
        Args:
            importance_score: Importance score of the memory item
            
        Returns:
            Importance score between 0 and 1
        """
        # Ensure the score is between 0 and 1
        return max(0.0, min(1.0, importance_score))
    
    def score_access_frequency(self, access_count: int, max_count: int = 100) -> float:
        """
        Score based on how frequently a memory item has been accessed.
        
        Args:
            access_count: Number of times the memory has been accessed
            max_count: Maximum access count to consider (for normalization)
            
        Returns:
            Frequency score between 0 and 1
        """
        # Normalize access count
        score = min(access_count, max_count) / max_count
        
        return score
    
    def calculate_combined_score(
        self,
        context_analysis: Dict[str, Any],
        memory_item: Dict[str, Any],
        weights: Optional[Dict[str, float]] = None
    ) -> float:
        """
        Calculate a combined relevance score for a memory item.
        
        Args:
            context_analysis: Analysis of the conversation context
            memory_item: The memory item to score
            weights: Weights for different scoring components
            
        Returns:
            Combined relevance score between 0 and 1
        """
        # Default weights
        default_weights = {
            "semantic_similarity": 0.5,
            "term_overlap": 0.2,
            "importance": 0.15,
            "recency": 0.1,
            "frequency": 0.05
        }
        
        # Use provided weights or defaults
        weights = weights or default_weights
        
        # Calculate individual scores
        scores = {}
        
        # Semantic similarity score
        if "embedding" in context_analysis and "embedding" in memory_item:
            scores["semantic_similarity"] = self.score_semantic_similarity(
                context_analysis["embedding"],
                memory_item["embedding"]
            )
        else:
            scores["semantic_similarity"] = 0.0
        
        # Term overlap score
        if "key_terms" in context_analysis and "value" in memory_item:
            scores["term_overlap"] = self.score_term_overlap(
                context_analysis["key_terms"],
                memory_item["value"]
            )
        else:
            scores["term_overlap"] = 0.0
        
        # Importance score
        if "importance_score" in memory_item:
            scores["importance"] = self.score_importance(memory_item["importance_score"])
        else:
            scores["importance"] = 0.5  # Default importance
        
        # Recency score
        if "last_accessed" in memory_item:
            import datetime
            scores["recency"] = self.score_recency(
                memory_item["last_accessed"],
                datetime.datetime.now()
            )
        else:
            scores["recency"] = 0.5  # Default recency
        
        # Frequency score
        if "access_count" in memory_item:
            scores["frequency"] = self.score_access_frequency(memory_item["access_count"])
        else:
            scores["frequency"] = 0.0  # Default frequency
        
        # Calculate weighted sum
        combined_score = sum(scores[key] * weights[key] for key in weights)
        
        return combined_score


class MemoryRetriever:
    """
    Retrieves relevant memory items based on the current context.
    
    This class is responsible for retrieving memory items that are relevant
    to the current conversation context, using various retrieval strategies.
    """
    
    def __init__(
        self,
        context_analyzer: Optional[ContextAnalyzer] = None,
        relevance_scorer: Optional[RelevanceScorer] = None,
        embedding_provider: Optional[EmbeddingProvider] = None
    ):
        """
        Initialize the memory retriever.
        
        Args:
            context_analyzer: Analyzer for conversation context
            relevance_scorer: Scorer for memory relevance
            embedding_provider: Provider for generating text embeddings
        """
        logger.info("Initializing MemoryRetriever")
        self.embedding_provider = embedding_provider or EmbeddingProvider()
        self.context_analyzer = context_analyzer or ContextAnalyzer(self.embedding_provider)
        self.relevance_scorer = relevance_scorer or RelevanceScorer(self.embedding_provider)
    
    def retrieve_by_key(self, memory_store: Dict[str, Any], key: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve a memory item by key.
        
        Args:
            memory_store: Store containing memory items
            key: Key of the memory to retrieve
            
        Returns:
            The memory item if found, None otherwise
        """
        return memory_store.get(key)
    
    def retrieve_by_type(self, memory_store: Dict[str, Any], memory_type: str) -> List[Dict[str, Any]]:
        """
        Retrieve memory items by type.
        
        Args:
            memory_store: Store containing memory items
            memory_type: Type of memories to retrieve
            
        Returns:
            List of memory items of the specified type
        """
        return [item for item in memory_store.values() if item.get("memory_type") == memory_type]
    
    def retrieve_by_semantic_search(
        self,
        memory_store: Dict[str, Any],
        query: str,
        limit: int = 10
    ) -> List[Tuple[Dict[str, Any], float]]:
        """
        Retrieve memory items by semantic search.
        
        Args:
            memory_store: Store containing memory items
            query: Search query
            limit: Maximum number of items to retrieve
            
        Returns:
            List of (memory item, similarity score) tuples
        """
        if not memory_store:
            return []
        
        # Generate embedding for the query
        query_embedding = self.embedding_provider.get_embedding(query)
        
        # Calculate similarity with all memory items
        similarities = []
        for key, item in memory_store.items():
            if "embedding" not in item:
                continue
            
            similarity = self.relevance_scorer.score_semantic_similarity(
                query_embedding,
                item["embedding"]
            )
            
            similarities.append((item, similarity))
        
        # Sort by similarity (descending)
        similarities.sort(key=lambda x: x[1], reverse=True)
        
        # Return top results
        return similarities[:limit]
    
    def retrieve_by_term_match(
        self,
        memory_store: Dict[str, Any],
        terms: List[str],
        limit: int = 10
    ) -> List[Tuple[Dict[str, Any], float]]:
        """
        Retrieve memory items by matching terms.
        
        Args:
            memory_store: Store containing memory items
            terms: List of terms to match
            limit: Maximum number of items to retrieve
            
        Returns:
            List of (memory item, match score) tuples
        """
        if not memory_store or not terms:
            return []
        
        # Calculate term overlap with all memory items
        matches = []
        for key, item in memory_store.items():
            if "value" not in item:
                continue
            
            score = self.relevance_scorer.score_term_overlap(terms, item["value"])
            
            if score > 0:
                matches.append((item, score))
        
        # Sort by match score (descending)
        matches.sort(key=lambda x: x[1], reverse=True)
        
        # Return top results
        return matches[:limit]
    
    def retrieve_by_context(
        self,
        memory_store: Dict[str, Any],
        context: str,
        limit: int = 10,
        weights: Optional[Dict[str, float]] = None
    ) -> List[Tuple[Dict[str, Any], float]]:
        """
        Retrieve memory items relevant to the current context.
        
        Args:
            memory_store: Store containing memory items
            context: The conversation context
            limit: Maximum number of items to retrieve
            weights: Weights for different scoring components
            
        Returns:
            List of (memory item, relevance score) tuples
        """
        if not memory_store:
            return []
        
        logger.info(f"Retrieving memories relevant to context (limit: {limit})")
        
        # Analyze the context
        context_analysis = self.context_analyzer.analyze_context(context)
        
        # Score all memory items
        scored_items = []
        for key, item in memory_store.items():
            score = self.relevance_scorer.calculate_combined_score(
                context_analysis,
                item,
                weights
            )
            
            scored_items.append((item, score))
        
        # Sort by relevance score (descending)
        scored_items.sort(key=lambda x: x[1], reverse=True)
        
        # Return top results
        results = scored_items[:limit]
        logger.info(f"Retrieved {len(results)} relevant memories")
        
        return results
    
    def retrieve_by_hybrid_search(
        self,
        memory_store: Dict[str, Any],
        context: str,
        query: str,
        limit: int = 10,
        context_weight: float = 0.7,
        query_weight: float = 0.3
    ) -> List[Tuple[Dict[str, Any], float]]:
        """
        Retrieve memory items using a hybrid of context and query.
        
        Args:
            memory_store: Store containing memory items
            context: The conversation context
            query: Explicit search query
            limit: Maximum number of items to retrieve
            context_weight: Weight for context-based retrieval
            query_weight: Weight for query-based retrieval
            
        Returns:
            List of (memory item, relevance score) tuples
        """
        if not memory_store:
            return []
        
        logger.info(f"Performing hybrid search (limit: {limit})")
        
        # Get context-based results
        context_results = self.retrieve_by_context(memory_store, context, limit * 2)
        
        # Get query-based results
        query_results = self.retrieve_by_semantic_search(memory_store, query, limit * 2)
        
        # Combine results with weighted scores
        combined_scores = {}
        
        for item, score in context_results:
            item_key = item.get("id", id(item))  # Use ID or object ID as key
            combined_scores[item_key] = (item, score * context_weight)
        
        for item, score in query_results:
            item_key = item.get("id", id(item))
            if item_key in combined_scores:
                # Add query score to existing item
                existing_item, existing_score = combined_scores[item_key]
                combined_scores[item_key] = (existing_item, existing_score + score * query_weight)
            else:
                # Add new item with query score
                combined_scores[item_key] = (item, score * query_weight)
        
        # Convert to list and sort by combined score
        results = list(combined_scores.values())
        results.sort(key=lambda x: x[1], reverse=True)
        
        # Return top results
        final_results = results[:limit]
        logger.info(f"Retrieved {len(final_results)} memories with hybrid search")
        
        return final_results


class MemoryRetrievalOptimizer:
    """
    Optimizes memory retrieval for the Advanced Memory System.
    
    This class provides a unified interface for optimized memory retrieval,
    combining various retrieval strategies and optimizations.
    """
    
    def __init__(
        self,
        memory_retriever: Optional[MemoryRetriever] = None,
        embedding_provider: Optional[EmbeddingProvider] = None
    ):
        """
        Initialize the memory retrieval optimizer.
        
        Args:
            memory_retriever: Retriever for memory items
            embedding_provider: Provider for generating text embeddings
        """
        logger.info("Initializing MemoryRetrievalOptimizer")
        self.embedding_provider = embedding_provider or EmbeddingProvider()
        self.memory_retriever = memory_retriever or MemoryRetriever(
            embedding_provider=self.embedding_provider
        )
        
        # Cache for recent retrievals
        self.retrieval_cache = {}
        self.cache_size = 100
    
    def retrieve_memories(
        self,
        memory_store: Dict[str, Any],
        context: str,
        query: Optional[str] = None,
        memory_type: Optional[str] = None,
        limit: int = 10,
        strategy: str = "context"
    ) -> List[Tuple[Dict[str, Any], float]]:
        """
        Retrieve relevant memories using the specified strategy.
        
        Args:
            memory_store: Store containing memory items
            context: The conversation context
            query: Explicit search query (optional)
            memory_type: Type of memories to retrieve (optional)
            limit: Maximum number of items to retrieve
            strategy: Retrieval strategy ("context", "semantic", "hybrid", "term", "type")
            
        Returns:
            List of (memory item, relevance score) tuples
        """
        logger.info(f"Retrieving memories with strategy: {strategy}")
        
        # Check cache first
        cache_key = f"{strategy}:{context[:100]}:{query or ''}:{memory_type or ''}:{limit}"
        if cache_key in self.retrieval_cache:
            logger.info("Using cached retrieval results")
            return self.retrieval_cache[cache_key]
        
        # Filter by type if specified
        if memory_type:
            filtered_store = {
                key: item for key, item in memory_store.items()
                if item.get("memory_type") == memory_type
            }
        else:
            filtered_store = memory_store
        
        # Retrieve using the specified strategy
        if strategy == "context":
            results = self.memory_retriever.retrieve_by_context(filtered_store, context, limit)
        elif strategy == "semantic":
            results = self.memory_retriever.retrieve_by_semantic_search(
                filtered_store, query or context, limit
            )
        elif strategy == "hybrid":
            results = self.memory_retriever.retrieve_by_hybrid_search(
                filtered_store, context, query or context, limit
            )
        elif strategy == "term":
            # Extract terms from context
            terms = self.memory_retriever.context_analyzer.extract_key_terms(context)
            results = self.memory_retriever.retrieve_by_term_match(filtered_store, terms, limit)
        elif strategy == "type":
            if not memory_type:
                logger.warning("No memory type specified for 'type' strategy")
                return []
            type_items = self.memory_retriever.retrieve_by_type(filtered_store, memory_type)
            # Sort by importance and recency
            scored_items = []
            for item in type_items:
                importance = item.get("importance_score", 0.5)
                recency = 0.5  # Default recency
                if "last_accessed" in item:
                    import datetime
                    recency = self.memory_retriever.relevance_scorer.score_recency(
                        item["last_accessed"],
                        datetime.datetime.now()
                    )
                score = importance * 0.7 + recency * 0.3
                scored_items.append((item, score))
            scored_items.sort(key=lambda x: x[1], reverse=True)
            results = scored_items[:limit]
        else:
            logger.warning(f"Unknown retrieval strategy: {strategy}")
            return []
        
        # Update cache
        self.retrieval_cache[cache_key] = results
        
        # Trim cache if needed
        if len(self.retrieval_cache) > self.cache_size:
            # Remove oldest entries
            oldest_keys = list(self.retrieval_cache.keys())[:-self.cache_size]
            for key in oldest_keys:
                del self.retrieval_cache[key]
        
        return results
    
    def optimize_retrieval_strategy(
        self,
        memory_store: Dict[str, Any],
        context: str,
        query: Optional[str] = None,
        memory_type: Optional[str] = None,
        limit: int = 10
    ) -> List[Tuple[Dict[str, Any], float]]:
        """
        Automatically select and use the best retrieval strategy.
        
        Args:
            memory_store: Store containing memory items
            context: The conversation context
            query: Explicit search query (optional)
            memory_type: Type of memories to retrieve (optional)
            limit: Maximum number of items to retrieve
            
        Returns:
            List of (memory item, relevance score) tuples
        """
        logger.info("Optimizing retrieval strategy")
        
        # Determine the best strategy based on inputs
        if query and len(query) > 10:
            # If a specific query is provided, use hybrid search
            strategy = "hybrid"
        elif memory_type:
            # If a specific memory type is requested, use type-based retrieval
            strategy = "type"
        elif len(context) < 50:
            # For very short contexts, use term matching
            strategy = "term"
        else:
            # Default to context-based retrieval
            strategy = "context"
        
        logger.info(f"Selected strategy: {strategy}")
        
        # Retrieve using the selected strategy
        return self.retrieve_memories(
            memory_store,
            context,
            query,
            memory_type,
            limit,
            strategy
        )
    
    def retrieve_and_rank(
        self,
        memory_store: Dict[str, Any],
        context: str,
        query: Optional[str] = None,
        memory_type: Optional[str] = None,
        limit: int = 10,
        diversity_factor: float = 0.2
    ) -> List[Dict[str, Any]]:
        """
        Retrieve and rank memories with diversity consideration.
        
        Args:
            memory_store: Store containing memory items
            context: The conversation context
            query: Explicit search query (optional)
            memory_type: Type of memories to retrieve (optional)
            limit: Maximum number of items to retrieve
            diversity_factor: Factor for promoting diversity (0-1)
            
        Returns:
            List of memory items
        """
        logger.info(f"Retrieving and ranking memories with diversity factor: {diversity_factor}")
        
        # Get initial results
        results = self.optimize_retrieval_strategy(
            memory_store,
            context,
            query,
            memory_type,
            limit * 2  # Get more results for diversity
        )
        
        if not results:
            return []
        
        # If diversity is not important, just return top results
        if diversity_factor <= 0:
            return [item for item, _ in results[:limit]]
        
        # Apply maximal marginal relevance for diversity
        selected_items = []
        selected_indices = []
        
        # Get all items and scores
        items = [item for item, _ in results]
        scores = [score for _, score in results]
        
        # Get embeddings for all items
        item_embeddings = []
        for item in items:
            if "embedding" in item:
                item_embeddings.append(item["embedding"])
            else:
                # Generate embedding for items without one
                value = item.get("value", "")
                embedding = self.embedding_provider.get_embedding(value)
                item_embeddings.append(embedding)
        
        # Select items one by one
        while len(selected_items) < limit and results:
            # If this is the first item, select the highest scoring one
            if not selected_items:
                best_idx = 0  # Index of highest scoring item
            else:
                # Apply maximal marginal relevance
                best_score = -1
                best_idx = -1
                
                for i in range(len(items)):
                    if i in selected_indices:
                        continue
                    
                    # Calculate similarity to already selected items
                    similarities = []
                    for j in selected_indices:
                        sim = cosine_similarity([item_embeddings[i]], [item_embeddings[j]])[0][0]
                        similarities.append(sim)
                    
                    max_similarity = max(similarities) if similarities else 0
                    
                    # Calculate MMR score
                    mmr_score = (1 - diversity_factor) * scores[i] - diversity_factor * max_similarity
                    
                    if mmr_score > best_score:
                        best_score = mmr_score
                        best_idx = i
            
            # Add the selected item
            selected_items.append(items[best_idx])
            selected_indices.append(best_idx)
        
        logger.info(f"Retrieved {len(selected_items)} diverse memories")
        return selected_items
