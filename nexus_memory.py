import json
import os
from typing import List, Dict

MEMORY_FILE = "nexus_memory.json"

class NexusMemory:
    """
    Auto-learning module for NexusPrime.
    Stores lessons from past successes/failures and retrieves them for context.
    """
    def __init__(self, memory_path: str = MEMORY_FILE):
        self.memory_path = memory_path
        self._load_memory()

    def _load_memory(self):
        if os.path.exists(self.memory_path):
            with open(self.memory_path, "r") as f:
                self.data = json.load(f)
        else:
            self.data = {"lessons": []}

    def _save_memory(self):
        with open(self.memory_path, "w") as f:
            json.dump(self.data, f, indent=2)

    def store_lesson(self, topic: str, context: str, outcome: str, solution: str):
        """
        Saves a lesson to the permanent memory.
        """
        lesson = {
            "topic": topic,
            "context": context,
            "outcome": outcome,
            "solution": solution
        }
        self.data["lessons"].append(lesson)
        self._save_memory()
        print(f"--- [Memory] Lesson stored for topic: {topic} ---")

    def retrieve_context(self, query: str) -> str:
        """
        Retrieves relevant lessons based on keyword matching (Simple RAG).
        In a real prod env, this would use vector embeddings.
        """
        relevant_lessons = []
        for lesson in self.data["lessons"]:
            if any(word in lesson["topic"].lower() for word in query.lower().split()):
                relevant_lessons.append(lesson)
        
        if not relevant_lessons:
            return "No prior lessons found for this topic."
        
        formatted = "### PREVIOUS LESSONS LEARNED:\n"
        for l in relevant_lessons:
            formatted += f"- **{l['topic']}**: {l['solution']}\n"
        return formatted

if __name__ == "__main__":
    # Test
    mem = NexusMemory()
    mem.store_lesson("pip_install", "Failed to install package", "fixed", "Use pip install --user")
    print(mem.retrieve_context("install pip package"))
