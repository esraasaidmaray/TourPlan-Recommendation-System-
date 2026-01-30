Tour_Recommender_Plan/
│
├── ingest.py          # Fetches POIs from Trekio API → normalize → save in SQLite + Parquet
├── features.py        # Load POIs texts → build embeddings (ST/TF-IDF) → save in SQLite
├── check_db.py        # (Optional helper) verify tables + embeddings stored correctly
│
├── poi.db             # SQLite database (pois, poi_texts, poi_embeddings)
├── poi_texts.parquet  # Backup snapshot of POI texts (optional)
│
└── requirements.txt   # Python dependencies (requests, pandas, numpy, sqlalchemy, sentence-transformers, scikit-learn, etc.)
