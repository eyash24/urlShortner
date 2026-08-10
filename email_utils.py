from email.message import EmailMessage
import aiosmtplib

from fastapi.templating import Jinja2Templates
from config import settings

async def send_email(
        to_email: str,
        subject: str,
        plain_text: str,
        html_content: str | None = None
) -> None:
    message = EmailMessage()
    message['From'] = settings.mail_from
    message['To'] = to_email
    message['Subject'] = subject
    message.set_content(plain_text)

    if html_content:
        message.add_alternative(html_content, subtype='html')

    