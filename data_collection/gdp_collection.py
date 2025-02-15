import os
import requests
from dotenv import load_dotenv
import csv
from datetime import datetime
import time
import pandas as pd

def load_fred_api_key():
    """Loads the FRED API key from the .env file."""
    load_dotenv()
    return os.getenv("FRED_API_KEY")

def get_fred_data(series_id):
    """Retrieves data for a specific series from FRED."""
    api_key = load_fred_api_key()
    if not api_key:
        print("Error: FRED API key not found.")
        return None

    url = "https://api.stlouisfed.org/fred/series/observations"
    params = {
        "series_id": series_id,
        "api_key": api_key,
        "file_type": "json",
        "observation_start": start_date,  # Use global start_date
        "observation_end": end_date,      # Use global end_date
    }

    try:
        response = requests.get(url, params=params)
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

        data = response.json()

        observations = []
        for obs in data["observations"]:
            if obs["value"] != ".":  # Handle missing values
                observations.append({"date": obs["date"], "value": obs["value"]})
        return observations

    except requests.exceptions.RequestException as e:
        print(f"Error during API request for series {series_id}: {e}")
        return None

def search_fred_series(search_text, start_date, end_date, tags=None, frequency=None):
    """Searches for FRED series IDs based on keywords, date range, and frequency."""
    api_key = load_fred_api_key()
    if not api_key:
        print("Error: FRED API key not found.")
        return []

    url = "https://api.stlouisfed.org/fred/series/search"
    params = {
        "search_text": search_text,
        "api_key": api_key,
        "file_type": "json",
        "observation_start": start_date,
        "observation_end": end_date,
        "frequency": frequency,
    }
    if tags:
        params["tag_names"] = ";".join(tags)

    try:
        response = requests.get(url, params=params)
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
            time.sleep(1)  # Default delay

        data = response.json()
        series_df = pd.DataFrame(data['seriess'])
        return series_df

    except requests.exceptions.RequestException as e:
        print(f"Error during series search: {e}")
        return []

def get_series_tags(series_id):
    """Retrieves tags for a given series ID."""
    api_key = load_fred_api_key()
    if not api_key:
        print("Error: FRED API key not found.")
        return []

    url = "https://api.stlouisfed.org/fred/series/tags"
    params = {
        "series_id": series_id,
        "api_key": api_key,
        "file_type": "json",
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        tags = [tag["name"] for tag in data["tags"]]
        return tags  # Return the tags

    except requests.exceptions.RequestException as e:
        print(f"Error retrieving tags for series {series_id}: {e}")
        return []

def save_series_to_csv(series_data, series_id, series_title, base_path='data_collection/dataset'):
    """Saves the series data to a CSV file, using series title for filename."""
    if not os.path.exists(base_path):
        os.makedirs(base_path)
    # Create a valid filename from the series title
    filename = "".join(x for x in series_title if x.isalnum()) + ".csv"
    file_path = os.path.join(base_path, filename)
    series_data.to_csv(file_path, index=False)



start_date = "2000-01-01"  # Global start date
end_date = "2023-12-31"    # Global end date

if __name__ == '__main__':
    search_terms = [
        "Federal Funds Rate",
        "Treasury Yields",
        "Trade Weighted U.S. Dollar Index"
    ]

    selected_series = set()  # Use a set to store unique series IDs
    keywords = {"interest", "inflation", "unemployment", "price", "employment", "rate", "index", "supply", "yield", "exchange", "housing", "production", "sales"}

    for term in search_terms:
        print(f"Searching for: {term}")
        search_results = search_fred_series(term, start_date, end_date, frequency='daily')

        for index, row in search_results.head(10).iterrows():
            series_id = row['id']
            series_title = row['title']
            print(f"  Series ID: {series_id}, Title: {series_title}")

            if any(keyword in series_title.lower() for keyword in keywords):
                print(f"  Fetching data for series ID: {series_id} (Title contains keyword)")
                tags = get_series_tags(series_id)  # Get and print tags
                data = get_fred_data(series_id)  # Fetch data (no date args)
                if data:
                    print(f"    Retrieved {len(data)} observations for series {series_id}.")
                    series_data = pd.DataFrame(data)
                    series_data['value'] = pd.to_numeric(series_data['value'], errors='coerce')
                    series_data.dropna(subset=['value'], inplace=True)
                    if not series_data.empty:
                        save_series_to_csv(series_data, series_id, series_title) # Pass title for filename
                        print(f"    Data for {series_id} saved to file.")
                    else:
                        print(f"    No data available for series: {series_id}")
                selected_series.add(series_id)  # Add to the set
            else:
                print(f"  Skipping series ID: {series_id} (Title does not contain keyword)")

        time.sleep(1)  # Respect API rate limits

    print(f"Selected series IDs: {selected_series}")
