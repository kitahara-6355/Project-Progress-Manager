import logging
from notion_spec_updater import NotionSpecUpdater
from slack_notifier import SlackNotifier
from dashboard_generator import DashboardGenerator

# Configure basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def main():
    """
    Main execution script that runs the full workflow:
    1. Adds a test spec to Notion.
    2. Records the result of that operation.
    3. Updates the spec status to 'Approved' if successful.
    4. Sends a Slack notification about the outcome.
    5. Generates and prints an updated dashboard.
    """
    try:
        spec_updater = NotionSpecUpdater()
        slack_notifier = SlackNotifier()
        dashboard = DashboardGenerator()
    except ValueError as e:
        logging.error(f"Initialization failed. Check your .env file. Error: {e}")
        return

    spec_name = "テスト仕様書"
    test_status = ""

    # Add a new test spec
    try:
        logging.info(f"Attempting to add spec: '{spec_name}'")
        spec_updater.add_spec(
            name=spec_name,
            version="v0.1",
            content="これはテストです",
            changelog="Initial test entry.",
            status="Draft"
        )
        test_status = "Success"
        logging.info(f"Successfully added spec: '{spec_name}'")
    except Exception as e:
        test_status = f"Fail: {str(e)}"
        logging.error(f"Failed to add spec: '{spec_name}'. Reason: {e}")

    # Record the result of the test (in this case, the 'add_spec' operation)
    try:
        logging.info(f"Recording test result for '{spec_name}'...")
        spec_updater.record_test_result(
            spec_name=spec_name,
            test_result=test_status
        )
        logging.info("Successfully recorded test result.")
    except Exception as e:
        logging.error(f"Failed to record test result for '{spec_name}'. Reason: {e}")

    # Auto-approval flow based on the test status
    if test_status == "Success":
        try:
            logging.info(f"Attempting to approve spec: '{spec_name}'")
            spec_updater.update_spec_status(
                name=spec_name,
                new_status="Approved"
            )
            logging.info(f"Successfully approved spec: '{spec_name}'")
            slack_notifier.send_message(
                f"✅ Specification '{spec_name}' was automatically approved."
            )
        except Exception as e:
            logging.error(f"Failed to approve spec '{spec_name}'. Reason: {e}")
            slack_notifier.send_message(
                f"⚠️ Approval failed for spec '{spec_name}' even though test succeeded. Reason: {e}"
            )
    else:
        slack_notifier.send_message(
            f"❌ Test failed for specification '{spec_name}': {test_status}"
        )

    # Generate and display the dashboard
    logging.info("Updating and generating dashboard...")
    dashboard.generate(spec_updater)


if __name__ == "__main__":
    main()
