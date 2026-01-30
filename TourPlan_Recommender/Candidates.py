
"""
running command in bash first 
pip install numpy
pip install sentence-transformers
pip install scikit-learn
pip install geopy  
python TourPlan_Recommender/Candidates.py
"""
# tourplan_recommender/candidates.py
"""
Candidates.py
-------------
Helper generators only (no DB writes here):
- get_candidates: semantic
- geo_candidates: by distance
- popularity_candidates: simple fallback
"""

import sqlite3
import logging
from typing import List, Dict, Any
from geopy.distance import geodesic
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from sentence_transformers import SentenceTransformer

DB_PATH = "poi.db"

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("candidates")

# ----------------- Load embedding model -----------------
try:
    model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2", device="cpu")
    log.info("✅ Loaded paraphrase-multilingual MiniLM model.")
except Exception as e:
    log.error(f"⚠️ Failed to load sentence-transformers model: {e}")
    model = None

# ----------------- Helper: enrich with metadata -----------------
def enrich_with_metadata(poi_ids: List[int]) -> Dict[int, Dict[str, Any]]:
    if not poi_ids:
        return {}
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    q_marks = ",".join("?" for _ in poi_ids)
    cur.execute(f"""
        SELECT id, city_name, country_name, type
        FROM pois
        WHERE id IN ({q_marks})
    """, poi_ids)
    rows = cur.fetchall()
    conn.close()
    return {r[0]: {"city": r[1], "country": r[2], "type": r[3]} for r in rows}

# ----------------- Semantic candidates -----------------
def get_candidates(query: str, country: str = None, city: str = None, k: int = 10) -> List[Dict[str, Any]]:
    """Return top-K semantic candidates with metadata (no DB writes)."""
    if model is None:
        log.warning("Model not loaded; returning empty list.")
        return []

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    query_vec = model.encode([query])
    query_vec = np.array(query_vec, dtype=np.float32)

    cur.execute("SELECT poi_id, vector FROM poi_embeddings WHERE lang='en'")
    rows = cur.fetchall()
    conn.close()

    results = []
    for poi_id, emb_blob in rows:
        emb = np.frombuffer(emb_blob, dtype=np.float32)
        sim = float(cosine_similarity(query_vec, [emb])[0][0])
        results.append({"poi_id": poi_id, "semantic": sim})

    # enrich
    meta = enrich_with_metadata([r["poi_id"] for r in results])
    for r in results:
        r.update(meta.get(r["poi_id"], {}))

    # optional filters
    if country:
        results = [r for r in results if (r.get("country") or "").lower() == country.lower()]
    if city:
        results = [r for r in results if (r.get("city") or "").lower() == city.lower()]

    return sorted(results, key=lambda x: x["semantic"], reverse=True)[:k]

# ----------------- Geo candidates -----------------
def geo_candidates(lat: float, lon: float, radius_km: float = 5.0, k: int = 10) -> List[Dict[str, Any]]:
    """Return POIs near given coordinates with metadata (no DB writes)."""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        SELECT id, latitude, longitude, city_name, country_name, type
        FROM pois
        WHERE latitude IS NOT NULL AND longitude IS NOT NULL
    """)
    rows = cur.fetchall()
    conn.close()

    results = []
    for poi_id, plat, plon, city_name, country_name, typ in rows:
        dist = geodesic((lat, lon), (plat, plon)).km
        if dist <= radius_km:
            results.append({
                "poi_id": poi_id,
                "distance_km": dist,
                "city": city_name,
                "country": country_name,
                "type": typ
            })

    return sorted(results, key=lambda x: x["distance_km"])[:k]

# ----------------- Popularity candidates -----------------
def popularity_candidates(k: int = 10) -> List[Dict[str, Any]]:
    """Return top-K POIs by ID order with metadata (no DB writes)."""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT id FROM pois ORDER BY id ASC LIMIT ?", (k,))
    rows = cur.fetchall()
    conn.close()

    results = [{"poi_id": r[0], "rank": i + 1} for i, r in enumerate(rows)]
    meta = enrich_with_metadata([r["poi_id"] for r in results])
    for r in results:
        r.update(meta.get(r["poi_id"], {}))
    return results

if __name__ == "__main__":
    log.info("🚀 Running candidates.py smoke test (no DB writes)")
    print(get_candidates("beach activities in Dahab", country="Egypt", city="Dahab", k=5))
    print(geo_candidates(28.4696, 34.4764, radius_km=3, k=5))
    print(popularity_candidates(5))

