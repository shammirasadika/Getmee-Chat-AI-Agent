from app.services.language_service import LanguageService
from app.services.retrieval_service import RetrievalService
from app.services.prompt_service import PromptService
from app.clients.llm_client import LLMClient
from app.services.session_service import SessionService
from app.core.config import settings
from app.models.chat import ChatRequest, ChatResponse
from app.utils.helpers import clean_context_chunk, is_meaningful_chunk, filter_relevant_chunks, is_language_clean, MIN_PRIMARY_CONFIDENCE

class ChatService:
    def __init__(self):
        self.language_service = LanguageService()
        self.retrieval_service = RetrievalService()
        self.prompt_service = PromptService()
        self.llm_client = LLMClient(settings.LLM_PROVIDER, settings.LLM_API_KEY)
        self.session_service = SessionService()

    def _extract_meaningful_chunks(self, retrieved: dict, query: str, label: str, is_cross_language: bool = False) -> tuple:
        """Extract, clean, validate, and relevance-filter chunks from retrieval results.
        Returns (relevant_chunks, max_overlap).
        """
        context_chunks = retrieved.get('documents', [])
        flat_chunks = [doc for chunk in context_chunks for doc in chunk]
        raw_count = len(flat_chunks)

        # Step 1: Clean
        cleaned = [clean_context_chunk(doc[:300]) for doc in flat_chunks[:5]]

        # Step 2: Meaningful filter
        meaningful = [c for c in cleaned if is_meaningful_chunk(c)]
        meaningful_count = len(meaningful)

        # Step 3: Relevance filter
        # For cross-language fallback, trust vector DB distance (keyword matching fails across languages)
        relevant, rejected_count, reasons, max_overlap = filter_relevant_chunks(
            meaningful, query, is_cross_language=is_cross_language
        )
        relevant = relevant[:2]

        print(
            f"[Chat] [{label}] Raw: {raw_count} → Meaningful: {meaningful_count} "
            f"→ Relevant: {len(relevant)} (rejected {rejected_count}) "
            f"[cross_lang={is_cross_language}, confidence={max_overlap:.2f}]",
            flush=True
        )
        for reason in reasons:
            print(f"[Chat] [{label}] Relevance: {reason}", flush=True)
        for i, c in enumerate(relevant):
            print(f"[Chat] [{label}] Chunk {i+1} ({len(c)} chars): '{c[:80]}...'", flush=True)
        return relevant, max_overlap

    async def _attempt_retrieval(self, query: str, original_query: str, language: str, label: str, is_cross_language: bool = False):
        """Attempt retrieval and return (retrieved, relevant_chunks, best_distance, confidence).
        query: the search query (may be translated)
        original_query: the user's original query (for relevance matching)
        is_cross_language: if True, skip keyword-based relevance (trust vector distance)
        confidence: keyword overlap ratio (0.0-1.0) — higher means chunks strongly match query
        """
        retrieved = await self.retrieval_service.retrieve(query)
        distance_ok = self.retrieval_service.has_relevant_results(retrieved)
        best_distance = self.retrieval_service.get_best_distance(retrieved)
        print(f"[Chat] [{label}] distance_ok={distance_ok}, best_distance={best_distance:.3f}", flush=True)
        if not distance_ok:
            return retrieved, [], best_distance, 0.0
        # For cross-language, trust vector similarity and only filter by content quality
        relevant, max_overlap = self._extract_meaningful_chunks(retrieved, query, label, is_cross_language=is_cross_language)
        return retrieved, relevant, best_distance, max_overlap

    async def handle_chat(self, request: ChatRequest) -> ChatResponse:
        # 1. Determine user language
        language = request.language or self.language_service.detect_language(request.message)
        lang_name = self.language_service.get_language_name(language)
        retrieval_language = language
        fallback_used = False

        print(f"[Chat] User language: {language} ({lang_name}) | Query: '{request.message[:80]}'", flush=True)

        # 2. Primary retrieval
        print(f"[Chat] Step 2: Primary retrieval in '{language}'...", flush=True)
        retrieved, relevant_chunks, primary_distance, primary_confidence = await self._attempt_retrieval(
            request.message, request.message, language, "PRIMARY"
        )

        # 3. Fallback if primary has no relevant chunks OR primary is weak (low confidence)
        primary_is_weak = relevant_chunks and primary_confidence < MIN_PRIMARY_CONFIDENCE
        if primary_is_weak:
            print(
                f"[Chat] Step 3: Primary has chunks but LOW confidence ({primary_confidence:.2f} < {MIN_PRIMARY_CONFIDENCE}) "
                f"— attempting fallback to find stronger match",
                flush=True
            )
        if not relevant_chunks or primary_is_weak:
            fallback_lang = self.language_service.get_fallback_language(language)
            print(f"[Chat] Step 3: Attempting fallback in '{fallback_lang}'...", flush=True)
            if fallback_lang != language:
                fallback_lang_name = self.language_service.get_language_name(fallback_lang)
                try:
                    translated_query = await self.llm_client.translate(
                        request.message, target_language=fallback_lang_name
                    )
                    print(f"[Chat] Translated query: '{translated_query[:80]}'", flush=True)
                    fb_retrieved, fb_chunks, fb_distance, fb_confidence = await self._attempt_retrieval(
                        translated_query, request.message, fallback_lang, "FALLBACK",
                        is_cross_language=True
                    )
                    # Use fallback if: primary had nothing, OR fallback is stronger than weak primary
                    use_fallback = False
                    if fb_chunks:
                        if not relevant_chunks:
                            use_fallback = True
                            print(f"[Chat] Fallback fills empty primary", flush=True)
                        elif primary_is_weak and fb_confidence > primary_confidence:
                            use_fallback = True
                            print(
                                f"[Chat] Fallback confidence ({fb_confidence:.2f}) > weak primary ({primary_confidence:.2f})",
                                flush=True
                            )
                        elif primary_is_weak:
                            print(
                                f"[Chat] Fallback not stronger ({fb_confidence:.2f} vs {primary_confidence:.2f}) — keeping weak primary",
                                flush=True
                            )
                    if use_fallback:
                        relevant_chunks = fb_chunks
                        retrieved = fb_retrieved
                        retrieval_language = fallback_lang
                        fallback_used = True
                        print(f"[Chat] Fallback SUCCESS — using '{fallback_lang}' results ({len(fb_chunks)} relevant chunks)", flush=True)
                    elif not fb_chunks:
                        print(f"[Chat] Fallback also has no relevant chunks in '{fallback_lang}'", flush=True)
                except Exception as e:
                    print(f"[Chat] Fallback error: {e}", flush=True)
            else:
                print(f"[Chat] No fallback language available", flush=True)

        # 4. If no relevant context in either language — generate helpful general answer
        if not relevant_chunks:
            if settings.ALLOW_GENERAL_FALLBACK:
                print(f"[Chat] Step 4: No relevant chunks — generating general helpful answer in '{lang_name}'", flush=True)
                from app.core.prompts import GENERAL_FALLBACK_PROMPT
                general_prompt = GENERAL_FALLBACK_PROMPT.format(
                    language=lang_name, question=request.message
                )
                fallback_answer = await self.llm_client.generate(general_prompt, language=lang_name)
                fallback_answer = fallback_answer.strip().strip('"').strip()
                # Validate language
                if not is_language_clean(fallback_answer, language):
                    fallback_answer = await self.llm_client.cleanup_language(fallback_answer, lang_name)
                await self.session_service.save_turn(request.session_id, {"user": request.message, "bot": fallback_answer})
                return ChatResponse(
                    answer=fallback_answer,
                    language=language,
                    sources=[],
                    fallback_used=True,
                    retrieval_language=retrieval_language
                )
            else:
                print(f"[Chat] Step 4: No relevant chunks — returning static fallback message", flush=True)
                fallback_message = self.language_service.get_fallback_message(language)
                await self.session_service.save_turn(request.session_id, {"user": request.message, "bot": fallback_message})
                return ChatResponse(
                    answer=fallback_message,
                    language=language,
                    sources=[],
                    fallback_used=True,
                    retrieval_language=retrieval_language
                )

        sources = [{"text": doc[:200]} for doc in relevant_chunks]

        # 5. Build prompt
        prompt = self.prompt_service.build_prompt(request.message, [relevant_chunks], language)

        # 6. Generate answer — always in user's language
        print(f"[Chat] Step 6: Generating answer in '{lang_name}' (retrieval was '{retrieval_language}')", flush=True)
        answer = await self.llm_client.generate(prompt, language=lang_name)

        # 7. Validate language
        if not is_language_clean(answer, language):
            print(f"[Chat] Step 7: Language validation FAILED for '{language}' — rewriting...", flush=True)
            answer = await self.llm_client.cleanup_language(answer, lang_name)

        # 8. Save session turn
        await self.session_service.save_turn(request.session_id, {"user": request.message, "bot": answer})

        print(f"[Chat] DONE — fallback_used={fallback_used}, retrieval_language={retrieval_language}", flush=True)
        return ChatResponse(
            answer=answer,
            language=language,
            sources=sources,
            fallback_used=fallback_used,
            retrieval_language=retrieval_language
        )

    async def handle_escalation(self, request):
        # Placeholder for escalation logic
        return {"escalated": True, "detail": "Escalation triggered."}
