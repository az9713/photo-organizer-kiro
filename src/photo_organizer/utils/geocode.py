"""
Utility for geocoding coordinates.
"""

import argparse
import sys
from pathlib import Path

from photo_organizer.services.geolocation import (
    GeocodingError,
    MockGeocodingService,
    NominatimGeocodingService,
)


def geocode_coordinates(latitude: float, longitude: float, use_mock: bool = False) -> None:
    """
    Geocode coordinates and print the result.
    
    Args:
        latitude: The latitude coordinate
        longitude: The longitude coordinate
        use_mock: Whether to use the mock geocoding service
    """
    # Create the appropriate geocoding service
    if use_mock:
        service = MockGeocodingService()
    else:
        service = NominatimGeocodingService()
    
    try:
        # Reverse geocode the coordinates
        location = service.reverse_geocode(latitude, longitude)
        
        print(f"Geocoding results for ({latitude}, {longitude}):")
        print("-" * 40)
        
        # Print the address components
        if location.street:
            print(f"Street: {location.street}")
        
        if location.city:
            print(f"City: {location.city}")
        
        if location.postal_code:
            print(f"Postal Code: {location.postal_code}")
        
        if location.country:
            print(f"Country: {location.country}")
        
        # Print the institution name
        institution_name = service.get_institution_name(latitude, longitude)
        if institution_name:
            print(f"Institution: {institution_name}")
        
        # Print the formatted address
        print(f"Formatted Address: {location.formatted_address}")
    
    except GeocodingError as e:
        print(f"Error: {e}")


def main() -> int:
    """Main entry point for the geocoding utility."""
    parser = argparse.ArgumentParser(description="Geocode coordinates")
    parser.add_argument("latitude", type=float, help="Latitude coordinate")
    parser.add_argument("longitude", type=float, help="Longitude coordinate")
    parser.add_argument("--mock", action="store_true", help="Use mock geocoding service")
    
    args = parser.parse_args()
    
    geocode_coordinates(args.latitude, args.longitude, args.mock)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())