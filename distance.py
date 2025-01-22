import math
from typing import List, Tuple


def calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Compute the distance between two geographical points.
    """
    radius = 6371.0  # Approximate radius of Earth in kilometers

    # Convert latitude and longitude to radians
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])

    # Compute differences
    diff_lat = lat2 - lat1
    diff_lon = lon2 - lon1

    # Apply formula
    a = math.sin(diff_lat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(diff_lon / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return radius * c


def find_closest(array1: List[Tuple[float, float]], array2: List[Tuple[float, float]]) -> List[Tuple[float, float]]:
    """
    For each point in the first list, find the nearest point in the second list.
    """
    results = []

    for point1 in array1:
        lat1, lon1 = point1
        smallest_distance = float('inf')
        nearest = None

        for point2 in array2:
            lat2, lon2 = point2
            dist = calculate_distance(lat1, lon1, lat2, lon2)
            if dist < smallest_distance:
                smallest_distance = dist
                nearest = point2

        results.append(nearest)

    return results


# Example use
if __name__ == "__main__":
    # Sample data
    list1 = [(52.2296756, 21.0122287), (41.8919300, 12.5113300)]
    list2 = [(48.856614, 2.3522219), (51.5073509, -0.1277583)]

    output = find_closest(list1, list2)
    print("Matches:", output)