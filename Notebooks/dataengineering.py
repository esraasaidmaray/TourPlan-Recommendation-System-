# import subprocess
# import sys
# import requests
# import pandas as pd
# import json
# import numpy as np
# from typing import Dict, List, Optional
# import time
# from urllib.parse import urljoin
# import warnings
# from requests.adapters import HTTPAdapter
# from urllib3.util.retry import Retry

# warnings.filterwarnings("ignore")


# def install(package: str):
#     subprocess.check_call([sys.executable, "-m", "pip", "install", package])


# for pkg in ["requests", "pandas", "numpy", "scikit-learn"]:
#     try:
#         __import__(pkg.replace("-", "_"))
#     except ImportError:
#         install(pkg)


# class HotelDataProcessor:
#     def __init__(self, base_url: str = "https://trekio.net/api/get-places-data",
#                 retries: int = 3, backoff_factor: float = 0.3):
#         self.base_url = base_url
#         self.raw_data: List[Dict] = []
#         self.processed_df: Optional[pd.DataFrame] = None

#         # session with retries
#         self.session = requests.Session()
#         retry = Retry(total=retries, backoff_factor=backoff_factor,
#                     status_forcelist=[429, 500, 502, 503, 504],
#                     allowed_methods=frozenset(['GET', 'POST']))
#         self.session.mount("https://", HTTPAdapter(max_retries=retry))
#         self.session.mount("http://", HTTPAdapter(max_retries=retry))

#     def fetch_single_page(self, page: int = 1, delay: float = 0.5,
#                         sample: bool = False, timeout: int = 30) -> Optional[Dict]:
#         try:
#             time.sleep(delay)
#             resp = self.session.get(self.base_url, params={"page": page}, timeout=timeout)
#             resp.raise_for_status()
#             data = resp.json()

#             if sample:
#                 if isinstance(data, list):
#                     return data[:2]
#                 if isinstance(data, dict) and "data" in data:
#                     d = data["data"]
#                     if isinstance(d, dict):
#                         return list(d.values())[:2]
#                     if isinstance(d, list):
#                         return d[:2]

#             return data
#         except requests.RequestException as e:
#             print(f"Error fetching page {page}: {e}")
#             return None

#     def fetch_all_data(self, max_pages: int = None, delay: float = 0.5) -> List[Dict]:
#         all_data: List[Dict] = []

#         first_page = self.fetch_single_page(1, delay)
#         if not first_page:
#             print("Invalid response or empty first page.")
#             return []

#         total_pages = first_page.get("last_page", 1)
#         if max_pages:
#             max_pages = min(max_pages, total_pages)
#         else:
#             max_pages = total_pages

#         # collect data from first page
#         if "data" in first_page:
#             d = first_page["data"]
#             if isinstance(d, dict):
#                 all_data.extend(list(d.values()))
#             elif isinstance(d, list):
#                 all_data.extend(d)

#         # collect remaining pages
#         for page in range(2, max_pages + 1):
#             page_data = self.fetch_single_page(page, delay)
#             if page_data and "data" in page_data:
#                 d = page_data["data"]
#                 if isinstance(d, dict):
#                     all_data.extend(list(d.values()))
#                 elif isinstance(d, list):
#                     all_data.extend(d)
#             else:
#                 print(f"Warning: failed to fetch or parse page {page}")

#         self.raw_data = all_data
#         return all_data

#     def explore_data_structure(self, sample_size: int = 5):
#         if not self.raw_data:
#             print("No data available. Call fetch_all_data first.")
#             return

#         print("=" * 60)
#         print("Data structure analysis")
#         print("=" * 60)
#         print(f"Total records: {len(self.raw_data)}")

#         sample_hotel = self.raw_data[0]
#         print("\nFirst record keys and value types:")
#         for k, v in sample_hotel.items():
#             if isinstance(v, dict):
#                 print(f"  {k}: dict keys -> {list(v.keys())}")
#             elif isinstance(v, list):
#                 print(f"  {k}: list length -> {len(v)}")
#             else:
#                 s = str(v) if v is not None else "None"
#                 print(f"  {k}: {type(v).__name__} -> {s[:80]}")

#         # languages
#         languages = set()
#         for hotel in self.raw_data[:10]:
#             name = hotel.get("name")
#             if isinstance(name, dict):
#                 languages.update(name.keys())

#         print("\nAvailable languages (sample of first 10 records):", list(languages))

#         # sample multilingual names if present
#         if isinstance(sample_hotel.get("name"), dict):
#             print("\nSample names:")
#             for lang, nm in sample_hotel["name"].items():
#                 print(f"  {lang}: {nm}")

#         # description (english) sample
#         if isinstance(sample_hotel.get("description"), dict):
#             en_desc = sample_hotel["description"].get("en", {})
#             if isinstance(en_desc, dict):
#                 print("\nDescription (en) sections:")
#                 for sec, items in en_desc.items():
#                     if isinstance(items, list):
#                         print(f"  {sec}: {len(items)} items. example -> {items[0][:80] if items else ''}")

#         # geography and types
#         cities = set()
#         countries = set()
#         types = set()
#         for hotel in self.raw_data:
#             cities.add(hotel.get("city_name", ""))
#             countries.add(hotel.get("country_name", ""))
#             types.add(hotel.get("type", ""))

#         print("\nGeography:")
#         print(f"  unique cities: {len([c for c in cities if c])}")
#         print(f"  unique countries: {len([c for c in countries if c])}")
#         print(f"  types sample: {list(types)[:10]}")

#     def preprocess_data(self, target_language: str = "en") -> pd.DataFrame:
#         if not self.raw_data:
#             print("No data available. Call fetch_all_data first.")
#             return pd.DataFrame()

#         rows = []
#         for hotel in self.raw_data:
#             row = {
#                 "hotel_id": hotel.get("id", ""),
#                 "city_id": hotel.get("city_id", ""),
#                 "hotel_name": self._extract_multilingual_text(hotel.get("name", {}), target_language),
#                 "short_description": self._extract_multilingual_text(hotel.get("short_description", {}), target_language),
#                 "city_name": hotel.get("city_name", ""),
#                 "country_name": hotel.get("country_name", ""),
#                 "type": hotel.get("type", ""),
#                 "latitude": hotel.get("latitude", 0.0),
#                 "longitude": hotel.get("longitude", 0.0),
#                 "location_url": hotel.get("location", ""),
#                 "created_at": hotel.get("created_at", "")
#             }

#             desc = hotel.get("description", {}).get(target_language, {})
#             if not isinstance(desc, dict):
#                 desc = {}

#             services = desc.get("Services & Facilities", [])
#             rooms = desc.get("Rooms", [])
#             attractions = desc.get("Nearby Attractions", [])
#             location_desc = " ".join(desc.get("Location", []))

#             row.update({
#                 "location_description": location_desc,
#                 "num_services": len(services),
#                 "services_list": "; ".join(services) if services else "",
#                 "has_concierge": any("concierge" in s.lower() for s in services),
#                 "has_fitness": any("fitness" in s.lower() or "gym" in s.lower() for s in services),
#                 "has_spa": any("spa" in s.lower() for s in services),
#                 "has_pool": any("pool" in s.lower() for s in services),
#                 "has_restaurant": any("restaurant" in s.lower() or "dining" in s.lower() for s in services),
#                 "num_room_features": len(rooms),
#                 "rooms_description": "; ".join(rooms) if rooms else "",
#                 "has_city_views": any("city view" in r.lower() for r in rooms),
#                 "has_balcony": any("balcon" in r.lower() for r in rooms),
#                 "has_smart_tech": any("smart" in r.lower() or "tech" in r.lower() for r in rooms),
#                 "num_attractions": len(attractions),
#                 "attractions_list": "; ".join(attractions) if attractions else "",
#                 "near_mosque": any("mosque" in a.lower() for a in attractions),
#                 "near_beach": any("beach" in a.lower() for a in attractions),
#                 "near_market": any("market" in a.lower() for a in attractions),
#                 "desc_length": len(self._extract_multilingual_text(hotel.get("short_description", {}), target_language))
#             })

#             row["total_features"] = row["num_services"] + row["num_room_features"] + row["num_attractions"]
#             rows.append(row)

#         self.processed_df = pd.DataFrame(rows)

#         self._create_price_category()
#         self._create_location_clusters()
#         self._create_feature_scores()

#         return self.processed_df

#     def _extract_multilingual_text(self, field, lang="en") -> str:
#         if isinstance(field, dict):
#             if lang in field:
#                 return field.get(lang, "")
#             for v in field.values():
#                 if isinstance(v, str) and v:
#                     return v
#             return ""
#         if isinstance(field, str):
#             return field
#         return ""

#     def _create_price_category(self):
#         if self.processed_df is None or self.processed_df.empty:
#             return
#         self.processed_df["price_category"] = "unknown"

#     def _create_location_clusters(self):
#         if self.processed_df is None or self.processed_df.empty:
#             return
#         self.processed_df["location_cluster"] = -1

#     def _create_feature_scores(self):
#         if self.processed_df is None or self.processed_df.empty:
#             return
#         bool_cols = ["has_concierge", "has_fitness", "has_spa", "has_pool", "has_restaurant",
#                     "has_city_views", "has_balcony", "has_smart_tech", "near_mosque", "near_beach", "near_market"]
#         for col in bool_cols:
#             if col not in self.processed_df.columns:
#                 self.processed_df[col] = False
#         self.processed_df["feature_score"] = self.processed_df[bool_cols].sum(axis=1).astype(int)


import os
import requests
import pandas as pd


# --------------------------
# Helper: normalize nested fields
# --------------------------
def normalize_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """
    Ensure all values are scalars (stringify dicts/lists) 
    so we can save to CSV/Parquet without errors.
    """
    for col in df.columns:
        df[col] = df[col].apply(
            lambda x: x if isinstance(x, (str, int, float, bool, type(None))) else str(x)
        )
    return df


# --------------------------
# Fetch Users API (one page)
# --------------------------
def fetch_users(url="http://trekio.net/api/admin/users") -> pd.DataFrame:
    print(f"Fetching users from {url}")
    r = requests.get(url)
    if r.status_code != 200:
        raise Exception(f"API error {r.status_code}: {r.text}")
    
    data = r.json()
    raw_items = data.get("data", data)
    if not isinstance(raw_items, list):
        raise Exception(f"Unexpected 'data' format: {type(raw_items)}")

    df = pd.DataFrame(raw_items)
    df["source"] = "users"
    df = normalize_dataframe(df)
    print(f"✅ Users fetched: {len(df)}")
    return df


# --------------------------
# Fetch Places API (paginated)
# --------------------------
def fetch_places(base_url="http://trekio.net/api/get-places-data") -> pd.DataFrame:
    print(f"Fetching places from {base_url}")

    all_data = []
    url = base_url
    page_num = 1

    while url:
        print(f"➡️ Page {page_num}: {url}")
        r = requests.get(url)
        if r.status_code != 200:
            raise Exception(f"API error {r.status_code}: {r.text}")
        
        data = r.json()
        raw_items = data.get("data", [])
        if isinstance(raw_items, dict):
            raw_items = raw_items.get("items") or list(raw_items.values())
        if not isinstance(raw_items, list):
            raise Exception(f"Unexpected 'data' format: {type(raw_items)}")

        all_data.extend(raw_items)

        # pagination
        url = data.get("next_page_url")
        page_num += 1

    df = pd.DataFrame(all_data)
    df["source"] = "places"
    df = normalize_dataframe(df)
    print(f"✅ Places fetched: {len(df)}")
    return df


# --------------------------
# Combine Users + Places
# --------------------------
def build_dataset(users_url="http://trekio.net/api/admin/users",
                  places_url="http://trekio.net/api/get-places-data",
                  final_csv="combined.csv",
                  final_parquet="combined.parquet"):
    users_df = fetch_users(users_url)
    places_df = fetch_places(places_url)

    # Union of columns
    all_cols = list(set(users_df.columns).union(set(places_df.columns)))
    users_df = users_df.reindex(columns=all_cols)
    places_df = places_df.reindex(columns=all_cols)

    # Merge
    combined_df = pd.concat([users_df, places_df], ignore_index=True)

    # Save
    combined_df.to_csv(final_csv, index=False, encoding="utf-8")
    combined_df.to_parquet(final_parquet, index=False, engine="pyarrow")

    print(f"✅ Combined dataset built: {len(combined_df)} rows")
    print(f"💾 Saved to {final_csv} and {final_parquet}")

    return combined_df


# --------------------------
# Run
# --------------------------
if __name__ == "__main__":
    df = build_dataset()
    print("Columns:", df.columns.tolist())
