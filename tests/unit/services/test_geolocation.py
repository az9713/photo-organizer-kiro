"""
Unit tests for the geolocation service.
"""

import json
from pathlib import Path
from unittest.mock import MagicMock, mock_open, patch

import pytest

from photo_organizer.models.image import GeoLocation
from photo_organizer.services.geolocation import (
    GeocodingError,
    MockGeocodingService,
    NominatimGeocodingService,
)


class TestNominatimGeocodingService:
    """Tests for the NominatimGeocodingService class."""

    def test_init(self, tmp_path) -> None:
        """Test initializing the service."""
        # Test with default parameters
        service = NominatimGeocodingService()
        assert service.user_agent == "PhotoOrganizer/1.0"
        assert service.cache_dir is None
        assert service.cache == {}
        
        # Test with custom parameters
        cache_dir = tmp_path / "cache"
        service = NominatimGeocodingService(user_agent="TestAgent", cache_dir=cache_dir)
        assert service.user_agent == "TestAgent"
        assert service.cache_dir == cache_dir
        assert service.cache == {}
        assert cache_dir.exists()

    def test_reverse_geocode(self) -> None:
        """Test reverse geocoding coordinates."""
        service = NominatimGeocodingService()
        
        # Mock the urlopen response
        mock_response = {
            "address": {
                "road": "Pennsylvania Ave NW",
                "house_number": "1600",
                "city": "Washington",
                "postcode": "20500",
                "country": "United States",
                "amenity": "The White House"
            },
            "display_name": "The White House, 1600 Pennsylvania Ave NW, Washington, DC 20500, United States"
        }
        
        with patch("urllib.request.urlopen") as mock_urlopen:
            mock_urlopen.return_value.read.return_value = json.dumps(mock_response).encode()
            
            location = service.reverse_geocode(38.8977, -77.0365)
            
            assert location.latitude == 38.8977
            assert location.longitude == -77.0365
            assert location.street == "1600 Pennsylvania Ave NW"
            assert location.city == "Washington"
            assert location.postal_code == "20500"
            assert location.country == "United States"
            assert location.institution_name == "The White House"

    def test_reverse_geocode_cache(self, tmp_path) -> None:
        """Test reverse geocoding with cache."""
        cache_dir = tmp_path / "cache"
        service = NominatimGeocodingService(cache_dir=cache_dir)
        
        # Mock the urlopen response
        mock_response = {
            "address": {
                "road": "Pennsylvania Ave NW",
                "house_number": "1600",
                "city": "Washington",
                "postcode": "20500",
                "country": "United States",
                "amenity": "The White House"
            }
        }
        
        # First call should make a request
        with patch("urllib.request.urlopen") as mock_urlopen:
            mock_urlopen.return_value.read.return_value = json.dumps(mock_response).encode()
            
            location1 = service.reverse_geocode(38.8977, -77.0365)
            
            # Check that the request was made
            assert mock_urlopen.called
        
        # Second call should use the cache
        with patch("urllib.request.urlopen") as mock_urlopen:
            location2 = service.reverse_geocode(38.8977, -77.0365)
            
            # Check that no request was made
            assert not mock_urlopen.called
            
            # Check that the results are the same
            assert location1.street == location2.street
            assert location1.city == location2.city

    def test_reverse_geocode_file_cache(self, tmp_path) -> None:
        """Test reverse geocoding with file cache."""
        cache_dir = tmp_path / "cache"
        service = NominatimGeocodingService(cache_dir=cache_dir)
        
        # Mock the urlopen response
        mock_response = {
            "address": {
                "road": "Pennsylvania Ave NW",
                "house_number": "1600",
                "city": "Washington",
                "postcode": "20500",
                "country": "United States",
                "amenity": "The White House"
            }
        }
        
        # First call should make a request and save to cache
        with patch("urllib.request.urlopen") as mock_urlopen:
            mock_urlopen.return_value.read.return_value = json.dumps(mock_response).encode()
            
            service.reverse_geocode(38.8977, -77.0365)
            
            # Check that the cache file was created
            cache_file = cache_dir / "38.8977_-77.0365.json"
            assert cache_file.exists()
        
        # Create a new service instance (to clear the in-memory cache)
        service2 = NominatimGeocodingService(cache_dir=cache_dir)
        
        # Second call should use the file cache
        with patch("urllib.request.urlopen") as mock_urlopen:
            location = service2.reverse_geocode(38.8977, -77.0365)
            
            # Check that no request was made
            assert not mock_urlopen.called
            
            # Check that the results are correct
            assert location.street == "1600 Pennsylvania Ave NW"
            assert location.city == "Washington"

    def test_reverse_geocode_error(self) -> None:
        """Test reverse geocoding with an error."""
        service = NominatimGeocodingService()
        
        # Mock urlopen to raise an exception
        with patch("urllib.request.urlopen", side_effect=Exception("Test error")):
            with pytest.raises(GeocodingError) as excinfo:
                service.reverse_geocode(38.8977, -77.0365)
            
            assert "Failed to reverse geocode" in str(excinfo.value)

    def test_parse_nominatim_response(self) -> None:
        """Test parsing a Nominatim response."""
        service = NominatimGeocodingService()
        
        # Test with a complete response
        response = {
            "address": {
                "road": "Pennsylvania Ave NW",
                "house_number": "1600",
                "city": "Washington",
                "postcode": "20500",
                "country": "United States",
                "amenity": "The White House"
            },
            "display_name": "The White House, 1600 Pennsylvania Ave NW, Washington, DC 20500, United States"
        }
        
        location = service._parse_nominatim_response(response, 38.8977, -77.0365)
        
        assert location.latitude == 38.8977
        assert location.longitude == -77.0365
        assert location.street == "1600 Pennsylvania Ave NW"
        assert location.city == "Washington"
        assert location.postal_code == "20500"
        assert location.country == "United States"
        assert location.institution_name == "The White House"
        
        # Test with a minimal response
        response = {
            "address": {
                "road": "Pennsylvania Ave NW"
            }
        }
        
        location = service._parse_nominatim_response(response, 38.8977, -77.0365)
        
        assert location.latitude == 38.8977
        assert location.longitude == -77.0365
        assert location.street == "Pennsylvania Ave NW"
        assert location.city is None
        assert location.postal_code is None
        assert location.country is None
        assert location.institution_name is None
        
        # Test with an empty response
        response = {}
        
        location = service._parse_nominatim_response(response, 38.8977, -77.0365)
        
        assert location.latitude == 38.8977
        assert location.longitude == -77.0365
        assert location.street is None
        assert location.city is None
        assert location.postal_code is None
        assert location.country is None
        assert location.institution_name is None

    def test_get_institution_name(self) -> None:
        """Test getting an institution name."""
        service = NominatimGeocodingService()
        
        # Mock reverse_geocode to return a location with an institution name
        location = GeoLocation(
            latitude=38.8977,
            longitude=-77.0365,
            institution_name="The White House"
        )
        
        with patch.object(service, "reverse_geocode", return_value=location):
            name = service.get_institution_name(38.8977, -77.0365)
            assert name == "The White House"
        
        # Mock reverse_geocode to return a location without an institution name
        location = GeoLocation(
            latitude=38.8977,
            longitude=-77.0365
        )
        
        # Mock _find_nearby_poi to return a name
        with patch.object(service, "reverse_geocode", return_value=location), \
             patch.object(service, "_find_nearby_poi", return_value="Nearby POI"):
            name = service.get_institution_name(38.8977, -77.0365)
            assert name == "Nearby POI"
        
        # Mock reverse_geocode to raise an exception
        with patch.object(service, "reverse_geocode", side_effect=GeocodingError("Test error")):
            name = service.get_institution_name(38.8977, -77.0365)
            assert name is None

    def test_find_nearby_poi(self) -> None:
        """Test finding a nearby POI."""
        service = NominatimGeocodingService()
        
        # Mock the urlopen response
        mock_response = {
            "elements": [
                {
                    "tags": {"name": "The White House"},
                    "lat": 38.8977,
                    "lon": -77.0365
                },
                {
                    "tags": {"name": "Washington Monument"},
                    "lat": 38.8895,
                    "lon": -77.0353
                }
            ]
        }
        
        with patch("urllib.request.urlopen") as mock_urlopen:
            mock_urlopen.return_value.read.return_value = json.dumps(mock_response).encode()
            
            name = service._find_nearby_poi(38.8977, -77.0365)
            assert name == "The White House"
        
        # Test with no results
        mock_response = {"elements": []}
        
        with patch("urllib.request.urlopen") as mock_urlopen:
            mock_urlopen.return_value.read.return_value = json.dumps(mock_response).encode()
            
            name = service._find_nearby_poi(38.8977, -77.0365)
            assert name is None
        
        # Test with an error
        with patch("urllib.request.urlopen", side_effect=Exception("Test error")):
            name = service._find_nearby_poi(38.8977, -77.0365)
            assert name is None

    def test_haversine_distance(self) -> None:
        """Test calculating the haversine distance."""
        service = NominatimGeocodingService()
        
        # Test with the same point
        distance = service._haversine_distance(38.8977, -77.0365, 38.8977, -77.0365)
        assert distance == 0
        
        # Test with different points
        # The White House to the Washington Monument is about 1km
        distance = service._haversine_distance(38.8977, -77.0365, 38.8895, -77.0353)
        assert 900 < distance < 1100


class TestMockGeocodingService:
    """Tests for the MockGeocodingService class."""

    def test_init(self) -> None:
        """Test initializing the service."""
        service = MockGeocodingService()
        assert len(service.mock_data) > 0

    def test_reverse_geocode_known_location(self) -> None:
        """Test reverse geocoding a known location."""
        service = MockGeocodingService()
        
        # Test with the White House coordinates
        location = service.reverse_geocode(38.8977, -77.0365)
        
        assert location.latitude == 38.8977
        assert location.longitude == -77.0365
        assert location.street == "1600 Pennsylvania Ave NW"
        assert location.city == "Washington"
        assert location.postal_code == "20500"
        assert location.country == "United States"
        assert location.institution_name == "The White House"

    def test_reverse_geocode_unknown_location(self) -> None:
        """Test reverse geocoding an unknown location."""
        service = MockGeocodingService()
        
        # Test with coordinates far from any known location
        location = service.reverse_geocode(0, 0)
        
        assert location.latitude == 0
        assert location.longitude == 0
        assert location.street == "Unknown Street"
        assert location.city == "Unknown City"
        assert location.country == "Unknown Country"
        assert location.institution_name is None

    def test_get_institution_name(self) -> None:
        """Test getting an institution name."""
        service = MockGeocodingService()
        
        # Test with the White House coordinates
        name = service.get_institution_name(38.8977, -77.0365)
        assert name == "The White House"
        
        # Test with coordinates far from any known location
        name = service.get_institution_name(0, 0)
        assert name is None