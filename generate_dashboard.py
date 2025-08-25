import json
import os
import logging
from jinja2 import Environment, FileSystemLoader
from config import DATA_DIR, DASHBOARD_DIR

def generate_dashboard():
    """
    Generates the HTML dashboard from the imported sources JSON file.
    """
    logging.info("Generating HTML dashboard...")

    try:
        # Set up Jinja2 environment
        env = Environment(loader=FileSystemLoader("templates"))
        template = env.get_template("dashboard_template.html")

        # Load the data
        json_path = os.path.join(DATA_DIR, "imported_sources.json")
        if not os.path.exists(json_path):
            logging.warning(f"  - Data file not found: {json_path}. Dashboard will be empty.")
            sources_data = []
        else:
            with open(json_path, "r", encoding="utf-8") as f:
                sources_data = json.load(f)

        # Render the template with data
        html_content = template.render(sources=sources_data)

        # Save the rendered HTML
        os.makedirs(DASHBOARD_DIR, exist_ok=True)
        output_path = os.path.join(DASHBOARD_DIR, "index.html")

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(html_content)

        logging.info(f"  - Dashboard successfully generated at '{output_path}'")
        return True
    except Exception as e:
        logging.error(f"  - Failed to generate dashboard: {e}")
        return False
