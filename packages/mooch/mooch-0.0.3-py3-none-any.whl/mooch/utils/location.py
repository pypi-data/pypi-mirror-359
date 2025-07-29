from __future__ import annotations

import requests

from mooch.exceptions import LocationError


class Location:
    def __init__(self, zip_code: int) -> None:
        """Initialize the Location class by providing a zip code."""
        self.zip_code = zip_code
        self.city = None
        self.state = None
        self.state_abbreviation = None
        self.latitude = None
        self.longitude = None

    def load(self) -> None:
        """Load the location data based on the provided zip code."""
        url = f"https://api.zippopotam.us/us/{self.zip_code}"
        res = requests.get(url, timeout=5)

        if res.status_code != 200:  # noqa: PLR2004
            message = f"Invalid zip code {self.zip_code}."
            raise LocationError(message)

        data = res.json()
        self.city = data["places"][0]["place name"]
        self.state = data["places"][0]["state"]
        self.state_abbreviation = data["places"][0]["state abbreviation"]
        self.latitude = data["places"][0]["latitude"]
        self.longitude = data["places"][0]["longitude"]
        return self
