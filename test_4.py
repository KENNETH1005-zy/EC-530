import math
import pandas as pd
import re
import json


# Haversine formula to calculate the great-circle distance
def haversine_distance(lat1, lon1, lat2, lon2):
    lat1, lon1, lat2, lon2 = map(math.radians, [float(lat1), float(lon1), float(lat2), float(lon2)])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    R = 6371.0  # Earth's radius in kilometers
    return R * c


# Function to clean latitude and longitude values with direction (N/S/E/W)
def clean_coordinates(value):
    match = re.search(r"([-+]?[0-9]*\.?[0-9]+)", value)
    if not match:
        raise ValueError(f"Cannot parse coordinate value: {value}")
    numeric_value = float(match.group(1))
    if 'S' in value or 'W' in value:  # South and West are negative
        return -numeric_value
    return numeric_value


# Convert DMS (degrees, minutes, seconds) to decimal degrees
def dms_to_decimal(degrees, minutes, seconds):
    return degrees + (minutes / 60.0) + (seconds / 3600.0)


def parse_dms_string(dms_string):
    parts = dms_string.split()
    degrees = float(parts[0])
    minutes = float(parts[1])
    seconds = 0.0 if len(parts) < 3 else float(parts[2])
    return dms_to_decimal(degrees, minutes, seconds)


# Read cities and airports data from CSV files
def load_data():
    # Read cities data
    cities_file = "Major_Cities_GPS_V2.csv"
    try:
        cities_data = pd.read_csv(cities_file)
        cities_data = cities_data[['City', 'Latitude', 'Longitude']].dropna()
        cities_data.rename(columns={'City': 'name', 'Latitude': 'lat', 'Longitude': 'lng'}, inplace=True)
        cities_data['lat'] = cities_data['lat'].apply(clean_coordinates)
        cities_data['lng'] = cities_data['lng'].apply(clean_coordinates)
    except Exception as e:
        print("Error loading cities data:", e)
        cities_data = pd.DataFrame()

    # Read airports data
    airports_file = "iata-icao.csv"
    try:
        airports_data = pd.read_csv(airports_file)
        airports_data = airports_data[['airport', 'latitude', 'longitude']].dropna()
    except Exception as e:
        print("Error loading airports data:", e)
        airports_data = pd.DataFrame()

    return cities_data, airports_data


# Find the closest airport to each city
def find_closest_locations(cities_data, airports_data):
    results = []
    for _, city_row in cities_data.iterrows():
        city_name = city_row['name']
        city_lat = city_row['lat']
        city_lon = city_row['lng']
        closest_location = None
        min_distance = float('inf')

        for _, airport_row in airports_data.iterrows():
            airport_name = airport_row['airport']
            airport_lat = airport_row['latitude']
            airport_lon = airport_row['longitude']
            distance = haversine_distance(city_lat, city_lon, airport_lat, airport_lon)

            if distance < min_distance:
                min_distance = distance
                closest_location = (airport_name, airport_lat, airport_lon)

        results.append({
            'city': city_name,
            'closest_location': closest_location[0],
            'distance_km': min_distance
        })

    return results


# Main execution
def main():
    cities_data, airports_data = load_data()

    if not cities_data.empty and not airports_data.empty:
        closest_locations = find_closest_locations(cities_data, airports_data)

        # Output results
        for result in closest_locations:
            print(
                f"City: {result['city']}, Closest Airport: {result['closest_location']}, Distance: {result['distance_km']:.2f} km")

        # Optionally save results to JSON
        output_json = json.dumps(closest_locations, indent=4)
        with open('closest_locations.json', 'w') as f:
            f.write(output_json)
        print("Closest locations data saved to closest_locations.json")
    else:
        print("No data available.")


# Run the script
if __name__ == "__main__":
    main()