from langdetect import detect

class LanguageService:
    @staticmethod
    def detect_language(text: str) -> str:
        try:
            lang = detect(text)
            if lang.startswith('es'):
                return 'es'
            return 'en'
        except Exception:
            return 'en'  # Default to English if detection fails
