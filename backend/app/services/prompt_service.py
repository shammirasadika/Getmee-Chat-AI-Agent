from app.services.language_service import LanguageService
from app.core.prompts import RAG_PROMPT, RAG_FORCE_ANSWER_PROMPT

class PromptService:
    @staticmethod
    def build_prompt(query: str, context_chunks: list, language: str) -> str:
        # context_chunks is a list of lists of strings (from ChromaDB)
        context_text = '\n'.join([doc for chunk in context_chunks for doc in chunk])
        lang_name = LanguageService.get_language_name(language)
        prompt = RAG_PROMPT.format(
            language=lang_name,
            context=context_text,
            question=query
        )
        print(f"[DEBUG] LLM PROMPT SENT TO MODEL:\n{prompt}", flush=True)
        return prompt

    @staticmethod
    def build_force_answer_prompt(query: str, context_chunks: list, language: str) -> str:
        context_text = '\n'.join([doc for chunk in context_chunks for doc in chunk])
        lang_name = LanguageService.get_language_name(language)
        return RAG_FORCE_ANSWER_PROMPT.format(
            language=lang_name,
            context=context_text,
            question=query
        )
