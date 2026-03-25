import os
from dotenv import load_dotenv

load_dotenv()

class EmailSettings:
    MAIL_USERNAME: str = os.getenv("MAIL_USERNAME", "")
    MAIL_PASSWORD: str = os.getenv("MAIL_PASSWORD", "")
    MAIL_FROM: str = os.getenv("MAIL_FROM", "")
    MAIL_PORT: int = int(os.getenv("MAIL_PORT", 587))
    MAIL_SERVER: str = os.getenv("MAIL_SERVER", "smtp.gmail.com")
    MAIL_STARTTLS: bool = os.getenv("MAIL_STARTTLS", os.getenv("MAIL_TLS", "True")) == "True"
    MAIL_SSL_TLS: bool = os.getenv("MAIL_SSL_TLS", os.getenv("MAIL_SSL", "False")) == "True"

email_settings = EmailSettings()
