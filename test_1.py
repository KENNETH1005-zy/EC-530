import math
import pandas as pd

# Haversine formula to calculate the great-circle distance
def haversine_distance(lat1, lon1, lat2, lon2):
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat / 2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    R = 6371.0  # Earth's radius in kilometers
    return R * c

# Your current location (BU Photonics Center)
current_location = (42.3505, -71.1054)  # Latitude and Longitude of BU Photonics Center

# Read local CSV file
data_file = "test1.csv"
try:
    # Check if file exists and is not empty
    data = pd.read_csv(data_file)
    if data.empty:
        raise ValueError("CSV file is empty.")
    # Extract relevant columns (Latitude and Longitude)
    data = data[['latitude', 'longitude']].dropna()  # Ensure no NaN values
except Exception as e:
    print(f"Error loading data: {e}")
    data = pd.DataFrame()

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

if not data.empty:
    closest_issues = find_closest_issues(current_location, data, top_n=10)
    if closest_issues:
        print(f"The {len(closest_issues)} closest issues are:")
        for lat, lon, distance in closest_issues:
            print(f"Issue at ({lat}, {lon}) is {distance:.2f} km away.")
    else:
        print("No issues found.")
else:
    print("No data available to process.")