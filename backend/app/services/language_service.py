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
    'en': "I couldn't find a relevant answer to your question. Your enquiry can be forwarded to our support team. Please provide your email address so a team member can contact you.",
    'es': "No pude encontrar una respuesta relevante a tu pregunta. Tu consulta puede ser enviada a nuestro equipo de soporte. Por favor, proporciona tu correo electrónico para que un miembro del equipo pueda contactarte.",
    'ar': "لم أتمكن من العثور على إجابة ذات صلة لسؤالك. يمكن إرسال استفسارك إلى فريق الدعم لدينا. يرجى تقديم عنوان بريدك الإلكتروني حتى يتمكن أحد أعضاء الفريق من التواصل معك.",
    'fr': "Je n'ai pas pu trouver de réponse pertinente à votre question. Votre demande peut être transmise à notre équipe d'assistance. Veuillez fournir votre adresse e-mail afin qu'un membre de l'équipe puisse vous contacter.",
    'zh': "我无法找到与您问题相关的回答。您的咨询可以转交给我们的支持团队。请提供您的电子邮件地址，以便团队成员与您联系。",
    'pt': "Não consegui encontrar uma resposta relevante para a sua pergunta. A sua consulta pode ser encaminhada à nossa equipa de suporte. Por favor, forneça o seu endereço de e-mail para que um membro da equipa possa contactá-lo.",
    'de': "Ich konnte keine relevante Antwort auf Ihre Frage finden. Ihre Anfrage kann an unser Support-Team weitergeleitet werden. Bitte geben Sie Ihre E-Mail-Adresse an, damit ein Teammitglied Sie kontaktieren kann.",
    'ja': "お探しの質問に関連する回答が見つかりませんでした。お問い合わせはサポートチームに転送できます。チームメンバーがご連絡できるよう、メールアドレスをご提供ください。",
    'ko': "귀하의 질문에 대한 관련 답변을 찾지 못했습니다. 문의 사항은 지원팀에 전달될 수 있습니다. 팀원이 연락드릴 수 있도록 이메일 주소를 제공해 주세요.",
    'hi': "आपके प्रश्न का कोई प्रासंगिक उत्तर नहीं मिला। आपकी पूछताछ हमारी सहायता टीम को भेजी जा सकती है। कृपया अपना ईमेल पता प्रदान करें ताकि टीम का कोई सदस्य आपसे संपर्क कर सके।",
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
