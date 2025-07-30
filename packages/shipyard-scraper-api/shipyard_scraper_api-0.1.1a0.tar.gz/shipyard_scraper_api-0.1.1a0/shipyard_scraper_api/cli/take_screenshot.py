import requests
import os
import pandas as pd
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed


def scrape_target(name, url, country, device, timestamp, api_key):
    print(f"Scraping {name} [{country}] on {device}...")

    payload = {
        "api_key": api_key,
        "url": url,
        "screenshot": "true",
        "device_type": device,
        "render": "true",
        "keep_headers": "true",
        "ultra_premium": "true",
        "output_format": "json",
    }

    try:
        response = requests.get("https://api.scraperapi.com/", params=payload)
        response.raise_for_status()

        screenshot_url = response.headers.get("sa-screenshot")
        if not screenshot_url:
            raise ValueError("No screenshot URL found in headers.")

        img_response = requests.get(screenshot_url)
        img_response.raise_for_status()

        sanitized_name = name.replace(" ", "_")
        img_filename = f"{sanitized_name}_{country}_{device}_screenshot_{timestamp}.png"
        with open(img_filename, "wb") as f:
            f.write(img_response.content)
        print(f"✔ Screenshot saved to {img_filename}")

    except requests.exceptions.RequestException as e:
        print(f"❌ Request error for {name} ({device}, {country}): {e}")
    except ValueError as ve:
        print(f"❌ Parsing error for {name} ({device}, {country}): {ve}")
    except Exception as e:
        print(f"❌ Unexpected error for {name} ({device}, {country}): {e}")


def screenscraper_from_csv(input_file):
    api_key = os.getenv("SCRAPER_API_TOKEN")
    if not api_key:
        raise ValueError("Missing required environment variable: SCRAPER_API_TOKEN")

    df = pd.read_csv(input_file)
    timestamp = datetime.now().strftime("%Y%m%d")
    devices = ["desktop", "mobile"]

    # Deduplicate using (name, url, country)
    unique_targets = set()
    for _, row in df.iterrows():
        unique_targets.add((row["Client"], row["Client_URL"], row["Country"]))
        unique_targets.add((row["Competitor"], row["Competitor_URL"], row["Country"]))

    # Prepare all jobs
    jobs = []
    for name, url, country in unique_targets:
        for device in devices:
            jobs.append((name, url, country, device, timestamp, api_key))

    # Run in parallel using threads
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = [executor.submit(scrape_target, *job) for job in jobs]
        for future in as_completed(futures):
            _ = future.result()  # trigger exception if any


if __name__ == "__main__":
    INPUT_FILE = os.getenv("INPUT_FILE")
    if not INPUT_FILE:
        raise ValueError("Missing INPUT_FILE environment variable.")
    screenscraper_from_csv(INPUT_FILE)
