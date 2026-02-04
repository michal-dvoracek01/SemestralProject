# Prague Real Estate Price Predictor and Metro Index

A data science project analyzing real estate prices in Prague based on proximity to metro stations.

## Project Overview

This project:
- Scrapes apartment listings from Sreality.cz (Czech real estate portal)
- Calculates distances to Prague Metro stations (Lines A, B, C)
- Analyzes price differences by metro station and line
- Builds a Linear Regression model to predict apartment prices

## Repository Structure
    
```
├── Estate_PRG.ipynb              # Main analysis notebook (run this!)
├── data/
│   ├── data_estate_processed_06012026.csv  # Processed dataset (ready to use)
│   └── metro_stations.csv        # Metro station coordinates
├── scraping_functions.py         # Step 1: Scrape basic listings from Sreality API
├── scrape_estate_details.py      # Step 2: Scrape additional details (floor, elevator)
├── data_preprocessing.py         # Step 3: Process raw data → final CSV
├── notebook_scraping.ipynb       # Scraping development notebook
├── requirements.txt              # Python dependencies
└── README.md
```

## How to Run

### Environment Setup
```bash
# Create virtual environment
python3 -m venv venv

# Activate it
# On macOS/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Run the Analysis
```bash
# Run the main analysis notebook
jupyter notebook Estate_PRG.ipynb
```

The notebook uses pre-processed data (`data/data_estate_processed_06012026.csv`) and runs without any additional setup.

### Fresh Data (Optional)

If you want to scrape fresh data instead of using the provided dataset:

```bash
# Step 1: Scrape basic listings from Sreality
python scraping_functions.py

# Step 2: Fetch additional details (floor, elevator, etc.)
python scrape_estate_details.py

# Step 3: Process into final format
python data_preprocessing.py

# Step 4: Run analysis
jupyter notebook Estate_PRG.ipynb
```

**Notes:**
- `metro_stations.csv` is pre-provided (metro stations are static infrastructure). Regenerating it requires Google Maps API credentials.
- Sreality listings change daily, so fresh scraping will produce different (but similar) results.
- The notebook automatically uses freshly processed data if available.

## Data Description

The dataset contains ~2800 apartment listings with features:
- **Price**: Total price in CZK
- **Area**: Usable area in m²
- **Location**: GPS coordinates, district (Praha 1-10)
- **Building**: Type (panel, brick, etc.), floor number
- **Amenities**: Elevator, terrace
- **Metro**: Distance to nearest station on each line (A, B, C)

## Analysis Results

- Most expensive stations are in the center: Malostranská (198k/m²), Muzeum (193k/m²), Náměstí Míru (192k/m²)
- Cheapest stations: Hlavní nádraží (123k/m²), Černý Most (132k/m²), Letňany (137k/m²)
- Metro line matters less than I expected - only ~3% difference between Line A and C
- Apartment area is the strongest predictor of price (correlation 0.66)
- See Estate_PRG.ipynb for more details

## Requirements

- Python 3.9+
- See `requirements.txt` for packages

## Disclaimer

This project is for educational purposes only.