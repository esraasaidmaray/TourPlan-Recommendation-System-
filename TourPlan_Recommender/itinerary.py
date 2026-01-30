import sqlite3
import logging
import random
from datetime import datetime, timedelta
import math
from typing import List, Dict, Any, Tuple

import os
from .data_preprocessor import initialize_data, get_pois_for_location, get_available_locations

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "poi.db")
logging.basicConfig(level=logging.INFO)
log = logging.getLogger("itinerary")

# ====== Themes (per spec) ======
TOUR_THEMES = {
    'cultural': {'keywords': ['museum','monument','historic','temple','gallery','heritage','church','mosque','castle','ruins'], 'boost': 0.25},
    'adventure': {'keywords': ['nature','beach','desert','hiking','diving','snorkel','quad','safari','kayak','trail','climb'], 'boost': 0.25},
    'foodies': {'keywords': ['restaurant','cafe','market','street food','bakery','eatery','diner'], 'boost': 0.30},
    'family': {'keywords': ['park','zoo','aquarium','children','playground','amusement','family'], 'boost': 0.20},
    'couples': {'keywords': ['romantic','sunset','candlelight','spa','scenic','viewpoint','resort'], 'boost': 0.25},
    'friends': {'keywords': ['bar','club','sports','fun','nightlife','escape room','bowling'], 'boost': 0.20},
}

# ====== Category normalization ======
def normalize_category(raw_type: str) -> str:
    if not raw_type:
        return "other"
    t = raw_type.lower()
    if any(x in t for x in ["hotel","resort","hostel","inn","lodg"]): return "hotel"
    if any(x in t for x in ["restaurant","cafe","bar","pub","food","eat"]): return "restaurant"
    if any(x in t for x in ["shop","mall","market","store","boutique","bazaar"]): return "shop"
    if any(x in t for x in ["museum","nature","beach","park","tourist","monument","landmark","viewpoint","temple","mosque","church","castle"]): 
        return "tourist place"
    if any(x in t for x in ["club","entertainment","nightlife"]): return "entertainment"
    return "other"

def classify_theme_text(text: str) -> List[str]:
    """Heuristic multi-label theme classifier from text."""
    if not text:
        return []
    text_l = text.lower()
    hits = []
    for theme, cfg in TOUR_THEMES.items():
        if any(kw in text_l for kw in cfg['keywords']):
            hits.append(theme)
    return hits

# ====== Diversify while forcing exactly one hotel ======
def select_with_hotel(candidates: List[Dict], plan_size:int=6, theme:str=None) -> List[Dict]:
    if plan_size < 2:
        plan_size = 2

    # pick best hotel
    hotels = [c for c in candidates if c["type"] == "hotel"]
    hotels.sort(key=lambda x: x["score"], reverse=True)
    hotel_pick = hotels[0] if hotels else None

    selected: List[Dict] = []
    seen_ids = set()

    if hotel_pick:
        selected.append(hotel_pick)
        seen_ids.add(hotel_pick["poi_id"])

    pool = [c for c in candidates if c["poi_id"] not in seen_ids]

    seen_types = {"hotel"} if hotel_pick else set()
    def theme_score(c):
        return 1 if (theme and theme in c.get("themes", [])) else 0

    pool.sort(key=lambda c: (theme_score(c), c["score"]), reverse=True)

    for c in pool:
        if len(selected) >= plan_size:
            break
        if c["poi_id"] in seen_ids:
            continue
        if c["type"] not in seen_types:
            selected.append(c)
            seen_types.add(c["type"])
            seen_ids.add(c["poi_id"])
        else:
            # allow at most 1 duplicate type if short on slots
            if sum(1 for s in selected if s["type"] == c["type"]) < 2:
                selected.append(c)
                seen_ids.add(c["poi_id"])

    # fallback: no hotel -> add dummy
    if not any(s["type"] == "hotel" for s in selected):
        selected.insert(0, {
            "poi_id": -1,
            "type": "hotel",
            "score": 0.0,
            "name": "Hotel check-in / rest",
            "description": "",
            "themes": []
        })

    # enforce single hotel
    hotels = [s for s in selected if s["type"] == "hotel"]
    if len(hotels) > 1:
        first_hotel = hotels[0]
        non_hotels = [s for s in selected if s["type"] != "hotel"]
        selected = [first_hotel] + non_hotels[:plan_size-1]

    return selected[:plan_size]

# ====== Time tiling across full day ======
def build_time_slots(start_time:str="09:00", end_time:str="22:00", n:int=6) -> List[Tuple[str,str]]:
    """Build n time slots between start and end, aligned to :00 or :30 only."""
    start = datetime.strptime(start_time, "%H:%M")
    end = datetime.strptime(end_time, "%H:%M")

    # Snap start to nearest half-hour down, end to nearest half-hour up
    def snap_down(dt: datetime) -> datetime:
        minute = 0 if dt.minute < 30 else 30
        return dt.replace(minute=minute, second=0, microsecond=0)

    def snap_up(dt: datetime) -> datetime:
        if dt.minute == 0:
            return dt.replace(second=0, microsecond=0)
        if dt.minute <= 30:
            return dt.replace(minute=30, second=0, microsecond=0)
        dt2 = dt.replace(minute=0, second=0, microsecond=0) + timedelta(hours=1)
        return dt2

    start = snap_down(start)
    end = snap_up(end)

    total_minutes = max(0, int((end - start).total_seconds() // 60))
    if n <= 0 or total_minutes == 0:
        return []

    # Compute step and round up to the next 30-minute multiple
    raw_step = math.ceil(total_minutes / n)
    step = max(30, int(math.ceil(raw_step / 30) * 30))

    slots: List[Tuple[str, str]] = []
    cur = start
    for i in range(n):
        nxt = cur + timedelta(minutes=step)
        if i == n - 1 or nxt > end:
            nxt = end
        # Ensure both times are on :00 or :30
        cur_str = cur.strftime("%H:%M")
        nxt_str = nxt.strftime("%H:%M")
        slots.append((cur_str, nxt_str))
        cur = nxt
        if cur >= end:
            break
    while len(slots) < n:
        slots.append((end.strftime("%H:%M"), end.strftime("%H:%M")))
    return slots[:n]

# ====== Public API ======
def build_itinerary(city: str = None, country: str = None, lang: str = "en",
                    plan_size: int = None, start_time: str = "09:00", end_time: str = "22:00",
                    theme: str = None) -> Dict[str, Any]:
    log.info(f"Building itinerary for city={city}, country={country}, plan_size={plan_size}, theme={theme}")

    # Initialize data preprocessor if not already done
    if not hasattr(build_itinerary, '_data_initialized'):
        log.info("Initializing data preprocessor...")
        if initialize_data():
            build_itinerary._data_initialized = True
            log.info("Data preprocessor initialized successfully")
        else:
            log.error("Failed to initialize data preprocessor")
            return {
                "days_count": 0,
                "name": f"Trip in {city}", 
                "short_description": "Failed to load data",
                "days": []
            }

    # 🔹 Use preprocessed data to find POIs
    pois_data = get_pois_for_location(city, country)
    
    if not pois_data:
        available_locations = get_available_locations()
        log.warning(f"No places found for {city}, {country}")
        log.info("Available locations:")
        for city_avail, country_avail, count in available_locations[:10]:
            log.info(f"  {city_avail}, {country_avail}: {count} POIs")
        
        return {
            "days_count": 0,
            "name": f"Trip in {city}", 
            "short_description": f"No places found for {city}, {country}",
            "days": []
        }

    # Process POIs into candidates
    candidates = []
    for poi_data in pois_data:
        base_type = normalize_category(poi_data["type"])
        themes = classify_theme_text(f"{base_type} {poi_data['name']} {poi_data['description']}")
        score = 1.0

        # boost لو فيه تطابق مع الـ theme المطلوب
        if theme and theme in themes:
            score += TOUR_THEMES[theme]["boost"]

        candidates.append({
            "poi_id": poi_data["poi_id"],
            "name": poi_data["name"],
            "type": base_type,
            "description": poi_data["description"],
            "themes": themes,
            "score": score,
            "city": poi_data["city"],
            "country": poi_data["country"]
        })

    if not candidates:
        return {
            "days_count": 0,
            "name": f"Trip in {city}", 
            "short_description": "No places found",
            "days": []
        }

    # Enhanced recommendation: Determine optimal days count (3-6) based on available places
    available_places = len(candidates)
    
    # Calculate optimal days based on available places
    if available_places >= 25:  # 5+ places per day for 5-6 days
        days_count = min(6, max(5, available_places // 5))
    elif available_places >= 20:  # 5+ places per day for 4 days
        days_count = 4
    elif available_places >= 15:  # 5+ places per day for 3 days
        days_count = 3
    else:
        # If fewer places, still create 3 days but with fewer places per day
        days_count = 3
    
    per_day = 5
    total_needed = days_count * per_day

    # 🔹 Enhanced selection: Better distribution across days
    selected = select_with_hotel(candidates, plan_size=total_needed, theme=theme)
    selected.sort(key=lambda x: (0 if x["type"] == "hotel" else 1, -x["score"]))

    # Ensure we have enough places for all days
    if len(selected) < total_needed:
        selected_ids = {s.get("poi_id") for s in selected}
        remaining = [c for c in candidates if c.get("poi_id") not in selected_ids]
        remaining.sort(key=lambda x: x.get("score", 0), reverse=True)
        
        # Add remaining places
        for c in remaining:
            if len(selected) >= total_needed:
                break
            selected.append(c)
        
        # If still short, add filler items
        while len(selected) < total_needed:
            selected.append({
                "poi_id": -2,
                "name": "Free time / transit",
                "type": "free time",
                "description": "Buffer time for rest or transit",
                "themes": [],
                "score": 0.0,
                "city": city,
                "country": country
            })

    # Enhanced distribution: Ensure each day gets diverse places
    days: List[Dict[str, Any]] = []
    for day_index in range(days_count):
        day_places = selected[day_index * per_day:(day_index + 1) * per_day]
        
        # Ensure each day has at least one non-filler place
        if day_index < len(selected) // per_day:
            day_places = selected[day_index * per_day:(day_index + 1) * per_day]
        else:
            # For remaining days, distribute remaining places
            remaining_places = selected[day_index * per_day:]
            day_places = remaining_places[:per_day]
        
        time_slots = build_time_slots(start_time, end_time, n=len(day_places))
        places_payload = []
        for (c, (s, e)) in zip(day_places, time_slots):
            places_payload.append({
                "id": c.get("poi_id"),
                "name": c.get("name"),
                "category": c.get("type"),
                "start": s,
                "end": e,
                "day": day_index + 1
            })
        days.append({
            "day": day_index + 1,
            "places": places_payload
        })

    # Enhanced plan name and short description generation
    def generate_tour_name(city: str, country: str, days_count: int) -> str:
        """Generate an engaging tour name based on city, country, and duration"""
        city_clean = city.title()
        country_clean = country.title()
        
        # Special cases for famous cities
        famous_cities = {
            "paris": "Parisian Adventure",
            "london": "London Explorer",
            "tokyo": "Tokyo Discovery",
            "new york": "NYC Experience",
            "rome": "Roman Holiday",
            "cairo": "Cairo Explorer",
            "dubai": "Dubai Luxury",
            "barcelona": "Barcelona Vibes",
            "sydney": "Sydney Explorer",
            "mumbai": "Mumbai Discovery"
        }
        
        city_key = city.lower()
        if city_key in famous_cities:
            return f"{days_count}-Day {famous_cities[city_key]}"
        else:
            return f"{days_count}-Day {city_clean} Discovery"
    
    def generate_tour_description(city: str, country: str, days_count: int, per_day: int, total_places: int) -> str:
        """Generate a compelling tour description"""
        city_clean = city.title()
        country_clean = country.title()
        
        # Create engaging descriptions based on duration
        duration_descriptions = {
            3: f"Perfect weekend getaway",
            4: f"Comprehensive exploration",
            5: f"Deep cultural immersion",
            6: f"Ultimate travel experience"
        }
        
        duration_desc = duration_descriptions.get(days_count, f"{days_count}-day adventure")
        
        return f"A {duration_desc} in {city_clean}, {country_clean}. Discover {total_places} carefully selected places across {days_count} days, with {per_day} unique experiences each day."
    
    plan_name = generate_tour_name(city, country, days_count)
    total_places = days_count * per_day
    short_desc = generate_tour_description(city, country, days_count, per_day, total_places)

    return {
        "days_count": days_count,
        "name": plan_name,
        "short_description": short_desc,
        "days": days
    }


if __name__=="__main__":
    log.info("🚀 Running itinerary.py smoke test")
    for theme in TOUR_THEMES.keys():
        print(f"\n=== {theme.capitalize()} Itinerary ===")
        result = build_itinerary(city="Cairo", country="Egypt", plan_size=6, theme=theme)
        for slot in result["slots"]:
            print(f"{slot['start']}-{slot['end']} | {slot['name']} | {slot['category']} | Score={slot['score']}")
