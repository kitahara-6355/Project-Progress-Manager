import logging

class DashboardGenerator:
    def generate(self, spec_updater):
        """
        Generates a simple text-based dashboard and prints it to the console.
        """
        logging.info("Generating dashboard...")
        try:
            # Re-using the query logic from the spec_updater.
            # Note: The user's provided code had this logic here, but it's better
            # to call a method on the updater if one exists. Let's assume we might
            # refactor later and for now, we query directly as per the user's snippet.
            results = spec_updater.notion.databases.query(database_id=spec_updater.database_id).get("results", [])
        except Exception as e:
            logging.error(f"Failed to query Notion database for dashboard: {e}")
            return

        approved = []
        drafts = []
        other_statuses = []

        for page in results:
            properties = page.get("properties", {})
            status_prop = properties.get("Status", {}).get("select")
            name_prop = properties.get("Name", {}).get("title", [])
            version_prop = properties.get("Version", {}).get("rich_text", [])

            status = status_prop.get("name", "Unknown") if status_prop else "Unknown"
            name = name_prop[0].get("text", {}).get("content") if name_prop else "Untitled"
            version = version_prop[0].get("text", {}).get("content") if version_prop else "N/A"

            entry = f"{name} v{version}"

            if status == "Approved":
                approved.append(entry)
            elif status == "Draft":
                drafts.append(entry)
            else:
                other_statuses.append(f"{entry} ({status})")

        # Print the dashboard to the console
        print("\n" + "="*20)
        print("=== PROJECT DASHBOARD ===")
        print("="*20)

        print("\n--- ✅ Approved Specs ---")
        if approved:
            for a in approved:
                print(f" - {a}")
        else:
            print(" (None)")

        print("\n--- 📝 Draft Specs ---")
        if drafts:
            for d in drafts:
                print(f" - {d}")
        else:
            print(" (None)")

        if other_statuses:
            print("\n--- 📊 Other Statuses ---")
            for o in other_statuses:
                print(f" - {o}")

        print("\n" + "="*20)
        logging.info("Dashboard generation complete.")
