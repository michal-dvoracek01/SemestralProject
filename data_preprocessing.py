"""
Data Preprocessing Pipeline for Prague Real Estate Analysis

This script processes raw scraped data into the final analysis-ready CSV.
It extracts features, calculates metro distances, and encodes categorical variables.

Usage:
    python data_preprocessing.py

Input files required:
    - data/data_estate.csv (raw data with details from scraping)
    - data/metro_stations.csv (metro station coordinates)

Output:
    - data/data_estate_processed.csv (ready for analysis)
"""

import pandas as pd
import numpy as np
import ast
import re
from math import radians, cos, sin, asin, sqrt


def safe_eval(x):
    """Safely evaluate string representations of Python objects."""
    try:
        return ast.literal_eval(x)
    except (ValueError, SyntaxError):
        return None


def extract_details(detail_str):
    """
    Extract property details from the API response detail field.
    
    Extracts: usable_area, total_area, floor, building_type, 
              building_condition, ownership, terrace, elevator
    """
    details_list = safe_eval(detail_str)
    if not isinstance(details_list, list):
        return {}
    
    extracted = {}
    for item in details_list:
        if not isinstance(item, dict):
            continue
            
        name = item.get('name')
        value = item.get('value')
        
        if not name:
            continue
            
        if 'Užitná ploch' in name:
            extracted['usable_area'] = value
        elif 'Celková plocha' in name:
            extracted['total_area'] = value
        elif 'Podlaží' in name:
            extracted['floor'] = value
        elif 'Stavba' in name:
            extracted['building_type'] = value
        elif 'Stav objektu' in name:
            extracted['building_condition'] = value
        elif 'Vlastnictví' in name:
            extracted['ownership'] = value
        elif 'Terasa' in name:
            extracted['terrace'] = value
        elif 'Výtah' in name:
            extracted['elevator'] = value
            
    return extracted


def extract_floor_num(floor_str):
    """
    Convert floor string to numeric value.
    
    Handles: 'přízemí' (ground floor) -> 0
             'suterén' (basement) -> -1
             '2. patro' -> 2
    """
    if not isinstance(floor_str, str):
        return 0
    floor_str = floor_str.lower()
    if 'přízemí' in floor_str:
        return 0
    elif 'suterén' in floor_str:
        return -1
    match = re.search(r'(-?\d+)', floor_str)
    if match:
        return int(match.group(1))
    return 0


def haversine(lon1, lat1, lon2, lat2):
    """
    Calculate the great circle distance between two points on earth (in meters).
    """
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
    
    dlon = lon2 - lon1 
    dlat = lat2 - lat1 
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a)) 
    r = 6371000  # Radius of earth in meters
    return c * r


def get_metro_distances(row, metro_df):
    """
    Calculate distance from apartment to nearest station on each metro line.
    
    Returns distances to lines A, B, C and the name of the nearest station.
    """
    flat_lat = row['latitude']
    flat_lon = row['longitude']
    
    if pd.isna(flat_lat) or pd.isna(flat_lon):
        return pd.Series([np.nan, np.nan, np.nan, None])
    
    results = {
        'dist_A': 99999,
        'dist_B': 99999,
        'dist_C': 99999,
        'nearest_name': None,
        'global_min_dist': 99999
    }
    
    for _, station in metro_df.iterrows():
        station_line = station['line']
        station_name = station['name']
        station_lat = station['lat']
        station_lng = station['lng']
        
        dist = haversine(flat_lon, flat_lat, station_lng, station_lat)
        
        col_name = f'dist_{station_line}'
        if col_name in results:
            if dist < results[col_name]:
                results[col_name] = dist
        
        if dist < results['global_min_dist']:
            results['global_min_dist'] = dist
            results['nearest_name'] = station_name

    return pd.Series([
        results['dist_A'], 
        results['dist_B'], 
        results['dist_C'], 
        results['nearest_name']
    ])


def process_raw_data(raw_data_path, metro_path, output_path=None):
    """
    Main processing function. Transforms raw scraped data into analysis-ready format.
    
    Args:
        raw_data_path: Path to raw estate data CSV
        metro_path: Path to metro stations CSV
        output_path: Where to save output (optional)
    
    Returns:
        Processed DataFrame
    
    Raises:
        FileNotFoundError: If input files don't exist
        ValueError: If required columns are missing
    """
    # Load data with error handling
    print("Loading data...")
    try:
        df = pd.read_csv(raw_data_path)
    except FileNotFoundError:
        raise FileNotFoundError(f"Raw data file not found: {raw_data_path}")
    
    try:
        metro = pd.read_csv(metro_path)
    except FileNotFoundError:
        raise FileNotFoundError(f"Metro stations file not found: {metro_path}")
    
    # Check required columns exist
    if 'price_czk' not in df.columns:
        raise ValueError("Missing required column: price_czk")
    
    print(f"Loaded {len(df)} records")
    
    # Drop unnecessary columns
    cols_to_drop = [
        'Unnamed: 0', 'hash_id', 'advert_images', 'advert_images_all', 
        'premise_logo', 'user_id', 'premise_id', 'price_summary', 
        'price_currency_cb', 'price_unit_cb', 'price_summary_unit_cb', 
        'has_matterport_url', 'has_video', 'advert_name', 'premise'
    ]
    df = df.drop(columns=cols_to_drop, errors='ignore')
    
    # Remove rows without price
    df = df.dropna(subset=['price_czk'])
    df = df.reset_index(drop=True)
    print(f"After removing missing prices: {len(df)} records")
    
    # Extract locality info
    print("Extracting locality...")
    df['locality_dict'] = df['locality'].apply(safe_eval)
    df['city'] = df['locality_dict'].apply(lambda x: x.get('city') if isinstance(x, dict) else None)
    df['district'] = df['locality_dict'].apply(lambda x: x.get('district') if isinstance(x, dict) else None)
    df['lat'] = df['locality_dict'].apply(lambda x: x.get('gps_lat') if isinstance(x, dict) else None)
    df['lon'] = df['locality_dict'].apply(lambda x: x.get('gps_lon') if isinstance(x, dict) else None)
    
    # Extract category names
    for col in ['category_main_cb', 'category_sub_cb', 'category_type_cb']:
        if col in df.columns:
            df[col] = df[col].apply(lambda x: safe_eval(x).get('name') if safe_eval(x) else None)
    
    # Extract details (floor, elevator, building type, etc)
    print("Extracting property details...")
    details_extracted = df['detail'].apply(extract_details)
    details_df = pd.DataFrame(details_extracted.tolist())
    df = pd.concat([df, details_df], axis=1)
    
    # Clean usable_area
    if 'usable_area' in df.columns:
        df['usable_area'] = pd.to_numeric(
            df['usable_area'].astype(str).str.replace(r'[^\d.]', '', regex=True), 
            errors='coerce'
        )
    
    # Extract floor number
    if 'floor' in df.columns:
        df['floor_num'] = df['floor'].apply(extract_floor_num)
    
    # Convert terrace/elevator to binary
    for col in ['terrace', 'elevator']:
        if col in df.columns:
            df[col] = df[col].fillna(0).astype(int)
    
    # Remove intermediate columns
    cols_to_remove = ['locality', 'locality_dict', 'detail', 'floor', 'price', 
                      'price_czk_m2', 'price_summary_czk', 'building_condition', 'total_area']
    df = df.drop(columns=cols_to_remove, errors='ignore')
    
    # Create 500m distance binary features from POI columns
    print("Creating distance features...")
    dist_cols = [col for col in df.columns if col.startswith('poi_')]
    for col in dist_cols:
        new_col_name = col.replace('poi_', '500m_')
        df[new_col_name] = (df[col] <= 500).astype(int)
    df = df.drop(columns=dist_cols, errors='ignore')
    
    # One-hot encode categorical columns
    print("Encoding categorical variables...")
    categorical_cols = [
        'category_main_cb', 'category_sub_cb', 'category_type_cb', 
        'city', 'district', 'building_type', 'ownership', 'condition'
    ]
    categorical_cols = [c for c in categorical_cols if c in df.columns]
    df = pd.get_dummies(df, columns=categorical_cols, drop_first=True)
    
    # Rename columns for clarity
    column_mapping = {
        'price_czk': 'price',
        'lat': 'latitude',
        'lon': 'longitude',
        'usable_area': 'area_usable',
        'terrace': 'has_terrace',
        'elevator': 'has_elevator',
        'floor_num': 'floor_number',
    }
    df = df.rename(columns=column_mapping)
    
    # Calculate metro distances
    print("Calculating metro distances...")
    df[['metro_dist_A', 'metro_dist_B', 'metro_dist_C', 'nearest_station']] = df.apply(
        lambda row: get_metro_distances(row, metro), axis=1
    )
    
    # Create 1000m metro binary features
    for line in ['A', 'B', 'C']:
        col = f'metro_dist_{line}'
        if col in df.columns:
            df[f'1000m_dist_{line}'] = (df[col] <= 1000).astype(int)
    
    # One-hot encode nearest station
    df = pd.get_dummies(df, columns=['nearest_station'], drop_first=True)
    
    print(f"Final dataset: {df.shape[0]} rows, {df.shape[1]} columns")
    
    # Save if output path provided
    if output_path:
        df.to_csv(output_path, index=False)
        print(f"Saved to {output_path}")
    
    return df


if __name__ == "__main__":
    try:
        # Process raw data into final format
        df = process_raw_data(
            raw_data_path="data/data_estate.csv",
            metro_path="data/metro_stations.csv",
            output_path="data/data_estate_processed.csv"
        )
        
        print("\nProcessed data preview:")
        print(df.head())
        print(f"\nColumns: {df.columns.tolist()}")
        print("\nNotebook will automatically use this file.")
        
    except FileNotFoundError as e:
        print(f"Error: {e}")
        print("Make sure you have run the scraping scripts first.")
    except ValueError as e:
        print(f"Data error: {e}")
        print("The input data may be corrupted or in wrong format.")