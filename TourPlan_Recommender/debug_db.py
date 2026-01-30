# """
# debug_db.py
# -----------
# Debug and fix database issues
# """

# import sqlite3
# import logging
# import os

# logging.basicConfig(level=logging.INFO)
# log = logging.getLogger("debug_db")

# DB_PATH = "poi.db"

# def check_database():
#     """Check database status and show statistics."""
#     if not os.path.exists(DB_PATH):
#         log.error(f"Database file {DB_PATH} does not exist!")
#         return
    
#     conn = sqlite3.connect(DB_PATH)
#     cur = conn.cursor()
    
#     # Check tables
#     cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
#     tables = cur.fetchall()
#     log.info(f"Tables found: {[t[0] for t in tables]}")
    
#     # Check POIs table
#     if ('pois',) in tables:
#         cur.execute("SELECT COUNT(*) FROM pois")
#         poi_count = cur.fetchone()[0]
#         log.info(f"POIs count: {poi_count}")
        
#         # Check for duplicates
#         cur.execute("""
#             SELECT external_id, COUNT(*) as count 
#             FROM pois 
#             GROUP BY external_id 
#             HAVING COUNT(*) > 1
#         """)
#         duplicates = cur.fetchall()
#         if duplicates:
#             log.warning(f"Found {len(duplicates)} duplicate external_ids:")
#             for ext_id, count in duplicates[:5]:  # Show first 5
#                 log.warning(f"  external_id {ext_id}: {count} times")
#         else:
#             log.info("No duplicate external_ids found")
    
#     # Check POI texts table
#     if ('poi_texts',) in tables:
#         cur.execute("SELECT COUNT(*) FROM poi_texts")
#         text_count = cur.fetchone()[0]
#         log.info(f"POI texts count: {text_count}")
    
#     conn.close()

# def fix_duplicates():
#     """Remove duplicate POIs keeping only the first occurrence."""
#     if not os.path.exists(DB_PATH):
#         log.error(f"Database file {DB_PATH} does not exist!")
#         return
    
#     conn = sqlite3.connect(DB_PATH)
#     cur = conn.cursor()
    
#     # Find duplicates
#     cur.execute("""
#         SELECT external_id, COUNT(*) as count 
#         FROM pois 
#         GROUP BY external_id 
#         HAVING COUNT(*) > 1
#     """)
#     duplicates = cur.fetchall()
    
#     if not duplicates:
#         log.info("No duplicates found")
#         conn.close()
#         return
    
#     log.info(f"Found {len(duplicates)} duplicate external_ids")
    
#     # Remove duplicates keeping the first occurrence
#     for ext_id, count in duplicates:
#         log.info(f"Removing {count-1} duplicates for external_id {ext_id}")
        
#         # Keep the first occurrence (lowest id)
#         cur.execute("""
#             DELETE FROM pois 
#             WHERE external_id = ? 
#             AND id NOT IN (
#                 SELECT MIN(id) 
#                 FROM pois 
#                 WHERE external_id = ?
#             )
#         """, (ext_id, ext_id))
    
#     conn.commit()
#     conn.close()
#     log.info("Duplicates removed successfully")

# def clear_database():
#     """Clear all data from database."""
#     if not os.path.exists(DB_PATH):
#         log.error(f"Database file {DB_PATH} does not exist!")
#         return
    
#     conn = sqlite3.connect(DB_PATH)
#     cur = conn.cursor()
    
#     # Drop all tables
#     cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
#     tables = cur.fetchall()
    
#     for table in tables:
#         table_name = table[0]
#         log.info(f"Dropping table: {table_name}")
#         cur.execute(f"DROP TABLE IF EXISTS {table_name}")
    
#     conn.commit()
#     conn.close()
#     log.info("Database cleared successfully")

# if __name__ == "__main__":
#     import sys
    
#     if len(sys.argv) < 2:
#         print("Usage:")
#         print("  python debug_db.py check     - Check database status")
#         print("  python debug_db.py fix       - Fix duplicate issues")
#         print("  python debug_db.py clear     - Clear all data")
#         sys.exit(1)
    
#     command = sys.argv[1]
    
#     if command == "check":
#         check_database()
#     elif command == "fix":
#         fix_duplicates()
#     elif command == "clear":
#         print("⚠️  WARNING: This will delete all data!")
#         response = input("Are you sure? (y/N): ")
#         if response.lower() == 'y':
#             clear_database()
#         else:
#             print("Operation cancelled.")
#     else:
#         print(f"Unknown command: {command}")
#         sys.exit(1)
import sqlite3
conn = sqlite3.connect("poi.db")
cur = conn.cursor()
cur.execute("SELECT COUNT(*), MIN(final_score), MAX(final_score) FROM scored_candidates")
print("rows, min_final, max_final =", cur.fetchone())
cur.execute("PRAGMA table_info(scored_candidates)")
print("columns =", [r[1] for r in cur.fetchall()])
conn.close()

