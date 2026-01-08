## 🏠 Prague Real Estate Price Predictor and Metro Index
A comprehensive end-to-end data science project that scrapes real estate listings from Sreality.cz, integrates geospatial data from the Prague Metro system (via Google Maps API), and creates a Linear Regression model to predict apartment prices in Prague.

## 📋 Project Overview
This repository contains a full pipeline that:

- Scrapes Data: Fetches thousands of real estate listings asynchronously from Sreality.cz (the largest Czech real estate portal).

- Geolocates: Uses the Google Maps API to get exact GPS coordinates for all Prague Metro stations.

- Feature Engineering:

  - Calculates the Haversine distance from every apartment to every metro station.

  - Identifies the nearest station and specific line (A, B, C).

  - Parses complex JSON metadata (floor, usable area, building material, ownership).

  - Modeling: Trains an Ordinary Least Squares (OLS) Linear Regression model to identify price drivers.

## 📂 Project Structure
├── Estate_PRG.ipynb                      # Main analysis notebook (EDA, Visualization, and OLS Modeling)
├── README.md                             # Project documentation
├── data_estate_processed_06012026.csv    # Final cleaned dataset ready for machine learning (Snapshot: Jan 6, 2026)
├── data_preprocessing.py                 # ETL script (not done yet)
├── metro_stations.csv                    # Dataset with GPS coordinates for all Prague Metro stations
├── notebook_scraping.ipynb               # Notebook used to execute the initial scraping workflow
├── requirements.txt                      # List of Python dependencies (pandas, googlemaps, sklearn, etc.)
└── scraping_functions.py                 # Script containing Sreality API and Google Locations API scraping logic

## ⚠️ Disclaimer
This project is for educational purposes only.

