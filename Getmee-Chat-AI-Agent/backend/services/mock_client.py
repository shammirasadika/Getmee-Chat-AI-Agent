class MockClient:
    def generate(self, message: str) -> str:
        return f"[MOCK RESPONSE] You asked: {message}"