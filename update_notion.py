import os
import json
import logging
from datetime import datetime
from notion_client import Client
from config import NOTION_TOKEN, NOTION_DATABASE_ID

def update_notion_from_json(json_file: str):
    """
    Creates a new page in a Notion database with the contents of a JSON file.

    This function reads a list of sources from a JSON file and adds them
    as content to a new page created in the specified database.
    """
    logging.info(f"Attempting to create new page in Notion DB {NOTION_DATABASE_ID} from '{json_file}'...")

    try:
        notion = Client(auth=NOTION_TOKEN)

        if not os.path.exists(json_file):
            logging.error(f"  - Source JSON file not found: {json_file}")
            return False

        with open(json_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        # --- Define the new page structure ---
        # The new page will have a title with the current date and time.
        # The database this page is added to MUST have a "Title" property.
        page_title = f"Data Import - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        new_page_properties = {
            "Name": { # Assumes the DB's title property is named "Name"
                "title": [{"text": {"content": page_title}}]
            }
        }

        # The content of the JSON file will become the content of the new page.
        child_blocks = [
            {
                "object": "block",
                "type": "heading_2",
                "heading_2": {"rich_text": [{"text": {"content": "Imported Files Summary"}}]}
            }
        ]
        if not data:
            child_blocks.append({
                "object": "block",
                "type": "paragraph",
                "paragraph": {"rich_text": [{"text": {"content": "No files were found to import."}}]}
            })
        else:
            # Create a bulleted list of the imported files
            bullet_list_items = []
            for item in data:
                bullet_list_items.append({
                    "object": "block",
                    "type": "bulleted_list_item",
                    "bulleted_list_item": {
                        "rich_text": [{
                            "type": "text",
                            "text": {"content": item.get("file", "Unknown file")}
                        }]
                    }
                })
            child_blocks.extend(bullet_list_items)

        # Create the new page in the database
        notion.pages.create(
            parent={"database_id": NOTION_DATABASE_ID},
            properties=new_page_properties,
            children=child_blocks
        )

        logging.info("  - New page created in Notion successfully.")
        return True
    except Exception as e:
        logging.error(f"  - Failed to create page in Notion: {e}")
        return False
