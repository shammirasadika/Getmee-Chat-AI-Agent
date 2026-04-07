from app.clients.postgres_client import PostgresClient
from app.clients.redis_client import RedisClient
from app.clients.email_client import EmailClient
from app.core.config import settings

COOLDOWN_KEY_PREFIX = "support_email_sent:"


class SupportService:
    def __init__(self):
        self.postgres = PostgresClient(settings.POSTGRES_URL)
        self.redis = RedisClient(settings.REDIS_URL)
        self._email_client = None

    @property
    def email_client(self):
        if self._email_client is None:
            self._email_client = EmailClient()
        return self._email_client

    async def handle_fallback_escalation(
        self,
        session_id: str,
        user_message: str,
        user_email: str,
        language: str,
        fallback_message: str = None,
        chat_summary: str = None,
        source: str = "rag_fallback",
    ) -> dict:
        """
        Full fallback escalation flow:
        1. Save support request in PostgreSQL (with user email + fallback answer)
        2. Check Redis cooldown for this session
        3. If cooldown not active, send email and set cooldown
        4. Update email_sent flag in PostgreSQL
        """
        # 1. Save to PostgreSQL (source of truth)
        request_id = await self.postgres.save_support_request({
            "session_id": session_id,
            "user_message": user_message,
            "user_email": user_email,
            "fallback_message": fallback_message,
            "language": language,
            "status": "pending",
            "email_sent": False,
            "chat_summary": chat_summary,
            "source": source,
        })
        print(f"[Support] Saved support request #{request_id} for session {session_id} | escalation_source={source}", flush=True)

        # 2. Check Redis cooldown
        cooldown_key = f"{COOLDOWN_KEY_PREFIX}{session_id}"
        cooldown_active = await self.redis.is_cooldown_active(cooldown_key)
        email_sent = False

        if cooldown_active:
            print(f"[Support] Cooldown active for {session_id} — skipping email", flush=True)
        else:
            # 3. Send email notification
            email_sent = await self._send_support_email(
                session_id, user_message, user_email, language, fallback_message, chat_summary, source
            )
            if email_sent:
                # Set cooldown in Redis
                await self.redis.set_cooldown(cooldown_key, settings.SUPPORT_EMAIL_COOLDOWN)
                print(f"[Support] Cooldown set for {session_id} ({settings.SUPPORT_EMAIL_COOLDOWN}s)", flush=True)

        # 4. Update email_sent flag in PostgreSQL
        await self.postgres.update_support_request_email(request_id, email_sent)

        return {
            "request_id": request_id,
            "email_sent": email_sent,
            "cooldown_active": cooldown_active,
        }

    async def _send_support_email(
        self, session_id: str, user_message: str, user_email: str,
        language: str, fallback_message: str = None, chat_summary: str = None, escalation_source: str = None, direct_support: bool = False
    ) -> bool:
        """Send email notification to support team with all relevant context."""
        if not settings.SUPPORT_EMAIL:
            print("[Support] SUPPORT_EMAIL not configured — skipping email", flush=True)
            return False
        try:
            from datetime import datetime, timezone
            timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")


            subject = f"[Getmee Support] New enquiry — {user_email} (Session {session_id[:12]})"


            # Always show both user question and chatbot response (even if empty)
            user_question_html = (
                f"<tr><td style='padding:8px 12px;font-weight:bold;vertical-align:top;'>User Issue/Comment:</td>"
                f"<td style='padding:8px 12px;'>{user_message or '<em>(not provided)</em>'}</td></tr>"
            )
            chatbot_response_html = (
                f"<tr><td style='padding:8px 12px;font-weight:bold;vertical-align:top;'>Chatbot Response:</td>"
                f"<td style='padding:8px 12px;'>{fallback_message if fallback_message else '<em>(not available)</em>'}</td></tr>"
            )
            escalation_source_html = ""
            if escalation_source:
                escalation_source_html = (
                    f"<tr style='background:#f0f4f8;'><td style='padding:8px 12px;font-weight:bold;'>Escalation Source:</td>"
                    f"<td style='padding:8px 12px;'>{escalation_source}</td></tr>"
                )

            # Build chat summary section
            summary_html = ""
            if chat_summary:
                formatted_summary = chat_summary.replace("\n", "<br>")
                summary_html = (
                    f"<h4 style='margin-top:20px;color:#333;'>Conversation History (Last 5 Turns)</h4>"
                    f"<div style='background:#f7f7f7;border-left:3px solid #4a90d9;padding:12px;font-size:13px;'>"
                    f"{formatted_summary}</div>"
                )

            # Add direct support note if relevant
            direct_support_html = ""
            if direct_support:
                direct_support_html = (
                    f"<div style='margin:12px 0;padding:10px;background:#e7f3fe;border-left:4px solid #2196f3;'>"
                    f"<strong>Direct Support Request:</strong> This request was submitted directly by the user, not triggered by chatbot fallback or unsatisfied feedback."
                    f"</div>"
                )

            body = (
                f"<div style='font-family:Arial,sans-serif;max-width:600px;'>"
                f"<h2 style='color:#d9534f;border-bottom:2px solid #d9534f;padding-bottom:8px;'>New Support Enquiry</h2>"
                f"<p style='color:#666;font-size:13px;'>Received at {timestamp}</p>"
                f"<table style='width:100%;border-collapse:collapse;margin:16px 0;'>"
                f"<tr style='background:#f0f4f8;'><td style='padding:8px 12px;font-weight:bold;width:160px;'>Session ID:</td>"
                f"<td style='padding:8px 12px;'><code>{session_id}</code></td></tr>"
                f"<tr><td style='padding:8px 12px;font-weight:bold;'>User Email:</td>"
                f"<td style='padding:8px 12px;'><a href='mailto:{user_email}'>{user_email}</a></td></tr>"
                f"<tr style='background:#f0f4f8;'><td style='padding:8px 12px;font-weight:bold;'>Language:</td>"
                f"<td style='padding:8px 12px;'>{language}</td></tr>"
                f"{escalation_source_html}"
                f"{user_question_html}"
                f"{chatbot_response_html}"
                f"</table>"
                f"{summary_html}"
                f"{direct_support_html}"
                f"<div style='margin-top:20px;padding:12px;background:#fff3cd;border:1px solid #ffc107;border-radius:4px;'>"
                f"<strong>Action Required:</strong> Please follow up with the user at <a href='mailto:{user_email}'>{user_email}</a>."
                f"</div>"
                f"</div>"
            )
            await self.email_client.send_email(
                subject=subject,
                recipients=[settings.SUPPORT_EMAIL],
                body=body,
            )
            print(f"[Support] Email sent to {settings.SUPPORT_EMAIL}", flush=True)
            return True
        except Exception as e:
            print(f"[Support] Failed to send email: {e}", flush=True)
            return False

    async def get_requests(self, status: str = None, limit: int = 50):
        """Retrieve support requests from PostgreSQL."""
        return await self.postgres.get_support_requests(status=status, limit=limit)
