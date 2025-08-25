import json
import logging
import os
import concurrent.futures
from notion_spec_updater import NotionSpecUpdater
from slack_notifier import SlackNotifier
from dashboard_generator import DashboardGenerator

# Configure basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def process_project(project_config: dict):
    """
    Processes a single project based on its configuration.
    This includes adding a spec, recording results, approving, and notifying.
    """
    project_name = project_config.get("name", "Unnamed Project")
    db_id = project_config.get("notion_database_id")
    webhook_url = project_config.get("slack_webhook_url")

    logging.info(f"--- Starting processing for project: {project_name} ---")

    if not db_id:
        logging.error(f"Skipping project '{project_name}' due to missing 'notion_database_id'.")
        return

    try:
        # Instantiate classes with project-specific config
        spec_updater = NotionSpecUpdater(database_id=db_id)
        slack_notifier = SlackNotifier(webhook_url=webhook_url)
    except ValueError as e:
        logging.error(f"Initialization failed for project '{project_name}'. Check .env file. Error: {e}")
        return

    spec_name = f"Test Spec for {project_name}"
    test_status = ""

    # 1. Add a new test spec
    try:
        spec_updater.add_spec(
            name=spec_name,
            version="v0.1",
            content="This is a test entry for multi-project setup.",
            changelog="Initial test entry.",
            status="Draft"
        )
        test_status = "Success"
        logging.info(f"[{project_name}] Successfully added spec: '{spec_name}'")
    except Exception as e:
        test_status = f"Fail: {str(e)}"
        logging.error(f"[{project_name}] Failed to add spec. Reason: {e}")

    # 2. Record the test result
    try:
        spec_updater.record_test_result(spec_name=spec_name, test_result=test_status)
    except Exception as e:
        logging.error(f"[{project_name}] Failed to record test result. Reason: {e}")

    # 3. Auto-approval flow
    if test_status == "Success":
        try:
            spec_updater.update_spec_status(name=spec_name, new_status="Approved")
            slack_notifier.send_message(f"✅ [{project_name}] Spec '{spec_name}' was automatically approved.")
        except Exception as e:
            logging.error(f"[{project_name}] Failed to approve spec. Reason: {e}")
            slack_notifier.send_message(f"⚠️ [{project_name}] Approval failed for spec '{spec_name}'. Reason: {e}")
    else:
        slack_notifier.send_message(f"❌ [{project_name}] Test failed for spec '{spec_name}': {test_status}")

    logging.info(f"--- Finished processing for project: {project_name} ---")
    # Return the updater instance for the dashboard
    return spec_updater

def main():
    """
    Main function to load configurations and process all projects.
    """
    config_path = "config.json"
    if not os.path.exists(config_path):
        logging.error(f"'{config_path}' not found. Please create it from 'config.json.example'.")
        return

    with open(config_path, "r", encoding="utf-8") as f:
        config = json.load(f)

    project_configs = config.get("projects", [])
    processed_results = [] # Will store tuples of (updater, config)

    # Use ThreadPoolExecutor to process projects in parallel
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        # Create a mapping from future to project config
        future_to_project = {executor.submit(process_project, proj): proj for proj in project_configs}

        logging.info(f"Submitted {len(future_to_project)} projects for processing.")

        for future in concurrent.futures.as_completed(future_to_project):
            project_config = future_to_project[future]
            try:
                # Get the result (the spec_updater instance) from the future
                updater_instance = future.result()
                if updater_instance:
                    # Store the successful result along with its config
                    processed_results.append((updater_instance, project_config))
            except Exception as exc:
                logging.error(f"Project '{project_config.get('name')}' generated an exception: {exc}")

    # 4. Generate the integrated dashboard from the successfully processed projects
    if processed_results:
        # Unzip the results into separate lists for the dashboard generator
        successful_updaters, successful_configs = zip(*processed_results)

        dashboard = DashboardGenerator()
        dashboard.generate_integrated(list(successful_updaters), list(successful_configs))

    logging.info("All projects processed.")

if __name__ == "__main__":
    main()
