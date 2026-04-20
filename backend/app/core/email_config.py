from app.core.config import settings


class EmailSettings:
    MAIL_USERNAME: str = settings.MAIL_USERNAME
    MAIL_PASSWORD: str = settings.MAIL_PASSWORD
    MAIL_FROM: str = settings.MAIL_FROM
    MAIL_PORT: int = settings.MAIL_PORT
    MAIL_SERVER: str = settings.MAIL_SERVER
    MAIL_STARTTLS: bool = settings.MAIL_STARTTLS
    MAIL_SSL_TLS: bool = settings.MAIL_SSL_TLS

email_settings = EmailSettings()
