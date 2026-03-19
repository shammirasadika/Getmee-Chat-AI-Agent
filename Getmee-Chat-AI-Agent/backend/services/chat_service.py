from services.ai_client import get_ai_client


class ChatService:
    def __init__(self):
        self.ai_client = get_ai_client()

    def process_message(self, request):
        user_message = request.message

        response = self.ai_client.chat(user_message)

        return {
            "reply": response
        }