import pandas as pd
import numpy as np
import statsmodels.api as sm
from statsmodels.stats.outliers_influence import variance_inflation_factor

# --- Dowloand and cleaning data  ---
def load_and_prepare_data(flats_path, metro_path):
    # Loanding files
    df_flats = pd.read_csv(flats_path)
    df_metro = pd.read_csv(metro_path)

    # Get price per m2
    df_flats['price_per_m2'] = df_flats['price'] / df_flats['area_usable']

    # Get station names from dummies
    station_cols = [c for c in df_flats.columns if c.startswith('nearest_station_')]
    df_flats['nearest_station'] = df_flats[station_cols].idxmax(axis=1).str.replace('nearest_station_', '')

    # Merge everything
    df_final = pd.merge(df_flats, df_metro[['name', 'line']],
                        left_on='nearest_station', right_on='name', how='left')

    return df_final.dropna(subset=['price_per_m2', 'line'])

# --- Basic analysis ---
def show_market_analysis(df):
    # Station prices
    station_stats = df.groupby('nearest_station')['price_per_m2'].mean().sort_values(ascending=False)

    print("--- Station Prices ---")
    print(f"Top 10 Most Expensive:\n{station_stats.head(10)}")
    print(f"\nTop 10 Cheapest:\n{station_stats.tail(10)}")

    # Prices by line
    line_stats = df.groupby('line')['price_per_m2'].mean().sort_values(ascending=False)
    print("\n--- Average Price by Line ---")
    print(line_stats)

    # Compare line A and C

    diff_ac = (line_stats['A'] / line_stats['C'] - 1) * 100
    print(f"\nLine A is {diff_ac:.2f}% more expensive than Line C")

# --- OLS Model ---
def run_regression_model(df, features):
    # Clean the data
    q_low, q_high = df['price'].quantile([0.05, 0.95])
    df_clean = df[(df['price'] > q_low) & (df['price'] < q_high)].copy()

    # Use log price
    df_clean['log_price'] = np.log(df_clean['price'])

    # Preparatin of  X and y
    df_model = df_clean.dropna(subset=['log_price'] + features)
    y = df_model['log_price']
    X = sm.add_constant(df_model[features])

    # Run OLS
    model = sm.OLS(y, X).fit()
    print("\n--- OLS Results ---")
    print(model.summary())

    # Check VIF (Multicollinearity)
    print("\n--- VIF Check ---")
    for i in range(1, X.shape[1]):
        vif = variance_inflation_factor(X.values, i)
        print(f"{X.columns[i]}: {vif:.2f}")

# --- Run ---

# Files
flats_file = "data_estate_processed_06012026 (1).csv"
metro_file = "metro_stations (1).csv"

# Start
data = load_and_prepare_data(flats_file, metro_file)
show_market_analysis(data)

# Run model
selected_features = ['area_usable', 'floor_number', 'has_elevator', '500m_metro_distance']
run_regression_model(data, selected_features)
