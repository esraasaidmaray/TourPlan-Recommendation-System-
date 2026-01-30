"""
ingest.py
---------------
Fetches data from Trekio API and stores it into a database (SQLite by default).
- Normalizes JSON structure (flattens nested descriptions).
- Stores multilingual texts in a separate table.
- Keeps raw JSON for reference/debugging.
- Exports a Parquet file for analytics.
"""
"""
pre run these commands 
pip install sqlalchemy requests
python ingest.py
"""

import requests
import json
import logging
import pandas as pd
from sqlalchemy import create_engine, Table, Column, Integer, String, Float, Text, MetaData, ForeignKey
from sqlalchemy.exc import SQLAlchemyError
#logging.basicConfig(level=logging.DEBUG)

# ----------------- Configuration -----------------
API_URL = "https://trekio.net/api/get-places-data"
DB_URL = "sqlite:///poi.db"  # Can be switched to PostgreSQL later
PARQUET_FILE = "pois.parquet"  # Path for Parquet export

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("ingest")

# ----------------- Table Definitions -----------------
meta = MetaData()

# Main POI table
pois = Table(
    "pois", meta,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("external_id", Integer, unique=True),  # Original ID from API (unique)
    Column("city_id", Integer),
    Column("city_name", Text),
    Column("country_name", Text),
    Column("type", String(50)),
    Column("latitude", Float),
    Column("longitude", Float),
    Column("location", Text),                # Google Maps link
    Column("created_at", Text),
    Column("raw_json", Text)                 # Full raw JSON stored as fallback
)

# Multilingual text table
poi_texts = Table(
    "poi_texts", meta,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("poi_id", Integer, ForeignKey("pois.id")),
    Column("lang", String(5)),               # Language code (en/ar/sq)
    Column("name", Text),
    Column("short_description", Text),
    Column("description", Text)
)

# ----------------- Helper Functions -----------------
def check_existing_poi(conn, external_id: int) -> bool:
    """Check if POI with given external_id already exists."""
    try:
        result = conn.execute(
            pois.select().where(pois.c.external_id == external_id)
        ).fetchone()
        return result is not None
    except Exception:
        return False

def fetch_page(page: int = 1, max_retries: int = 3):
    """Fetch a single page of data from the Trekio API with retry logic."""
    url = f"{API_URL}?page={page}"
    
    for attempt in range(max_retries):
        try:
            resp = requests.get(url, timeout=15)
            resp.raise_for_status()
            data = resp.json()
            
            # Log page info
            if "data" in data:
                records = data.get("data", {})
                if isinstance(records, dict):
                    count = len(records)
                elif isinstance(records, list):
                    count = len(records)
                else:
                    count = 0
                log.info(f"Page {page}: Found {count} records")
            
            return data
            
        except requests.exceptions.Timeout:
            log.warning(f"Timeout on page {page}, attempt {attempt + 1}/{max_retries}")
            if attempt == max_retries - 1:
                log.error(f"Failed to fetch page {page} after {max_retries} attempts")
                return None
        except Exception as e:
            log.error(f"Failed to fetch page {page}: {e}")
            return None
    
    return None

def flatten_description(desc_field):
    """Flatten description field (handles dicts, lists, and strings)."""
    if not desc_field:
        return ""
    if isinstance(desc_field, str):
        return desc_field
    if isinstance(desc_field, dict):
        texts = []
        for key, value in desc_field.items():
            if isinstance(value, list):
                # Handle lists of strings
                texts.extend([str(item) for item in value if item])
            elif isinstance(value, dict):
                # Handle nested dictionaries
                for sub_key, sub_value in value.items():
                    if isinstance(sub_value, list):
                        texts.extend([str(item) for item in sub_value if item])
                    else:
                        texts.append(str(sub_value))
            else:
                texts.append(str(value))
        return " ".join(texts)
    if isinstance(desc_field, list):
        return " ".join([str(x) for x in desc_field if x])  
    return str(desc_field)

# ----------------- Ingestion Logic -----------------
def ingest_data(clear_existing: bool = False):
    """Fetches all paginated data and stores normalized results into DB + Parquet."""
    engine = create_engine(DB_URL, echo=False, future=True)
    
    # Clear existing data if requested
    if clear_existing:
        log.info("Clearing existing database...")
        meta.drop_all(engine)
    
    meta.create_all(engine)

    all_pois = []       # Will be used for Parquet export
    all_texts = []      # Will be used for Parquet export

    with engine.begin() as conn:
        inserted = 0
        page = 1
        max_pages = 1000  # Safety limit to prevent infinite loops
        consecutive_empty_pages = 0
        max_empty_pages = 3  # Stop after 3 consecutive empty pages

        while page <= max_pages:
            data = fetch_page(page)
            if not data or "data" not in data:
                log.info(f"No data found on page {page} -> stopping.")
                break

            records = data.get("data", {})

            # Data can be returned as dict {"5250": {...}} or list [{...}, {...}]
            if isinstance(records, dict):
                iterable = records.values()
                record_count = len(records)
            elif isinstance(records, list):
                iterable = records
                record_count = len(records)
            else:
                log.info(f"Unexpected data format on page {page} -> stopping.")
                break

            # Check for empty page
            if record_count == 0:
                consecutive_empty_pages += 1
                log.info(f"Page {page} is empty (consecutive empty: {consecutive_empty_pages})")
                if consecutive_empty_pages >= max_empty_pages:
                    log.info(f"Stopping after {max_empty_pages} consecutive empty pages")
                    break
                page += 1
                continue
            else:
                consecutive_empty_pages = 0  # Reset counter

            # Insert each POI record
            for item in iterable:
                try:
                    external_id = item.get("id")
                    
                    # Check if POI already exists
                    if check_existing_poi(conn, external_id):
                        log.debug(f"POI with external_id {external_id} already exists, skipping...")
                        continue
                    
                    # Insert into pois table
                    poi_row = {
                        "external_id": external_id,
                        "city_id": item.get("city_id"),
                        "city_name": item.get("city_name", {}).get("en") if isinstance(item.get("city_name"), dict) else item.get("city_name"),
                        "country_name": item.get("country_name", {}).get("en") if isinstance(item.get("country_name"), dict) else item.get("country_name"),
                        "type": item.get("type"),
                        "latitude": item.get("latitude"),
                        "longitude": item.get("longitude"),
                        "location": item.get("location"),
                        "created_at": item.get("created_at"),
                        "raw_json": json.dumps(item, ensure_ascii=False)
                    }
                    res = conn.execute(pois.insert().values(**poi_row))
                    poi_id = res.inserted_primary_key[0]

                    # Collect for Parquet export
                    poi_row["db_id"] = poi_id
                    all_pois.append(poi_row)

                    # Insert multilingual texts
                    for lang in ["en", "ar", "sq"]:
                        nm = short = desc = None

                        # Name
                        if isinstance(item.get("name"), dict):
                            nm = item["name"].get(lang)
                        elif isinstance(item.get("name"), str):
                            nm = item["name"]

                        # Short description
                        if isinstance(item.get("short_description"), dict):
                            short = item["short_description"].get(lang)
                        elif isinstance(item.get("short_description"), str):
                            short = item["short_description"]

                        # Long description
                        desc_raw = None
                        if isinstance(item.get("description"), dict):
                            desc_raw = item["description"].get(lang)
                        elif isinstance(item.get("description"), str):
                            desc_raw = item["description"]

                        desc = flatten_description(desc_raw)

                        text_row = {
                            "poi_id": poi_id,
                            "lang": lang,
                            "name": nm,
                            "short_description": short,
                            "description": desc
                        }
                        conn.execute(poi_texts.insert().values(**text_row))
                        all_texts.append(text_row)

                    inserted += 1

                except SQLAlchemyError as e:
                    log.error(f"Database insert error: {e}")
                    continue

            log.info(f"Finished page {page} with {record_count} records (Total inserted so far: {inserted})")
            page += 1  # Move to next page

        log.info(f"Total inserted: {inserted} POIs")

    # ----------------- Export to Parquet -----------------
    try:
        df_pois = pd.DataFrame(all_pois)
        df_texts = pd.DataFrame(all_texts)

        with pd.ExcelWriter("pois_and_texts.xlsx") as writer:
            df_pois.to_excel(writer, sheet_name="pois", index=False)
            df_texts.to_excel(writer, sheet_name="poi_texts", index=False)

        df_pois.to_parquet("pois.parquet", index=False)
        df_texts.to_parquet("poi_texts.parquet", index=False)

        log.info(f"Parquet export completed: pois.parquet & poi_texts.parquet")
    except Exception as e:
        log.error(f"Failed to export Parquet: {e}")

if __name__ == "__main__":
    import sys
    
    # Check if user wants to clear existing data
    clear_existing = "--clear" in sys.argv
    
    if clear_existing:
        print("⚠️  WARNING: This will delete all existing data!")
        response = input("Are you sure? (y/N): ")
        if response.lower() != 'y':
            print("Operation cancelled.")
            sys.exit(0)
    
    ingest_data(clear_existing=clear_existing)
