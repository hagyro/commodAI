import math
import requests
import operator
import numpy as np
from datetime import datetime
import calendar
import csv
import os
import time
from abc import ABC, abstractmethod


def load_noaa_api_key():
    """Loads the NOAA API key from the environment variable."""
    api_key = os.getenv("NOAA_TOKEN")
    if not api_key:
        raise ValueError("NOAA_TOKEN environment variable not set.")
    return api_key


class StationClusterer(ABC):
    """Abstract base class for station clusterers."""

    @abstractmethod
    def get_cluster(self, latitude, longitude):
        """Returns the cluster ID for a given station."""
        pass


class SimpleRegionClusterer(StationClusterer):
    """Clusters stations into geographical regions."""

    def get_cluster(self, latitude, longitude):
        """Assigns stations to regions based on latitude and longitude."""
        if latitude < 35:
            return "South"
        elif latitude >= 35 and longitude > -80:
            return "East"
        elif latitude >= 35 and -100 < longitude <= -80:
            return "Mid"
        elif latitude >= 35 and longitude <= -100:
            return "West"
        else:
            return "Unknown"  # Handle cases outside the defined regions

import math
import requests
import operator
import numpy as np
from datetime import datetime
import calendar
import csv

start_date = "2000-01-01"  # Global start date
end_date = "2023-12-31"    # Global end date

def get_gps_bounding_box(latitude, longitude, deg_lat, deg_lon, verbose):
    """
    Returns a bounding box.
    """
    if deg_lat < 0: raise Exception("ERROR: deg_lat passed to get_gps_bounding_box is invalid")
    if not isinstance(deg_lat, float): raise Exception("ERROR: deg_lat passed to get_gps_bounding_box is invalid")
    if deg_lon < 0: raise Exception("ERROR: deg_lon passed to get_gps_bounding_box is invalid")
    if not isinstance(deg_lon, float): raise Exception("ERROR: deg_lon passed to get_gps_bounding_box is invalid")

    if latitude >= 0:
        if latitude + deg_lat >= 90.0:
            n = 90.0 * np.sign(latitude)
            s = latitude - deg_lat
        else:
            n = latitude + deg_lat
            s = latitude - deg_lat

    else:
        # latitude < 0
        if abs(latitude) + deg_lat >= 90.0:
            n = 90.0 * np.sign(latitude)
            s = (abs(latitude) - deg_lat) * np.sign(latitude)
        else:
            n = latitude + deg_lat
            s = latitude - deg_lat

    if longitude >= 0:
        if longitude + deg_lon >= 180.0:
            w = 180.0 * np.sign(longitude)
            e = longitude - deg_lon
        else:
            w = longitude + deg_lon
            e = longitude - deg_lon

    else:
        # longitude < 0
        if abs(longitude) + deg_lon >= 180.0:
            w = 180.0 * np.sign(longitude)
            e = (abs(longitude) - deg_lon) * np.sign(longitude)
        else:
            w = longitude + deg_lon
            e = longitude - deg_lon

    if verbose: print(round(n,1), round(latitude,1), round(s,1), "\\t", round(w,1), round(longitude,1), round(e,1))

    return n, w, s, e

def haversine_distance(lat1, lon1, lat2, lon2):
    """
    Returns the distance in meters between two GPS coordinates.
    """
    # Radius of the Earth in meters
    earth_radius_m = 6371000.0

    # Convert latitude and longitude from degrees to radians
    lat1_rad = math.radians(lat1)
    lon1_rad = math.radians(lon1)
    lat2_rad = math.radians(lat2)
    lon2_rad = math.radians(lon2)

    # Differences between the latitudes and longitudes
    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad

    # Haversine formula
    a = math.sin(dlat / 2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    # Calculate the distance
    distance = earth_radius_m * c

    return distance

def elevation_by_lat_lon(lat1, lon1):
    """
    Returns the elevation in meters for the specified latitude/longitude.
    Uses Open-Elevation API.
    """
    url = f'https://api.open-elevation.com/api/v1/lookup?locations={lat1},{lon1}'
    try:
        resp = requests.get(url).json()
    except Exception as e:
        print(f'ERROR: {e}, {url}')
        return None

    if not resp or 'results' not in resp:
        print("Failed to get elevation data.")
        return None

    results = resp['results'][0]
    if 'elevation' not in results:
        print("Elevation data not found in response.")
        return None
    elevation = float(results['elevation'])
    return elevation

def get_stations_by_bounding_box(noaa_token, verbose=False):
    """
    Retrieves all weather stations within a bounding box encompassing the contiguous United States.

    Args:
        noaa_token (str): NOAA API token.
        verbose (bool):  Print verbose output.

    Returns:
        list: A list of dictionaries, each representing a station with 'id', 'latitude', and 'longitude'.
    """
    # Bounding box for the contiguous United States
    north = 49.384358
    west = -125.000000
    south = 24.396308
    east = -66.885444
    bbox_str = f'{south},{west},{north},{east}'

    url = f'https://www.ncei.noaa.gov/access/services/search/v1/data?dataset=daily-summaries&boundingBox={bbox_str}&fields=id,latitude,longitude'
    headers = {'token': noaa_token}
    stations = []
    offset = 0
    total_stations = 0 # Initialize total_stations

    while True: # Loop for pagination
        try:
            paginated_url = f'{url}&offset={offset}' if offset > 0 else url # Add offset if > 0
            response = requests.get(paginated_url, headers=headers)
            response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)

            # Rate limiting
            rate_limit_limit = response.headers.get('X-RateLimit-Limit')
            rate_limit_remaining = response.headers.get('X-RateLimit-Remaining')
            retry_after = response.headers.get('Retry-After')

            if rate_limit_limit:
                print(f"Rate Limit: {rate_limit_limit}")
            if rate_limit_remaining:
                print(f"Rate Limit Remaining: {rate_limit_remaining}")
            if retry_after:
                print(f"Retry-After: {retry_after} seconds")
                time.sleep(int(retry_after))
            elif rate_limit_remaining and int(rate_limit_remaining) < 5:
                print("Rate limit approaching. Waiting 2 seconds...")
                time.sleep(2)
            else:
                time.sleep(1) # Default delay
            
            # Specific error handling for 400
            if response.status_code == 400:
                print(f"Error: 400 Bad Request. Check API parameters. URL: {response.url}")
                return None

            search_results = response.json()

            if not search_results or 'results' not in search_results:
                if offset == 0: # Only print if no stations found on first request
                    print("No stations found within the bounding box.")
                break  # Exit loop if no results

            for station in search_results['results']:
                if 'id' in station and 'latitude' in station and 'longitude' in station:
                    stations.append({
                        'id': station['id'],
                        'latitude': float(station['latitude']),
                        'longitude': float(station['longitude'])
                    })

            # Pagination check
            if 'metadata' in search_results and 'next' in search_results['metadata']:
                # The API uses a 'next' URL for pagination.  Extract the offset.
                next_url = search_results['metadata']['next']
                offset_start = next_url.find("offset=")
                if offset_start != -1:
                    offset_end = next_url.find("&", offset_start)
                    if offset_end == -1:
                        offset = int(next_url[offset_start + len("offset="):])
                    else:
                        offset = int(next_url[offset_start + len("offset="):offset_end])
                else:  # No offset found, stop pagination
                    break
            elif 'metadata' in search_results and 'totalCount' in search_results['metadata']:
                # Alternatively, check for totalCount and calculate offset
                total_stations = search_results['metadata']['totalCount']
                offset += len(search_results['results'])
                if offset >= total_stations:
                    break # Exit if we have all stations
            else:
                break # No pagination info, exit loop

        except requests.exceptions.RequestException as e:
            print(f"Error during station search: {e}")
            return None

    print(f"Retrieved {len(stations)} stations.") # Print total stations retrieved
    return stations

import pandas as pd


def aggregate_weather_data():
    """
    Retrieves and aggregates weather data by geographical regions.

    1. Gets the list of stations using `get_stations_by_bounding_box`.
    2. Creates an instance of `SimpleRegionClusterer`.
    3. Iterates through the stations:
        - Get the cluster ID using `clusterer.get_cluster(latitude, longitude)`.
        - Retrieve weather data for the station using `get_noaa_data`.
        - Store the data in a suitable data structure (e.g., a dictionary keyed by date and region).
    4. After retrieving data for all stations, calculate the daily average `TMIN`, `TMAX`, `PRCP`, `AWND`, `SNOW`, and `SNWD` for each region. Calculate `TAVG` as `(TMIN + TMAX) / 2`.
    5. Create a Pandas DataFrame from the aggregated data, with dates as the index and columns for each region and variable (e.g., "East_TMIN", "Mid_TMAX", "West_PRCP", etc.).
    6. Save the dataframe in 'dataset/aggregated_weather.csv'
    """
    noaa_token = load_noaa_api_key()
    stations = get_stations_by_bounding_box(noaa_token)
    clusterer = SimpleRegionClusterer()

    # Data structure to store aggregated data: {date: {region: {data_type: [values]}}}  Example: {'2024-01-01': {'East': {'TMIN': [50, 52], 'TMAX': [60, 65]}}} 
    aggregated_data = {}

    for station in stations:
        cluster_id = clusterer.get_cluster(station['latitude'], station['longitude'])
        weather_data = get_noaa_data(station['id'], start_date, end_date)

        if weather_data:
            for record in weather_data:
                date = record['DATE']
                if date not in aggregated_data:
                    aggregated_data[date] = {}
                if cluster_id not in aggregated_data[date]:
                    aggregated_data[date][cluster_id] = {
                        'TMIN': [], 'TMAX': [], 'PRCP': [], 'AWND': [], 'SNOW': [], 'SNWD': []
                    }

                for data_type in ['TMIN', 'TMAX', 'PRCP', 'AWND', 'SNOW', 'SNWD']:
                    if data_type in record and record[data_type] is not None:
                        aggregated_data[date][cluster_id][data_type].append(float(record[data_type]))

    # Calculate daily averages and create DataFrame
    data_for_df = []
    for date, region_data in aggregated_data.items():
        row = {'DATE': date}
        for region, values in region_data.items():
            for data_type in ['TMIN', 'TMAX', 'PRCP', 'AWND', 'SNOW', 'SNWD']:
                if values[data_type]:  # Check if the list is not empty
                    row[f'{region}_{data_type}'] = np.mean(values[data_type])
                else:
                    row[f'{region}_{data_type}'] = np.nan  # Or some other placeholder for missing data

            # Calculate TAVG
            if f'{region}_TMIN' in row and f'{region}_TMAX' in row:
                row[f'{region}_TAVG'] = (row[f'{region}_TMIN'] + row[f'{region}_TMAX']) / 2
            else:
                row[f'{region}_TAVG'] = np.nan

        data_for_df.append(row)

    df = pd.DataFrame(data_for_df)
    df.set_index('DATE', inplace=True)
    df.sort_index(inplace=True)

    # Create the 'dataset' directory if it doesn't exist
    os.makedirs('dataset', exist_ok=True)

    df.to_csv('dataset/aggregated_weather.csv')
    print(f"Successfully aggregated weather data. Output saved to dataset/aggregated_weather.csv")



def get_noaa_data(station_id, start_date, end_date):
    """
    Retrieves daily weather data from the NOAA API for a specific station.

    Args:
        station_id (str): The ID of the weather station.
        start_date (str): The start date in YYYY-MM-DD format.
        end_date (str): The end date in YYYY-MM-DD format.

    Returns:
        list: A list of dictionaries, where each dictionary represents a daily
              weather observation. Returns None if the API request fails
              or no data is found.
    """
    noaa_token = load_noaa_api_key()  # Use the load_noaa_api_key function

    url = "https://www.ncei.noaa.gov/access/services/data/v1"
    params = {
        "dataset": "daily-summaries",
        "dataTypes": "TMIN,TMAX,PRCP,SNOW,SNWD,AWND",
        "stations": station_id,
        "startDate": start_date,
        "endDate": end_date,
        "format": "json",
        "units": "standard",
        "includeAttributes": "false",
    }
    headers = {"token": noaa_token}

    try:
        response = requests.get(url, params=params, headers=headers)
        response.raise_for_status()

        # Rate limiting
        rate_limit_limit = response.headers.get('X-RateLimit-Limit')
        rate_limit_remaining = response.headers.get('X-RateLimit-Remaining')
        retry_after = response.headers.get('Retry-After')

        if rate_limit_limit:
            print(f"Rate Limit: {rate_limit_limit}")
        if rate_limit_remaining:
            print(f"Rate Limit Remaining: {rate_limit_remaining}")
        if retry_after:
            print(f"Retry-After: {retry_after} seconds")
            time.sleep(int(retry_after))
        elif rate_limit_remaining and int(rate_limit_remaining) < 5:
            print("Rate limit approaching. Waiting 2 seconds...")
            time.sleep(2)
        else:
            time.sleep(1) # Default delay

        # Specific error handling for 400
        if response.status_code == 400:
            print(f"Error: 400 Bad Request. Check API parameters. URL: {response.url}")
            return None

        data = response.json()

        if 'results' not in data:
            print(f"No data found for station {station_id} and date range {start_date} to {end_date}.")
            return None

        return data["results"]

    except requests.exceptions.RequestException as e:
        print(f"Error during API request: {e}")
        return None

if __name__ == '__main__':
    aggregate_weather_data()