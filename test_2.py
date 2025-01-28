import math
import pandas as pd
import json


# Haversine formula to calculate the great-circle distance
def haversine_distance(lat1, lon1, lat2, lon2):
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    R = 6371.0  # Earth's radius in kilometers
    return R * c


# Read CSV files for issues, cities, and airports
issue_data_file = "test1.csv"
cities_file = "world_cities.csv"
airports_file = "iata-icao.csv"

try:
    # Load issue data
    issues_data = pd.read_csv(issue_data_file)
    issues_data = issues_data[['latitude', 'longitude']].dropna()  # Ensure no NaN values

    # Load city and airport data
    cities_data = pd.read_csv(cities_file)
    airports_data = pd.read_csv(airports_file)

    # Clean city and airport data
    cities_data = cities_data[['name', 'lat', 'lng']].dropna()
    airports_data = airports_data[['airport', 'latitude', 'longitude']].dropna()
except Exception as e:
    print("Error loading data:", e)
    issues_data = pd.DataFrame()
    cities_data = pd.DataFrame()
    airports_data = pd.DataFrame()


# Find the closest reported issue to a given location
def find_closest_issue(current_location, data):
    current_lat, current_lon = current_location
    closest_issue = None
    min_distance = float('inf')

    for _, row in data.iterrows():
        issue_lat, issue_lon = row['latitude'], row['longitude']
        distance = haversine_distance(current_lat, current_lon, issue_lat, issue_lon)

        if distance < min_distance:
            min_distance = distance
            closest_issue = (issue_lat, issue_lon, distance)

    return closest_issue


# Find the closest reported issues
def find_closest_issues(current_location, data, top_n=10):
    current_lat, current_lon = current_location
    results = []

    for _, row in data.iterrows():
        issue_lat, issue_lon = row['latitude'], row['longitude']
        distance = haversine_distance(current_lat, current_lon, issue_lat, issue_lon)
        results.append((issue_lat, issue_lon, distance))

    # Sort by distance and return the top N closest issues
    results.sort(key=lambda x: x[2])
    return results[:top_n]


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


# Example of how to use the functions
if not issues_data.empty:
    current_location = (42.3505, -71.1054)  # Example location (BU Photonics Center)

    # Find the closest issue
    closest_issue = find_closest_issue(current_location, issues_data)
    if closest_issue:
        lat, lon, distance = closest_issue
        print(f"The closest issue is at ({lat}, {lon}) and is {distance:.2f} km away.")
    else:
        print("No issues found.")

    # Find the closest 10 issues
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
    # Find closest airport for each city and save to JSON
    closest_locations = find_closest_locations(cities_data, airports_data)

    # Convert results to JSON format
    output_json = json.dumps(closest_locations, indent=4)

    # Save the results to a JSON file
    with open('closest_locations.json', 'w') as f:
        f.write(output_json)

    print("Closest locations data saved to closest_locations.json")
else:
    print("No city or airport data available.")