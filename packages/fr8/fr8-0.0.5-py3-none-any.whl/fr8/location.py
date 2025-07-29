from geopy.geocoders import Nominatim
from geopy.distance import geodesic
from geopy.exc import GeocoderTimedOut

def calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    return geodesic((lat1, lon1), (lat2, lon2)).km

def get_location(address: str) -> tuple[float, float]:
    geolocator = Nominatim(user_agent="fr8")
    location = geolocator.geocode(address)
    return location

def fr8_location(address: str) -> float:
    try:
        location = get_location(address)
    except GeocoderTimedOut:
        return "address not found"
    fr8 = get_location("Otaranta 4, 02150 Espoo")
    return calculate_distance(location.latitude, location.longitude, fr8.latitude, fr8.longitude)