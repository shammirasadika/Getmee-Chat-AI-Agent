class PromptService:
    @staticmethod
    def build_prompt(query: str, context_chunks: list, language: str) -> str:
        context_text = '\n'.join([chunk['text'] for chunk in context_chunks])
        prompt = f"Answer the following question in {language}:\nContext:\n{context_text}\nQuestion: {query}"
        return prompt
