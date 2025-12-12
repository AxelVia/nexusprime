"""Enhanced memory module with RAG using embeddings."""

from __future__ import annotations

import json
import os
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from ..utils.logging import get_logger

logger = get_logger(__name__)

# Optional: Try to import sentence-transformers for embeddings
try:
    from sentence_transformers import SentenceTransformer
    import numpy as np
    EMBEDDINGS_AVAILABLE = True
except ImportError:
    EMBEDDINGS_AVAILABLE = False
    logger.warning("sentence-transformers not available. Falling back to keyword search.")


class NexusMemory:
    """
    Enhanced auto-learning module for NexusPrime with RAG capabilities.
    Stores lessons from past successes/failures and retrieves them using embeddings.
    """
    
    def __init__(self, memory_path: str = "nexus_memory.json", use_embeddings: bool = True):
        """
        Initialize NexusMemory.
        
        Args:
            memory_path: Path to JSON storage file
            use_embeddings: Whether to use embeddings (requires sentence-transformers)
        """
        self.memory_path = memory_path
        self.use_embeddings = use_embeddings and EMBEDDINGS_AVAILABLE
        self.model: Optional[Any] = None
        
        if self.use_embeddings:
            try:
                self.model = SentenceTransformer('all-MiniLM-L6-v2')
                logger.info("Embeddings model loaded: all-MiniLM-L6-v2")
            except Exception as e:
                logger.warning(f"Failed to load embeddings model: {e}. Falling back to keyword search.")
                self.use_embeddings = False
        
        self._load_memory()
    
    def _load_memory(self) -> None:
        """Load memory from disk."""
        if os.path.exists(self.memory_path):
            try:
                with open(self.memory_path, "r", encoding="utf-8") as f:
                    self.data = json.load(f)
                logger.info(f"Memory loaded: {len(self.data.get('lessons', []))} lessons")
            except json.JSONDecodeError as e:
                logger.error(f"Invalid JSON in memory file: {e}")
                self.data = {"lessons": []}
            except (OSError, IOError) as e:
                logger.error(f"Failed to load memory file: {e}")
                self.data = {"lessons": []}
        else:
            self.data = {"lessons": []}
            logger.info("No existing memory file. Starting fresh.")
    
    def _save_memory(self) -> None:
        """Save memory to disk."""
        try:
            with open(self.memory_path, "w", encoding="utf-8") as f:
                json.dump(self.data, f, indent=2, ensure_ascii=False)
            logger.debug(f"Memory saved to {self.memory_path}")
        except (OSError, IOError) as e:
            logger.error(f"Failed to save memory: {e}")
    
    def _compute_embedding(self, text: str) -> Optional[List[float]]:
        """
        Compute embedding for text.
        
        Args:
            text: Text to embed
        
        Returns:
            Embedding vector or None if unavailable
        """
        if not self.use_embeddings or self.model is None:
            return None
        
        try:
            embedding = self.model.encode(text)
            return embedding.tolist()
        except Exception as e:
            logger.error(f"Failed to compute embedding: {e}")
            return None
    
    def store_lesson(
        self,
        topic: str,
        context: str,
        outcome: str,
        solution: str
    ) -> str:
        """
        Save a lesson to permanent memory.
        
        Args:
            topic: Lesson topic
            context: Context in which lesson was learned
            outcome: Outcome (success/failure)
            solution: Solution or learning
        
        Returns:
            Unique lesson ID
        """
        lesson_id = str(uuid.uuid4())
        timestamp = datetime.now().isoformat()
        
        # Compute embedding from topic + context
        embedding_text = f"{topic} {context}"
        embedding = self._compute_embedding(embedding_text)
        
        lesson: Dict[str, Any] = {
            "id": lesson_id,
            "topic": topic,
            "context": context,
            "outcome": outcome,
            "solution": solution,
            "timestamp": timestamp
        }
        
        if embedding is not None:
            lesson["embedding"] = embedding
        
        self.data["lessons"].append(lesson)
        self._save_memory()
        
        logger.info(f"Lesson stored: {topic} (ID: {lesson_id})")
        return lesson_id
    
    def retrieve_context(self, query: str, top_k: int = 5) -> str:
        """
        Retrieve relevant lessons based on query.
        Uses cosine similarity if embeddings available, else keyword matching.
        
        Args:
            query: Search query
            top_k: Maximum number of lessons to return
        
        Returns:
            Formatted string of relevant lessons
        """
        lessons = self.data.get("lessons", [])
        
        if not lessons:
            return "No prior lessons found."
        
        if self.use_embeddings and self.model is not None:
            return self._retrieve_with_embeddings(query, top_k)
        else:
            return self._retrieve_with_keywords(query, top_k)
    
    def _retrieve_with_embeddings(self, query: str, top_k: int) -> str:
        """Retrieve using cosine similarity on embeddings."""
        query_embedding = self._compute_embedding(query)
        
        if query_embedding is None:
            logger.warning("Failed to compute query embedding, falling back to keywords")
            return self._retrieve_with_keywords(query, top_k)
        
        # Filter lessons that have embeddings
        lessons_with_embeddings = [
            l for l in self.data["lessons"] if "embedding" in l
        ]
        
        if not lessons_with_embeddings:
            logger.warning("No lessons with embeddings found, falling back to keywords")
            return self._retrieve_with_keywords(query, top_k)
        
        # Compute similarities
        similarities = []
        query_emb_np = np.array(query_embedding)
        
        for lesson in lessons_with_embeddings:
            lesson_emb = np.array(lesson["embedding"])
            # Cosine similarity
            similarity = np.dot(query_emb_np, lesson_emb) / (
                np.linalg.norm(query_emb_np) * np.linalg.norm(lesson_emb)
            )
            similarities.append((lesson, float(similarity)))
        
        # Sort by similarity (descending)
        similarities.sort(key=lambda x: x[1], reverse=True)
        
        # Take top_k
        top_lessons = similarities[:top_k]
        
        if not top_lessons:
            return "No relevant lessons found."
        
        formatted = "### PREVIOUS LESSONS LEARNED:\n"
        for lesson, score in top_lessons:
            formatted += f"- **{lesson['topic']}** (similarity: {score:.2f}): {lesson['solution']}\n"
        
        logger.debug(f"Retrieved {len(top_lessons)} lessons using embeddings")
        return formatted
    
    def _retrieve_with_keywords(self, query: str, top_k: int) -> str:
        """Retrieve using simple keyword matching (fallback)."""
        query_words = set(query.lower().split())
        relevant_lessons = []
        
        for lesson in self.data["lessons"]:
            topic_words = set(lesson["topic"].lower().split())
            context_words = set(lesson["context"].lower().split())
            
            # Count matching words
            matches = len(query_words & (topic_words | context_words))
            if matches > 0:
                relevant_lessons.append((lesson, matches))
        
        # Sort by match count
        relevant_lessons.sort(key=lambda x: x[1], reverse=True)
        
        # Take top_k
        top_lessons = relevant_lessons[:top_k]
        
        if not top_lessons:
            return "No prior lessons found for this topic."
        
        formatted = "### PREVIOUS LESSONS LEARNED:\n"
        for lesson, _ in top_lessons:
            formatted += f"- **{lesson['topic']}**: {lesson['solution']}\n"
        
        logger.debug(f"Retrieved {len(top_lessons)} lessons using keywords")
        return formatted
    
    def delete_lesson(self, lesson_id: str) -> bool:
        """
        Delete a lesson by ID.
        
        Args:
            lesson_id: Unique lesson ID
        
        Returns:
            True if deleted, False if not found
        """
        original_count = len(self.data["lessons"])
        self.data["lessons"] = [l for l in self.data["lessons"] if l.get("id") != lesson_id]
        
        if len(self.data["lessons"]) < original_count:
            self._save_memory()
            logger.info(f"Lesson deleted: {lesson_id}")
            return True
        
        logger.warning(f"Lesson not found for deletion: {lesson_id}")
        return False
    
    def list_lessons(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        List all lessons.
        
        Args:
            limit: Optional limit on number of lessons
        
        Returns:
            List of lessons (most recent first)
        """
        lessons = sorted(
            self.data.get("lessons", []),
            key=lambda x: x.get("timestamp", ""),
            reverse=True
        )
        
        if limit:
            return lessons[:limit]
        return lessons
