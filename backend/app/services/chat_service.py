STATIC_RESPONSES = {
    'en': {
        'bot_name': "My name is {bot_name}.",
        'nice_to_meet_you': "Nice to meet you!",
        'you_are_welcome': "You're welcome! Let me know if you need anything else.",
        'fallback': "I couldn’t find a relevant answer to your question.",
        'no_name': "I don’t have your name yet.",
        'your_name_is': "Your name is {name}.",
        'language_chosen': "You chose {language}.",
        'no_language': "I don’t know your chosen language yet.",
        'support_escalation': "Your query can be sent to our support team. Please provide your email so a team member can contact you.",
        # Feedback-related
        'feedback_thank_you': "Thank you for your feedback!",
        'feedback_prompt': "Please rate your experience.",
        'submit': "Submit",
        'cancel': "Cancel",
    },
    'es': {
        'bot_name': "Me llamo {bot_name}.",
        'nice_to_meet_you': "¡Mucho gusto!",
        'you_are_welcome': "De nada. Avísame si necesitas algo más.",
        'fallback': "No pude encontrar una respuesta relevante a tu pregunta.",
        'no_name': "No tengo tu nombre todavía.",
        'your_name_is': "Tu nombre es {name}.",
        'language_chosen': "Elegiste {language}.",
        'no_language': "Todavía no sé qué idioma elegiste.",
        'support_escalation': "Tu consulta puede ser enviada a nuestro equipo de soporte. Por favor, proporciona tu correo electrónico para que un miembro del equipo pueda contactarte.",
        # Feedback-related
        'feedback_thank_you': "¡Gracias por tus comentarios!",
        'feedback_prompt': "Por favor califica tu experiencia.",
        'submit': "Enviar",
        'cancel': "Cancelar",
    }
}
from app.services.language_service import LanguageService
from app.services.retrieval_service import RetrievalService
from app.services.prompt_service import PromptService
from app.clients.llm_client import LLMClient
from app.services.session_service import SessionService
from app.services.message_service import MessageService
from app.core.config import settings
from app.models.chat import ChatRequest, ChatResponse
from app.utils.helpers import clean_context_chunk, is_meaningful_chunk, filter_relevant_chunks, is_language_clean, MIN_PRIMARY_CONFIDENCE
import uuid
import re


class ChatService:
    BOT_NAME = "Getmee Chatbot"

    SMALL_TALK_KEYWORDS = {
        # English
        "thanks": "You’re welcome! Let me know if you need anything else.",
        "thank you": "You’re welcome! Let me know if you need anything else.",
        "ok": "Alright. Let me know if you need help with anything else.",
        "okay": "Alright. Let me know if you need help with anything else.",
        "hello": "Hello! How can I help you today?",
        "hi": "Hello! How can I help you today?",
        "bye": "Goodbye! Feel free to come back anytime.",
        "goodbye": "Goodbye! Feel free to come back anytime.",
        "sure": "Alright! Let me know if you have more questions.",
        "got it": "Great! Let me know if you need anything else.",
        # Spanish
        "gracias": "¡De nada! Avísame si necesitas algo más.",
        "muchas gracias": "¡De nada! Avísame si necesitas algo más.",
        "vale": "De acuerdo. Avísame si necesitas ayuda con algo más.",
        "de acuerdo": "De acuerdo. Avísame si necesitas ayuda con algo más.",
        "hola": "¡Hola! ¿En qué puedo ayudarte hoy?",
        "buenas": "¡Hola! ¿En qué puedo ayudarte hoy?",
        "adiós": "¡Adiós! No dudes en volver cuando quieras.",
        "adios": "¡Adiós! No dudes en volver cuando quieras.",
        "hasta luego": "¡Hasta luego! No dudes en volver cuando quieras.",
        "seguro": "¡De acuerdo! Avísame si tienes más preguntas.",
        "entendido": "¡Genial! Avísame si necesitas algo más.",
    }

    def _detect_context_update(self, message: str) -> str:
        """
        Extracts the user's name from the message if present.
        Supports 'my name is ...', 'i am ...', and "i'm ..." patterns anywhere in the message.
        Returns the first matched name, or None if not found.
        """
        patterns = [
            r"\bmy name is\s+([A-Za-z'-]+)",
            r"\bi am\s+([A-Za-z'-]+)",
            r"\bi'm\s+([A-Za-z'-]+)"
        ]
        for pat in patterns:
            match = re.search(pat, message, re.IGNORECASE)
            if match:
                name = match.group(1)
                return name
        return None

    # Phrases that mean "yes, continue / do what you suggested"
    _CONFIRMATION_PATTERNS = [
        r"^(ok|okay|ok+)[\.!]*$",
        r"^(yes|yeah|yep|yup|ya)[\.!]*$",
        r"^sure[\.!]*$",
        r"^(go ahead|do it|proceed|continue)[\.!]*$",
        r"^i (want|want that|want to)[\.!]*$",
        r"^i'?d like( that)?[\.!]*$",
        r"^(please|pls)[\.!]*$",
        r"^(sounds good|great|perfect)[\.!]*$",
        r"^(do it|let'?s do it)[\.!]*$",
        r"^i (am |'m )?(interested|ready)[\.!]*$",
    ]

    def _detect_confirmation(self, message: str) -> bool:
        """Return True when the message is a short confirmation with no new topic."""
        msg = message.strip().lower()
        for pattern in self._CONFIRMATION_PATTERNS:
            if re.match(pattern, msg):
                return True
        return False

    def _detect_small_talk(self, message: str) -> str:
        msg = message.strip().lower()
        for k, v in self.SMALL_TALK_KEYWORDS.items():
            if msg == k:
                return v
        return None

    def _detect_low_intent(self, message: str) -> str:
        msg = message.strip().lower()
        # Regex patterns for flexible matching (English and Spanish)
        patterns = [
            # English
            r"^h+m+$",           # hm, hmm, hmmm, etc.
            r"^o+k+a*y*\.*$",   # ok, okay, ok..., okay...
            r"^t+h+a+n+k+s*\.*$", # thanks, thanksss, thanks...
            r"^t+h+a+n+k\s*y+\.*$", # thank you, thank you...
            r"^h+i+\.*$",        # hi, hii, hi...
            r"^h+e+l+l+o+\.*$",  # hello, helloo, hello...
            r"^b+y+e+\.*$",      # bye, byee, bye...
            r"^s+u+r+e+\.*$",    # sure, sureee, sure...
            r"^g+o+t+\s*i+t+\.*$", # got it, got it...
            # Spanish
            r"^m+$",              # mmm, mmmm, etc.
            r"^g+r+a+c+i+a+s*\.*$", # gracias, graciasss, gracias...
            r"^m+u+c+h+a+s*\s*g+r+a+c+i+a+s*\.*$", # muchas gracias...
            r"^h+o+l+a+\.*$",    # hola, holaa, hola...
            r"^b+u+e+n+a+s+\.*$", # buenas, buenasss, etc.
            r"^a+d+i+o+s+\.*$",  # adios, adiosss, adiós...
            r"^h+a+s+t+a+\s+l+u+e+g+o+\.*$", # hasta luego...
            r"^v+a+l+e+\.*$",    # vale, valeee, etc.
            r"^d+e+\s+a+c+u+e+r+d+o+\.*$", # de acuerdo...
            r"^s+e+g+u+r+o+\.*$", # seguro, segurooo, etc.
            r"^e+n+t+e+n+d+i+d+o+\.*$", # entendido, entendidooo, etc.
        ]
        responses = [
            # English
            "Let me know if you need help with anything.",
            "Alright. Let me know if you need help with anything else.",
            "You’re welcome! Let me know if you need anything else.",
            "You’re welcome! Let me know if you need anything else.",
            "Hello! How can I help you today?",
            "Hello! How can I help you today?",
            "Goodbye! Feel free to come back anytime.",
            "Alright! Let me know if you have more questions.",
            "Great! Let me know if you need anything else.",
            # Spanish
            "Avísame si necesitas ayuda con algo.",
            "¡De nada! Avísame si necesitas algo más.",
            "¡De nada! Avísame si necesitas algo más.",
            "¡Hola! ¿En qué puedo ayudarte hoy?",
            "¡Hola! ¿En qué puedo ayudarte hoy?",
            "¡Adiós! No dudes en volver cuando quieras.",
            "¡Hasta luego! No dudes en volver cuando quieras.",
            "De acuerdo. Avísame si necesitas ayuda con algo más.",
            "De acuerdo. Avísame si necesitas ayuda con algo más.",
            "¡De acuerdo! Avísame si tienes más preguntas.",
            "¡Genial! Avísame si necesitas algo más.",
        ]
        for pat, resp in zip(patterns, responses):
            if re.match(pat, msg):
                return resp
        return None

    def _detect_question_intent(self, message: str) -> bool:
        msg = message.strip().lower()
        # Custom: Answer bot name
        if any(
            phrase in msg
            for phrase in [
                "what is your name",
                "who are you",
                "your name",
                "cómo te llamas",
                "cual es tu nombre",
                "quién eres"
            ]
        ):
            # Always respond in the selected language (default English)
            lang = self.selected_language if hasattr(self, 'selected_language') and self.selected_language else 'en'
            if lang == 'es':
                return f"Me llamo {self.BOT_NAME}."
            return f"My name is {self.BOT_NAME}."

        if '?' in msg:
            return True
        question_starts = (
            'how', 'what', 'why', 'when', 'where', 'can', 'do', 'is', 'are', 'does', 'could', 'would', 'should', 'will', 'did', 'who', 'whom', 'whose', 'which', 'may', 'shall',
            'cómo', 'qué', 'por qué', 'cuándo', 'dónde', 'puede', 'hace', 'es', 'son', 'podría', 'haría', 'debería', 'será', 'hizo', 'quién', 'cuyo', 'cuál', 'puede', 'debe'
        )
        # Check if message starts with a question word (allow leading punctuation/whitespace)
        msg_start = msg.lstrip(' .,!')
        for q in question_starts:
            if msg_start.startswith(q + ' '):
                return True
        return False

    def _answer_from_session_context(self, message: str, recent_messages: list) -> str:
        msg = message.strip().lower()
        # Simple logic for demo: look for name or last user message
        if "what is my name" in msg:
            # Look for a message like "my name is ..."
            for m in reversed(recent_messages):
                if m.get("role") == "user" and "my name is" in m.get("text", "").lower():
                    # Extract name
                    parts = m["text"].split("my name is", 1)
                    if len(parts) > 1:
                        name = parts[1].strip().split()[0]
                        return f"Your name is {name}."
            return "I don’t know your name yet."
        if "what did i just say" in msg:
            # Return last user message (excluding current)
            user_msgs = [m["text"] for m in recent_messages if m.get("role") == "user"]
            if len(user_msgs) > 1:
                return f"You just said: '{user_msgs[-2]}'."
            return "I don’t have your previous message."
        if "what language did i choose" in msg or "what is my language" in msg:
            for m in reversed(recent_messages):
                if m.get("role") == "user" and m.get("language"):
                    return f"You chose {m['language']}."
            return "I don’t know your chosen language yet."
        return None

    async def _get_session_context_answer(self, msg: str, session_key: str, language: str, session_uuid: str, message: str, target_language: str = None):
        # Try to get user_name from Redis context
        if "what is my name" in msg:
            ctx = await self.message_service.redis_session.get_context(session_key)
            user_name = ctx.get("user_name") if ctx else None
            lang = target_language or language or 'en'
            if user_name:
                answer = STATIC_RESPONSES[lang]['your_name_is'].format(name=user_name)
            else:
                answer = STATIC_RESPONSES[lang]['no_name']
            return ChatResponse(
                answer=answer,
                language=lang,
                sources=[],
                fallback_used=False,
                retrieval_language=lang,
                message_id=None,
                session_uuid=str(session_uuid),
                show_feedback=False,
            )
        # ...existing code...
        return None

    def __init__(self):
        self.language_service = LanguageService()
        self.retrieval_service = RetrievalService()
        self.prompt_service = PromptService()
        self.llm_client = LLMClient(settings.LLM_PROVIDER, settings.LLM_API_KEY)
        self.session_service = SessionService()
        self.message_service = MessageService()

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
        # Always set the selected language for this request
        self.selected_language = request.language or 'en'
        print(f"[Chat] Incoming request.language: {request.language}", flush=True)

        # 0. Ensure session exists in PG + Redis
        session_key = request.session_id  # frontend sends this as session_key
        session = await self.session_service.get_or_create_session(session_key, request.language)
        session_uuid = session["id"]  # PG UUID

        # 1. Question intent detection (takes priority)
        # Multi-intent/context: always update context if 'my name is ...' is present
        name_update = self._detect_context_update(request.message)
        if name_update:
            await self.message_service.redis_session.update_context(session_key, user_name=name_update)
        # Check for both bot name and user name questions in the same message
        msg_lower = request.message.strip().lower()
        lang = request.language or 'en'
        responses = []
        # Bot name intent
        bot_name_intent = any(
            phrase in msg_lower
            for phrase in [
                "what is your name",
                "who are you",
                "your name",
                "cómo te llamas",
                "cual es tu nombre",
                "quién eres"
            ]
        )
        if bot_name_intent:
            responses.append(STATIC_RESPONSES[lang]['bot_name'].format(bot_name=self.BOT_NAME))
        # User name intent
        user_name_intent = "what is my name" in msg_lower
        if user_name_intent:
            ctx = await self.message_service.redis_session.get_context(session_key)
            user_name = ctx.get("user_name") if ctx else None
            if user_name:
                responses.append(STATIC_RESPONSES[lang]['your_name_is'].format(name=user_name))
            else:
                responses.append(STATIC_RESPONSES[lang]['no_name'])
        if responses:
            await self.message_service.save_user_message(
                session_id=session_uuid, session_key=session_key,
                text=request.message, language=lang,
            )
            print(f"[Chat] Final answer language: {lang}", flush=True)
            return ChatResponse(
                answer="\n".join(responses),
                language=lang,
                sources=[],
                fallback_used=False,
                retrieval_language=lang,
                message_id=None,
                session_uuid=str(session_uuid),
                show_feedback=False,
            )
        # Fallback to original logic for other cases
        q_intent = self._detect_question_intent(request.message)
        if isinstance(q_intent, str):
            await self.message_service.save_user_message(
                session_id=session_uuid, session_key=session_key,
                text=request.message, language=lang,
            )
            print(f"[Chat] Final answer language: {lang}", flush=True)
            return ChatResponse(
                answer=q_intent,
                language=lang,
                sources=[],
                fallback_used=False,
                retrieval_language=lang,
                message_id=None,
                session_uuid=str(session_uuid),
                show_feedback=False,
            )
        elif q_intent:
            # 1a. Context update detection (no RAG, no fallback)
            name_update = self._detect_context_update(request.message)
            if name_update:
                language = request.language or self.language_service.detect_language(request.message)
                # Store name in Redis context (as user_name)
                await self.message_service.redis_session.update_context(session_key, user_name=name_update)
                await self.message_service.save_user_message(
                    session_id=session_uuid, session_key=session_key,
                    text=request.message, language=language,
                )
                lang = request.language or 'en'
                print(f"[Chat] Final answer language: {lang}", flush=True)
                return ChatResponse(
                    answer=STATIC_RESPONSES[lang]['nice_to_meet_you'],
                    language=lang,
                    sources=[],
                    fallback_used=False,
                    retrieval_language=lang,
                    message_id=None,
                    session_uuid=str(session_uuid),
                    show_feedback=False,
                )
            # 1b. Session context question (from Redis)
            recent_messages = []
            try:
                recent_messages = await self.message_service.redis_session.get_messages(session_key)
            except Exception:
                pass
            msg = request.message.strip().lower()
            language = request.language or self.language_service.detect_language(request.message)
            session_context_answer = await self._get_session_context_answer(msg, session_key, language, session_uuid, request.message, target_language=request.language)
            if session_context_answer:
                await self.message_service.save_user_message(
                    session_id=session_uuid, session_key=session_key,
                    text=request.message, language=language,
                )
                print(f"[Chat] Final answer language: {language}", flush=True)
                return session_context_answer
        else:
            # 2. Small-talk/low-intent detection (only if not a question)
            small_talk_resp = self._detect_small_talk(request.message) or self._detect_low_intent(request.message)
            if small_talk_resp:
                # Always translate small talk/greeting to the dropdown-selected language (even if already in that language)
                answer = small_talk_resp
                try:
                    answer = await self.llm_client.translate(answer, target_language=request.language)
                except Exception as e:
                    print(f"[Chat] Small talk translation error: {e}", flush=True)
                await self.message_service.save_user_message(
                    session_id=session_uuid, session_key=session_key,
                    text=request.message, language=request.language,
                )
                print(f"[Chat] Final answer language: {request.language}", flush=True)
                return ChatResponse(
                    answer=answer,
                    language=request.language,
                    sources=[],
                    fallback_used=False,
                    retrieval_language=request.language,
                    message_id=None,
                    session_uuid=str(session_uuid),
                    show_feedback=False,
                )

        # 3. Context update detection (no RAG, no fallback)
        name_update = self._detect_context_update(request.message)
        if name_update:
            language = request.language or self.language_service.detect_language(request.message)
            answer = STATIC_RESPONSES[language]['nice_to_meet_you']
            # Store name in Redis context (as user_name)
            await self.message_service.redis_session.update_context(session_key, user_name=name_update)
            await self.message_service.save_user_message(
                session_id=session_uuid, session_key=session_key,
                text=request.message, language=language,
            )
            print(f"[Chat] Final answer language: {language}", flush=True)
            return ChatResponse(
                answer=answer,
                language=language,
                sources=[],
                fallback_used=False,
                retrieval_language=language,
                message_id=None,
                session_uuid=str(session_uuid),
                show_feedback=False,
            )

        # 4. Proceed as before: Save user message to PG + Redis, then RAG

        # 5. Proceed as before: Save user message to PG + Redis
        language = request.language or self.language_service.detect_language(request.message)
        lang_name = self.language_service.get_language_name(language)
        retrieval_language = language
        fallback_used = False

        print(f"[Chat] User language: {language} ({lang_name}) | Query: '{request.message[:80]}'", flush=True)

        user_msg = await self.message_service.save_user_message(
            session_id=session_uuid, session_key=session_key,
            text=request.message, language=language,
        )

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

        # 4. If no relevant context in either language — strict fallback (NO LLM generation)
        if not relevant_chunks:
            print(f"[Chat] Step 4: No relevant chunks — returning strict fallback message (LLM skipped)", flush=True)
            fallback_message = self.language_service.get_fallback_message(request.language)
            # If fallback_message is not in the selected language, translate it
            if request.language != language:
                try:
                    fallback_message = await self.llm_client.translate(fallback_message, target_language=request.language)
                except Exception as e:
                    print(f"[Chat] Fallback translation error: {e}", flush=True)

            # Save bot fallback message to PG + Redis (sets feedback_state)
            bot_msg = await self.message_service.save_bot_message(
                session_id=session_uuid, session_key=session_key,
                text=fallback_message, language=request.language,
                fallback_used=True, source_type="fallback",
            )
            # Legacy turn save
            await self.session_service.save_turn(request.session_id, {"user": request.message, "bot": fallback_message})

            return ChatResponse(
                answer=fallback_message,
                language=request.language,
                sources=[],
                fallback_used=True,
                requires_email=True,
                retrieval_language=retrieval_language,
                message_id=str(bot_msg["id"]),
                session_uuid=str(session_uuid),
                show_feedback=True,
            )

        sources = [{"text": doc[:200]} for doc in relevant_chunks]

        # 5. Build prompt
        prompt = self.prompt_service.build_prompt(request.message, [relevant_chunks], request.language)

        # 6. Generate answer — always in dropdown-selected language
        print(f"[Chat] Step 6: Generating answer in '{request.language}' (retrieval was '{retrieval_language}')", flush=True)
        answer = await self.llm_client.generate(prompt, language=request.language)

        # 7. Validate language
        if not is_language_clean(answer, request.language):
            print(f"[Chat] Step 7: Language validation FAILED for '{request.language}' — rewriting...", flush=True)
            answer = await self.llm_client.cleanup_language(answer, request.language)

        # 8. Save bot message to PG + Redis (sets feedback_state)
        bot_msg = await self.message_service.save_bot_message(
            session_id=session_uuid, session_key=session_key,
            text=answer, language=request.language,
            fallback_used=fallback_used, source_type="kb",
        )
        # Legacy turn save
        await self.session_service.save_turn(request.session_id, {"user": request.message, "bot": answer})

        # Store this query as last_topic so follow-up confirmations can re-use it.
        if not fallback_used:
            try:
                await self.message_service.redis_session.update_context(session_key, last_topic=request.message)
            except Exception:
                pass

        print(f"[Chat] DONE — fallback_used={fallback_used}, retrieval_language={retrieval_language}", flush=True)
        return ChatResponse(
            answer=answer,
            language=request.language,
            sources=sources,
            fallback_used=fallback_used,
            retrieval_language=retrieval_language,
            message_id=str(bot_msg["id"]),
            session_uuid=str(session_uuid),
            show_feedback=True,
        )

    async def handle_escalation(self, request):
        # Placeholder for escalation logic
        return {"escalated": True, "detail": "Escalation triggered."}
