"""
Data Preprocessor for Travel Planner
=====================================
Fetches all POI data from database and creates comprehensive lookup system
"""

import sqlite3
import logging
from typing import Dict, List, Any, Tuple
from collections import defaultdict
import os

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "poi.db")
logging.basicConfig(level=logging.INFO)
log = logging.getLogger("data_preprocessor")

class POIDataPreprocessor:
    """Preprocesses and stores all POI data for fast lookup"""
    
    def __init__(self):
        self.all_pois: List[Dict] = []
        self.city_country_lookup: Dict[Tuple[str, str], List[Dict]] = defaultdict(list)
        self.city_lookup: Dict[str, List[Dict]] = defaultdict(list)
        self.country_lookup: Dict[str, List[Dict]] = defaultdict(list)
        self.available_locations: List[Tuple[str, str, int]] = []
        self.is_loaded = False
        
    def load_all_data(self, lang: str = "en") -> bool:
        """Load all POI data from database and create lookup structures"""
        try:
            log.info("Loading all POI data from database...")
            conn = sqlite3.connect(DB_PATH)
            cur = conn.cursor()
            
            # Fetch all POIs with their text data
            cur.execute("""
                SELECT p.id, pt.name, p.type, pt.description, p.city_name, p.country_name
                FROM pois p
                LEFT JOIN poi_texts pt ON p.id = pt.poi_id AND pt.lang=?
                ORDER BY p.city_name, p.country_name, p.id
            """, (lang,))
            
            rows = cur.fetchall()
            conn.close()
            
            if not rows:
                log.error("No data found in database")
                return False
            
            # Process all POIs
            self.all_pois = []
            for poi_id, name, raw_type, desc, city_name, country_name in rows:
                if not city_name or not country_name:
                    continue
                    
                poi_data = {
                    "poi_id": poi_id,
                    "name": name or "Unknown",
                    "type": raw_type or "other",
                    "description": desc or "",
                    "city": city_name.strip(),
                    "country": country_name.strip(),
                    "city_lower": city_name.lower().strip(),
                    "country_lower": country_name.lower().strip()
                }
                
                self.all_pois.append(poi_data)
                
                # Create lookup structures
                city_key = city_name.lower().strip()
                country_key = country_name.lower().strip()
                city_country_key = (city_key, country_key)
                
                self.city_country_lookup[city_country_key].append(poi_data)
                self.city_lookup[city_key].append(poi_data)
                self.country_lookup[country_key].append(poi_data)
            
            # Create available locations list
            location_counts = defaultdict(int)
            for poi in self.all_pois:
                key = (poi["city"], poi["country"])
                location_counts[key] += 1
            
            self.available_locations = [
                (city, country, count) 
                for (city, country), count in location_counts.items()
            ]
            self.available_locations.sort(key=lambda x: x[2], reverse=True)
            
            self.is_loaded = True
            log.info(f"Loaded {len(self.all_pois)} POIs from {len(self.available_locations)} locations")
            
            # Log top locations for debugging
            log.info("Top 10 locations by POI count:")
            for city, country, count in self.available_locations[:10]:
                log.info(f"  {city}, {country}: {count} POIs")
            
            return True
            
        except Exception as e:
            log.error(f"Error loading data: {e}")
            return False
    
    def find_pois_for_location(self, city: str, country: str) -> List[Dict]:
        """Find POIs for a specific city/country with fuzzy matching"""
        if not self.is_loaded:
            log.warning("Data not loaded, attempting to load...")
            if not self.load_all_data():
                return []
        
        city_clean = city.lower().strip()
        country_clean = country.lower().strip()
        
        # Try exact match first
        exact_key = (city_clean, country_clean)
        if exact_key in self.city_country_lookup:
            pois = self.city_country_lookup[exact_key]
            log.info(f"Found {len(pois)} POIs for exact match: {city}, {country}")
            return pois
        
        # Try city-only match
        if city_clean in self.city_lookup:
            pois = self.city_lookup[city_clean]
            log.info(f"Found {len(pois)} POIs for city match: {city}")
            return pois
        
        # Try country-only match
        if country_clean in self.country_lookup:
            pois = self.country_lookup[country_clean]
            log.info(f"Found {len(pois)} POIs for country match: {country}")
            return pois
        
        # Try fuzzy matching
        fuzzy_matches = []
        for poi in self.all_pois:
            city_match = city_clean in poi["city_lower"] or poi["city_lower"] in city_clean
            country_match = country_clean in poi["country_lower"] or poi["country_lower"] in country_clean
            
            if city_match or country_match:
                fuzzy_matches.append(poi)
        
        if fuzzy_matches:
            log.info(f"Found {len(fuzzy_matches)} POIs for fuzzy match: {city}, {country}")
            return fuzzy_matches
        
        # No matches found
        log.warning(f"No POIs found for {city}, {country}")
        log.info("Available locations:")
        for city_avail, country_avail, count in self.available_locations[:10]:
            log.info(f"  {city_avail}, {country_avail}: {count} POIs")
        
        return []
    
    def get_available_locations(self) -> List[Tuple[str, str, int]]:
        """Get list of all available locations with POI counts"""
        return self.available_locations.copy()
    
    def get_location_suggestions(self, partial_city: str = "", partial_country: str = "") -> List[Tuple[str, str, int]]:
        """Get location suggestions based on partial input"""
        suggestions = []
        partial_city_lower = partial_city.lower()
        partial_country_lower = partial_country.lower()
        
        for city, country, count in self.available_locations:
            city_match = not partial_city_lower or partial_city_lower in city.lower()
            country_match = not partial_country_lower or partial_country_lower in country.lower()
            
            if city_match or country_match:
                suggestions.append((city, country, count))
        
        return suggestions[:20]  # Limit to top 20 suggestions

# Global instance
preprocessor = POIDataPreprocessor()

def initialize_data():
    """Initialize the data preprocessor"""
    return preprocessor.load_all_data()

def get_pois_for_location(city: str, country: str) -> List[Dict]:
    """Get POIs for a specific location"""
    return preprocessor.find_pois_for_location(city, country)

def get_available_locations() -> List[Tuple[str, str, int]]:
    """Get all available locations"""
    return preprocessor.get_available_locations()

def get_location_suggestions(partial_city: str = "", partial_country: str = "") -> List[Tuple[str, str, int]]:
    """Get location suggestions"""
    return preprocessor.get_location_suggestions(partial_city, partial_country)

if __name__ == "__main__":
    # Test the preprocessor
    log.info("Testing data preprocessor...")
    if initialize_data():
        log.info("Data loaded successfully!")
        
        # Test some locations
        test_locations = [
            ("Cairo", "Egypt"),
            ("Paris", "France"),
            ("Tokyo", "Japan"),
            ("New York", "USA"),
            ("London", "UK")
        ]
        
        for city, country in test_locations:
            pois = get_pois_for_location(city, country)
            log.info(f"{city}, {country}: {len(pois)} POIs found")
    else:
        log.error("Failed to load data")
