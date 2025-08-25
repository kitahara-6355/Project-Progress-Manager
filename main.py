import json
import logging
import os
import concurrent.futures
import subprocess
from notion_spec_updater import NotionSpecUpdater
from slack_notifier import SlackNotifier
from dashboard_generator import DashboardGenerator

# Configure basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def run_test_command(command: str) -> (str, str):
    """
    Executes a shell command and captures its output.

    Args:
        command (str): The command to execute.

    Returns:
        A tuple containing the status ('Success' or 'Fail') and the
        combined stdout/stderr of the command.
    """
    logging.info(f"Executing test command: '{command}'")
    # Security Note: shell=True can be a security risk if the command comes
    # from an untrusted source. Here, we trust the user's config.json.
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            check=False  # Don't raise exception on non-zero exit code
        )
        if result.returncode == 0:
            logging.info("Test command executed successfully.")
            return "Success", result.stdout
        else:
            logging.error(f"Test command failed with exit code {result.returncode}.")
            return "Fail", result.stderr + "\n" + result.stdout
    except Exception as e:
        logging.error(f"An exception occurred while running the test command: {e}")
        return "Fail", str(e)

def process_project(project_config: dict):
    """
    Processes a single project: runs its test command and updates Notion/Slack.
    """
    project_name = project_config.get("name", "Unnamed Project")
    db_id = project_config.get("notion_database_id")
    webhook_url = project_config.get("slack_webhook_url")
    test_command = project_config.get("test_command")
    spec_name = project_config.get("spec_name_to_update")

    logging.info(f"--- Starting processing for project: {project_name} ---")

    if not all([db_id, test_command, spec_name]):
        logging.error(f"Skipping project '{project_name}' due to missing configuration "
                      f"('notion_database_id', 'test_command', or 'spec_name_to_update').")
        return None

    try:
        spec_updater = NotionSpecUpdater(database_id=db_id)
        slack_notifier = SlackNotifier(webhook_url=webhook_url)
    except ValueError as e:
        logging.error(f"Initialization failed for project '{project_name}'. Check .env file. Error: {e}")
        return None

    # 1. Run the actual test command
    test_status, test_output = run_test_command(test_command)

    # 2. Record the test result in Notion
    try:
        spec_updater.record_test_result(spec_name=spec_name, test_result=f"{test_status}: {test_output[:1500]}")
    except Exception as e:
        logging.error(f"[{project_name}] Failed to record test result for spec '{spec_name}'. Reason: {e}")

    # 3. Auto-approval flow based on test result
    if test_status == "Success":
        try:
            spec_updater.update_spec_status(name=spec_name, new_status="Approved")
            slack_notifier.send_message(f"✅ [{project_name}] Tests passed for '{spec_name}'. Spec automatically approved.")
        except Exception as e:
            logging.error(f"[{project_name}] Failed to approve spec '{spec_name}'. Reason: {e}")
            slack_notifier.send_message(f"⚠️ [{project_name}] Approval failed for spec '{spec_name}'. Reason: {e}")
    else:
        try:
            spec_updater.update_spec_status(name=spec_name, new_status="Fail")
            slack_notifier.send_message(f"❌ [{project_name}] Tests failed for '{spec_name}'. See Notion for details.")
        except Exception as e:
            logging.error(f"[{project_name}] Failed to update spec status to 'Fail'. Reason: {e}")

    logging.info(f"--- Finished processing for project: {project_name} ---")
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
