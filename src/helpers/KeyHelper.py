import sqlite3
import uuid
import time
import random
import json
from hashlib import sha256
from contextlib import closing
from dataclasses import dataclass


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
    stats: list[tuple[str, int, str, float]]
    failed: int


class Database:
    def __init__(self, db_path: str = "db/keys.db"):
        self.db_path = db_path
        try:
            self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
            self.cursor = self.conn.cursor()
            self._initialize_db()
        except sqlite3.DatabaseError as e:
            raise DatabaseError(f"Database connection error: {e}")

    def _initialize_db(self):
        query = '''
        CREATE TABLE IF NOT EXISTS keys (
            key TEXT PRIMARY KEY,
            timestamp INTEGER,
            bought INTEGER,
            solved INTEGER,
            total_requests INTEGER,
            stats TEXT,
            failed INTEGER
        )
        '''
        try:
            self.cursor.execute(query)
            self.conn.commit()
        except sqlite3.DatabaseError as e:
            raise DatabaseError(f"Database initialization error: {e}")

    def execute_query(self, query: str, params: tuple = ()):  # writes
        try:
            with closing(self.conn.cursor()) as cursor:
                cursor.execute(query, params)
                self.conn.commit()
        except sqlite3.DatabaseError as e:
            raise DatabaseError(f"Query execution error: {e}")

    def fetch_all(self, query: str, params: tuple = ()) -> list:
        try:
            with closing(self.conn.cursor()) as cursor:
                cursor.execute(query, params)
                return cursor.fetchall()
        except sqlite3.DatabaseError as e:
            raise DatabaseError(f"Error fetching data: {e}")


class KeyManager:
    def __init__(self, db: Database):
        self.db = db

    def generate_key(self, bought: int, prefix: str = "CS") -> str:
        random_segment = self._generate_random_key_segment()
        unhashed = f"{prefix}-{random_segment}".upper()
        hashed = self._hash_key(unhashed)
        ts = int(time.time())
        # initial empty stats and zero failed
        initial_stats = json.dumps([])
        try:
            self.db.execute_query(
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

    def _row_to_key(self, row: tuple) -> Key:
        stats = json.loads(row[5] or '[]')
        return Key(row[0], row[1], row[2], row[3], row[4], stats, row[6])

    def get_key_data(self, key: str) -> Key:
        hashed = self._hash_key(key)
        rows = self.db.fetch_all("SELECT * FROM keys WHERE key = ?", (hashed,))
        if not rows:
            raise KeyNotFoundError(f"Key {key} not found.")
        return self._row_to_key(rows[0])

    def update_key_balance(self, key: str, amount: int, operation: str):
        data = self.get_key_data(key)
        if operation not in ("add", "remove"):
            raise InvalidOperationError(f"Invalid operation: {operation}")
        new_bought = data.bought + amount if operation == "add" else max(0, data.bought - amount)
        try:
            self.db.execute_query(
                "UPDATE keys SET bought = ? WHERE key = ?",
                (new_bought, self._hash_key(key))
            )
        except DatabaseError as e:
            raise DatabaseError(f"Failed to update balance: {e}")

    def delete_key(self, key: str):
        try:
            self.db.execute_query("DELETE FROM keys WHERE key = ?", (self._hash_key(key),))
        except DatabaseError as e:
            raise DatabaseError(f"Failed to delete key: {e}")

    def list_keys(self) -> dict[str, Key]:
        rows = self.db.fetch_all("SELECT * FROM keys")
        return {row[0]: self._row_to_key(row) for row in rows}

    def add_solved_request(self, key: str, amount: int):
        try:
            self.db.execute_query(
                f'''UPDATE keys
                   SET solved = solved + {amount}, total_requests = total_requests + {amount}
                   WHERE key = ?''',
                (self._hash_key(key),)
            )
        except DatabaseError as e:
            raise DatabaseError(f"Failed to update solved count: {e}")

    def add_total_request(self, key: str):
        try:
            self.db.execute_query(
                "UPDATE keys SET total_requests = total_requests + 1 WHERE key = ?",
                (self._hash_key(key),)
            )
        except DatabaseError as e:
            raise DatabaseError(f"Failed to update total requests: {e}")

    def add_stat(self, key: str, site: str, status: str, cost: float):
        data = self.get_key_data(key)
        entry = (site, int(time.time()), status, cost)
        data.stats.append(entry)
        try:
            self.db.execute_query(
                "UPDATE keys SET stats = ? WHERE key = ?",
                (json.dumps(data.stats), self._hash_key(key))
            )
        except DatabaseError as e:
            raise DatabaseError(f"Failed to add stats entry: {e}")

    def increment_failed(self, key: str):
        try:
            self.db.execute_query(
                "UPDATE keys SET failed = failed + 1 WHERE key = ?",
                (self._hash_key(key),)
            )
        except DatabaseError as e:
            raise DatabaseError(f"Failed to increment failed count: {e}")


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

    def get_all_keys(self) -> dict[str, Key]:
        return self.key_manager.list_keys()

    def get_balance(self, key: str) -> int:
        return self.key_manager.get_key_data(key).bought

    def add_solved_request(self, key: str, amount: int = 1):
        self.key_manager.add_solved_request(key, amount)

    def add_total_request(self, key: str):
        self.key_manager.add_total_request(key)

    def key_exists(self, key: str) -> bool:
        try:
            self.key_manager.get_key_data(key)
            return True
        except KeyNotFoundError:
            return False

    def add_stat(self, key: str, site: str, status: str, cost: float):
        self.key_manager.add_stat(key, site, status, cost)

    def increment_failed(self, key: str):
        self.key_manager.increment_failed(key)

if __name__ == "__main__":
    keyservice = KeyService()

    key = keyservice.generate_new_key(100_000, "UFCR")

    print(key)

    data = keyservice.key_manager.get_key_data(key)

    print(data)