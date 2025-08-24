import os
from notion_client import Client
from dotenv import load_dotenv

class NotionSpecUpdater:
    def __init__(self):
        load_dotenv()
        self.notion = Client(auth=os.getenv("NOTION_API_TOKEN"))
        self.database_id = os.getenv("NOTION_DATABASE_ID")

    def add_spec(self, name, version, content, changelog, status):
        new_page_properties = {
            "Name": {"title": [{"text": {"content": name}}]},
            "Version": {"rich_text": [{"text": {"content": version}}]},
            "Content": {"rich_text": [{"text": {"content": content}}]},
            "Changelog": {"rich_text": [{"text": {"content": changelog}}]},
            "Status": {"select": {"name": status}},
            "Test Result": {"rich_text": [{"text": {"content": ""}}]}
        }
        self.notion.pages.create(
            parent={"database_id": self.database_id},
            properties=new_page_properties
        )

    def update_spec_version(self, name, new_version, changelog):
        page = self._find_page_by_name(name)
        if page:
            self.notion.pages.update(
                page_id=page["id"],
                properties={
                    "Version": {"rich_text": [{"text": {"content": new_version}}]},
                    "Changelog": {"rich_text": [{"text": {"content": changelog}}]}
                }
            )

    def update_spec_status(self, name, new_status):
        page = self._find_page_by_name(name)
        if page:
            self.notion.pages.update(
                page_id=page["id"],
                properties={"Status": {"select": {"name": new_status}}}
            )

    def record_test_result(self, spec_name, test_result):
        page = self._find_page_by_name(spec_name)
        if page:
            self.notion.pages.update(
                page_id=page["id"],
                properties={"Test Result": {"rich_text": [{"text": {"content": test_result}}]}}
            )

    def _find_page_by_name(self, name):
        # Note: For large databases, filtering via the API call is more efficient.
        # This implementation iterates through all results.
        response = self.notion.databases.query(database_id=self.database_id)
        for page in response.get("results", []):
            page_properties = page.get("properties", {})
            name_property = page_properties.get("Name", {}).get("title", [])
            if name_property:
                title = name_property[0].get("text", {}).get("content")
                if title == name:
                    return page
        return None
