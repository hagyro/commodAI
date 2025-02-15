# commodAI: Proactive Commodity Market Analysis and Early Warning System

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Description

commodAI is an open-source project aimed at developing a proactive early warning system for commodity market instability.  The system leverages machine learning, specifically time series anomaly detection and ensemble clustering, combined with external data sources that capture real-world events, to predict potential price shocks in commodity markets.  It moves beyond traditional statistical methods by incorporating diverse data streams and advanced analytical techniques to provide a more comprehensive and nuanced understanding of market dynamics.

## Objectives

*   **Robust Anomaly Detection:** Identify periods of unusual price behavior in historical commodity market data using the Isolation Forest algorithm. This system focuses on identifying *regions* of anomalous behavior, not just isolated data points.
*   **Ensemble Clustering:** Group similar anomaly periods using a combination of clustering techniques (K-means, DBSCAN, Hierarchical Clustering) to categorize different types of market shocks.
*   **External Data Integration:** Incorporate data from news articles, social media (Twitter/X), macroeconomic indicators (US GDP), and weather data to provide context and potential causal links to identified market anomalies.
*   **Early Warning System:** Develop a predictive model that uses the combined market and external data to forecast potential future periods of instability for individual commodities and across the market.
*   **Interactive Visualization:** Provide an interactive dashboard (within the Jupyter Notebook) to visualize time series data, detected anomalies, clustering results, and external data correlations.
*   **Reproducible Research:** Ensure the entire project is reproducible within a specified, self-contained environment (MacBook M1 Pro, Sonoma 14.7.3, Python 3.9.7).

## Innovation

commodAI distinguishes itself from traditional approaches through:

*   **Unsupervised Learning:** Employs Isolation Forest for anomaly detection, which doesn't require pre-labeled data and can discover novel market disruption patterns.
*   **Ensemble Methods:** Combines multiple clustering algorithms for a more robust and accurate classification of anomaly types.
*   **Data Fusion:** Integrates diverse data sources (market data, news, social media, macroeconomics, weather) to capture complex relationships and potential hidden drivers.
*   **Predictive Capability:**  Moves beyond descriptive analysis to provide proactive warnings of potential market instability.

## Data Sources

*   **Commodity Price Data:** Historical daily closing prices for 18 commodities (2000-2023) - *Provided in the repository*.
*   **News Articles:** GDELT Project API (primary), NewsAPI.org (secondary), New York Times Archive API (optional).
*   **Social Media:** Twitter API (Academic Research Product Track).
*   **Macroeconomic Data:** Federal Reserve Economic Data (FRED) - US GDP.
*   **Weather Data:** NOAA Daily Summaries API, OpenWeatherMap API (secondary), Visual Crossing API.

## Technology Stack

*   **Programming Language:** Python 3.9.7
*   **Environment:** `venv` (Python's built-in virtual environment)
*   **Primary Libraries:**
    *   `pandas`
    *   `numpy`
    *   `scikit-learn`
    *   `scipy`
    *   `plotly`
    *   `requests`
    *   `beautifulsoup4` (optional, for web scraping if necessary)
    *   `tweepy` (for Twitter API)
    *   `gdeltpy` (for GDELT API)
    *   `python-dotenv`

## Installation

1.  **Clone the Repository:**

    ```bash
    git clone <repository_url>
    cd <repository_directory>
    ```

2.  **Create and Activate a Virtual Environment:**

    ```bash
    python3.9 -m venv .venv
    source .venv/bin/activate  # On macOS/Linux
    # Or
    .venv\Scripts\activate  # On Windows
    ```

3.  **Install Dependencies:**

    ```bash
    pip install -r requirements.txt
    ```
    (A `requirements.txt` file will be generated and included in the repository as the project evolves, listing all necessary packages and their versions).

4.  **API Keys (where applicable):**
    *   You will need to obtain API keys for GDELT, Twitter, FRED, and NOAA (or the alternative weather APIs) if you intend to use the live data fetching capabilities.
    *   Create a `.env` file in the project root directory to store your API keys securely. Use a `.env.example` as a template (also included in the repository).  The notebook will load these keys using the `python-dotenv` package.  **Do not commit your `.env` file to version control!**

    Example `.env` file:

    ```
    GDELT_API_KEY=your_gdelt_api_key
    TWITTER_API_KEY=your_twitter_api_key
    TWITTER_API_SECRET=your_twitter_api_secret
    TWITTER_BEARER_TOKEN=your_twitter_bearer_token
    FRED_API_KEY=your_fred_api_key
    NOAA_API_KEY=your_noaa_api_key
    ```

5.  **Run the Jupyter Notebook:**

    ```bash
    jupyter notebook commodAI.ipynb
    ```

## Project Structure

*   `commodAI.ipynb`:  The main Jupyter Notebook containing all the code, analysis, and visualizations.
*   `data/`: Directory for storing data files (the provided commodity price data, and any downloaded data from APIs).
*   `utils/`:  (Will be created) Directory for storing utility functions and helper scripts.
*   `requirements.txt`:  List of required Python packages.
*   `.env.example`: Template for storing API keys.
*   `README.md`: This file.

## Contributing

We welcome contributions to the commodAI project! Here's how you can contribute:

1.  **Fork the Repository:** Create a fork of the repository on your own GitHub account.
2.  **Create a Branch:** Create a new branch for your feature or bug fix. Use a descriptive name (e.g., `feature/add-gdelt-integration`, `bugfix/handle-api-error`).
3.  **Make Changes:** Implement your changes, following the coding style and guidelines (see below).
4.  **Test Your Code:** Ensure your code works correctly and doesn't introduce any regressions.
5.  **Commit Changes:** Commit your changes with clear and concise commit messages.
6.  **Create a Pull Request:** Submit a pull request from your branch to the main repository's `main` branch.  Provide a detailed description of your changes and any relevant context.
7.  **Code Review:** The project maintainers will review your code and provide feedback.

**Coding Guidelines:**

*   Follow PEP 8 style guidelines.
*   Write clear and concise comments.
*   Use descriptive variable and function names.
*   Implement robust error handling.
*   Keep code modular and reusable.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details. This is a permissive open-source license that allows for reuse and modification, even for commercial purposes.
```

Key Changes:

*   **Environment:** Replaced all references to `conda` and `Anaconda` with `python3.9 -m venv .venv` and the appropriate activation commands for macOS/Linux and Windows.
*   **Python Version:** Explicitly specified `python3.9` in the `venv` creation command to ensure the correct Python version is used.
*   **Installation - Step 2** Added the different commands for activating the venv depending on the OS (Windows or macOS/Linux)

This revised version is now fully compatible with using Python's built-in virtual environment system, making it more accessible to users who prefer not to use Anaconda.  The instructions are clear and platform-specific.
