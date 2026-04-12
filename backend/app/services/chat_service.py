STATIC_RESPONSES = {
    'en': {
        'bot_name': "My name is {bot_name}.",
        'bot_intro': "I'm {bot_name}, your AI support assistant. I can guide you with your questions and platform-related help. How can I assist you today?",
        'email_multiple_found': "I found multiple email addresses: {emails}. Please reply with the one you want me to save (you can send the email or its number).",
        'email_pick_invalid': "I still need one email from this list: {emails}. Please reply with the email or its number.",
        'email_saved': "Thanks! I have successfully saved your email address: {email}. Our team can use this to contact you.",
        'email_invalid': "That email format looks invalid. Please share a valid email address.",
        'email_save_failed': "I found your email, but I could not save it right now. Please try again.",
        'nice_to_meet_you': "Nice to meet you!",
        'nice_to_meet_you_named': "Nice to meet you, {name}! How can I help you today?",
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
        'bot_intro': "Soy {bot_name}, tu asistente de soporte con IA. Puedo guiarte con tus preguntas y ayudarte con la plataforma. ¿Cómo puedo ayudarte hoy?",
        'email_multiple_found': "Encontre varios correos: {emails}. Responde con el que quieres que guarde (puedes enviar el correo o su numero).",
        'email_pick_invalid': "Aun necesito un correo de esta lista: {emails}. Responde con el correo o su numero.",
        'email_saved': "Gracias! He guardado correctamente tu correo: {email}. Nuestro equipo puede usarlo para contactarte.",
        'email_invalid': "El formato del correo no parece valido. Comparte un correo electronico valido.",
        'email_save_failed': "Encontre tu correo, pero no pude guardarlo ahora. Intentalo de nuevo.",
        'nice_to_meet_you': "¡Mucho gusto!",
        'nice_to_meet_you_named': "Mucho gusto, {name}. En que puedo ayudarte hoy?",
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
from app.services.support_service import SupportService
from app.services.support_ticket_service import SupportTicketService
from app.clients.postgres_client import PostgresClient
from app.core.config import settings
from app.models.chat import ChatRequest, ChatResponse
from app.utils.helpers import clean_context_chunk, is_meaningful_chunk, filter_relevant_chunks, is_language_clean, MIN_PRIMARY_CONFIDENCE, normalize_query
import re
import uuid




class ChatService:
    @staticmethod
    def extract_topic_terms(text: str) -> list:
        stopwords = {
            "how", "what", "who", "when", "where", "why",
            "is", "are", "do", "does", "did", "can", "could", "would", "should",
            "the", "a", "an", "my", "your", "our", "their",
            "question", "answer", "response", "help", "support", "information"
        }
        terms = []
        for word in re.findall(r"\b[\w\-']+\b", text.lower()):
            if word not in stopwords and len(word) > 2:
                terms.append(word)
        return terms

    @staticmethod
    def chunk_matches_query_topic(query: str, chunk: str) -> bool:
        topic_terms = ChatService.extract_topic_terms(query)
        if not topic_terms:
            return True  # No meaningful topic terms to check — accept
        # Normalize both query terms and chunk text for fair comparison
        from app.utils.helpers import normalize_query
        chunk_normalized = normalize_query(chunk)
        # Also normalize topic terms (strip hyphens so "white-label" matches "white label")
        normalized_terms = [t.replace("-", " ") for t in topic_terms]
        # Extract question portion for matching (more specific, avoids false positives from answer text)
        q_match = re.search(r"question:\s*(.*?)(answer:|$)", chunk_normalized, re.IGNORECASE | re.DOTALL)
        match_text = q_match.group(1).strip() if q_match else chunk_normalized
        # Also normalize hyphens in match text
        match_text_nohyphen = match_text.replace("-", " ")
        matches = [t for t in normalized_terms if t in match_text_nohyphen]
        print(f"[DEBUG] topic_filter: terms={normalized_terms}, matches={matches}, match_text='{match_text_nohyphen[:100]}'", flush=True)
        if len(normalized_terms) <= 3:
            return len(matches) >= 1
        return len(matches) >= 2
    # Language-agnostic intent patterns
    INTENT_PATTERNS = {
        "greeting": [
            # English
            "hi", "hello", "hey", "hey there", "hello there", "hi there", "yo",
            # Spanish
            "hola", "hola 👋", "hola!", "qué tal", "qué tal?", "buenas"
        ],
        "buenos_dias": ["good morning", "buenos días"],
        "buenas_tardes": ["good afternoon", "buenas tardes"],
        "buenas_noches": ["good evening", "buenas noches"],
        "thanks": [
            # English
            "thanks", "thank you", "thx", "thanks a lot", "thank u", "tysm", "appreciate it",
            # Spanish
            "gracias", "gracias!", "muchas gracias", "mil gracias", "te lo agradezco"
        ],
        "acknowledgement": [
            # English
            "ok", "okay", "got it", "sure", "alright", "cool", "nice", "okay thanks", "gotcha", "makes sense",
            # Spanish
            "vale", "de acuerdo", "entendido", "seguro", "perfecto", "está bien", "esta bien", "claro", "genial"
        ],
        "goodbye": [
            # English
            "bye", "goodbye", "see you", "see ya", "later", "take care",
            # Spanish
            "adios", "adiós", "hasta luego", "hasta pronto", "nos vemos", "chao"
        ],
        "low_intent": [
            # English
            "hm", "hmm", "hmmm", "mm", "mmm", "um", "uhh", "ah", "oh", "yeah", "yup", "nope", "nah",
            # Spanish
            "mmm", "eh", "ah", "oh", "sí", "si", "no", "nop"
        ],
        "help_request": [
            # English variations
            "help", "help me", "i need help", "can you help", "can you help me",
            "support me", "i need support", "can you support me",
            "assist me", "i need assistance", "can you assist me",
            "can you help with", "need help", "need assistance",
            "help please", "assist please", "please help",
            "help!", "i'm stuck", "i'm confused",
            "what should i do", "what do i do",
            # Spanish variations
            "ayuda", "ayudame", "necesito ayuda", "puedes ayudarme",
            "puedes ayudar", "dame ayuda",
            "soporte", "necesito soporte", "puedo pedir soporte",
            "asistencia", "necesito asistencia", "asisteme",
            "ayuda por favor", "asiste por favor",
            "ayuda!", "estoy atascado", "estoy confundido",
            "qué debo hacer", "qué hago"
        ]
    }

    INTENT_RESPONSES = {
        "en": {
            "greeting": "Hello! How can I help you today?",
            "buenos_dias": "Good morning! How can I help you today?",
            "buenas_tardes": "Good afternoon! How can I help you today?",
            "buenas_noches": "Good evening! How can I help you today?",
            "thanks": "You’re welcome! Let me know if you need anything else.",
            "acknowledgement": "Alright. Let me know if you need help with anything else.",
            "goodbye": "Goodbye! Feel free to come back anytime.",
            "low_intent": "Let me know if you need help with anything.",
            "help_request": "Sure, I'm here to help! What do you need assistance with?"
        },
        "es": {
            "greeting": "¡Hola! ¿En qué puedo ayudarte hoy?",
            "buenos_dias": "¡Buenos días! ¿En qué puedo ayudarte hoy?",
            "buenas_tardes": "¡Buenas tardes! ¿En qué puedo ayudarte hoy?",
            "buenas_noches": "¡Buenas noches! ¿En qué puedo ayudarte hoy?",
            "thanks": "¡De nada! Avísame si necesitas algo más.",
            "acknowledgement": "De acuerdo. Avísame si necesitas ayuda con algo más.",
            "goodbye": "¡Adiós! No dudes en volver cuando quieras.",
            "low_intent": "Avísame si necesitas ayuda con algo.",
            "help_request": "¡Claro! Estoy aquí para ayudarte. ¿Con qué necesitas ayuda?"
        }
    }

    def _detect_intent(self, message: str) -> str | None:
        msg = message.strip().lower()
        for intent, phrases in self.INTENT_PATTERNS.items():
            if msg in phrases:
                return intent
        return None

    def _detect_low_intent_pattern(self, message: str) -> str | None:
        msg = message.strip().lower()
        patterns = {
            "low_intent": [
                r"^h+m+$",   # hm, hmm, hmmm
                r"^m+$",     # m, mm, mmm
            ]
        }
        for intent, regexes in patterns.items():
            for pat in regexes:
                if re.match(pat, msg):
                    return intent
        return None

    FEEDBACK_INTERVAL = 3  # Configurable interval for per-message feedback
    OVERALL_RATING_INTERVAL = 3  # Configurable interval for overall session rating popup

    def _contains_support_keywords(self, answer: str) -> bool:
        keywords = [
            "contact support",
            "support team",
            "support staff",
            "staff assistant",
            "further support",
            "further assistance",
            "help desk",
            "reach out to our support",
            "contact our support",
            "contact our staff",
            "contact assistance",
            "support for further assistance",
        ]
        answer_lower = answer.lower()
        return any(kw in answer_lower for kw in keywords)
    def _get_unsatisfied_support_prompt(self, language: str) -> str:
        messages = {
            "en": "Please provide your email address so our support team can contact you.",
            "es": "Por favor, proporciona tu correo electrónico para que nuestro equipo de soporte pueda contactarte."
        }
        return messages.get(language, messages["en"])
    async def _prepare_new_support_submission(self, session_key: str):
        """
        Reset the per-submission guard so the next actual submission increments support_request_count.
        Call this before opening a new support submission popup.
        """
        context = await self.message_service.redis_session.get_context(session_key)
        context = context or {}
        context["_support_counted_this_submission"] = False
        await self.message_service.redis_session.set_context(session_key, context)
    def _is_support_limit_reached(self, support_context: dict) -> bool:
        return support_context.get("support_request_count", 0) >= 2

    def _get_unsatisfied_limit_message(self, language: str) -> str:
        messages = {
            "en": "You’ve already contacted our support team. Please be patient — a team member will assist you soon.",
            "es": "Ya has contactado a nuestro equipo de soporte. Por favor, ten paciencia — un miembro del equipo te ayudará pronto."
        }
        return messages.get(language, messages["en"])

    def _get_direct_support_limit_message(self, language: str) -> str:
        messages = {
            "en": "You have reached the maximum number of support requests. Please be patient — a team member will contact you soon.",
            "es": "Has alcanzado el número máximo de solicitudes de soporte. Por favor, ten paciencia — un miembro del equipo se pondrá en contacto contigo pronto."
        }
        return messages.get(language, messages["en"])

    def _detect_reescalation_intent(self, message: str) -> bool:
        msg = message.strip().lower()
        phrases = [
            # English
            "i need staff support",
            "i need to contact human",
            "i need human support",
            "i still need help",
            "still need help",
            "contact support again",
            "my issue is not solved",
            "no one contacted me",
            "escalate again",
            "open another ticket",
            # Spanish
            "necesito ayuda del personal",
            "necesito contactar a un humano",
            "necesito soporte humano",
            "todavía necesito ayuda",
            "contactar soporte otra vez",
            "mi problema no está resuelto",
            "nadie me contactó",
        ]
        return any(p in msg for p in phrases)

    def _get_recontact_confirmation_message(self, language: str) -> str:
        messages = {
            "en": "Your enquiry has already been submitted for this session. Do you want to contact human support again?",
            "es": "Tu consulta ya ha sido enviada para esta sesión. ¿Quieres contactar soporte humano de nuevo?"
        }
        return messages.get(language, messages["en"])

    async def _get_support_context(self, session_key: str) -> dict:
        """
        Get support-related state from Redis context.
        """
        context = await self.message_service.redis_session.get_context(session_key)
        context = context or {}
        return {
            "support_request_sent": context.get("support_request_sent", False),
            "support_email": context.get("support_email"),
            "support_ticket_id": context.get("support_ticket_id"),
            "support_status": context.get("support_status"),
            "support_request_count": context.get("support_request_count", 0),
            "recontact_confirmation_shown": context.get("recontact_confirmation_shown", False),
        }

    async def _mark_support_submitted(
        self,
        session_key: str,
        email: str,
        ticket_id: str = None,
        status: str = "open"
    ) -> None:
        """
        Mark support escalation as submitted in Redis context.
        Only increment support_request_count after actual submission (not on confirmation).
        """
        context = await self.message_service.redis_session.get_context(session_key)
        context = context or {}
        context["support_request_sent"] = True
        context["support_email"] = email
        context["support_ticket_id"] = ticket_id or str(uuid.uuid4())
        context["support_status"] = status
        # Only increment if not already incremented for this submission
        if not context.get("_support_counted_this_submission", False):
            context["support_request_count"] = context.get("support_request_count", 0) + 1
            context["_support_counted_this_submission"] = True
        await self.message_service.redis_session.set_context(session_key, context)

    async def _clear_support_state(self, session_key: str) -> None:
        """
        Optional helper if you want to reset support state later.
        """
        context = await self.message_service.redis_session.get_context(session_key)
        context = context or {}
        context["support_request_sent"] = False
        context["support_email"] = None
        context["support_ticket_id"] = None
        context["support_status"] = None
        await self.message_service.redis_session.set_context(session_key, context)

    def _get_repeat_escalation_message(self, language: str) -> str:
        messages = {
            "en": "Your enquiry has already been submitted. A team member will contact you soon.",
            "es": "Tu consulta ya ha sido enviada. Un miembro del equipo se pondrá en contacto contigo pronto."
        }
        return messages.get(language, messages["en"])

    def _get_email_received_message(self, language: str) -> str:
        messages = {
            "en": "Thanks! I’ve received your email. Please describe your issue below so our support team can assist you.",
            "es": "¡Gracias! Hemos recibido tu correo electrónico. Por favor describe tu problema a continuación para que nuestro equipo de soporte pueda ayudarte."
        }
        return messages.get(language, messages["en"])

    def _get_first_support_prompt(self, language: str) -> str:
        messages = {
            "en": (
                "I couldn’t find a relevant answer to your question. "
                "Your enquiry can be forwarded to our support team. "
                "Please provide your email address so a team member can contact you."
            ),
            "es": (
                "No pude encontrar una respuesta relevante a tu pregunta. "
                "Tu consulta puede ser enviada a nuestro equipo de soporte. "
                "Por favor, proporciona tu correo electrónico para que un miembro del equipo pueda contactarte."
            ),
        }
        return messages.get(language, messages["en"])
    async def _handle_follow_up_message(self, message: str, session_key: str, language: str) -> str:
        """
        Detect and answer follow-up memory questions about recent conversation history.
        Reads from Redis message history (session:{session_key}:messages).
        Returns a direct answer string if matched, else None.
        """
        # Normalize message
        msg = message.strip().lower()
        # English and Spanish patterns
        user_last_patterns = [
            # English
            "what did i just say", "what did i say", "repeat my last message", "repeat my last user message",
            # Spanish
            "qué acabo de decir", "qué dije", "repite mi último mensaje", "repite mi último mensaje de usuario"
        ]
        user_prev_patterns = [
            # English
            "what did i say before that", "what did i say earlier", "what did i say before",
            # Spanish
            "qué dije antes", "qué dije antes de eso", "qué dije anteriormente"
        ]
        bot_last_patterns = [
            # English
            "what did you just say", "repeat your last message", "what was your last reply", "repeat your last response",
            # Spanish
            "qué acabas de decir", "repite tu último mensaje", "cuál fue tu última respuesta", "repite tu última respuesta"
        ]
        # Fuzzy match: allow for small variations (e.g., ignore punctuation, allow extra words)
        def match_any(phrases):
            for p in phrases:
                if p in msg:
                    return True
            return False
        # Get recent messages from Redis
        recent_messages = await self.message_service.redis_session.get_messages(session_key)
        if not recent_messages:
            recent_messages = []
        # Helper: get last/previous user/bot message (excluding current)
        def get_last_message(role, skip=0):
            count = 0
            for m in reversed(recent_messages):
                if m.get("role") == role:
                    if count == skip:
                        return m.get("text")
                    count += 1
            return None
        # A. Last user message (excluding current)
        if match_any(user_last_patterns):
            # The most recent user message before the current one
            # Assume the current message is not yet in history, so skip=0 is last user message
            last_user = get_last_message("user", skip=0)
            if last_user:
                if language == "es":
                    return f"Acabas de decir: '{last_user}'."
                return f"You just said: '{last_user}'."
            else:
                if language == "es":
                    return "No tengo tu mensaje anterior."
                return "I don’t have your previous message."
        # B. Previous user message before that
        if match_any(user_prev_patterns):
            # The user message before the last one (skip=1)
            prev_user = get_last_message("user", skip=1)
            if prev_user:
                if language == "es":
                    return f"Antes de eso, dijiste: '{prev_user}'."
                return f"Before that, you said: '{prev_user}'."
            else:
                if language == "es":
                    return "No tengo tu mensaje anterior."
                return "I don’t have your previous message."
        # C. Last bot message
        if match_any(bot_last_patterns):
            last_bot = get_last_message("bot", skip=0)
            if last_bot:
                if language == "es":
                    return f"Dije: '{last_bot}'."
                return f"I said: '{last_bot}'."
            else:
                if language == "es":
                    return "No tengo mi respuesta anterior."
                return "I don’t have my previous response."
        return None
    async def get_support_submission_state(self, session_key: str):
        """Return support submission state from Redis for the current session."""
        support_state = await self.message_service.redis_session.get_support_state(session_key)
        context = await self.message_service.redis_session.get_context(session_key)
        return {
            "support_request_sent": (context or {}).get("support_request_sent", False),
            "support_email": (context or {}).get("support_email"),
            "support_state": support_state,
        }
    BOT_NAME = "Getmee Chatbot"

    # SMALL_TALK_KEYWORDS removed; replaced by INTENT_PATTERNS/INTENT_RESPONSES

    def _detect_context_update(self, message: str) -> str:
        """
        Extracts the user's name from the message if present.
        Supports 'my name is ...', 'i am ...', and "i'm ..." patterns anywhere in the message.
        Returns the first matched name (multi-word, up to punctuation or end), or None if not found.
        """
        # Allow Unicode letters, apostrophes, hyphens, spaces; stop at punctuation or line end
        patterns = [
            r"\bmy name is\s+([\w'\- ]{1,100})",
            r"\bi am\s+([\w'\- ]{1,100})",
            r"\bi'm\s+([\w'\- ]{1,100})"
        ]
        from app.utils.helpers import NAME_DETECTION_STOPWORDS
        stopwords = NAME_DETECTION_STOPWORDS
        for pat in patterns:
            match = re.search(pat, message, re.IGNORECASE | re.UNICODE)
            if match:
                name = match.group(1).strip()
                name = re.split(r'[.,!?;:\n\r]', name)[0].strip()
                # Split into words, ignore if more than 2 words or contains stopwords
                words = [w for w in name.split() if w]
                if 0 < len(words) <= 2 and not any(w.lower() in stopwords for w in words):
                    return name
        return None

    # _detect_small_talk removed; replaced by _detect_intent

    # _detect_low_intent now handled by _detect_low_intent_pattern

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
                return STATIC_RESPONSES[lang].get('bot_intro', STATIC_RESPONSES[lang]['bot_name']).format(bot_name=self.BOT_NAME)
            return STATIC_RESPONSES[lang].get('bot_intro', STATIC_RESPONSES[lang]['bot_name']).format(bot_name=self.BOT_NAME)

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

    def _looks_like_missing_info_answer(self, text: str) -> bool:
        if not text:
            return False
        t = text.strip().lower()
        patterns = [
            r"couldn['\u2019]?t find",
            r"could not find",
            r"no relevant (answer|information)",
            r"i (don['\u2019]?t|do not) have (enough )?information",
            r"unable to find",
        ]
        return any(re.search(p, t) for p in patterns)

    def _extract_emails_from_message(self, message: str) -> list:
        if not message:
            return []
        matches = re.findall(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b", message)
        unique = []
        seen = set()
        for email in matches:
            lowered = email.lower()
            if lowered not in seen:
                seen.add(lowered)
                unique.append(email)
        return unique

    def _is_valid_email(self, email: str) -> bool:
        if not email:
            return False
        if len(email) > 254:
            return False
        return re.fullmatch(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", email) is not None

    def _looks_like_email_attempt(self, message: str) -> bool:
        if not message:
            return False
        lowered = message.lower()
        return "@" in message or "email" in lowered or "mail" in lowered

    def _format_email_candidates(self, emails: list) -> str:
        return ", ".join(f"{idx + 1}. {value}" for idx, value in enumerate(emails))

    def _resolve_selected_email(self, message: str, candidates: list) -> str:
        if not message:
            return None
        text = message.strip()
        if text.isdigit():
            idx = int(text)
            if 1 <= idx <= len(candidates):
                return candidates[idx - 1]

        emails_in_msg = self._extract_emails_from_message(text)
        if emails_in_msg:
            selected = emails_in_msg[0]
            candidate_map = {c.lower(): c for c in candidates}
            return candidate_map.get(selected.lower())

        normalized = text.lower().strip(" .,!?")
        for candidate in candidates:
            if normalized == candidate.lower():
                return candidate
        return None

    async def _store_user_email(self, session_key: str, session_uuid: str, email: str) -> bool:
        try:
            await self.db.update_session_email(session_uuid, email)
            await self.message_service.redis_session.update_context(session_key, user_email=email)

            ctx = await self.message_service.redis_session.get_context(session_key)
            db_session = await self.db.get_or_create_session(session_key)
            return (ctx or {}).get("user_email") == email and (db_session or {}).get("user_email") == email
        except Exception as e:
            print(f"[Chat] Email store error: {e}", flush=True)
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
            print(f"[DEBUG] Redis context for session_key={session_key}: {ctx}")
            user_name = ctx.get("user_name") if ctx else None
            lang = target_language or language or 'en'
       
            # Fallback to 'en' if lang not in STATIC_RESPONSES
            if lang not in STATIC_RESPONSES:              
                lang = 'en'
            if user_name:              
                answer = STATIC_RESPONSES[lang].get('your_name_is', "Your name is {name}.").format(name=user_name)
            else:             
                answer = STATIC_RESPONSES[lang].get('no_name', "I don’t have your name yet.")
            #print(f"[DEBUG] what is my name? user_name={user_name}, lang={lang}, answer={answer}")
            return ChatResponse(
                answer=answer,
                language=lang,
                sources=[],
                fallback_used=False,
                requires_email=False,
                retrieval_language=lang,
                message_id=None,
                session_uuid=str(session_uuid),
                show_feedback=False,
                show_support_options=False,
                prefilled_email=None,
                support_comment_enabled=None,
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
        self.support_service = SupportService()
        self.support_ticket_service = SupportTicketService()
        self.db = PostgresClient(settings.POSTGRES_URL)

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

        # Bot name Q&A (e.g., 'what is your name?')
        msg = request.message.strip().lower()
        bot_name_phrases = [
            "what is your name",
            "who are you",
            "your name",
            "cómo te llamas",
            "cual es tu nombre",
            "quién eres"
        ]
        if any(phrase in msg for phrase in bot_name_phrases):
            print("[Chat] Bot name Q&A triggered", flush=True)
            lang = getattr(self, 'selected_language', None) or request.language or 'en'
            bot_name = getattr(self, 'BOT_NAME', 'Getmee Chatbot')
            # Ensure session_uuid is available, fallback to 'unknown' if not
            session_uuid_str = str(locals().get('session_uuid', 'unknown'))
            responses = STATIC_RESPONSES.get(lang, STATIC_RESPONSES['en'])
            answer = responses.get(
                'bot_intro',
                "I'm {bot_name}, your AI support assistant. I can guide you with your questions and platform-related help. How can I assist you today?"
            ).format(bot_name=bot_name)
            return ChatResponse(
                answer=answer,
                language=lang,
                sources=[],
                fallback_used=False,
                requires_email=False,
                retrieval_language=lang,
                message_id=None,
                session_uuid=session_uuid_str,
                show_feedback=False,
            )

        import re
        self.selected_language = request.language or 'en'
        print(f"[Chat] Incoming request.language: {request.language}", flush=True)

        # 0. Ensure session exists in PG + Redis
        session_key = request.session_id  # frontend sends this as session_key
        session = await self.session_service.get_or_create_session(session_key, request.language)
        session_uuid = session["id"]  # PG UUID

        # --- LANGUAGE CHANGE TRACKING (per session) ---
        # Get session context from Redis
        session_context = await self.session_service.redis_session.get_context(session_key) or {}
        prev_language = session_context.get("preferred_language")
        incoming_language = request.language or "en"
        # If no previous language (first message in session), always set language_changed = False
        if prev_language is None:
            language_changed = False
            # Initialize session context language
            session_context["preferred_language"] = incoming_language
            await self.session_service.redis_session.set_context(session_key, session_context)
            # Also update DB
            await self.session_service.db.connect()
            async with self.session_service.db.pool.acquire() as conn:
                await conn.execute(
                    "UPDATE chat_sessions SET preferred_language=$1 WHERE id=$2",
                    incoming_language, session_uuid,
                )
        else:
            # Compare only with previous language in this session
            if prev_language != incoming_language:
                language_changed = True
                # Update session context and DB
                session_context["preferred_language"] = incoming_language
                await self.session_service.redis_session.set_context(session_key, session_context)
                await self.session_service.db.connect()
                async with self.session_service.db.pool.acquire() as conn:
                    await conn.execute(
                        "UPDATE chat_sessions SET preferred_language=$1 WHERE id=$2",
                        incoming_language, session_uuid,
                    )
            else:
                language_changed = False

        # Save user message to chat_messages table (add language_changed)
        user_msg = await self.message_service.save_user_message(
            session_id=session_uuid,
            session_key=session_key,
            text=request.message,
            language=request.language,
            language_changed=language_changed
        )

        # Ensure retrieval_language and fallback_used are always initialized
        # retrieval_language should always reflect the language of the retrieval attempt
        retrieval_language = None
        fallback_used = False

        # 1. Email detection and validation (always check if input looks like an email)
        email_pattern = r"[\w.\-+]+@[\w.\-]+\.\w+"
        email_match = re.search(email_pattern, request.message)
        support_context = await self._get_support_context(session_key)
        lang = request.language or "en"
        max_support_requests = 2  # Enforced by _is_support_limit_reached
        reescalation_intent = self._detect_reescalation_intent(request.message)
        # Always validate if input contains '@' and is not a valid email
        if ("@" in request.message and not email_match):
            return ChatResponse(
                answer="It seems like you have entered an invalid email address. Please enter a valid email address if you would like to proceed.",
                language=lang,
                sources=[],
                fallback_used=False,
                requires_email=False,
                retrieval_language=lang,
                message_id=None,
                session_uuid=str(session_uuid),
                show_feedback=False,
                prefilled_email=None,
                support_comment_enabled=False,
                show_support_options=False,
                allow_recontact=False,
                show_recontact_confirmation=False,
                support_submit_label=None,
            )


        # --- CENTRALIZED SUPPORT LIMIT LOGIC ---
        # 1. Unsatisfied click (frontend should set a flag or special message, e.g. request.unsatisfied_click)
        if hasattr(request, 'unsatisfied_click') and getattr(request, 'unsatisfied_click', False):
            if self._is_support_limit_reached(support_context):
                print("[DEBUG] Support limit reached. Returning requires_email=False")
                return ChatResponse(
                    answer=self._get_unsatisfied_limit_message(lang),
                    language=lang,
                    sources=[],
                    fallback_used=False,
                    requires_email=False,
                    retrieval_language=lang,
                    message_id=None,
                    session_uuid=str(session_uuid),
                    show_feedback=False,
                    prefilled_email=None,
                    support_comment_enabled=False,
                    show_support_options=False,
                    allow_recontact=False,
                    show_recontact_confirmation=False,
                    support_submit_label=None,
                )
            # Below limit: allow popup (reset guard before opening popup)
            await self._prepare_new_support_submission(session_key)
            # Set escalation_source in Redis for Unsatisfied escalation
            await self.message_service.redis_session.update_context(session_key, escalation_source="Unsatisfied escalation")
            print("[DEBUG] Support limit NOT reached. Returning requires_email=True, prefilled_email=", support_context.get("support_email"))
            # Determine if this is first escalation or re-escalation
            support_count = support_context.get("support_request_count", 0)
            if support_count == 0:
                submit_label = "Contact Support"
            else:
                submit_label = "Contact again"
            response = ChatResponse(
                answer=self._get_unsatisfied_support_prompt(lang),
                language=lang,
                sources=[],
                fallback_used=False,
                requires_email=True,
                retrieval_language=lang,
                message_id=None,
                session_uuid=str(session_uuid),
                show_feedback=False,
                prefilled_email=support_context.get("support_email"),
                support_comment_enabled=True,
                show_support_options=True,
                allow_recontact=False,
                show_recontact_confirmation=False,
                support_submit_label=submit_label,
            )
            print("[DEBUG] Unsatisfied branch response:", response)
            return response

        # 2. Explicit recontact confirmation (user clicked Yes to recontact)
        if hasattr(request, 'recontact_confirmed') and getattr(request, 'recontact_confirmed', False):
            if self._is_support_limit_reached(support_context):
                return ChatResponse(
                    answer=self._get_direct_support_limit_message(lang),
                    language=lang,
                    sources=[],
                    fallback_used=False,
                    requires_email=False,
                    retrieval_language=lang,
                    message_id=None,
                    session_uuid=str(session_uuid),
                    show_feedback=False,
                    prefilled_email=None,
                    support_comment_enabled=False,
                    show_support_options=False,
                    allow_recontact=False,
                    show_recontact_confirmation=False,
                    support_submit_label=None,
                )
            # Below limit: allow second escalation (reset guard before opening popup)
            await self._prepare_new_support_submission(session_key)
            return ChatResponse(
                answer=self._get_email_received_message(lang),
                language=lang,
                sources=[],
                fallback_used=False,
                requires_email=True,
                retrieval_language=lang,
                message_id=None,
                session_uuid=str(session_uuid),
                show_feedback=False,
                prefilled_email=support_context.get("support_email"),
                support_comment_enabled=True,
                show_support_options=True,
                allow_recontact=False,
                show_recontact_confirmation=False,
                support_submit_label="Contact again",
            )

        # 3. Direct email / human support / re-escalation intent (not confirmation dialog)
        if email_match or reescalation_intent:
            if self._is_support_limit_reached(support_context):
                return ChatResponse(
                    answer=self._get_direct_support_limit_message(lang),
                    language=lang,
                    sources=[],
                    fallback_used=False,
                    requires_email=False,
                    retrieval_language=lang,
                    message_id=None,
                    session_uuid=str(session_uuid),
                    show_feedback=False,
                    prefilled_email=None,
                    support_comment_enabled=False,
                    show_support_options=False,
                    allow_recontact=False,
                    show_recontact_confirmation=False,
                    support_submit_label=None,
                )
            # Below limit: allow normal escalation flow (reset guard before opening popup)
            if email_match and not support_context.get("support_request_sent"):
                detected_email = email_match.group(0)
                await self._prepare_new_support_submission(session_key)
                await self.session_service.update_session_email(session_key, detected_email)
                # Set escalation_source in Redis for Direct escalation
                await self.message_service.redis_session.update_context(session_key, escalation_source="Direct escalation")
                localized_msg = self._get_email_received_message(lang)
                await self.message_service.redis_session.push_message(
                    session_key,
                    {"role": "user", "text": request.message, "language": lang}
                )
                await self.message_service.redis_session.push_message(
                    session_key,
                    {"role": "bot", "text": localized_msg, "language": lang}
                )
                return ChatResponse(
                    answer=localized_msg,
                    language=lang,
                    sources=[],
                    fallback_used=False,
                    requires_email=True,
                    retrieval_language=lang,
                    message_id=None,
                    session_uuid=str(session_uuid),
                    show_feedback=False,
                    prefilled_email=detected_email,
                    support_comment_enabled=True,
                    show_support_options=True,
                    allow_recontact=False,
                    show_recontact_confirmation=False,
                    support_submit_label=None,
                    escalation_source="Direct escalation",
                )
                # If support keywords are detected and support popup is triggered, set escalation_source
            # If support already submitted, show confirmation dialog
            if support_context.get("support_request_sent"):
                confirmation_msg = {
                    "en": "Your request has already been submitted to human support for this session. Do you want to contact support again?",
                    "es": "Tu consulta ya fue enviada al soporte humano en esta sesión. ¿Quieres contactar al soporte nuevamente?"
                }.get(lang, self._get_recontact_confirmation_message(lang))
                return ChatResponse(
                    answer=confirmation_msg,
                    language=lang,
                    sources=[],
                    fallback_used=False,
                    requires_email=False,
                    retrieval_language=lang,
                    message_id=None,
                    session_uuid=str(session_uuid),
                    show_feedback=False,
                    prefilled_email=support_context.get("support_email"),
                    support_comment_enabled=False,
                    show_support_options=False,
                    allow_recontact=True,
                    show_recontact_confirmation=True,
                    support_submit_label=None,
                )

        # 3. Handle recontact_declined (user clicked No)
        if hasattr(request, 'recontact_declined') and getattr(request, 'recontact_declined', False):
            return ChatResponse(
                answer="Okay, let us know if you need anything else.",
                language=lang,
                sources=[],
                fallback_used=False,
                requires_email=False,
                retrieval_language=lang,
                message_id=None,
                session_uuid=str(session_uuid),
                show_feedback=True,
                prefilled_email=None,
                support_comment_enabled=False,
                show_support_options=False,
                allow_recontact=False,
                show_recontact_confirmation=False,
                support_submit_label=None,
            )

        # 2. Support intent detection (if any, not shown in this excerpt)
        # ...existing support intent logic if present...

        # 3. Small talk and low intent detection (language-agnostic input, language-specific output)
        lang = request.language or 'en'
        intent = self._detect_intent(request.message)
        if not intent:
            intent = self._detect_low_intent_pattern(request.message)
        if intent:
            answer = self.INTENT_RESPONSES.get(lang, self.INTENT_RESPONSES["en"]).get(intent)
            await self.message_service.redis_session.push_message(
                session_key, {"role": "user", "text": request.message, "language": lang}
            )
            await self.message_service.redis_session.push_message(
                session_key, {"role": "bot", "text": answer, "language": lang}
            )
            return ChatResponse(
                answer=answer,
                language=lang,
                sources=[],
                fallback_used=False,
                requires_email=False,
                retrieval_language=lang,
                message_id=None,
                session_uuid=str(session_uuid),
                show_feedback=False,
            )

        # 5. Follow-up message handling (new logic)
        follow_up_answer = await self._handle_follow_up_message(request.message, session_key, self.selected_language)
        if follow_up_answer is not None:
            lang = request.language or 'en'
            await self.message_service.redis_session.push_message(session_key, {"role": "user", "text": request.message, "language": lang})
            await self.message_service.redis_session.push_message(session_key, {"role": "bot", "text": follow_up_answer, "language": lang})
            return ChatResponse(
                answer=follow_up_answer,
                language=lang,
                sources=[],
                fallback_used=False,
                requires_email=False,
                retrieval_language=lang,
                message_id=None,
                session_uuid=str(session_uuid),
                show_feedback=False,
            )

        # 6. Bot identity Q&A (already handled above)

        # 7. Context Q&A (e.g., 'what is my name?')
        context_answer = await self._get_session_context_answer(request.message, session_key, self.selected_language, session_uuid, request.message)
        if context_answer:
            # Save user message and bot reply to Redis
            lang = request.language or 'en'
            await self.message_service.redis_session.push_message(session_key, {"role": "user", "text": request.message, "language": lang})
            await self.message_service.redis_session.push_message(session_key, {"role": "bot", "text": context_answer.answer, "language": lang})
            return context_answer

        # 8. Name/context update detection
        name = self._detect_context_update(request.message)
        if name:
            ctx = await self.message_service.redis_session.get_context(session_key)
            ctx = ctx or {}
            ctx["user_name"] = name
            await self.message_service.redis_session.set_context(session_key, ctx)
            lang = request.language or 'en'
            responses = STATIC_RESPONSES.get(lang, STATIC_RESPONSES['en'])
            nice_msg = responses.get('nice_to_meet_you_named', "Nice to meet you, {name}! How can I help you today?").format(name=name)
            await self.message_service.redis_session.push_message(session_key, {"role": "user", "text": request.message, "language": lang})
            await self.message_service.redis_session.push_message(session_key, {"role": "bot", "text": nice_msg, "language": lang})
            return ChatResponse(
                answer=nice_msg,
                language=lang,
                sources=[],
                fallback_used=False,
                requires_email=False,
                retrieval_language=lang,
                message_id=None,
                session_uuid=str(session_uuid),
                show_feedback=False,
            )

        # ...existing logic follows (question intent, RAG, fallback, etc)...




        # --- Multilingual Retrieval Flow (fully correct) ---
        selected_language = request.language or "en"   # UI language for answer and fallback
        alternate_language = "es" if selected_language == "en" else "en"
        input_language = self.language_service.detect_language(request.message)
        retrieval_language = selected_language
        fallback_used = False


        # --- Retrieval thresholds ---
        PRIMARY_CONFIDENCE_THRESHOLD = MIN_PRIMARY_CONFIDENCE
        FALLBACK_CONFIDENCE_THRESHOLD = 0.15
        FALLBACK_DISTANCE_THRESHOLD = 1.0

        # 1. Build primary query in selected UI language
        if input_language == selected_language:
            primary_query = normalize_query(request.message)
        else:
            raw_translated = await self.llm_client.translate(
                request.message,
                target_language=self.language_service.get_language_name(selected_language)
            )
            primary_query = normalize_query(raw_translated)
        print(f"[DEBUG] Normalized primary_query: '{primary_query}'", flush=True)

        retrieved, relevant_chunks, primary_distance, primary_confidence = await self._attempt_retrieval(
            primary_query,
            primary_query,
            selected_language,
            "PRIMARY",
            is_cross_language=(input_language != selected_language)
        )

        print(f"[DEBUG] PRIMARY: query='{primary_query}', confidence={primary_confidence:.3f}, distance={primary_distance:.3f}", flush=True)
        print(f"[DEBUG] PRIMARY: chunks before filtering: {len(relevant_chunks)}", flush=True)

        active_confidence = primary_confidence
        retrieval_query_for_validation = primary_query
        retrieval_confidence_for_validation = primary_confidence
        retrieval_language = selected_language

        # 2. Fallback: search in alternate language if primary fails
        fb_chunks = []
        fb_confidence = 0.0
        fb_distance = 0.0
        fb_retrieved = None
        fallback_query = None
        if not relevant_chunks or primary_confidence < PRIMARY_CONFIDENCE_THRESHOLD:
            if input_language == alternate_language:
                fallback_query = normalize_query(request.message)
            else:
                raw_fb_translated = await self.llm_client.translate(
                    request.message,
                    target_language=self.language_service.get_language_name(alternate_language)
                )
                fallback_query = normalize_query(raw_fb_translated)
            print(f"[DEBUG] Normalized fallback_query: '{fallback_query}'", flush=True)
            print(f"[Chat] Step 3: Attempting fallback in '{alternate_language}'...", flush=True)
            fb_retrieved, fb_chunks, fb_distance, fb_confidence = await self._attempt_retrieval(
                fallback_query,
                fallback_query,
                alternate_language,
                "FALLBACK",
                is_cross_language=True
            )
            print(f"[DEBUG] FALLBACK: query='{fallback_query}', confidence={fb_confidence:.3f}, distance={fb_distance:.3f}", flush=True)
            print(f"[DEBUG] FALLBACK: chunks before filtering: {len(fb_chunks)}", flush=True)
            # Accept fallback only if chunks exist AND (confidence >= threshold OR distance <= threshold)
            if fb_chunks and (fb_confidence >= FALLBACK_CONFIDENCE_THRESHOLD or fb_distance <= FALLBACK_DISTANCE_THRESHOLD):
                relevant_chunks = fb_chunks
                retrieved = fb_retrieved
                retrieval_language = alternate_language
                fallback_used = True
                active_confidence = fb_confidence
                retrieval_query_for_validation = fallback_query
                retrieval_confidence_for_validation = fb_confidence
                print(f"[Chat] Fallback SUCCESS — using '{alternate_language}' results ({len(fb_chunks)} relevant chunks)", flush=True)
            else:
                print(f"[Chat] Fallback rejected: chunks={len(fb_chunks)}, confidence={fb_confidence:.3f}, distance={fb_distance:.3f}", flush=True)



        # --- Semantic filtering (define helpers locally) ---

        def _has_pronoun(text, lang):
            if lang == "es":
                pronouns = ["mi", "mis", "nuestro", "nuestra", "tu", "tus"]
            else:
                pronouns = ["my", "our", "your"]
            text_l = text.lower()
            return any(f" {p} " in f" {text_l} " for p in pronouns)

        def _direct_entity_match(query, chunk, lang):
            import string
            if lang == "es":
                stopwords = set(["mi", "mis", "nuestro", "nuestra", "tu", "tus", "el", "la", "los", "las", "un", "una", "unos", "unas", "es", "son", "quien", "que", "donde", "cuando", "como", "cual", "de", "a", "en", "con", "y", "o", "por", "para", "del", "al"])
            else:
                stopwords = set(["my", "our", "your", "the", "a", "an", "is", "are", "who", "what", "where", "when", "how", "which", "of", "to", "in", "on", "for", "with", "and", "or", "by", "at", "from"])
            query_tokens = [w.strip(string.punctuation).lower() for w in query.split() if w.strip(string.punctuation).lower() not in stopwords and len(w.strip(string.punctuation)) > 1]
            chunk_l = chunk.lower()
            return any(qt in chunk_l for qt in query_tokens)

        query_lang_for_filter = self.language_service.detect_language(retrieval_query_for_validation)
        def _is_semantically_relevant(chunk, query, max_overlap):
            if len(chunk.strip()) < 25 and max_overlap < 0.5:
                return False
            if max_overlap < 0.3:
                return False
            # Only apply pronoun/entity rule for English queries
            if query_lang_for_filter == "en":
                if _has_pronoun(query, "en") and not _direct_entity_match(query, chunk, "en"):
                    return False
            # For Spanish, skip this strict rule
            if len(chunk.strip().split()) <= 2 and max_overlap < 0.7:
                return False
            # --- Topic-aware filter: require topic overlap ---
            if not ChatService.chunk_matches_query_topic(query, chunk):
                return False
            return True



        filtered_chunks = []
        if relevant_chunks:
            for c in relevant_chunks:
                if _is_semantically_relevant(c, retrieval_query_for_validation, retrieval_confidence_for_validation):
                    filtered_chunks.append(c)
        print(f"[DEBUG] Chunks after semantic filtering: {len(filtered_chunks)}", flush=True)
        relevant_chunks = filtered_chunks




        # --- Final guard: if no valid grounded chunks, do not call LLM ---
        if not relevant_chunks or all(not (c and c.strip()) for c in relevant_chunks):
            print(
                f"[Chat] FINAL GUARD: No semantically relevant chunks after filtering (retrieval={retrieval_language}) — skipping LLM",
                flush=True
            )
            fallback_message = self._get_first_support_prompt(request.language or "en")
            support_context = await self._get_support_context(session_key)
            prefilled_email = support_context.get("support_email") if support_context else None

            bot_msg = await self.message_service.save_bot_message(
                session_id=session_uuid,
                session_key=session_key,
                text=fallback_message,
                language=request.language,
                fallback_used=True,
                source_type="fallback",
            )

            await self.session_service.save_turn(
                request.session_id,
                {"user": request.message, "bot": fallback_message}
            )
            await self.message_service.redis_session.update_context(
                session_key,
                escalation_source="Fallback escalation"
            )

            return ChatResponse(
                answer=fallback_message,
                language=request.language,
                sources=[],
                fallback_used=True,
                retrieval_language=retrieval_language,
                message_id=str(bot_msg["id"]),
                session_uuid=str(session_uuid),
                show_feedback=False,
                requires_email=True,
                support_submit_label=None,
                prefilled_email=prefilled_email,
                support_comment_enabled=True,
                show_support_options=True,
                allow_recontact=False,
                show_recontact_confirmation=False,
            )


        # Remove duplicate fallback/no-answer blocks after the final guard. Only the strict guard above controls the no-answer flow.
        sources = [{"text": doc[:200]} for doc in relevant_chunks]


        # If relevant chunks exist, keep current flow exactly as it is
        print(f"[DEBUG] About to call LLM. relevant_chunks: {relevant_chunks}", flush=True)

        # 5. Translate user question to context language for prompt matching
        #    Response language is always request.language (unchanged)
        prompt_query = request.message
        if input_language != retrieval_language:
            prompt_query = await self.llm_client.translate(
                request.message,
                target_language=self.language_service.get_language_name(retrieval_language)
            )
            print(f"[Chat] Step 5: Translated prompt question to '{retrieval_language}': '{prompt_query}'", flush=True)

        # 5b. Build prompt — question in context language, response language stays as selected
        prompt = self.prompt_service.build_prompt(prompt_query, [relevant_chunks], request.language)

        # 6. Generate answer — always in dropdown-selected language
        print(f"[Chat] Step 6: Generating answer in '{request.language}' (retrieval was '{retrieval_language}')", flush=True)
        answer = await self.llm_client.generate(prompt, language=request.language)

        # 6b. Guard: if context exists and is strong (distance < 1.5) but model still produced
        # missing-info text, retry once with a forced grounded prompt.
        # Skip retry for marginal/weak matches to avoid hallucination risk.
        FORCE_RETRY_DISTANCE_THRESHOLD = 1.5
        if (
            relevant_chunks
            and primary_distance < FORCE_RETRY_DISTANCE_THRESHOLD
            and self._looks_like_missing_info_answer(answer)
        ):
            print(
                f"[Chat] Step 6b: Detected fallback-like answer despite relevant context "
                f"(distance={primary_distance:.3f}) — retrying with forced grounded prompt",
                flush=True
            )
            retry_prompt = self.prompt_service.build_force_answer_prompt(request.message, [relevant_chunks], language)
            answer = await self.llm_client.generate(retry_prompt, language=lang_name)
        elif relevant_chunks and self._looks_like_missing_info_answer(answer):
            print(
                f"[Chat] Step 6b: Fallback-like answer but distance={primary_distance:.3f} >= {FORCE_RETRY_DISTANCE_THRESHOLD} "
                f"— treating as genuine no-info (skip retry to avoid hallucination)",
                flush=True
            )
            answer = self.language_service.get_fallback_message(language)
            fallback_used = True

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

        # --- Feedback and overall rating popup logic ---
        context = await self.message_service.redis_session.get_context(session_key) or {}
        bot_count = context.get("bot_message_count", 0)
        overall_count = context.get("bot_response_count", 0)
        # Determine if the answer is meaningful (not fallback, not support, not intent-based small talk/low intent)
        intent = self._detect_intent(request.message)
        if not intent:
            intent = self._detect_low_intent_pattern(request.message)
        is_meaningful = not (
            fallback_used
            or self._contains_support_keywords(answer)
            or intent
        )
        if is_meaningful:
            bot_count += 1
            context["bot_message_count"] = bot_count
            overall_count += 1
            context["bot_response_count"] = overall_count
            await self.message_service.redis_session.set_context(session_key, context)
        # For RAG answers (not fallback), always allow feedback (show_feedback True)
        show_feedback = not fallback_used or True  # Always show feedback for all normal answers
        # If you want interval-based feedback, use:
        # show_feedback = (bot_count % self.FEEDBACK_INTERVAL == 0) if bot_count > 0 else False
        show_overall_rating_popup = (overall_count % self.OVERALL_RATING_INTERVAL == 0) if overall_count > 0 else False

        # Debug print removed
        trigger_support = self._contains_support_keywords(answer)
        support_popup_message = None
        escalation_source = None
        if trigger_support:
            support_popup_message = "Please describe your issue for our support team."
            escalation_source = "Rag escalation"
            await self.message_service.redis_session.update_context(session_key, escalation_source=escalation_source)
        # If the support popup is being opened for a direct user action (not fallback/unsatisfied/keyword), set escalation_source
        if not fallback_used and not trigger_support and not (hasattr(request, 'unsatisfied_click') and getattr(request, 'unsatisfied_click', False)):
            await self.message_service.redis_session.update_context(session_key, escalation_source="User direct request")
            escalation_source = "User direct request"
        return ChatResponse(
            answer=answer,
            language=request.language,
            sources=sources,
            fallback_used=fallback_used,
            retrieval_language=retrieval_language,
            message_id=str(bot_msg["id"]),
            session_uuid=str(session_uuid),
            show_feedback=show_feedback,
            show_overall_rating_popup=show_overall_rating_popup,
            requires_email=trigger_support,
            support_submit_label=None,
            prefilled_email=None,
            support_comment_enabled=None,
            show_support_options=False,
            show_recontact_confirmation=False,
            escalation_source=escalation_source,
            # Only add this field if relevant
            **({"support_popup_message": support_popup_message} if support_popup_message else {})
        )

    async def handle_escalation(self, request):
        # Placeholder for escalation logic
        return {"escalated": True, "detail": "Escalation triggered."}
