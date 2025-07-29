import asyncio
import json
import logging
import os
import sqlite3
import time
from typing import Union

import httpx
import platformdirs

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DATABASE_URL = "https://mvhs-app-d04d2.firebaseio.com"

APP_NAME = "mvhs-schedule"

CACHE_EXPIRATION_SECONDS = 24 * 3600  # 1 day


class FirebaseFetcher:
    _instance = None  # Singleton instance for managing global state
    _initialized = False

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(FirebaseFetcher, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._initialized = True

        self.current_fetches = {}
        self._db_conn = None

        self.cache_dir = platformdirs.user_cache_dir(APP_NAME)
        self.db_file = os.path.join(self.cache_dir, "firebase_cache.db")

        self._init_db()

        self._client = httpx.AsyncClient()

        self.root_dict = {}
        self.timestamp_root_dict = {}
        asyncio.create_task(self._load_cache_from_db_on_startup())

    async def _load_cache_from_db_on_startup(self):
        """Loads the entire cache from the SQLite DB into memory on startup."""
        logger.debug("Loading cache from database on startup...")
        try:
            self.root_dict, self.timestamp_root_dict = self._get_full_cache_from_db()
            logger.debug("Cache loaded.")
        except Exception as e:
            logger.error(f"Failed to load cache from database on startup: {e}")
            self.root_dict = {}
            self.timestamp_root_dict = {}

    def _init_db(self):
        """Initializes the SQLite database schema."""
        os.makedirs(self.cache_dir, exist_ok=True)
        self._db_conn = sqlite3.connect(self.db_file)
        self._db_conn.row_factory = sqlite3.Row
        cursor = self._db_conn.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS cache_data (
                path TEXT PRIMARY KEY,
                data TEXT,
                timestamp REAL
            )
        """
        )
        self._db_conn.commit()
        logger.info(f"SQLite cache database initialized at {self.db_file}")

    def _get_db_connection(self) -> sqlite3.Connection:
        """Returns the database connection (or creates it if closed)."""
        if self._db_conn is None or not isinstance(self._db_conn, sqlite3.Connection):
            self._db_conn = sqlite3.connect(self.db_file)
            self._db_conn.row_factory = sqlite3.Row
        return self._db_conn

    def _get_full_cache_from_db(self) -> tuple[dict, dict]:
        """Retrieves all cached data and timestamps from the database."""
        conn = self._get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT path, data, timestamp FROM cache_data")

        full_data = {}
        full_timestamps = {}

        for row in cursor.fetchall():
            path_parts = row["path"].split("/")

            current_data_level = full_data
            current_timestamp_level = full_timestamps

            for part in path_parts[:-1]:
                current_data_level = current_data_level.setdefault(part, {})
                current_timestamp_level = current_timestamp_level.setdefault(part, {})

            last_part = path_parts[-1]
            try:
                current_data_level[last_part] = json.loads(row["data"])
            except json.JSONDecodeError:
                logger.warning(f"Corrupted JSON data for path: {row['path']}")
                current_data_level[last_part] = None

            current_timestamp_level[last_part] = {"timestamp": row["timestamp"]}

        return full_data, full_timestamps

    def _save_to_local_cache(self, path: str, data: dict):
        """Saves data to the in-memory cache and persists to SQLite."""
        conn = self._get_db_connection()
        cursor = conn.cursor()
        current_time = time.time() * 1000

        # Update in-memory cache (root_dict, timestamp_root_dict)
        dict_cursor = self.root_dict
        timestamp_cursor = self.timestamp_root_dict

        split_path = path.split("/")
        for i in range(len(split_path) - 1):
            part = split_path[i]
            dict_cursor = dict_cursor.setdefault(part, {})
            timestamp_cursor = timestamp_cursor.setdefault(part, {})

        last_part = split_path[-1]
        dict_cursor[last_part] = data
        timestamp_cursor[last_part] = {"timestamp": current_time}

        # Persist to SQLite DB
        try:
            cursor.execute(
                """
                INSERT OR REPLACE INTO cache_data (path, data, timestamp)
                VALUES (?, ?, ?)
                """,
                (path, json.dumps(data), current_time),
            )
            conn.commit()
            logger.debug(f"Path '{path}' cached to SQLite.")
        except Exception as e:
            logger.error(f"Error saving path '{path}' to SQLite cache: {e}")

    def _check_local_cache(self, path: str) -> Union[dict, None]:
        """
        Checks the local in-memory cache for the given path.
        Returns the cached data if valid, or None if not found or expired.

        :param path: The path to check in the local cache.
        :return: Cached data if valid, otherwise None.
        """
        dict_cursor = self.root_dict
        timestamp_cursor = self.timestamp_root_dict
        split_path = path.split("/")

        cached_data = None
        cached_timestamp = None

        # Traverse the in-memory cache to find the data and timestamp
        for i, part in enumerate(split_path):
            if part not in dict_cursor:
                cached_data = None  # Path not found in cache
                break
            if i == len(split_path) - 1:  # Last part of the path
                cached_data = dict_cursor[part]
                cached_timestamp_entry = timestamp_cursor.get(part)
                if cached_timestamp_entry:
                    cached_timestamp = cached_timestamp_entry.get("timestamp")
                break
            dict_cursor = dict_cursor[part]
            # Use .get to avoid KeyError if path not fully in timestamp
            timestamp_cursor = timestamp_cursor.get(part, {})

        if cached_data is not None and cached_timestamp is not None:
            current_time_ms = time.time() * 1000
            if (current_time_ms - cached_timestamp) < CACHE_EXPIRATION_SECONDS * 1000:
                logger.debug(f"Using cached data for '{path}'.")
                return cached_data
            else:
                logger.debug(f"Cached data for '{path}' expired.")
        return None

    async def get_from_db(self, path: str) -> dict:
        """
        Fetches data from Firebase, with in-flight request deduplication and
        local persistent caching.

        :param path: The path to fetch from Firebase.
        :return: The fetched data as a dictionary.
        """
        # --- In-flight cache check ---
        if path in self.current_fetches:
            logger.debug(f"Request for '{path}' already in progress.")
            try:
                response = await self.current_fetches[path]
                return response
            except Exception as e:
                # If the other in-flight fetch failed, remove it and re-attempt
                logger.warning(f"Previous fetch for '{path}' failed: {e}. Retrying.")
                del self.current_fetches[path]
                # Fall through to new fetch

        # --- Check local cache ---
        cached_data = self._check_local_cache(path)
        if cached_data is not None:
            return cached_data

        # --- Perform fetch ---
        fetch_task = asyncio.create_task(self._perform_fetch(path))
        self.current_fetches[path] = fetch_task

        try:
            data = await fetch_task
            # Store in local cache only if fetch was successful
            self._save_to_local_cache(path, data)
            return data
        except Exception as e:
            logger.error(f"Error fetching '{path}' from Firebase: {e}")
            raise
        finally:
            # Always clean up the in-flight cache
            if path in self.current_fetches:
                del self.current_fetches[path]

    async def _perform_fetch(self, path: str) -> dict:
        """
        Internal helper to perform the actual HTTP fetch.

        :param path: The path to fetch from Firebase.
        :return: The fetched data as a dictionary.
        """
        try:
            response = await self._client.get(f"{DATABASE_URL}/{path}.json")
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            logger.error(
                f"HTTP error fetching '{path}': {e.response.status_code}"
                f" - Response: {e.response.text}"
            )
            raise
        except httpx.RequestError as e:
            logger.error(f"Network error fetching '{path}': {e}")
            raise
        except json.JSONDecodeError as e:
            logger.error(
                f"JSON decode error for '{path}': {e}" f" - Response: {response.text}"
            )
            raise

    async def close(self):
        """
        Closes the HTTP client and database connection.
        """
        if self._client:
            await self._client.aclose()
        if self._db_conn:
            self._db_conn.close()
            logger.debug("Database connection closed.")
