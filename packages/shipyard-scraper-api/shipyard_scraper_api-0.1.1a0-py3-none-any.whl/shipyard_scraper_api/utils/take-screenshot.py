import argparse
import os
import sys
from datetime import datetime

import requests
from shipyard_templates import ShipyardLogger, ExitCodeException, Messaging
from scraper_api.scraper_api import ScraperAPI  # adjust if needed

logger = ShipyardLogger().get_logger()


def get_args():
    parser = argparse.ArgumentParser(
        description="Take a screenshot of a webpage using ScraperAPI."
    )
    parser.add_argument(
        "--output",
        type=str,
        required=True,
        help="Base output path for the screenshot image (no extension)",
    )
    return parser.parse_args()


def take_screenshot(scraper: ScraperAPI, output_base: str):
    """
    Takes desktop and mobile screenshots using ScraperAPI and saves them to output_base.
    """
    timestamp = datetime.now().strftime("%Y%m%d")

    for device in ["desktop", "mobile"]:
        logger.debug(f"Taking {device} screenshot of {scraper.target_url}...")

        payload = {
            "api_key": scraper.api_key,
            "url": scraper.target_url,
            "screenshot": "true",
            "device_type": device,
            "render": "true",
            "keep_headers": "true",
            "ultra_premium": "false",
            "output_format": "json",
        }

        try:
            response = requests.get(scraper.API_ENDPOINT, params=payload)
            response.raise_for_status()
            data = response.json()

            screenshot_url = data.get("sa-screenshot")
            if not screenshot_url:
                raise ExitCodeException(
                    f"No screenshot URL returned for {device} device.",
                    scraper.EXIT_CODE_SCRAPE_FAILED,
                )

            img_response = requests.get(screenshot_url)
            img_response.raise_for_status()

            output_file = f"{output_base}_{device}_{timestamp}.png"
            with open(output_file, "wb") as f:
                f.write(img_response.content)

            logger.success(f"Saved {device} screenshot to {output_file}")

        except requests.RequestException as e:
            logger.error(f"Request failed while scraping {device}: {e}")
            raise ExitCodeException(str(e), scraper.EXIT_CODE_SCRAPE_FAILED)


def main():
    try:
        args = get_args()
        scraper = ScraperAPI()

        if scraper.connect() != 0:
            raise ExitCodeException(
                "Could not authenticate with ScraperAPI",
                scraper.EXIT_CODE_INVALID_CREDENTIALS,
            )

        take_screenshot(scraper, args.output)

    except ExitCodeException as e:
        logger.error(e)
        sys.exit(e.exit_code)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        sys.exit(Messaging.EXIT_CODE_UNKNOWN_ERROR)
    else:
        logger.info("Screenshots captured successfully.")


if __name__ == "__main__":
    main()
