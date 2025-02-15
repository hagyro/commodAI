import pandas as pd
from datetime import datetime
from gdelt_data import get_gdelt_news_summary


def synthesize_data(commodities_file, gdp_file, weather_file, output_file):
    """
    Combines data from the commodities, GDP, and weather CSV files.

    Args:
        commodities_file (str): Path to the commodities_DB.csv file.
        gdp_file (str): Path to the gdp.csv file.
        weather_file (str): Path to the weather.csv file.
        output_file (str): Path to the output CSV file.

    Returns:
        None. Writes the combined data to the specified output file.
    """
    try:
        # Read commodities data, handling potential encoding and delimiter issues
        commodities_df = pd.read_csv(commodities_file, delimiter=';')
        if '﻿date' in commodities_df.columns:
            commodities_df.rename(columns={'﻿date': 'date'}, inplace=True)
        # Ensure date column is in datetime format
        commodities_df['date'] = pd.to_datetime(commodities_df['date'], format='%m/%d/%y')

        # Read GDP data
        gdp_df = pd.read_csv(gdp_file)
        gdp_df['date'] = pd.to_datetime(gdp_df['date'], format='%Y-%m-%d')

        # Read weather data
        weather_df = pd.read_csv(weather_file)
        weather_df['DATE'] = pd.to_datetime(weather_df['DATE'], format='%Y-%m-%d')
        # Rename DATE column to date for merging
        weather_df.rename(columns={'DATE': 'date'}, inplace=True)

        # Merge dataframes
        merged_df = pd.merge(commodities_df, gdp_df, on='date', how='left')
        merged_df = pd.merge(merged_df, weather_df, on='date', how='left')

        # Handle missing values (fill with None)
        merged_df.fillna(value=None, inplace=True)

        # Write to output file
        merged_df.to_csv(output_file, index=False)

    except Exception as e:
        print(f"Error during data synthesis: {e}")


def add_news_summary(input_file, output_file, anomaly_dates):
    """
    Combines data from the commodities, GDP, and weather CSV files, and adds news summaries for anomaly periods.

    Args:
        input_file (str): Path to the combined CSV file (e.g., experiment_data_commodAI.csv).
        output_file (str): Path to the output CSV file (same name, overwriting).
        anomaly_dates (list): A list of date ranges [['YYYY-MM-DD', 'YYYY-MM-DD'], ...].

    Returns:
        None. Writes the updated data to the output file.
    """
    try:
        df = pd.read_csv(input_file)
        df['date'] = pd.to_datetime(df['date'])
        df['news_summary'] = None

        query = "(market OR economy OR commodity) AND (instability OR volatility OR crisis)"

        for start_date_str, end_date_str in anomaly_dates:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d')

            start_date_gdelt = start_date.strftime('%Y%m%d%H%M%S')
            end_date_gdelt = end_date.strftime('%Y%m%d%H%M%S')

            summary = get_gdelt_news_summary(query, start_date_gdelt, end_date_gdelt)

            if summary:
                for i in range(len(df)):
                    if start_date <= df['date'].iloc[i] <= end_date:
                        df.loc[i, 'news_summary'] = summary

        df.to_csv(output_file, index=False)

    except Exception as e:
        print(f"Error adding news summaries: {e}")


if __name__ == '__main__':
    # Example Usage (replace with your actual file paths)
    commodities_file = 'dataset/commodities_DB.csv'
    gdp_file = 'dataset/gdp.csv'
    weather_file = 'dataset/weather.csv'
    output_file = 'dataset/experiment_data_commodAI.csv'
    synthesize_data(commodities_file, gdp_file, weather_file, output_file)

    # Example anomaly dates (replace with actual anomaly detection results)
    from anomaly_detection import detect_gdp_anomalies, detect_weather_anomalies
    gdp_anomalies = detect_gdp_anomalies()
    weather_anomalies = detect_weather_anomalies()
    anomaly_dates = gdp_anomalies + weather_anomalies

    add_news_summary(output_file, output_file, anomaly_dates)

    print("Data synthesis complete. Check dataset/experiment_data_commodAI.csv")