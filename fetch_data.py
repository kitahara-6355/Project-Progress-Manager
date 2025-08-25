import os
import json
from config import DATA_DIR
import logging

def ensure_data_dir():
    """Ensures the data directory exists."""
    os.makedirs(DATA_DIR, exist_ok=True)

def fetch_html_txt_files():
    """
    Reads all .html and .txt files from the DATA_DIR.
    """
    ensure_data_dir()
    sources = []
    logging.info(f"Fetching files from '{DATA_DIR}' directory...")
    try:
        for file_name in os.listdir(DATA_DIR):
            if file_name.endswith((".html", ".txt")):
                try:
                    with open(os.path.join(DATA_DIR, file_name), 'r', encoding='utf-8') as f:
                        content = f.read()
                    sources.append({"file": file_name, "content": content})
                    logging.info(f"  - Successfully read {file_name}")
                except Exception as e:
                    logging.error(f"  - Failed to read {file_name}: {e}")
    except Exception as e:
        logging.error(f"Could not read from data directory '{DATA_DIR}': {e}")
    return sources

def save_json(data, filename):
    """Saves the given data structure as a JSON file."""
    ensure_data_dir()
    filepath = os.path.join(DATA_DIR, filename)
    logging.info(f"Saving JSON data to '{filepath}'...")
    try:
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        logging.info("  - Save successful.")
    except Exception as e:
        logging.error(f"  - Failed to save JSON to {filepath}: {e}")

def main():
    """
    Main function for this module. Fetches data, processes it,
    and saves the results as JSON files.
    """
    sources = fetch_html_txt_files()
    save_json(sources, "imported_sources.json")

    # Simple domain aggregation example
    domain_count = {}
    for s in sources:
        # A simple way to get a "domain" from a filename like "projectA_feature.html"
        domain = s["file"].split("_")[0]
        domain_count[domain] = domain_count.get(domain, 0) + 1

    top20 = sorted(domain_count.items(), key=lambda x: x[1], reverse=True)[:20]
    save_json(top20, "top20_domains.json")

    return sources, top20

if __name__ == "__main__":
    # This allows running the data fetching process independently for testing.
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    main()
