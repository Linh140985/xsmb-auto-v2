import cloudscraper

import fetch_xsmb


class ScraperAdapter:
    def __init__(self):
        self._client = cloudscraper.create_scraper(
            browser={'browser': 'chrome', 'platform': 'windows', 'mobile': False}
        )

    def get(self, *args, **kwargs):
        return self._client.get(*args, **kwargs)


fetch_xsmb.requests = ScraperAdapter()
fetch_xsmb.main()
