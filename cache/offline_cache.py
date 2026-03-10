"""
SQLite-based offline cache for the farming assistant.
Stores recent queries and responses so the app works without internet.
Critical for rural areas with spotty connectivity.
"""
import sqlite3
import hashlib
import time
import os
import config


class OfflineCache:
    def __init__(self, db_path=None):
        self.db_path = db_path or config.CACHE_DB_PATH
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self._init_db()

    def _init_db(self):
        """Create cache table if it doesn't exist."""
        conn = sqlite3.connect(self.db_path)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS cache (
                query_hash TEXT PRIMARY KEY,
                query_text TEXT,
                response TEXT,
                created_at REAL,
                access_count INTEGER DEFAULT 1
            )
        """)
        conn.commit()
        conn.close()

    def get(self, query):
        """Look up cached response for a query. Returns None if miss or expired."""
        query_hash = self._hash(query)
        conn = sqlite3.connect(self.db_path)
        cursor = conn.execute(
            "SELECT response, created_at FROM cache WHERE query_hash = ?",
            (query_hash,)
        )
        row = cursor.fetchone()

        if row is None:
            conn.close()
            return None

        response, created_at = row
        age_hours = (time.time() - created_at) / 3600

        if age_hours > config.CACHE_EXPIRY_HOURS:
            # Expired, but still return it if we're offline
            # The caller can decide whether to use stale data
            conn.execute("DELETE FROM cache WHERE query_hash = ?", (query_hash,))
            conn.commit()
            conn.close()
            print(f"[CACHE] Expired entry removed: {query[:40]}")
            return None

        # Update access count
        conn.execute(
            "UPDATE cache SET access_count = access_count + 1 WHERE query_hash = ?",
            (query_hash,)
        )
        conn.commit()
        conn.close()
        return response

    def put(self, query, response):
        """Store a query-response pair in cache."""
        query_hash = self._hash(query)
        conn = sqlite3.connect(self.db_path)

        # Enforce max cache size
        count = conn.execute("SELECT COUNT(*) FROM cache").fetchone()[0]
        if count >= config.CACHE_MAX_ENTRIES:
            # Remove least accessed entries
            conn.execute("""
                DELETE FROM cache WHERE query_hash IN (
                    SELECT query_hash FROM cache
                    ORDER BY access_count ASC, created_at ASC
                    LIMIT 50
                )
            """)

        conn.execute(
            "INSERT OR REPLACE INTO cache (query_hash, query_text, response, created_at) VALUES (?, ?, ?, ?)",
            (query_hash, query, response, time.time())
        )
        conn.commit()
        conn.close()

    def get_size(self):
        """Return number of cached entries."""
        try:
            conn = sqlite3.connect(self.db_path)
            count = conn.execute("SELECT COUNT(*) FROM cache").fetchone()[0]
            conn.close()
            return count
        except Exception:
            return 0

    def clear(self):
        """Clear all cache entries."""
        conn = sqlite3.connect(self.db_path)
        conn.execute("DELETE FROM cache")
        conn.commit()
        conn.close()
        print("[CACHE] All entries cleared")

    def _hash(self, text):
        """Hash query text for lookup key."""
        return hashlib.sha256(text.strip().lower().encode("utf-8")).hexdigest()[:32]
