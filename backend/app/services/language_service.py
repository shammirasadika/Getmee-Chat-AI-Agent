from langdetect import detect

SUPPORTED_LANGUAGES = {'en', 'es', 'ar', 'fr', 'zh', 'pt', 'de', 'ja', 'ko', 'hi'}

# Simple translation pairs for fallback retrieval
FALLBACK_LANGUAGE_MAP = {
    'en': 'es',
    'es': 'en',
}

LANGUAGE_NAMES = {
    'en': 'English',
    'es': 'Spanish',
    'ar': 'Arabic',
    'fr': 'French',
    'zh': 'Chinese',
    'pt': 'Portuguese',
    'de': 'German',
    'ja': 'Japanese',
    'ko': 'Korean',
    'hi': 'Hindi',
}

FALLBACK_MESSAGES = {
    'en': "I couldn't find information related to your question.",
    'es': "No pude encontrar información relacionada con tu consulta.",
}

class LanguageService:
    @staticmethod
    def detect_language(text: str) -> str:
        try:
            lang = detect(text)
            # Map language codes (e.g. 'zh-cn' -> 'zh')
            lang = lang.split('-')[0]
            if lang in SUPPORTED_LANGUAGES:
                return lang
            return 'en'
        except Exception:
            return 'en'  # Default to English if detection fails

    @staticmethod
    def get_fallback_language(language: str) -> str:
        """Return the alternative language for fallback retrieval."""
        return FALLBACK_LANGUAGE_MAP.get(language, 'en')

    @staticmethod
    def get_language_name(code: str) -> str:
        return LANGUAGE_NAMES.get(code, 'English')

    @staticmethod
    def get_fallback_message(language: str) -> str:
        return FALLBACK_MESSAGES.get(language, FALLBACK_MESSAGES['en'])
