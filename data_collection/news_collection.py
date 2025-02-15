import requests
from datetime import datetime
from dotenv import load_dotenv
import os
import google.generativeai as genai

load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=GOOGLE_API_KEY)


def get_gdelt_data(query, start_date, end_date):
    """
    Fetches data from the GDELT API.

    Args:
        query (str): The search query string.
        start_date (str): The start date in YYYYMMDDHHMMSS format.
        end_date (str): The end date in YYYYMMDDHHMMSS format.

    Returns:
        list: A list of articles, or None if an error occurs.
    """
    url = "https://api.gdeltproject.org/api/v2/doc/doc"
    params = {
        "query": query,
        "mode": "artlist",
        "format": "json",
        "startdatetime": start_date,
        "enddatetime": end_date,
        "maxrecords": 250,
    }
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()  # Raise an exception for bad status codes
        return response.json().get('articles', [])
    except requests.exceptions.RequestException as e:
        print(f"Error fetching GDELT data: {e}")
        return None


def get_gdelt_news_summary(query, start_date, end_date):
    """
    Retrieves news articles from GDELT for a specific date range and uses the Google Gemini API to summarize them.

    Args:
        query (str): The search query string for GDELT.
        start_date (str): The start date in YYYYMMDDHHMMSS format.
        end_date (str): The end date in YYYYMMDDHHMMSS format.

    Returns:
        str: A string containing the summarized news content, or None if an error occurs.
    """
    articles = get_gdelt_data(query, start_date, end_date)
    if not articles:
        return None

    headlines = [f"{article.get('title', '')} - {article.get('url', '')}" for article in articles]
    prompt = (
        "Summarize the following news headlines, focusing on any information related to market instability, "
        "economic downturns, or fluctuations in commodity prices. Extract and highlight any specific numbers, "
        "statistics, or quantitative data mentioned. Be concise and factual. Here are the headlines:\n\n"
        + "\n".join(headlines)
    )

    try:
        model = genai.GenerativeModel('gemini-2.0-flash-thinking-exp-01-21')
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        print(f"Error with Gemini API: {e}")
        return None