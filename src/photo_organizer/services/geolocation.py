"""
Geolocation processing service for reverse geocoding coordinates.
"""

from __future__ import annotations

import json
import time
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, Optional, Tuple
from urllib.error import URLError
from urllib.parse import urlencode
from urllib.request import urlopen

from photo_organizer.models.image import GeoLocation


class GeocodingError(Exception):
    """Exception raised for geocoding errors."""
    pass


class GeocodingService(ABC):
    """
    Abstract base class for geocoding services.
    """
    
    @abstractmethod
    def reverse_geocode(self, latitude: float, longitude: float) -> GeoLocation:
        """
        Convert coordinates to an address.
        
        Args:
            latitude: The latitude coordinate
            longitude: The longitude coordinate
            
        Returns:
            A GeoLocation object with address information
        """
        pass
    
    @abstractmethod
    def get_institution_name(self, latitude: float, longitude: float) -> Optional[str]:
        """
        Get the name of an institution at the given coordinates, if available.
        
        Args:
            latitude: The latitude coordinate
            longitude: The longitude coordinate
            
        Returns:
            The name of the institution, or None if not available
        """
        pass


class NominatimGeocodingService(GeocodingService):
    """
    Geocoding service implementation using Nominatim (OpenStreetMap).
    """
    
    def __init__(self, user_agent: str = "PhotoOrganizer/1.0", cache_dir: Optional[Path] = None) -> None:
        """
        Initialize the NominatimGeocodingService.
        
        Args:
            user_agent: The user agent to use for requests
            cache_dir: Directory to cache geocoding results
        """
        self.user_agent = user_agent
        self.cache_dir = cache_dir
        self.cache: Dict[str, Dict] = {}
        
        # Create cache directory if specified
        if cache_dir:
            cache_dir.mkdir(parents=True, exist_ok=True)
    
    def reverse_geocode(self, latitude: float, longitude: float) -> GeoLocation:
        """
        Convert coordinates to an address using Nominatim.
        
        Args:
            latitude: The latitude coordinate
            longitude: The longitude coordinate
            
        Returns:
            A GeoLocation object with address information
        """
        # Check cache first
        cache_key = f"{latitude},{longitude}"
        if cache_key in self.cache:
            return self._parse_nominatim_response(self.cache[cache_key], latitude, longitude)
        
        # Check file cache if enabled
        if self.cache_dir:
            cache_file = self.cache_dir / f"{cache_key.replace(',', '_')}.json"
            if cache_file.exists():
                try:
                    with open(cache_file, "r") as f:
                        data = json.load(f)
                        self.cache[cache_key] = data
                        return self._parse_nominatim_response(data, latitude, longitude)
                except (json.JSONDecodeError, IOError):
                    # If cache file is invalid, continue with API request
                    pass
        
        # Build the request URL
        params = {
            "format": "json",
            "lat": str(latitude),
            "lon": str(longitude),
            "zoom": "18",  # Highest zoom level for most detailed information
            "addressdetails": "1"
        }
        
        url = f"https://nominatim.openstreetmap.org/reverse?{urlencode(params)}"
        
        try:
            # Make the request
            headers = {"User-Agent": self.user_agent}
            request = urlopen(url, timeout=10)
            response = request.read()
            
            # Parse the response
            data = json.loads(response)
            
            # Cache the result
            self.cache[cache_key] = data
            
            # Save to file cache if enabled
            if self.cache_dir:
                try:
                    with open(cache_file, "w") as f:
                        json.dump(data, f)
                except IOError:
                    # If saving to cache fails, just continue
                    pass
            
            return self._parse_nominatim_response(data, latitude, longitude)
        
        except (URLError, json.JSONDecodeError, KeyError) as e:
            raise GeocodingError(f"Failed to reverse geocode coordinates ({latitude}, {longitude}): {e}")
    
    def get_institution_name(self, latitude: float, longitude: float) -> Optional[str]:
        """
        Get the name of an institution at the given coordinates, if available.
        
        Args:
            latitude: The latitude coordinate
            longitude: The longitude coordinate
            
        Returns:
            The name of the institution, or None if not available
        """
        try:
            # Try to reverse geocode the coordinates
            location = self.reverse_geocode(latitude, longitude)
            
            # Check if we already have an institution name
            if location.institution_name:
                return location.institution_name
            
            # Otherwise, try to find a POI (Point of Interest) nearby
            return self._find_nearby_poi(latitude, longitude)
        
        except GeocodingError:
            return None
    
    def _parse_nominatim_response(self, data: Dict, latitude: float, longitude: float) -> GeoLocation:
        """
        Parse a Nominatim response into a GeoLocation object.
        
        Args:
            data: The Nominatim response data
            latitude: The original latitude coordinate
            longitude: The original longitude coordinate
            
        Returns:
            A GeoLocation object with address information
        """
        # Create a GeoLocation object with the coordinates
        location = GeoLocation(latitude=latitude, longitude=longitude)
        
        # Extract address components
        if "address" in data:
            address = data["address"]
            
            # Street address (road + house number if available)
            road = address.get("road") or address.get("pedestrian") or address.get("footway")
            house_number = address.get("house_number", "")
            if road and house_number:
                location.street = f"{house_number} {road}"
            elif road:
                location.street = road
            
            # City (try different fields that might contain the city name)
            location.city = (
                address.get("city") or
                address.get("town") or
                address.get("village") or
                address.get("hamlet") or
                address.get("suburb")
            )
            
            # Postal code
            location.postal_code = address.get("postcode")
            
            # Country
            location.country = address.get("country")
            
            # Try to find an institution name
            location.institution_name = (
                address.get("amenity") or
                address.get("tourism") or
                address.get("leisure") or
                address.get("building") or
                address.get("historic") or
                address.get("shop") or
                address.get("office")
            )
            
            # If the display_name field contains a more specific name, use it
            if "display_name" in data and not location.institution_name:
                display_parts = data["display_name"].split(",")
                if display_parts and len(display_parts[0].strip()) > 0:
                    location.institution_name = display_parts[0].strip()
        
        return location
    
    def _find_nearby_poi(self, latitude: float, longitude: float) -> Optional[str]:
        """
        Find a nearby point of interest.
        
        Args:
            latitude: The latitude coordinate
            longitude: The longitude coordinate
            
        Returns:
            The name of the POI, or None if not found
        """
        # Build the request URL for the Overpass API
        # This query finds the nearest named feature within 100 meters
        query = f"""
        [out:json];
        (
          node["name"](around:100,{latitude},{longitude});
          way["name"](around:100,{latitude},{longitude});
          relation["name"](around:100,{latitude},{longitude});
        );
        out center;
        """
        
        params = {
            "data": query
        }
        
        url = f"https://overpass-api.de/api/interpreter?{urlencode(params)}"
        
        try:
            # Make the request
            headers = {"User-Agent": self.user_agent}
            request = urlopen(url, timeout=10)
            response = request.read()
            
            # Parse the response
            data = json.loads(response)
            
            # Find the closest feature with a name
            closest_distance = float("inf")
            closest_name = None
            
            for element in data.get("elements", []):
                if "name" in element.get("tags", {}):
                    name = element["tags"]["name"]
                    
                    # Calculate distance
                    if "lat" in element and "lon" in element:
                        element_lat = element["lat"]
                        element_lon = element["lon"]
                    elif "center" in element:
                        element_lat = element["center"]["lat"]
                        element_lon = element["center"]["lon"]
                    else:
                        continue
                    
                    distance = self._haversine_distance(
                        latitude, longitude, element_lat, element_lon
                    )
                    
                    if distance < closest_distance:
                        closest_distance = distance
                        closest_name = name
            
            return closest_name
        
        except (URLError, json.JSONDecodeError, KeyError):
            # If the request fails, just return None
            return None
    
    def _haversine_distance(
        self, lat1: float, lon1: float, lat2: float, lon2: float
    ) -> float:
        """
        Calculate the great-circle distance between two points.
        
        Args:
            lat1: Latitude of the first point
            lon1: Longitude of the first point
            lat2: Latitude of the second point
            lon2: Longitude of the second point
            
        Returns:
            The distance in meters
        """
        from math import asin, cos, radians, sin, sqrt
        
        # Convert decimal degrees to radians
        lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
        
        # Haversine formula
        dlon = lon2 - lon1
        dlat = lat2 - lat1
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * asin(sqrt(a))
        r = 6371000  # Radius of Earth in meters
        
        return c * r


class MockGeocodingService(GeocodingService):
    """
    Mock geocoding service for testing.
    """
    
    def __init__(self) -> None:
        """Initialize the MockGeocodingService."""
        self.mock_data = {
            # White House
            (38.8977, -77.0365): GeoLocation(
                latitude=38.8977,
                longitude=-77.0365,
                street="1600 Pennsylvania Ave NW",
                city="Washington",
                postal_code="20500",
                country="United States",
                institution_name="The White House"
            ),
            # Eiffel Tower
            (48.8584, 2.2945): GeoLocation(
                latitude=48.8584,
                longitude=2.2945,
                street="Champ de Mars, 5 Avenue Anatole France",
                city="Paris",
                postal_code="75007",
                country="France",
                institution_name="Eiffel Tower"
            ),
            # Sydney Opera House
            (-33.8568, 151.2153): GeoLocation(
                latitude=-33.8568,
                longitude=151.2153,
                street="Bennelong Point",
                city="Sydney",
                postal_code="2000",
                country="Australia",
                institution_name="Sydney Opera House"
            )
        }
    
    def reverse_geocode(self, latitude: float, longitude: float) -> GeoLocation:
        """
        Convert coordinates to an address using mock data.
        
        Args:
            latitude: The latitude coordinate
            longitude: The longitude coordinate
            
        Returns:
            A GeoLocation object with address information
        """
        # Find the closest mock location
        closest_location = None
        closest_distance = float("inf")
        
        for coords, location in self.mock_data.items():
            mock_lat, mock_lon = coords
            distance = abs(latitude - mock_lat) + abs(longitude - mock_lon)
            
            if distance < closest_distance:
                closest_distance = distance
                closest_location = location
        
        # If we found a close enough match, return it
        if closest_distance < 0.1 and closest_location:
            return closest_location
        
        # Otherwise, return a generic location
        return GeoLocation(
            latitude=latitude,
            longitude=longitude,
            street="Unknown Street",
            city="Unknown City",
            country="Unknown Country"
        )
    
    def get_institution_name(self, latitude: float, longitude: float) -> Optional[str]:
        """
        Get the name of an institution at the given coordinates, if available.
        
        Args:
            latitude: The latitude coordinate
            longitude: The longitude coordinate
            
        Returns:
            The name of the institution, or None if not available
        """
        location = self.reverse_geocode(latitude, longitude)
        return location.institution_name