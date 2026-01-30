"""
features.py
---------------
Loads POIs from SQLite/Parquet, generates text embeddings, 
and stores them in SQLite for retrieval.
"""
import logging
import sqlite3
import pandas as pd
import numpy as np

from sklearn.feature_extraction.text import TfidfVectorizer
logging.basicConfig(level=logging.DEBUG)

# Try to use sentence-transformers (multilingual embeddings), fallback to TF-IDF
try:
    from sentence_transformers import SentenceTransformer
    HAS_ST = True
except ImportError:
    HAS_ST = False

DB_PATH = "poi.db"
PARQUET_FILE = "poi_texts.parquet"

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("features")

# ----------------- Load Data -----------------
def load_poi_texts() -> pd.DataFrame:
    """
    Load POI multilingual texts from SQLite (default).
    Fallback: parquet if SQL not available.
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        df = pd.read_sql("SELECT * FROM poi_texts", conn)
        conn.close()
        log.info(f"Loaded {len(df)} rows from SQLite.")
        return df
    except Exception as e:
        log.warning(f"Failed to read from SQLite ({e}), trying parquet.")
        try:
            df = pd.read_parquet(PARQUET_FILE)
            log.info(f"Loaded {len(df)} rows from parquet.")
            return df
        except Exception as e2:
            log.error(f"Failed to read parquet as well ({e2}). Returning empty DataFrame.")
            return pd.DataFrame()

# ----------------- Embeddings -----------------
def build_embeddings(df: pd.DataFrame, lang: str = "en") -> pd.DataFrame:
    """
    Build embeddings for POI texts in a given language.
    Returns DataFrame with poi_id, lang, embedding (np.array).
    """
    df_lang = df[df["lang"] == lang].copy()
    texts = (
        df_lang["name"].fillna("") + " " +
        df_lang["short_description"].fillna("") + " " +
        df_lang["description"].fillna("")
    ).tolist()

    embeddings = None

    if HAS_ST:
        try:
            log.info("Using SentenceTransformer for embeddings.")
            model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2", device="cpu")

            # Encode in small batches to avoid OOM
            batch_size = 64
            embeddings = []
            for i in range(0, len(texts), batch_size):
                batch = texts[i:i+batch_size]
                batch_emb = model.encode(batch, show_progress_bar=True, convert_to_numpy=True)
                embeddings.extend(batch_emb)

        except Exception as e:
            log.warning(f"SentenceTransformer failed ({e}). Falling back to TF-IDF.")
            embeddings = None

    if embeddings is None:
        log.info("Using TF-IDF fallback for embeddings.")
        vectorizer = TfidfVectorizer(max_features=512)
        embeddings = vectorizer.fit_transform(texts).toarray()

    df_lang["embedding"] = list(embeddings)
    return df_lang[["poi_id", "lang", "embedding"]]

# ----------------- Save to SQLite -----------------
def save_embeddings(df_emb: pd.DataFrame):
    """
    Save embeddings into SQLite as BLOBs.
    Each embedding is stored as float32 bytes.
    """
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS poi_embeddings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        poi_id INTEGER,
        lang TEXT,
        vector BLOB,
        FOREIGN KEY (poi_id) REFERENCES pois(id)
    )
    """)

    for _, row in df_emb.iterrows():
        vector = np.array(row["embedding"], dtype=np.float32).tobytes()
        cur.execute(
            "INSERT INTO poi_embeddings (poi_id, lang, vector) VALUES (?, ?, ?)",
            (int(row["poi_id"]), row["lang"], vector)
        )
    conn.commit()
    conn.close()
    log.info(f"Saved {len(df_emb)} embeddings into SQLite.")

# ----------------- Main -----------------
def main():
    df = load_poi_texts()
    if df.empty:
        log.warning("No data found. Run ingest.py first.")
        return
    df_emb = build_embeddings(df, lang="en")  # Default language = English
    save_embeddings(df_emb)

if __name__ == "__main__":
    main()
