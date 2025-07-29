from geopy.geocoders import Nominatim
from geopy.distance import geodesic

def calculate_distance(lat1, lon1, lat2, lon2):
    return geodesic((lat1, lon1), (lat2, lon2)).km

def get_location(address):
    geolocator = Nominatim(user_agent="fr8")
    location = geolocator.geocode(address)
    return location

def fr8_location(address):
    location = get_location(address)
    fr8 = get_location("Otaranta 4, 02150 Espoo")
    return calculate_distance(location.latitude, location.longitude, fr8.latitude, fr8.longitude)