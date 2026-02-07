"""
Scrape additional estate details from Sreality API.
This script fetches detailed information (floor, elevator, building type, etc.)
for each estate listing. It requires hash_ids from the initial scraping.
"""

import asyncio
import httpx
import pandas as pd
from tqdm.asyncio import tqdm

MAX_CONCURRENT_REQUESTS = 10


async def get_estate_detail(client, hash_id, semaphore):
    """Fetch detailed info for single estate from Sreality API."""
    url = f"https://www.sreality.cz/api/cs/v2/estates/{hash_id}"
    headers = {"User-Agent": "Mozilla/5.0"}
    
    async with semaphore:
        try:
            await asyncio.sleep(0.05)  # Small delay to not overwhelm server
            r = await client.get(url, headers=headers, timeout=15)
            r.raise_for_status()
            data_json = r.json()
            
            items = data_json.get("items", [])
            detail = items if items else None
            return {'hash_id': hash_id, 'detail': detail}
        except Exception as e:
            return {'hash_id': hash_id, 'detail': f"Error: {e}"}


async def run_scraping(hash_ids):
    """Run async scraping for all hash_ids."""
    semaphore = asyncio.Semaphore(MAX_CONCURRENT_REQUESTS)
    limits = httpx.Limits(max_keepalive_connections=5, max_connections=MAX_CONCURRENT_REQUESTS)
    
    async with httpx.AsyncClient(limits=limits, follow_redirects=True) as client:
        tasks = [get_estate_detail(client, hid, semaphore) for hid in hash_ids]
        results = await tqdm.gather(*tasks)
        return results


def scrape_details_for_estates(hash_ids):
    """Main function to scrape estate details."""
    results = asyncio.run(run_scraping(hash_ids))
    return pd.DataFrame(results)


if __name__ == "__main__":
    
    try:
        from scraping_functions import sreality_scrape
        
        basic_data = sreality_scrape()
        
        if 'hash_id' not in basic_data.columns:
            raise ValueError("Missing hash_id column in scraped data")
        
        hash_ids = basic_data["hash_id"].tolist()
        details_df = scrape_details_for_estates(hash_ids)
        merged = details_df.merge(basic_data, on='hash_id', how='left')
        merged.to_csv("data/data_estate.csv", index=False)
        print("Saved to data/data_estate.csv")
        
    except ImportError:
        print("Error: Could not import scraping_functions.py")
    except ValueError as e:
        print(f"Data error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")
