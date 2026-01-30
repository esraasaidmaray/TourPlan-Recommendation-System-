"""
models.py
---------------
Scoring & reranking logic for POI candidates.
- Combines semantic, geo-distance, category, and diversity scores.
- Saves reranked results into SQLite table `scored_candidates`.
"""

import sqlite3
import logging
from typing import List, Dict, Any
from math import isfinite

# ----------------- Config -----------------
DB_PATH = "poi.db"

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("models")


# ----------------- Helper functions -----------------
def normalize_score(value: float, min_val: float, max_val: float) -> float:
    """Normalize a score into [0,1] range with guardrails."""
    try:
        if max_val == min_val:
            return 0.5  # neutral if no spread
        if not isfinite(value):
            return 0.0
        return (value - min_val) / (max_val - min_val)
    except Exception:
        return 0.0


def category_match(poi_type: str, user_interests: List[str]) -> float:
    """Return 1.0 if POI type matches user interests, else 0."""
    if not poi_type or not user_interests:
        return 0.0
    return 1.0 if poi_type.lower() in [x.lower() for x in user_interests] else 0.0


def diversity_penalty(selected: List[Dict], current_cat: str) -> float:
    """Apply penalty if too many POIs of the same category already selected."""
    if not current_cat:
        return 0.0
    count_same = sum(1 for c in selected if (c.get("type") or "").lower() == current_cat.lower())
    return -0.2 * count_same


# ----------------- SQLite setup -----------------
def init_scored_table():
    """Create scored_candidates table if not exists."""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS scored_candidates (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        poi_id INTEGER,
        city TEXT,
        country TEXT,
        type TEXT,
        semantic REAL,
        distance REAL,
        category_score REAL,
        diversity_score REAL,
        final_score REAL,
        explanation TEXT
    )
    """)
    conn.commit()
    conn.close()
    log.info("✅ scored_candidates table ensured in DB.")


def clear_scored_candidates():
    """Optional: clear table to avoid duplicates across runs."""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("DELETE FROM scored_candidates")
    conn.commit()
    conn.close()
    log.info("🧹 cleared scored_candidates table.")


def save_scored_candidates(reranked: List[Dict[str, Any]]):
    """Insert reranked results into scored_candidates table."""
    if not reranked:
        log.warning("No candidates to save.")
        return
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.executemany("""
    INSERT INTO scored_candidates 
    (poi_id, city, country, type, semantic, distance, category_score, diversity_score, final_score, explanation)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, [
        (
            r.get("poi_id"), r.get("city"), r.get("country"), r.get("type"),
            r.get("semantic"), r.get("distance"), r.get("category_score"),
            r.get("diversity_score"), r.get("final_score"), r.get("explanation")
        )
        for r in reranked
    ])
    conn.commit()
    conn.close()
    log.info(f"💾 Saved {len(reranked)} scored candidates into DB")


# ----------------- Core scoring -----------------
def score_items(candidates: List[Dict[str, Any]], user_ctx: Dict[str, Any], weights: Dict[str, float]) -> List[Dict[str, Any]]:
    """
    Compute weighted scores for candidates and return reranked list.

    Expected candidate keys from generators:
      - semantic candidates: 'semantic' + metadata  (from Candidates.get_candidates)
      - geo candidates: 'distance_km' + metadata    (from Candidates.geo_candidates)
      - popularity candidates: 'rank' + metadata    (from Candidates.popularity_candidates)
    """
    # prepare ranges
    sem_vals = [c.get("semantic", 0.0) for c in candidates if "semantic" in c]
    sem_min, sem_max = (min(sem_vals), max(sem_vals)) if sem_vals else (0.0, 1.0)

    dist_vals = [c.get("distance_km", 0.0) for c in candidates if "distance_km" in c]
    dist_min, dist_max = (min(dist_vals), max(dist_vals)) if dist_vals else (0.0, 1.0)

    reranked = []
    selected_for_div = []

    for c in candidates:
        semantic_raw = c.get("semantic", 0.0)
        semantic_norm = normalize_score(semantic_raw, sem_min, sem_max) if sem_vals else 0.5

        # nearer is better -> invert normalized distance
        distance_raw = c.get("distance_km", None)
        if distance_raw is None or not dist_vals:
            distance_norm = 0.5
        else:
            distance_norm = 1 - normalize_score(distance_raw, dist_min, dist_max)

        category_score = category_match(c.get("type"), user_ctx.get("interests", []))
        diversity_score = diversity_penalty(selected_for_div, c.get("type"))

        final_score = (
            weights.get("semantic", 0.5) * semantic_norm +
            weights.get("distance", 0.3) * distance_norm +
            weights.get("category", 0.15) * category_score +
            weights.get("diversity", 0.05) * diversity_score
        )

        item = {
            "poi_id": c.get("poi_id"),
            "city": c.get("city"),
            "country": c.get("country"),
            "type": c.get("type"),
            "semantic": round(float(semantic_norm), 3),
            "distance": round(float(distance_norm), 3),
            "category_score": round(float(category_score), 3),
            "diversity_score": round(float(diversity_score), 3),
            "final_score": round(float(final_score), 3),
            "explanation": f"sem:{semantic_norm:.2f}, dist:{distance_norm:.2f}, cat:{category_score:.2f}, div:{diversity_score:.2f}"
        }
        reranked.append(item)
        selected_for_div.append({"type": c.get("type")})

    return sorted(reranked, key=lambda x: x["final_score"], reverse=True)


def rerank(candidates: List[Dict[str, Any]], user_ctx: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Wrapper with default weights for reranking."""
    default_weights = {"semantic": 0.5, "distance": 0.3, "category": 0.15, "diversity": 0.05}
    return score_items(candidates, user_ctx, default_weights)


# ----------------- Smoke Test -----------------
if __name__ == "__main__":
    # Import matches your uploaded module name
    from Candidates import get_candidates, geo_candidates, popularity_candidates  # :contentReference[oaicite:1]{index=1}

    log.info("🚀 Running models.py smoke test")
    init_scored_table()
    clear_scored_candidates()

    # Example user context
    user_ctx = {
        "country": "Egypt",
        "city": "Dahab",
        "interests": ["hotel", "nature"],
        "language": "en",
        "budget": "medium"
    }

    # Generate candidates
    semantic_cands = get_candidates("beach resort", country="Egypt", city="Dahab", k=50)  # returns 'semantic' key :contentReference[oaicite:2]{index=2}
    geo_cands = geo_candidates(lat=28.47, lon=34.48, radius_km=5, k=50)                  # returns 'distance_km' key :contentReference[oaicite:3]{index=3}
    pop_cands = popularity_candidates(k=50)                                              # returns 'rank' key :contentReference[oaicite:4]{index=4}

    # Merge unique candidates by poi_id (semantic wins on ties)
    merged_by_id = {}
    for src in (pop_cands + geo_cands + semantic_cands):
        merged_by_id[src["poi_id"]] = {**merged_by_id.get(src["poi_id"], {}), **src}
    merged = list(merged_by_id.values())

    # Rerank
    reranked = rerank(merged, user_ctx)

    # Save into DB
    save_scored_candidates(reranked)

    # Print top results
    for r in reranked[:5]:
        print(r)
