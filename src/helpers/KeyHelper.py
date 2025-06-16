import sqlite3
import uuid
import time
import random
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


class Database:
    def __init__(self, db_path="db/keys.db"):
        self.db_path = db_path
        try:
            self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
            self.cursor = self.conn.cursor()
            self._initialize_db()
        except sqlite3.DatabaseError as e:
            raise DatabaseError(f"Database connection error: {str(e)}")

    def _initialize_db(self):
        query = """
        CREATE TABLE IF NOT EXISTS keys (
            key TEXT PRIMARY KEY,
            timestamp INTEGER,
            bought INTEGER,
            solved INTEGER,
            total_requests INTEGER
        )
        """
        try:
            self.cursor.execute(query)
            self.conn.commit()
        except sqlite3.DatabaseError as e:
            raise DatabaseError(f"Database initialization error: {str(e)}")

    def execute_query(self, query: str, params: tuple = ()):
        try:
            with closing(self.conn.cursor()) as cursor:
                cursor.execute(query, params)
                self.conn.commit()
        except sqlite3.DatabaseError as e:
            raise DatabaseError(f"Query execution error: {str(e)}")

    def fetch_all(self, query: str, params: tuple = ()):
        try:
            with closing(self.conn.cursor()) as cursor:
                cursor.execute(query, params)
                return cursor.fetchall()
        except sqlite3.DatabaseError as e:
            raise DatabaseError(f"Error fetching data: {str(e)}")


class KeyManager:
    def __init__(self, db: Database):
        self.db = db

    def generate_key(self, bought: int) -> str:
        random_key_segment = self._generate_random_key_segment()
        full_unhashed_key = f"CAI-{random_key_segment}"
        hashed_key = self._hash_key(full_unhashed_key)
        timestamp = int(time.time())

        try:
            self.db.execute_query(
                """
                INSERT INTO keys (key, timestamp, bought, solved, total_requests)
                VALUES (?, ?, ?, ?, ?)
            """,
                (hashed_key, timestamp, bought, 0, 0),
            )
        except DatabaseError as e:
            raise DatabaseError(f"Failed to generate new key: {str(e)}")

        return full_unhashed_key

    def _generate_random_key_segment(self) -> str:
        return f"{uuid.uuid4().hex[:16].upper()}{int(time.time()) - random.randint(1, 10000000)}"

    def _hash_key(self, key: str) -> str:
        return sha256(key.encode()).hexdigest()

    def get_key_data(self, key: str) -> Key:
        hashed_key = self._hash_key(key)
        result = self.db.fetch_all("SELECT * FROM keys WHERE key = ?", (hashed_key,))
        if result:
            return Key(*result[0])
        raise KeyNotFoundError(f"Key {key} not found in the database.")

    def update_key_balance(self, key: str, amount: int, operation: str):
        hashed_key = self._hash_key(key)
        key_data = self.get_key_data(key)

        if operation not in ["add", "remove"]:
            raise InvalidOperationError(
                f"Invalid operation: {operation}. Use 'add' or 'remove'."
            )

        if operation == "add":
            new_balance = key_data.bought + amount
        elif operation == "remove":
            new_balance = max(0, key_data.bought - amount)

        try:
            self.db.execute_query(
                """
                UPDATE keys
                SET bought = ?
                WHERE key = ?
            """,
                (new_balance, hashed_key),
            )
        except DatabaseError as e:
            raise DatabaseError(f"Failed to update balance for key {key}: {str(e)}")

    def delete_key(self, key: str):
        hashed_key = self._hash_key(key)
        try:
            self.db.execute_query("DELETE FROM keys WHERE key = ?", (hashed_key,))
        except DatabaseError as e:
            raise DatabaseError(f"Failed to delete key {key}: {str(e)}")

    def list_keys(self):
        result = self.db.fetch_all("SELECT * FROM keys")
        return {row[0]: Key(*row) for row in result}


class KeyService:
    def __init__(self, db_path="db/keys.db"):
        self.db = Database(db_path)
        self.key_manager = KeyManager(self.db)

    def generate_new_key(self, bought: int) -> str:
        try:
            return self.key_manager.generate_key(bought)
        except DatabaseError as e:
            raise DatabaseError(f"Error generating key: {str(e)}")

    def add_balance(self, key: str, amount: int):
        try:
            self.key_manager.update_key_balance(key, amount, "add")
        except (KeyNotFoundError, InvalidOperationError, DatabaseError) as e:
            raise e

    def remove_balance(self, key: str, amount: int):
        try:
            self.key_manager.update_key_balance(key, amount, "remove")
        except (KeyNotFoundError, InvalidOperationError, DatabaseError) as e:
            raise e

    def delete_key(self, key: str):
        try:
            self.key_manager.delete_key(key)
        except DatabaseError as e:
            raise DatabaseError(f"Error deleting key: {str(e)}")

    def get_all_keys(self):
        try:
            return self.key_manager.list_keys()
        except DatabaseError as e:
            raise DatabaseError(f"Error retrieving keys: {str(e)}")
