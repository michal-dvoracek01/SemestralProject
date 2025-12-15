import pandas as pd
import googlemaps
import time
import requests
from google.cloud import secretmanager

def get_secret(project_id, secret_id, version_id="latest"):
    client = secretmanager.SecretManagerServiceClient()
    name = f"projects/{project_id}/secrets/{secret_id}/versions/{version_id}"
    response = client.access_secret_version(name=name)
    return response.payload.data.decode("UTF-8")


def load_metro_data(api_key, sleep_time=0.1):
    """
    Loads Prague metro stations and fetches GPS coordinates using Google Maps API.
    
    Returns:
        pandas.DataFrame with columns: line, name, lat, lng
    """

    prague_metro = {
        "A": [
            "Nemocnice Motol", "Petřiny", "Nádraží Veleslavín", "Bořislavka",
            "Dejvická", "Hradčanská", "Malostranská", "Staroměstská",
            "Můstek", "Muzeum", "Náměstí Míru", "Jiřího z Poděbrad",
            "Flora", "Želivského", "Strašnická", "Skalka", "Depo Hostivař"
        ],
        "B": [
            "Zličín", "Stodůlky", "Luka", "Lužiny", "Hůrka",
            "Nové Butovice", "Jinonice", "Radlická", "Smíchovské nádraží",
            "Anděl", "Karlovo náměstí", "Národní třída", "Můstek",
            "Náměstí Republiky", "Florenc", "Křižíkova", "Invalidovna",
            "Palmovka", "Českomoravská", "Vysočanská", "Kolbenova",
            "Hloubětín", "Rajská zahrada", "Černý Most"
        ],
        "C": [
            "Letňany", "Prosek", "Střížkov", "Ládví", "Kobylisy",
            "Nádraží Holešovice", "Vltavská", "Florenc", "Hlavní nádraží",
            "Muzeum", "I. P. Pavlova", "Vyšehrad", "Pražského povstání",
            "Pankrác", "Budějovická", "Kačerov", "Roztyly",
            "Chodov", "Opatov", "Háje"
        ]
    }

    gmaps = googlemaps.Client(key=api_key)

    records = []

    def get_station_coordinates(line, station_name):
        try:
            query = f"Metro {line} {station_name}, Prague, Czech Republic"
            response = gmaps.places(query=query)

            if response["status"] == "OK" and response["results"]:
                loc = response["results"][0]["geometry"]["location"]
                return loc["lat"], loc["lng"]
            else:
                return None, None

        except Exception as e:
            print(f"Error for {station_name}: {e}")
            return None, None

    print("Starting GPS extraction...")

    for line, stations in prague_metro.items():
        print(f"--- Line {line} ---")

        for station in stations:
            lat, lng = get_station_coordinates(line, station)

            records.append({
                "line": line,
                "name": station,
                "lat": lat,
                "lng": lng
            })

            print(f"{station}: {lat}, {lng}")
            time.sleep(sleep_time)

    return pd.DataFrame(records)

import requests
import pandas as pd


def sreality_scrape():
    """Scrapes flat listings from Sreality.cz for Prague based on building conditions.
    """
    BASE_URL = (
        "https://www.sreality.cz/api/v1/estates/search?"
        "category_main_cb=1"
        "&locality_country_id=112"
        "&locality_region_id=10"
        "&building_condition={condition}"
        "&ownership=1"
        "&limit={limit}"
        "&offset={offset}"
        "&sort=-date"
        "&lang=cs"
    )

    limit = 22
    all_dfs = []

    condition_map = {
        1: "very good",
        2: "good",
        4: "in development",
        6: "new"
    }

    for condition_code, condition_name in condition_map.items():
        print(f"\n🔄 Downloading flats: {condition_name}")
        offset = 0
        total_results = float("inf")
        all_results = []

        try:
            while offset < total_results:
                url = BASE_URL.format(
                    condition=condition_code,
                    limit=limit,
                    offset=offset
                )

                response = requests.get(url)
                response.raise_for_status()
                data = response.json()

                results = data.get("results", [])
                if not results:
                    break

                all_results.extend(results)

                if total_results == float("inf"):
                    total_results = data["pagination"]["total"]

                offset += limit

            df = pd.DataFrame(all_results)
            df["condition"] = condition_name

            print(f"✅ {len(df)} flats downloaded ({condition_name})")
            all_dfs.append(df)

        except requests.exceptions.RequestException as e:
            print(f"❌ Error for condition {condition_name}: {e}")

    return pd.concat(all_dfs, ignore_index=True)

if __name__ == "__main__":

    API_KEY = get_secret(
    project_id="325399643255",
    secret_id="API_KEY_Google"
    )
    metro_df = load_metro_data(API_KEY)
    print("\nMetro data preview:")
    print(metro_df.head())

    sreality_df = sreality_scrape()
    print("\nSreality data preview:")
    print(sreality_df.head())