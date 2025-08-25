import requests
import logging
from config import SLACK_WEBHOOK_URL

def send_slack_message(text: str):
    """
    Sends a message to the configured Slack webhook URL.
    """
    if not SLACK_WEBHOOK_URL or "your_slack_webhook_url" in SLACK_WEBHOOK_URL:
        logging.warning(f"Slack notification not sent (URL not configured): {text}")
        return

    logging.info(f"Sending Slack notification...")
    payload = {"text": text}

    try:
        response = requests.post(SLACK_WEBHOOK_URL, json=payload, timeout=5)
        response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)
        logging.info("  - Slack notification sent successfully.")
    except requests.exceptions.RequestException as e:
        logging.error(f"  - Failed to send Slack notification: {e}")
