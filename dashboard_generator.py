import logging

class DashboardGenerator:
    def _get_project_data(self, spec_updater):
        """Fetches and categorizes specs for a single project."""
        project_dashboard = {"Approved": [], "Draft": [], "Other": []}
        try:
            results = spec_updater.notion.databases.query(
                database_id=spec_updater.database_id
            ).get("results", [])
        except Exception as e:
            logging.error(f"Failed to query database {spec_updater.database_id}: {e}")
            return project_dashboard

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
                project_dashboard["Approved"].append(entry)
            elif status == "Draft":
                project_dashboard["Draft"].append(entry)
            else:
                project_dashboard["Other"].append(f"{entry} ({status})")
        return project_dashboard

    def generate_integrated(self, spec_updaters: list, project_configs: list):
        """
        Generates an integrated dashboard for multiple projects.
        """
        logging.info("Generating integrated dashboard...")

        print("\n" + "="*30)
        print("=== INTEGRATED DASHBOARD ===")
        print("="*30)

        for i, updater in enumerate(spec_updaters):
            project_name = project_configs[i].get("name", f"Project {i+1}")
            print(f"\n--- Project: {project_name} ---")

            data = self._get_project_data(updater)

            print("  ✅ Approved Specs:")
            if data["Approved"]:
                for item in data["Approved"]:
                    print(f"    - {item}")
            else:
                print("    (None)")

            print("  📝 Draft Specs:")
            if data["Draft"]:
                for item in data["Draft"]:
                    print(f"    - {item}")
            else:
                print("    (None)")

            if data["Other"]:
                print("  📊 Other Statuses:")
                for item in data["Other"]:
                    print(f"    - {item}")

        print("\n" + "="*30)
        logging.info("Integrated dashboard generation complete.")
