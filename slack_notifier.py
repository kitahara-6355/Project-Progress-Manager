import os
import requests
from dotenv import load_dotenv
import logging

class SlackNotifier:
    def __init__(self):
        load_dotenv()
        self.webhook_url = os.getenv("SLACK_WEBHOOK_URL")
        if not self.webhook_url:
            logging.warning("SLACK_WEBHOOK_URL is not set. Slack notifications will be disabled.")

    def send_message(self, message):
        if not self.webhook_url:
            logging.warning(f"Slack notification not sent (URL not configured): {message}")
            return

        try:
            payload = {"text": message}
            response = requests.post(self.webhook_url, json=payload)
            response.raise_for_status()
            logging.info("Slack notification sent successfully.")
        except requests.exceptions.RequestException as e:
            logging.error(f"Failed to send Slack notification: {e}")
