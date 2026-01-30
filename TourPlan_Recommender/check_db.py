# check_db.py
import sqlite3
import numpy as np

conn = sqlite3.connect("poi.db")
cur = conn.cursor()

# 1) Show tables
cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cur.fetchall()
print("Tables:", tables)

# 2) Count embeddings
cur.execute("SELECT COUNT(*) FROM poi_embeddings;")
count = cur.fetchone()[0]
print("Number of embeddings:", count)

# 3) Show sample rows
cur.execute("""
    SELECT id, poi_id, lang, length(vector) as vec_size 
    FROM poi_embeddings 
    LIMIT 5;
""")
rows = cur.fetchall()
print("Sample rows:", rows)

# 4) Decode one embedding
cur.execute("SELECT poi_id, lang, vector FROM poi_embeddings LIMIT 1;")
poi_id, lang, vector_bytes = cur.fetchone()
vector = np.frombuffer(vector_bytes, dtype=np.float32)
print("POI:", poi_id, "| Lang:", lang, "| Vector shape:", vector.shape)
