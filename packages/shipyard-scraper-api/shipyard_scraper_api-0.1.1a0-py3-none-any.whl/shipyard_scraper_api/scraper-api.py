import os
import requests
from datetime import datetime

from shipyard_templates import Messaging, ShipyardLogger, ExitCodeException

logger = ShipyardLogger().get_logger()


class ScraperAPI(Messaging):
    """
    A client for interacting with ScraperAPI to perform web scraping
    tasks such as rendering pages and fetching HTML responses.
    """

    API_ENDPOINT = "https://api.scraperapi.com/"
    EXIT_CODE_INVALID_CREDENTIALS = 100
    EXIT_CODE_SCRAPE_FAILED = 101

    def __init__(self):
        self.target_url = os.getenv("SCRAPE_TARGET_URL")
        self.client_slug = os.getenv("ALLI_CLIENT_SLUG")
        self.api_key = os.getenv("SCRAPER_API_TOKEN")
        self.timestamp = datetime.now().strftime("%Y%m%d")

        if not all([self.target_url, self.client_slug, self.api_key]):
            raise ExitCodeException(
                "Missing one or more required environment variables: "
                "SCRAPE_TARGET_URL, ALLI_CLIENT_SLUG, SCRAPER_API_TOKEN",
                self.EXIT_CODE_INVALID_CREDENTIALS,
            )

    def connect(self) -> int:
        """
        Test ScraperAPI credentials by making a basic request.

        Returns:
            int: 0 if connection is successful, 1 otherwise.
        """
        test_payload = {
            "api_key": self.api_key,
            "url": "https://example.com",
            "render": "false",
            "output_format": "json",
        }

        try:
            response = requests.get(self.API_ENDPOINT, params=test_payload)
            response.raise_for_status()
            logger.authtest("Successfully connected to ScraperAPI")
            return 0
        except requests.RequestException as e:
            logger.authtest(f"Failed to connect to ScraperAPI: {e}")
            return 1

    def scrape(self) -> None:
        """
        Performs a scrape using ScraperAPI for both desktop and mobile user agents.
        Saves the raw JSON response to disk.
        """
        devices = ["desktop", "mobile"]

        for device in devices:
            logger.debug(f"Scraping {device} version of {self.target_url}...")

            payload = {
                "api_key": self.api_key,
                "url": self.target_url,
                "device_type": device,
                "render": "true",
                "keep_headers": "true",
                "ultra_premium": "false",
                "output_format": "json",
            }

            try:
                response = requests.get(self.API_ENDPOINT, params=payload)
                response.raise_for_status()

                json_filename = (
                    f"{self.client_slug}_{device}_scrape_{self.timestamp}.json"
                )
                with open(json_filename, "w", encoding="utf-8") as f:
                    f.write(response.text)

                logger.success(f"Scraped {device} version and saved to {json_filename}")

            except requests.RequestException as e:
                logger.error(f"Request failed for {device} scrape: {e}")
                raise ExitCodeException(
                    f"Scraping failed for {device} version",
                    self.EXIT_CODE_SCRAPE_FAILED,
                )
