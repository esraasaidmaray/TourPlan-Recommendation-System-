# itinerary.py
import sqlite3
import logging
import random
from datetime import datetime, timedelta
from typing import List, Dict, Any, Tuple

DB_PATH = "poi.db"
logging.basicConfig(level=logging.INFO)
log = logging.getLogger("itinerary")

# ====== Themes (per spec) ======
TOUR_THEMES = {
    'cultural': {'boost': 0.25},
    'adventure': {'boost': 0.25},
    'foodies': {'boost': 0.30},
    'family': {'boost': 0.20},
    'couples': {'boost': 0.25},
    'friends': {'boost': 0.20},
}

# ====== Light type normalization ======
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

# ====== Fetch POIs directly from DB (using theme column) ======
def fetch_candidates(city:str=None, country:str=None, lang:str="en", theme:str=None, limit:int=200) -> List[Dict]:
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    query = """
        SELECT p.id, pt.name, p.type, pt.description, p.city_name, p.country_name, pt.theme
        FROM pois p
        LEFT JOIN poi_texts pt ON p.id = pt.poi_id AND pt.lang=?
        WHERE LOWER(p.city_name) = LOWER(?) AND LOWER(p.country_name) = LOWER(?)
        LIMIT ?
    """
    cur.execute(query, (lang, city, country, limit))
    rows = cur.fetchall()
    conn.close()

    candidates = []
    for r in rows:
        poi_id, name, raw_type, desc, city_name, country_name, theme_db = r
        base_type = normalize_category(raw_type)
        score = 1.0

        # boost لو theme المطلوب نفس اللي في DB
        if theme and theme_db == theme:
            score += TOUR_THEMES[theme]["boost"]

        candidates.append({
            "poi_id": poi_id,
            "name": name or "Unknown",
            "type": base_type,
            "description": desc or "",
            "themes": [theme_db] if theme_db else [],
            "city": city_name,
            "country": country_name,
            "score": score
        })

    # shuffle to break ties
    random.shuffle(candidates)
    return candidates

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

    pool.sort(key=lambda c: (1 if (theme and theme in c.get("themes", [])) else 0, c["score"]), reverse=True)

    seen_types = {"hotel"} if hotel_pick else set()
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
            if sum(1 for s in selected if s["type"] == c["type"]) < 2:
                selected.append(c)
                seen_ids.add(c["poi_id"])

    if not any(s["type"] == "hotel" for s in selected):
        selected.insert(0, {
            "poi_id": -1,
            "type": "hotel",
            "score": 0.0,
            "name": "Hotel check-in / rest",
            "description": "",
            "themes": []
        })

    hotels = [s for s in selected if s["type"] == "hotel"]
    if len(hotels) > 1:
        first_hotel = hotels[0]
        non_hotels = [s for s in selected if s["type"] != "hotel"]
        selected = [first_hotel] + non_hotels[:plan_size-1]

    return selected[:plan_size]

# ====== Time tiling across full day ======
def build_time_slots(start_time:str="09:00", end_time:str="22:00", n:int=6) -> List[Tuple[str,str]]:
    start = datetime.strptime(start_time,"%H:%M")
    end = datetime.strptime(end_time,"%H:%M")
    total_minutes = int((end - start).total_seconds() // 60)
    step = max(total_minutes // n, 30)
    slots = []
    cur = start
    for i in range(n):
        nxt = cur + timedelta(minutes=step)
        if i == n-1 or nxt > end:
            nxt = end
        slots.append((cur.strftime("%H:%M"), nxt.strftime("%H:%M")))
        cur = nxt
        if cur >= end:
            break
    while len(slots) < n:
        slots.append((end.strftime("%H:%M"), end.strftime("%H:%M")))
    return slots[:n]

# ====== Public API ======
def build_itinerary(city: str = None, country: str = None, lang: str = "en",
                    plan_size: int = 6, start_time: str = "09:00", end_time: str = "22:00",
                    theme: str = None) -> Dict[str, Any]:
    log.info(f"Building itinerary for city={city}, country={country}, plan_size={plan_size}, theme={theme}")

    candidates = fetch_candidates(city=city, country=country, lang=lang, theme=theme, limit=200)
    if not candidates:
        return {"slots": []}

    selected = select_with_hotel(candidates, plan_size=plan_size, theme=theme)
    selected.sort(key=lambda x: (0 if x["type"]=="hotel" else 1, -x["score"]))

    time_slots = build_time_slots(start_time, end_time, n=len(selected))
    slots = []
    for c, (s, e) in zip(selected, time_slots):
        slots.append({
            "start": s,
            "end": e,
            "name": c["name"],
            "category": c["type"],
            "score": round(float(c.get("score", 1.0)), 3)
        })

    hotels = [sl for sl in slots if sl["category"] == "hotel"]
    if not hotels:
        slots.insert(0, {
            "start": "09:00", "end": "10:00",
            "name": "Hotel check-in / rest",
            "category": "hotel",
            "score": 0.0
        })
        slots = slots[:plan_size]
    elif len(hotels) > 1:
        first_hotel = hotels[0]
        non_hotels = [sl for sl in slots if sl["category"] != "hotel"]
        slots = [first_hotel] + non_hotels[:plan_size-1]

    return {"slots": slots}

if __name__=="__main__":
    log.info("🚀 Running itinerary.py smoke test")
    for theme in TOUR_THEMES.keys():
        print(f"\n=== {theme.capitalize()} Itinerary ===")
        result = build_itinerary(city="Cairo", country="Egypt", plan_size=6, theme=theme)
        for slot in result["slots"]:
            print(f"{slot['start']}-{slot['end']} | {slot['name']} | {slot['category']} | Score={slot['score']}")
