import pytest
import requests

from mooch.exceptions import LocationError
from mooch.utils.location import Location


def test_zip_to_city_state_success(monkeypatch):
    class MockResponse:
        status_code = 200

        def json(self):
            return {
                "country": "United States",
                "country abbreviation": "US",
                "post code": "62704",
                "places": [
                    {
                        "place name": "Springfield",
                        "longitude": "-89.6889",
                        "latitude": "39.7725",
                        "state": "Illinois",
                        "state abbreviation": "IL",
                    },
                ],
            }

    def mock_get(url, timeout):
        assert url == "https://api.zippopotam.us/us/62704"
        assert timeout == 5
        return MockResponse()

    monkeypatch.setattr(requests, "get", mock_get)
    location = Location(62704).load()
    assert location.city == "Springfield"
    assert location.state == "Illinois"
    assert location.state_abbreviation == "IL"
    assert location.latitude == "39.7725"
    assert location.longitude == "-89.6889"


def test_zip_to_city_state_failure_status(monkeypatch):
    class MockResponse:
        status_code = 404

    def mock_get(url, timeout):
        return MockResponse()

    monkeypatch.setattr(requests, "get", mock_get)
    with pytest.raises(LocationError) as excinfo:
        location = Location(99999).load()
    assert "Invalid zip code 99999." in str(excinfo.value)


def test_zip_to_city_state_request_timeout(monkeypatch):
    def mock_get(url, timeout):
        raise requests.Timeout("Request timed out")

    monkeypatch.setattr(requests, "get", mock_get)
    with pytest.raises(requests.Timeout):
        location = Location(90210).load()
