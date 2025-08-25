import os
import json
import logging
from notion_client import Client
from config import NOTION_TOKEN, NOTION_PAGE_ID

def update_notion_from_json(json_file: str):
    """
    Updates a Notion page with the contents of a JSON file.

    This function reads a list of sources from a JSON file and appends
    a summary of the filenames to a single block on the specified Notion page.
    """
    logging.info(f"Attempting to update Notion page {NOTION_PAGE_ID} from '{json_file}'...")

    try:
        notion = Client(auth=NOTION_TOKEN)

        if not os.path.exists(json_file):
            logging.error(f"  - Source JSON file not found: {json_file}")
            return False

        with open(json_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        # Create a simple text block with a list of filenames.
        # The user's spec implies a single block update.
        content_text = "Imported Files Summary:\n" + "\n".join([f"- {d['file']}" for d in data])

        notion.blocks.children.append(
            block_id=NOTION_PAGE_ID,
            children=[
                {
                    "object": "block",
                    "type": "paragraph",
                    "paragraph": {
                        "rich_text": [{
                            "type": "text",
                            "text": {"content": content_text}
                        }]
                    }
                }
            ]
        )
        logging.info("  - Notion page updated successfully.")
        return True
    except Exception as e:
        logging.error(f"  - Failed to update Notion: {e}")
        return False
