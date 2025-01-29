from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
import os
import logging


class SendGrid():
    __client = None

    def __new__(cls):
        if not cls.__client:
            cls.__client = SendGridAPIClient(
                api_key=os.environ.get('SENDGRID_API_KEY'))

        instance = super().__new__(cls)
        return instance

    def send_email(self, to_email: str, subject: str, content: str, from_email = None) -> bool:
        try:
            message = Mail(
                from_email=from_email or os.environ.get('SENDGRID_FROM_EMAIL'),
                to_emails=to_email,
                subject=subject,
                html_content=content)
            self.__client.send(message)
            return True
        except Exception as e:
            logging.error(
                f"An error occurred while sending the email: {str(e)}")
            return False