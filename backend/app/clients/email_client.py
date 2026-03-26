from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from app.core.email_config import email_settings


class EmailClient:
    def __init__(self):
        conf = ConnectionConfig(
            MAIL_USERNAME=email_settings.MAIL_USERNAME,
            MAIL_PASSWORD=email_settings.MAIL_PASSWORD,
            MAIL_FROM=email_settings.MAIL_FROM,
            MAIL_PORT=email_settings.MAIL_PORT,
            MAIL_SERVER=email_settings.MAIL_SERVER,
            MAIL_STARTTLS=email_settings.MAIL_STARTTLS,
            MAIL_SSL_TLS=email_settings.MAIL_SSL_TLS,
            USE_CREDENTIALS=True
        )
        self.fm = FastMail(conf)

    async def send_email(self, subject: str, recipients: list, body: str):
        message = MessageSchema(
            subject=subject,
            recipients=recipients,
            body=body,
            subtype="html"
        )
        await self.fm.send_message(message)
