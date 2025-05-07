from geopy.distance import distance
from geopy.point import Point
from geopy.geocoders import Nominatim
from clipboard import copy

origin = Point(36.0218624, 129.3123584)

def main(bearings):
    geolocator = Nominatim(user_agent="geo_query")
    for bearing in bearings:
        print(f'{bearing = }')
        new_location = distance(miles=6815.600826213392).destination(origin, bearing=bearing)
        location = geolocator.reverse((new_location.latitude, new_location.longitude), language="en")
        if location and location.raw.get("address"):
            address = location.raw["address"]
            road = address.get("road")
            city = address.get("city") or address.get("town") or address.get("village")
            postcode = address.get("postcode")
            addition = location.address.split(', ')
            if addition[0].isdigit():
                road = addition[0] + ' ' + road
            elif addition[1].isdigit():
                road = addition[1] + ' ' + road
            if road is not None and city is not None and postcode is not None and 'Texas' in location.address:
                print(f'{bearing} ->', f'{new_location.latitude}, {new_location.longitude}', end=' ')
                print(location.address, end=' ')
                print("utflag{"+f"{road}-{city}-{postcode}".lower().replace(' ', '-')+"}")
                input()