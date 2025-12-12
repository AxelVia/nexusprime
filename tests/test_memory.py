"""Tests for NexusMemory module."""

from __future__ import annotations

import json
import pytest

from nexusprime.integrations.memory import NexusMemory


class TestNexusMemory:
    """Test cases for NexusMemory."""
    
    def test_init_creates_empty_memory(self, temp_memory_file):
        """Test that initialization creates empty memory."""
        memory = NexusMemory(memory_path=temp_memory_file, use_embeddings=False)
        assert memory.data == {"lessons": []}
    
    def test_store_lesson(self, temp_memory_file):
        """Test storing a lesson."""
        memory = NexusMemory(memory_path=temp_memory_file, use_embeddings=False)
        
        lesson_id = memory.store_lesson(
            topic="Testing",
            context="Unit test context",
            outcome="Success",
            solution="Use pytest"
        )
        
        assert len(memory.data["lessons"]) == 1
        assert memory.data["lessons"][0]["topic"] == "Testing"
        assert memory.data["lessons"][0]["id"] == lesson_id
    
    def test_retrieve_context_keywords(self, temp_memory_file):
        """Test retrieving context with keyword matching."""
        memory = NexusMemory(memory_path=temp_memory_file, use_embeddings=False)
        
        memory.store_lesson(
            topic="Python Testing",
            context="Unit testing",
            outcome="Success",
            solution="Use pytest framework"
        )
        
        memory.store_lesson(
            topic="JavaScript Testing",
            context="Unit testing",
            outcome="Success",
            solution="Use Jest"
        )
        
        result = memory.retrieve_context("Python testing")
        assert "Python Testing" in result
        assert "pytest" in result
    
    def test_retrieve_context_no_matches(self, temp_memory_file):
        """Test retrieving context with no matches."""
        memory = NexusMemory(memory_path=temp_memory_file, use_embeddings=False)
        
        memory.store_lesson(
            topic="Testing",
            context="Unit test",
            outcome="Success",
            solution="Use pytest"
        )
        
        result = memory.retrieve_context("completely different topic")
        assert "No prior lessons found" in result
    
    def test_delete_lesson(self, temp_memory_file):
        """Test deleting a lesson."""
        memory = NexusMemory(memory_path=temp_memory_file, use_embeddings=False)
        
        lesson_id = memory.store_lesson(
            topic="Testing",
            context="Unit test",
            outcome="Success",
            solution="Use pytest"
        )
        
        assert len(memory.data["lessons"]) == 1
        
        deleted = memory.delete_lesson(lesson_id)
        assert deleted is True
        assert len(memory.data["lessons"]) == 0
    
    def test_delete_nonexistent_lesson(self, temp_memory_file):
        """Test deleting a lesson that doesn't exist."""
        memory = NexusMemory(memory_path=temp_memory_file, use_embeddings=False)
        
        deleted = memory.delete_lesson("nonexistent-id")
        assert deleted is False
    
    def test_list_lessons(self, temp_memory_file):
        """Test listing lessons."""
        memory = NexusMemory(memory_path=temp_memory_file, use_embeddings=False)
        
        memory.store_lesson("Topic 1", "Context 1", "Success", "Solution 1")
        memory.store_lesson("Topic 2", "Context 2", "Success", "Solution 2")
        
        lessons = memory.list_lessons()
        assert len(lessons) == 2
    
    def test_list_lessons_with_limit(self, temp_memory_file):
        """Test listing lessons with limit."""
        memory = NexusMemory(memory_path=temp_memory_file, use_embeddings=False)
        
        memory.store_lesson("Topic 1", "Context 1", "Success", "Solution 1")
        memory.store_lesson("Topic 2", "Context 2", "Success", "Solution 2")
        memory.store_lesson("Topic 3", "Context 3", "Success", "Solution 3")
        
        lessons = memory.list_lessons(limit=2)
        assert len(lessons) == 2
    
    def test_persistence(self, temp_memory_file):
        """Test that lessons are persisted to disk."""
        memory1 = NexusMemory(memory_path=temp_memory_file, use_embeddings=False)
        memory1.store_lesson("Topic", "Context", "Success", "Solution")
        
        # Create new instance to load from disk
        memory2 = NexusMemory(memory_path=temp_memory_file, use_embeddings=False)
        assert len(memory2.data["lessons"]) == 1
        assert memory2.data["lessons"][0]["topic"] == "Topic"
