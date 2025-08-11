import sqlite3
import uuid
import time
import random
import json
import threading

from dataclasses    import dataclass
from hashlib        import sha256
from typing         import List, Tuple, Dict, Optional

class KeyNotFoundError(Exception):
    pass

class InvalidOperationError(Exception):
    pass

class DatabaseError(Exception):
    pass

@dataclass
class Key:
    key: str
    timestamp: int
    bought: int
    solved: int
    total_requests: int
    stats: List[Tuple[str, int, str, float]]
    failed: int

class Database:
    def __init__(self, db_path: str = "db/keys.db", busy_timeout: float = 30.0):
        self.db_path = db_path
        self._local = threading.local()
        self._busy_timeout = busy_timeout
        
        conn = sqlite3.connect(self.db_path, timeout=self._busy_timeout, check_same_thread=False)
        try:
            conn.execute("PRAGMA journal_mode=WAL;")
            conn.execute("PRAGMA synchronous=NORMAL;")
            conn.execute("PRAGMA foreign_keys=ON;")
            conn.commit()
            self._initialize_db(conn)
        finally:
            conn.close()

    def _get_conn(self) -> sqlite3.Connection:
        """Return a thread-local connection (each thread has its own)."""
        conn = getattr(self._local, "conn", None)
        if conn is None:
            conn = sqlite3.connect(self.db_path, timeout=self._busy_timeout, check_same_thread=True)
            conn.execute("PRAGMA journal_mode=WAL;")
            conn.execute("PRAGMA synchronous=NORMAL;")
            conn.execute("PRAGMA foreign_keys=ON;")
            conn.row_factory = sqlite3.Row
            self._local.conn = conn
        return conn

    def _initialize_db(self, conn: Optional[sqlite3.Connection] = None):
        close_after = False
        if conn is None:
            conn = self._get_conn()
            close_after = False
            
        queries = [
            '''
            CREATE TABLE IF NOT EXISTS keys (
                key TEXT PRIMARY KEY,
                timestamp INTEGER,
                bought INTEGER DEFAULT 0,
                solved INTEGER DEFAULT 0,
                total_requests INTEGER DEFAULT 0,
                stats TEXT DEFAULT '[]',
                failed INTEGER DEFAULT 0
            )
            ''',
            '''
            CREATE TABLE IF NOT EXISTS stats (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                key TEXT NOT NULL,
                site TEXT NOT NULL,
                ts INTEGER NOT NULL,
                status TEXT NOT NULL,
                cost REAL NOT NULL,
                FOREIGN KEY(key) REFERENCES keys(key) ON DELETE CASCADE
            )
            ''',
            'CREATE INDEX IF NOT EXISTS idx_stats_key ON stats(key);'
        ]
        cur = conn.cursor()
        try:
            for q in queries:
                cur.execute(q)
            conn.commit()
        except sqlite3.DatabaseError as e:
            raise DatabaseError(f"Database initialization error: {e}")
        finally:
            cur.close()
            if close_after:
                conn.close()

    def _with_retry(self, fn, *args, **kwargs):
        """Run fn with retries/backoff on SQLITE_BUSY/locked."""
        max_retries = 6
        backoff = 0.02
        for attempt in range(max_retries):
            try:
                return fn(*args, **kwargs)
            except sqlite3.OperationalError as e:
                msg = str(e).lower()
                if "locked" in msg or "database is locked" in msg or "database is busy" in msg:
                    
                    time.sleep(backoff)
                    backoff = min(backoff * 2, 1.0)
                    continue
                raise DatabaseError(f"Operational error: {e}")
            except sqlite3.DatabaseError as e:
                raise DatabaseError(f"Database error: {e}")
        raise DatabaseError("Max retries exceeded due to database lock/busy")

    def execute_write(self, query: str, params: tuple = ()):
        def _exe():
            conn = self._get_conn()
            cur = conn.cursor()
            try:
                cur.execute("BEGIN IMMEDIATE;")
                cur.execute(query, params)
                conn.commit()
            finally:
                cur.close()
        return self._with_retry(_exe)

    def fetch_all(self, query: str, params: tuple = ()) -> list:
        def _fn():
            conn = self._get_conn()
            cur = conn.cursor()
            try:
                cur.execute(query, params)
                rows = cur.fetchall()
                return rows
            finally:
                cur.close()
        return self._with_retry(_fn)

    def fetch_one(self, query: str, params: tuple = ()):
        rows = self.fetch_all(query, params)
        return rows[0] if rows else None

class KeyManager:
    def __init__(self, db: Database):
        self.db = db

    def generate_key(self, bought: int, prefix: str = "CS") -> str:
        random_segment = self._generate_random_key_segment()
        unhashed = f"{prefix}-{random_segment}".upper()
        hashed = self._hash_key(unhashed)
        ts = int(time.time())
        initial_stats = json.dumps([])
        try:
            self.db.execute_write(
                '''
                INSERT INTO keys (key, timestamp, bought, solved, total_requests, stats, failed)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                ''',
                (hashed, ts, bought, 0, 0, initial_stats, 0)
            )
        except DatabaseError as e:
            raise DatabaseError(f"Failed to generate new key: {e}")

        return unhashed

    def _generate_random_key_segment(self) -> str:
        return f"{uuid.uuid4().hex.upper()}{int(time.time()) - random.randint(1, 10_000_000)}"

    def _hash_key(self, key: str) -> str:
        raw = sha256(key.encode()).hexdigest()[:50]
        parts = [raw[i : i + 5] for i in range(0, len(raw), 5)]
        if len(parts) >= 6:
            parts[4], parts[5] = "CHASH", "CS#AI"
        return '-'.join(parts).upper()

    def _row_to_key(self, row: sqlite3.Row, stats_rows: List[sqlite3.Row]) -> Key:
        # row mapping: key, timestamp, bought, solved, total_requests, stats(json), failed
        legacy_stats = []
        try:
            legacy_stats = json.loads(row["stats"] or "[]")
        except Exception:
            legacy_stats = []
        # stats_rows are rows from stats table: site, ts, status, cost
        new_stats = [(r["site"], r["ts"], r["status"], float(r["cost"])) for r in stats_rows]
        # merge preserving order (legacy first then new) but avoid duplicates
        combined = legacy_stats + new_stats
        return Key(
            key=row["key"],
            timestamp=row["timestamp"],
            bought=row["bought"],
            solved=row["solved"],
            total_requests=row["total_requests"],
            stats=combined,
            failed=row["failed"]
        )

    def get_key_data(self, key: str, stats_limit: int = 1000) -> Key:
        hashed = self._hash_key(key)
        row = self.db.fetch_one("SELECT * FROM keys WHERE key = ?", (hashed,))
        if not row:
            raise KeyNotFoundError(f"Key {key} not found.")
        stats_rows = self.db.fetch_all(
            "SELECT site, ts, status, cost FROM stats WHERE key = ? ORDER BY ts DESC LIMIT ?",
            (hashed, stats_limit)
        )
        return self._row_to_key(row, stats_rows)

    def update_key_balance(self, key: str, amount: int, operation: str):
        if operation not in ("add", "remove"):
            raise InvalidOperationError(f"Invalid operation: {operation}")
        hashed = self._hash_key(key)
        if operation == "add":
            query = "UPDATE keys SET bought = bought + ? WHERE key = ?"
            params = (amount, hashed)
        else:
            # ensure not negative using CASE
            query = "UPDATE keys SET bought = CASE WHEN bought >= ? THEN bought - ? ELSE 0 END WHERE key = ?"
            params = (amount, amount, hashed)
        try:
            self.db.execute_write(query, params)
        except DatabaseError as e:
            raise DatabaseError(f"Failed to update balance: {e}")

    def delete_key(self, key: str):
        try:
            self.db.execute_write("DELETE FROM keys WHERE key = ?", (self._hash_key(key),))
        except DatabaseError as e:
            raise DatabaseError(f"Failed to delete key: {e}")

    def list_keys(self) -> Dict[str, Key]:
        rows = self.db.fetch_all("SELECT * FROM keys")
        result: Dict[str, Key] = {}
        for row in rows:
            stats_rows = self.db.fetch_all("SELECT site, ts, status, cost FROM stats WHERE key = ? ORDER BY ts DESC LIMIT ?",
                                          (row["key"], 100))
            result[row["key"]] = self._row_to_key(row, stats_rows)
        return result

    def add_solved_request(self, key: str, amount: int):
        try:
            self.db.execute_write(
                "UPDATE keys SET solved = solved + ?, total_requests = total_requests + ? WHERE key = ?",
                (amount, amount, self._hash_key(key))
            )
        except DatabaseError as e:
            raise DatabaseError(f"Failed to update solved count: {e}")

    def add_total_request(self, key: str):
        try:
            self.db.execute_write(
                "UPDATE keys SET total_requests = total_requests + 1 WHERE key = ?",
                (self._hash_key(key),)
            )
        except DatabaseError as e:
            raise DatabaseError(f"Failed to update total requests: {e}")

    def add_stat(self, key: str, site: str, status: str, cost: float):
        hashed = self._hash_key(key)
        ts = int(time.time())
        try:
            # Append to stats table (cheap INSERT). We deliberately avoid re-writing large JSON blobs.
            self.db.execute_write(
                "INSERT INTO stats (key, site, ts, status, cost) VALUES (?, ?, ?, ?, ?)",
                (hashed, site, ts, status, float(cost))
            )
        except DatabaseError as e:
            raise DatabaseError(f"Failed to add stats entry: {e}")

    def increment_failed(self, key: str):
        try:
            self.db.execute_write(
                "UPDATE keys SET failed = failed + 1 WHERE key = ?",
                (self._hash_key(key),)
            )
        except DatabaseError as e:
            raise DatabaseError(f"Failed to increment failed count: {e}")

    def key_exists(self, key: str) -> bool:
        row = self.db.fetch_one("SELECT 1 FROM keys WHERE key = ? LIMIT 1", (self._hash_key(key),))
        return bool(row)

# ---------- Service facade ----------
class KeyService:
    def __init__(self, db_path: str = "db/keys.db"):
        self.key_manager = KeyManager(Database(db_path))

    def generate_new_key(self, bought: int, prefix: str = "CS") -> str:
        return self.key_manager.generate_key(bought, prefix)

    def add_balance(self, key: str, amount: int):
        self.key_manager.update_key_balance(key, amount, "add")

    def remove_balance(self, key: str, amount: int):
        self.key_manager.update_key_balance(key, amount, "remove")

    def delete_key(self, key: str):
        self.key_manager.delete_key(key)

    def get_all_keys(self) -> dict:
        return self.key_manager.list_keys()

    def get_balance(self, key: str) -> int:
        return self.key_manager.get_key_data(key).bought

    def add_solved_request(self, key: str, amount: int = 1):
        self.key_manager.add_solved_request(key, amount)

    def add_total_request(self, key: str):
        self.key_manager.add_total_request(key)

    def key_exists(self, key: str) -> bool:
        return self.key_manager.key_exists(key)

    def add_stat(self, key: str, site: str, status: str, cost: float):
        self.key_manager.add_stat(key, site, status, cost)

    def increment_failed(self, key: str):
        self.key_manager.increment_failed(key)
