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

## 📁 Project Structure

- **Estate_PRG.ipynb**  
  Main analysis notebook (EDA, visualization, OLS modeling)

- **README.md**  
  Project documentation and usage instructions

- **data_estate_processed_06012026.csv**  
  Final cleaned and feature-engineered dataset  
  (Snapshot: January 6, 2026, ready for machine learning)

- **data_preprocessing.py**  
  ETL pipeline for data cleaning and feature engineering  
  *(Work in progress)*

- **metro_stations.csv**  
  GPS coordinates of all Prague metro stations  
  (used for distance-based features)

- **notebook_scraping.ipynb**  
  Notebook used to run and debug the initial data scraping workflow

- **scraping_functions.py**  
  Scraping logic:
  - Sreality.cz API
  - Google Places / Locations API

- **requirements.txt**  
  Python dependencies  

## ⚠️ Disclaimer
This project is for educational purposes only.

