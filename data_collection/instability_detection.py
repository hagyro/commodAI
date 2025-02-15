import pandas as pd
from sklearn.ensemble import IsolationForest
from datetime import datetime, timedelta

def detect_anomalies(data_file, column_name, method='isolation_forest', contamination=0.05, window_size=7):
    """
    Detects anomalies in a time series data column within a CSV file.

    Args:
        data_file (str): Path to the CSV file (e.g., 'dataset/gdp.csv').
        column_name (str): Name of the column to analyze (e.g., 'value', 'TMIN').
        method (str): Anomaly detection method ('isolation_forest' or 'moving_average'). Default: 'isolation_forest'.
        contamination (float): Contamination factor for Isolation Forest (default: 0.05).
        window_size (int): Window size for moving average method (default: 7).

    Returns:
        list: A list of date ranges (start and end dates) where anomalies were detected.
              Format: [['YYYY-MM-DD', 'YYYY-MM-DD'], ...].
              Returns an empty list if no anomalies are found or an error occurs.
    """
    try:
        df = pd.read_csv(data_file, parse_dates=['date'])
        df['date'] = pd.to_datetime(df['date'], format='%m/%d/%y').dt.strftime('%Y-%m-%d')
        df['date'] = pd.to_datetime(df['date'])

        if method == 'isolation_forest':
            model = IsolationForest(contamination=contamination, random_state=42)
            model.fit(df[[column_name]])
            df['anomaly'] = model.predict(df[[column_name]])
            df['anomaly'] = df['anomaly'].apply(lambda x: 1 if x == -1 else 0)  # Convert -1 to 1, 1 to 0

        elif method == 'moving_average':
            rolling_mean = df[column_name].rolling(window=window_size).mean()
            rolling_std = df[column_name].rolling(window=window_size).std()
            threshold_upper = rolling_mean + (3 * rolling_std)
            threshold_lower = rolling_mean - (3 * rolling_std)
            df['anomaly'] = ((df[column_name] > threshold_upper) | (df[column_name] < threshold_lower)).astype(int)
            # Handle edge cases where rolling mean/std are NaN
            df['anomaly'] = df['anomaly'].fillna(0)

        else:
            raise ValueError("Invalid method. Choose 'isolation_forest' or 'moving_average'.")

        # Find contiguous regions of anomalies
        anomaly_dates = []
        start_date = None
        for i in range(len(df)):
            if df['anomaly'].iloc[i] == 1:
                if start_date is None:
                    start_date = df['date'].iloc[i]
            elif start_date is not None:
                end_date = df['date'].iloc[i-1]
                anomaly_dates.append([start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d')])
                start_date = None
        if start_date is not None:  # Check if the last segment is an anomaly
            end_date = df['date'].iloc[-1]
            anomaly_dates.append([start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d')])

        return anomaly_dates

    except FileNotFoundError:
        print(f"Error: File not found: {data_file}")
        return []
    except KeyError:
        print(f"Error: Column '{column_name}' not found in {data_file}")
        return []
    except ValueError as e:
        print(f"Error: {e}")
        return []
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return []
def detect_gdp_anomalies():
    """
    Wrapper function for detect_anomalies() to detect GDP anomalies.

    Returns:
        list: A list of date ranges where anomalies were detected.
    """
    return detect_anomalies('dataset/gdp.csv', 'value')

def detect_weather_anomalies():
    """
    Wrapper function for detect_anomalies() to detect weather anomalies.

    Returns:
        list: A list of date ranges where anomalies were detected.
    """
    anomaly_dates = []
    for column in ['TMIN', 'TMAX', 'PRCP']:
        anomaly_dates.extend(detect_anomalies('dataset/weather.csv', column))
    return anomaly_dates