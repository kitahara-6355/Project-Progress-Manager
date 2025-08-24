import os
import requests
from dotenv import load_dotenv
import logging

class SlackNotifier:
    def __init__(self, webhook_url: str):
        """
        Initializes the Slack notifier.
        The webhook URL is passed in to make the class reusable for
        different projects/channels.
        """
        self.webhook_url = webhook_url
        if not self.webhook_url:
            logging.warning("SlackNotifier initialized with no webhook URL. Notifications will be disabled.")

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
