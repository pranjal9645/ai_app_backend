import resend

from app.core.config import settings


class EmailService:

    def __init__(self):
        resend.api_key = settings.resend_api_key

    def send_password_reset_email(
        self,
        recipient_email: str,
        reset_token: str,
    ) -> None:

        reset_url = (
            f"{settings.password_reset_frontend_url}"
            f"?token={reset_token}"
        )

        params: resend.Emails.SendParams = {
            "from": settings.email_from,
            "to": [recipient_email],
            "subject": "Reset your password",
            "html": f"""
                <html>
                    <body>
                        <h2>Reset your password</h2>

                        <p>
                            We received a request to reset your password.
                        </p>

                        <p>
                            Click the link below to choose a new password:
                        </p>

                        <p>
                            <a href="{reset_url}">
                                Reset Password
                            </a>
                        </p>

                        <p>
                            This link will expire in
                            {settings.password_reset_token_expire_minutes}
                            minutes.
                        </p>

                        <p>
                            If you did not request this password reset,
                            you can safely ignore this email.
                        </p>
                    </body>
                </html>
            """,
        }

        resend.Emails.send(params)