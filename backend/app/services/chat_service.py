from app.services.language_service import LanguageService
from app.services.retrieval_service import RetrievalService
from app.services.prompt_service import PromptService
from app.clients.llm_client import LLMClient
from app.services.session_service import SessionService
from app.core.config import settings
from app.models.chat import ChatRequest, ChatResponse

class ChatService:
    def __init__(self):
        self.language_service = LanguageService()
        self.retrieval_service = RetrievalService()
        self.prompt_service = PromptService()
        self.llm_client = LLMClient(settings.LLM_PROVIDER, settings.LLM_API_KEY)
        self.session_service = SessionService()

    async def handle_chat(self, request: ChatRequest) -> ChatResponse:
        # 1. Determine language
        language = request.language or self.language_service.detect_language(request.message)
        # 2. Retrieve context
        retrieved = await self.retrieval_service.retrieve(request.message)
        context_chunks = retrieved.get('documents', []) if retrieved else []
        # 3. Build prompt
        prompt = self.prompt_service.build_prompt(request.message, context_chunks, language)
        # 4. Generate answer
        answer = await self.llm_client.generate(prompt, language=language)
        # 5. Save session turn
        await self.session_service.save_turn(request.session_id, {"user": request.message, "bot": answer})
        # 6. Fallback logic
        fallback_used = not bool(context_chunks)
        return ChatResponse(
            answer=answer,
            language=language,
            sources=context_chunks,
            fallback_used=fallback_used
        )

    async def handle_escalation(self, request):
        # Placeholder for escalation logic
        return {"escalated": True, "detail": "Escalation triggered."}
