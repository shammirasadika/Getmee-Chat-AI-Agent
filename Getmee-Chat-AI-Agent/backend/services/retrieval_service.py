import json
import re
from pathlib import Path


class RetrievalService:

    def __init__(self):
        # path to knowledge.json
        self.knowledge_path = (
            Path(__file__).resolve().parent.parent / "data" / "knowledge.json"
        )

    def clean_text(self, text: str) -> str:
        """
        Lowercase + remove punctuation.
        """
        text = text.lower()
        return re.sub(r"[^\w\s]", "", text)

    def retrieve(self, query: str) -> str:
        """
        Simple keyword-based retrieval using word overlap scoring.
        Longer matching words get higher weight.
        """
        try:
            with open(self.knowledge_path, "r", encoding="utf-8") as file:
                data = json.load(file)

            cleaned_query = self.clean_text(query)
            query_words = set(cleaned_query.split())

            best_match = None
            max_score = 0

            for item in data:
                cleaned_content = self.clean_text(item["content"])
                content_words = set(cleaned_content.split())

                # find overlapping words
                overlap = query_words.intersection(content_words)

                # weighted score: longer words matter more
                score = sum(len(word) for word in overlap)

                if score > max_score:
                    max_score = score
                    best_match = item["content"]

            if best_match:
                return best_match

            return "No relevant information found."

        except Exception as e:
            return f"Error retrieving knowledge: {str(e)}"