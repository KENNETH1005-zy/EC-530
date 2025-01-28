import math
import pandas as pd
import json

# Haversine formula to calculate the great-circle distance
def haversine_distance(lat1, lon1, lat2, lon2):
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat / 2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    R = 6371.0  # Earth's radius in kilometers
    return R * c

# Convert DMS (degrees, minutes, seconds) to decimal degrees
def dms_to_decimal(degrees, minutes, seconds):
    return degrees + (minutes / 60.0) + (seconds / 3600.0)

def parse_dms_string(dms_string):
    parts = dms_string.split()
    degrees = float(parts[0])
    minutes = float(parts[1])
    seconds = 0.0 if len(parts) < 3 else float(parts[2])
    return dms_to_decimal(degrees, minutes, seconds)

# Read CSV files for cities and airports
def load_data(cities_file="world_cities.csv", airports_file="iata-icao.csv", issues_file="test1.csv"):
    try:
        cities_data = pd.read_csv(cities_file)
        airports_data = pd.read_csv(airports_file)
        issues_data = pd.read_csv(issues_file)

        # Adjust column names for cities
        cities_data = cities_data[['name', 'lat', 'lng']].dropna()
        cities_data['lat'] = cities_data['lat'].apply(lambda x: parse_dms_string(x))
        cities_data['lng'] = cities_data['lng'].apply(lambda x: parse_dms_string(x))

        # Adjust column names for airports
        airports_data = airports_data[['airport', 'latitude', 'longitude']].dropna()

        # Adjust column names for issues (make sure the file has latitude and longitude)
        issues_data = issues_data[['latitude', 'longitude']].dropna()

        return cities_data, airports_data, issues_data
    except Exception as e:
        print("Error loading data:", e)
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

# Find the closest location (issue or airport) for each city
def find_closest_location(data, target_data, is_issue=True):
    results = []

    for _, row in data.iterrows():
        name = row['name'] if not is_issue else None
        city_lat = row['lat']
        city_lon = row['lng'] if not is_issue else None
        closest_location = None
        min_distance = float('inf')

        for _, target_row in target_data.iterrows():
            target_name = target_row['airport'] if is_issue else None
            target_lat = target_row['latitude']
            target_lon = target_row['longitude']

            distance = haversine_distance(city_lat, city_lon, target_lat, target_lon)
            if distance < min_distance:
                min_distance = distance
                closest_location = target_name or (target_lat, target_lon)

        results.append({
            'city': name,
            'closest_location': closest_location,
            'distance_km': min_distance
        })

    return results

# Find the closest issues to current location
def find_closest_issues(current_location, issues_data, top_n=10):
    current_lat, current_lon = current_location
    results = []

    for _, row in issues_data.iterrows():
        issue_lat, issue_lon = row['latitude'], row['longitude']
        distance = haversine_distance(current_lat, current_lon, issue_lat, issue_lon)
        results.append((issue_lat, issue_lon, distance))

    results.sort(key=lambda x: x[2])
    return results[:top_n]

# Main execution
if __name__ == "__main__":
    # Load data
    cities_data, airports_data, issues_data = load_data()

    # Current location (BU Photonics Center)
    current_location = (42.3505, -71.1054)

    # Check for available data
    if not issues_data.empty:
        # Find closest issues
        closest_issues = find_closest_issues(current_location, issues_data, top_n=10)
        if closest_issues:
            print("The 10 closest issues are:")
            for lat, lon, distance in closest_issues:
                print(f"Issue at ({lat}, {lon}) is {distance:.2f} km away.")
        else:
            print("No issues found.")
    else:
        print("No issues data available.")

    if not cities_data.empty and not airports_data.empty:
        # Find closest airport for each city
        closest_airports = find_closest_location(cities_data, airports_data, is_issue=False)

        # Print closest airports to each city
        for result in closest_airports:
            print(f"City: {result['city']}, Closest Airport: {result['closest_location']}, Distance: {result['distance_km']:.2f} km")

        # Optionally save to JSON file
        with open('closest_locations.json', 'w') as f:
            json.dump(closest_airports, f, indent=4)
        print("Closest locations data saved to closest_locations.json")
    else:
        print("No city or airport data available.")