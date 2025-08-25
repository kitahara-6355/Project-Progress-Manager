import logging
import os
from fetch_data import main as fetch_main
from update_notion import update_notion_from_json
from slack_notify import send_slack_message
from generate_dashboard import generate_dashboard
from config import LOG_FILE, DATA_DIR

def setup_logging():
    """Configures the logging for the application."""
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(levelname)s] - %(message)s',
        handlers=[
            logging.FileHandler(LOG_FILE, 'w', 'utf-8'),
            logging.StreamHandler() # Also print logs to console
        ]
    )

def main_process():
    """
    Runs the main data processing and reporting workflow.
    """
    logging.info("===== Main Process Started =====")

    try:
        # Step 1: Fetch data from local files
        logging.info("--- Step 1: Fetching data ---")
        sources, top20 = fetch_main()
        if not sources:
            logging.warning("No source files found. Process might not have expected data.")
        send_slack_message("✅ [Step 1/3] Data fetching complete.")

        # Step 2: Update Notion
        logging.info("--- Step 2: Updating Notion ---")
        json_file_path = os.path.join(DATA_DIR, "imported_sources.json")
        if update_notion_from_json(json_file_path):
            send_slack_message("✅ [Step 2/3] Notion page updated successfully.")
        else:
            send_slack_message("❌ [Step 2/3] Failed to update Notion page.")

        # Step 3: Generate Dashboard
        logging.info("--- Step 3: Generating dashboard ---")
        if generate_dashboard():
            send_slack_message("✅ [Step 3/3] HTML dashboard generated successfully.")
        else:
            send_slack_message("❌ [Step 3/3] Failed to generate HTML dashboard.")

        logging.info("===== Main Process Finished Successfully =====")
        send_slack_message("🚀 All tasks completed successfully!")

    except Exception as e:
        logging.critical(f"A critical error occurred in the main process: {e}", exc_info=True)
        send_slack_message(f"🚨 CRITICAL ERROR: The main process failed. Check logs for details. Error: {e}")

if __name__ == "__main__":
    setup_logging()
    main_process()
