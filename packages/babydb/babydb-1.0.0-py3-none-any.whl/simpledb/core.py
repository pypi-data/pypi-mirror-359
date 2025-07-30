import json
import os
import shlex
import csv
import threading
import tempfile
import time
import re
import shutil
import subprocess
import gzip
import logging
import configparser
import pkg_resources
import importlib.resources
from collections import defaultdict
from threading import Timer
from contextlib import contextmanager
from copy import deepcopy
from pathlib import Path

logging.basicConfig(level=logging.INFO, filename='simpledb.log', format='%(asctime)s - %(levelname)s - %(message)s')

class BTreeNode:
    def __init__(self, leaf=True):
        self.keys = []
        self.children = []
        self.leaf = leaf

class SimpleDB:
    def __init__(self, db_file=None, files_dir=None):
        config = configparser.ConfigParser()
        try:
            with importlib.resources.files('simpledb').joinpath('config.ini').open('r', encoding='utf-8') as f:
                config.read_file(f)
        except FileNotFoundError:
            raise FileNotFoundError("config.ini not found in the simpledb package")
        
        self.db_file = Path(db_file or config['SimpleDB'].get('db_file', 'database.json.gz'))
        self.files_dir = Path(files_dir or config['SimpleDB'].get('files_dir', 'files'))
        self.db_file.parent.mkdir(parents=True, exist_ok=True)
        self.files_dir.mkdir(parents=True, exist_ok=True)
        self.store = {}
        self.value_index = defaultdict(list)
        self.inverted_index = defaultdict(list)
        self.btree_root = BTreeNode()
        self.transaction_log = []
        self.transaction_active = False
        self.lock = threading.RLock()
        self.current_user = None
        self.current_role = None
        self.users = {
            "admin": {"password": "admin123", "role": "admin"},
            "user": {"password": "user123", "role": "user"}
        }
        self.load()

    @contextmanager
    def timeout(self, seconds):
        def timeout_handler():
            raise TimeoutError("Operation timed out")
        timer = Timer(seconds, timeout_handler)
        timer.start()
        try:
            yield
        finally:
            timer.cancel()

    def login(self, username, password):
        logging.info("Attempting to acquire lock for login")
        if not self.lock.acquire(timeout=5):
            logging.error("Timeout acquiring lock for login")
            raise TimeoutError("Timeout acquiring lock for login")
        try:
            logging.info(f"Processing login for user '{username}'")
            if username in self.users and self.users[username]["password"] == password:
                self.current_user = username
                self.current_role = self.users[username]["role"]
                logging.info(f"Logged in as {username} with role {self.current_role}")
                return f"Logged in as {username} ({self.current_role})"
            return "Error: Invalid username or password"
        finally:
            logging.info("Releasing lock for login")
            self.lock.release()

    def logout(self):
        logging.info("Attempting to acquire lock for logout")
        if not self.lock.acquire(timeout=5):
            logging.error("Timeout acquiring lock for logout")
            raise TimeoutError("Timeout acquiring lock for logout")
        try:
            logging.info("Processing logout")
            if not self.current_user:
                return "Error: No user is logged in"
            username = self.current_user
            self.current_user = None
            self.current_role = None
            logging.info("Logged out")
            return f"Logged out user {username}"
        finally:
            logging.info("Releasing lock for logout")
            self.lock.release()

    def load(self):
        logging.info("Attempting to acquire lock for load")
        if not self.lock.acquire(timeout=5):
            logging.error("Timeout acquiring lock for load")
            raise TimeoutError("Timeout acquiring lock for load")
        try:
            logging.info("Entering load method")
            legacy_db_file = self.db_file.with_suffix('.json')
            if legacy_db_file.exists():
                logging.info(f"Found legacy {legacy_db_file}, converting to {self.db_file}")
                with open(legacy_db_file, 'r') as f:
                    self.store = json.load(f)
                for key, value in self.store.items():
                    if isinstance(value, dict) and "file_path" in value:
                        value["file_paths"] = [{"path": value["file_path"], "original_ext": os.path.splitext(value["file_path"])[1], "size": os.path.getsize(value["file_path"]), "original_size": os.path.getsize(value["file_path"]), "uploaded": time.strftime("%Y-%m-%dT%H:%M:%S"), "mime": self._get_mime_type(value["file_path"])}]
                        del value["file_path"]
                self.save()
                os.remove(legacy_db_file)
                logging.info(f"Converted and removed {legacy_db_file}")
            if self.db_file.exists():
                try:
                    with self.timeout(5):
                        logging.info("Opening compressed database file for reading")
                        with gzip.open(self.db_file, 'rt', encoding='utf-8') as f:
                            logging.info("Reading compressed database file")
                            self.store = json.load(f)
                            if not isinstance(self.store, dict):
                                raise ValueError("Invalid database format")
                    logging.info("Rebuilding indices")
                    self.rebuild_indices()
                    logging.info(f"Loaded compressed database from {self.db_file}")
                except (json.JSONDecodeError, ValueError):
                    logging.error(f"{self.db_file} is corrupted. Starting with an empty database.")
                    self.store = {}
                    self.save()
                except TimeoutError:
                    logging.error(f"Timeout while reading {self.db_file}")
                except Exception as e:
                    logging.error(f"Error loading database: {e}")
            else:
                logging.info("No database file found. Starting with an empty database.")
            logging.info("Exiting load method")
        finally:
            logging.info("Releasing lock for load")
            self.lock.release()

    def save(self):
        logging.info("Attempting to acquire lock for save")
        if not self.lock.acquire(timeout=5):
            logging.error("Timeout acquiring lock for save")
            raise TimeoutError("Timeout acquiring lock for save")
        try:
            logging.info("Entering save method")
            db_dir = str(self.db_file.parent)
            if not os.access(db_dir, os.W_OK):
                logging.error(f"No write permission for directory {db_dir}")
                raise PermissionError(f"No write permission for directory {db_dir}")
            if self.db_file.exists() and not os.access(self.db_file, os.W_OK):
                logging.error(f"No write permission for {self.db_file}")
                raise PermissionError(f"No write permission for {self.db_file}")
            try:
                if self.db_file.exists() and self.db_file.stat().st_size > 0:
                    backup_file = str(self.db_file) + '.bak'
                    with self.timeout(5):
                        logging.info("Creating backup")
                        with open(self.db_file, 'rb') as src, open(backup_file, 'wb') as dst:
                            dst.write(src.read())
                            logging.info("Backup created")
                with self.timeout(5):
                    logging.info("Creating temporary file")
                    with tempfile.NamedTemporaryFile('wb', delete=False, dir=db_dir, suffix='.gz') as temp_file:
                        logging.info("Writing to compressed temporary file")
                        with gzip.GzipFile(fileobj=temp_file, mode='wb') as gz:
                            gz.write(json.dumps(self.store, indent=2).encode('utf-8'))
                        temp_file.flush()
                        os.fsync(temp_file.fileno())
                        temp_name = temp_file.name
                    logging.info(f"Renaming {temp_name} to {self.db_file}")
                    os.replace(temp_name, self.db_file)
                    logging.info(f"Saved compressed database to {self.db_file}")
                logging.info("File write completed")
            except TimeoutError:
                logging.error(f"Timeout while writing to {self.db_file}")
                raise
            except Exception as e:
                logging.error(f"Error saving database: {e}")
                raise
            logging.info("Exiting save method")
        finally:
            logging.info("Releasing lock for save")
            self.lock.release()

    def _get_mime_type(self, file_path):
        ext = os.path.splitext(file_path)[1].lower()
        return {'jpg': 'image/jpeg', 'jpeg': 'image/jpeg', 'png': 'image/png', 'gif': 'image/gif', 'pdf': 'application/pdf', 'doc': 'application/msword', 'docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'}.get(ext[1:], 'application/octet-stream')

    def upload(self, key, file_path):
        logging.info("Attempting to acquire lock for upload")
        if not self.lock.acquire(timeout=5):
            logging.error("Timeout acquiring lock for upload")
            raise TimeoutError("Timeout acquiring lock for upload")
        try:
            logging.info(f"Uploading file for key '{key}'")
            if not self.current_user or self.current_role != "admin":
                return "Error: Admin privileges required to upload files"
            if key not in self.store:
                return f"Error: Key '{key}' not found."
            if not os.path.exists(file_path):
                return f"Error: File '{file_path}' not found."
            allowed_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.pdf', '.doc', '.docx'}
            file_ext = os.path.splitext(file_path)[1].lower()
            if file_ext not in allowed_extensions:
                return f"Error: Unsupported file type. Allowed: {', '.join(allowed_extensions)}"
            file_size = os.path.getsize(file_path)
            if file_size > 10 * 1024 * 1024:  # 10MB limit
                return "Error: File size exceeds 10MB limit"
            dest_filename = f"{key}_{os.path.basename(file_path)}.gz"
            dest_path = self.files_dir / dest_filename
            with open(file_path, 'rb') as src, gzip.open(dest_path, 'wb') as dst:
                shutil.copyfileobj(src, dst)
            compressed_size = os.path.getsize(dest_path)
            file_metadata = {
                "path": str(dest_path),
                "original_ext": file_ext,
                "size": compressed_size,
                "original_size": file_size,
                "uploaded": time.strftime("%Y-%m-%dT%H:%M:%S"),
                "mime": self._get_mime_type(file_path)
            }
            if "file_paths" not in self.store[key]:
                self.store[key]["file_paths"] = []
            self.store[key]["file_paths"].append(file_metadata)
            if self.transaction_active:
                self.transaction_log.append(("upload", key, None))
                logging.info(f"Added upload operation to transaction log for {key}")
            if not self.transaction_active:
                logging.info("Calling save method")
                self.save()
            logging.info(f"Uploaded compressed file for {key}: {dest_path}")
            return f"Uploaded compressed file for {key}: {dest_path} (Original size: {file_size} bytes, Compressed size: {compressed_size} bytes)"
        finally:
            logging.info("Releasing lock for upload")
            self.lock.release()

    def get_file(self, key, index=None):
        logging.info("Attempting to acquire lock for get_file")
        if not self.lock.acquire(timeout=5):
            logging.error("Timeout acquiring lock for get_file")
            raise TimeoutError("Timeout acquiring lock for get_file")
        try:
            logging.info(f"Retrieving file for key '{key}'")
            if not self.current_user:
                return "Error: Must be logged in to access files"
            if key not in self.store:
                return f"Error: Key '{key}' not found."
            if "file_paths" not in self.store[key] or not self.store[key]["file_paths"]:
                return f"Error: No files associated with key '{key}'."
            file_paths = self.store[key]["file_paths"]
            if index is not None:
                try:
                    index = int(index)
                    if index < 0 or index >= len(file_paths):
                        return f"Error: Invalid file index {index}. Available: 0 to {len(file_paths)-1}"
                    file_metadata = file_paths[index]
                    file_path = file_metadata["path"]
                    original_ext = file_metadata["original_ext"]
                    metadata_str = f"Size: {file_metadata['size']} bytes, Original size: {file_metadata['original_size']} bytes, Uploaded: {file_metadata['uploaded']}, MIME: {file_metadata['mime']}"
                except ValueError:
                    return "Error: Index must be an integer"
            else:
                return "\n".join(f"[{i}] {f['path']} (Size: {f['size']} bytes, Original size: {f['original_size']} bytes, Uploaded: {f['uploaded']}, MIME: {f['mime']})" for i, f in enumerate(file_paths))
            if not os.path.exists(file_path):
                return f"Error: File '{file_path}' not found on disk."
            temp_dir = tempfile.gettempdir()
            temp_filename = f"{key}_decompressed{original_ext}"
            temp_path = os.path.join(temp_dir, temp_filename)
            try:
                with gzip.open(file_path, 'rb') as src, open(temp_path, 'wb') as dst:
                    shutil.copyfileobj(src, dst)
                if os.name == 'nt':
                    subprocess.run(['start', '', temp_path], shell=True, check=True)
                elif os.name == 'posix':
                    viewers = [('xdg-open', ['xdg-open', temp_path]), ('eog', ['eog', temp_path]), ('firefox', ['firefox', temp_path])]
                    for viewer_name, viewer_cmd in viewers:
                        if shutil.which(viewer_name):
                            subprocess.run(viewer_cmd, check=True)
                            return f"Opened file: {file_path} with {viewer_name} ({metadata_str})"
                    return f"File path: {temp_path} (No viewer installed; install 'eog' or 'firefox' with 'sudo apt install eog firefox' or open manually) ({metadata_str})"
                return f"Opened file: {temp_path} ({metadata_str})"
            except Exception as e:
                return f"File path: {temp_path} (Open manually due to error: {e}) ({metadata_str})"
            finally:
                if os.path.exists(temp_path):
                    os.remove(temp_path)
        finally:
            logging.info("Releasing lock for get_file")
            self.lock.release()

    def download_file(self, key, index=None, dest_path=None):
        logging.info("Attempting to acquire lock for download_file")
        if not self.lock.acquire(timeout=5):
            logging.error("Timeout acquiring lock for download_file")
            raise TimeoutError("Timeout acquiring lock for download_file")
        try:
            logging.info(f"Downloading file for key '{key}'")
            if not self.current_user:
                return "Error: Must be logged in to download files"
            if key not in self.store:
                return f"Error: Key '{key}' not found."
            if "file_paths" not in self.store[key] or not self.store[key]["file_paths"]:
                return f"Error: No files associated with key '{key}'."
            file_paths = self.store[key]["file_paths"]
            if index is not None:
                try:
                    index = int(index)
                    if index < 0 or index >= len(file_paths):
                        return f"Error: Invalid file index {index}. Available: 0 to {len(file_paths)-1}"
                    file_metadata = file_paths[index]
                    file_path = file_metadata["path"]
                    original_ext = file_metadata["original_ext"]
                except ValueError:
                    return "Error: Index must be an integer"
            else:
                if len(file_paths) > 1:
                    return f"Error: Multiple files exist. Specify an index (0 to {len(file_paths)-1}): {', '.join(f['path'] for f in file_paths)}"
                file_metadata = file_paths[0]
                file_path = file_metadata["path"]
                original_ext = file_metadata["original_ext"]
            if not os.path.exists(file_path):
                return f"Error: File '{file_path}' not found on disk."
            if not dest_path:
                dest_path = f"{key}_decompressed{original_ext}"
            try:
                with gzip.open(file_path, 'rb') as src, open(dest_path, 'wb') as dst:
                    shutil.copyfileobj(src, dst)
                return f"Downloaded decompressed file to: {dest_path}"
            except Exception as e:
                return f"Error downloading file: {e}"
        finally:
            logging.info("Releasing lock for download_file")
            self.lock.release()

    def delete(self, key):
        logging.info("Attempting to acquire lock for delete")
        if not self.lock.acquire(timeout=5):
            logging.error("Timeout acquiring lock for delete")
            raise TimeoutError("Timeout acquiring lock for delete")
        try:
            logging.info(f"Attempting to delete key '{key}'")
            if not self.current_user or self.current_role != "admin":
                return "Error: Admin privileges required to delete"
            if key not in self.store:
                return f"Error: Key '{key}' not found."
            value = deepcopy(self.store[key])
            try:
                if self.transaction_active:
                    self.transaction_log.append(("delete", key, value))
                    logging.info(f"Added delete operation to transaction log for {key}")
                if "file_paths" in value:
                    for file_metadata in value["file_paths"]:
                        if os.path.exists(file_metadata["path"]):
                            os.remove(file_metadata["path"])
                            logging.info(f"Deleted compressed file {file_metadata['path']}")
                del self.store[key]
                logging.info(f"Removed key '{key}' from store")
                value_key = json.dumps(value, sort_keys=True)
                if key in self.value_index[value_key]:
                    self.value_index[value_key].remove(key)
                    logging.info(f"Removed key '{key}' from value_index for value {value_key}")
                    if not self.value_index[value_key]:
                        del self.value_index[value_key]
                        logging.info(f"Deleted empty value_index entry for {value_key}")
                value_str = str(value).lower()
                words = set(re.findall(r'\b\w+\b', value_str))
                for word in words:
                    if word and key in self.inverted_index[word]:
                        self.inverted_index[word].remove(key)
                        if not self.inverted_index[word]:
                            del self.inverted_index[word]
                            logging.info(f"Deleted empty inverted_index entry for word '{word}'")
                self.btree_root.keys = [(k, v) for k, v in self.btree_root.keys if k != key]
                logging.info(f"Removed {key} from B-tree")
                if not self.transaction_active:
                    logging.info("Calling save method")
                    self.save()
                logging.info(f"Completed deletion of key '{key}'")
                return f"Deleted key: {key}"
            except Exception as e:
                logging.error(f"Error during delete: {e}")
                return f"Error deleting key '{key}': {e}"
        finally:
            logging.info("Releasing lock for delete")
            self.lock.release()

    def rollback(self):
        logging.info("Attempting to acquire lock for rollback")
        if not self.lock.acquire(timeout=5):
            logging.error("Timeout acquiring lock for rollback")
            raise TimeoutError("Timeout acquiring lock for rollback")
        try:
            logging.info("Rolling back transaction")
            if not self.current_user:
                return "Error: Must be logged in to rollback a transaction"
            if not self.transaction_active:
                return "Error: No transaction in progress."
            try:
                for op, key, old_value in self.transaction_log:
                    if op == "create":
                        if key in self.store:
                            value = self.store[key]
                            if isinstance(value, dict) and "file_paths" in value:
                                for file_metadata in value["file_paths"]:
                                    if os.path.exists(file_metadata["path"]):
                                        os.remove(file_metadata["path"])
                            del self.store[key]
                            value_key = json.dumps(old_value, sort_keys=True) if old_value is not None else None
                            if value_key and key in self.value_index[value_key]:
                                self.value_index[value_key].remove(key)
                                if not self.value_index[value_key]:
                                    del self.value_index[value_key]
                            value_str = str(old_value).lower() if old_value else ""
                            words = set(re.findall(r'\b\w+\b', value_str))
                            for word in words:
                                if word and key in self.inverted_index[word]:
                                    self.inverted_index[word].remove(key)
                                    if not self.inverted_index[word]:
                                        del self.inverted_index[word]
                            self.btree_root.keys = [(k, v) for k, v in self.btree_root.keys if k != key]
                    elif op == "update":
                        self.store[key] = old_value
                        self.rebuild_indices()
                    elif op == "delete":
                        self.store[key] = old_value
                        self.rebuild_indices()
                    elif op == "upload":
                        if key in self.store and isinstance(self.store[key], dict) and "file_paths" in self.store[key]:
                            if self.store[key]["file_paths"]:
                                last_file = self.store[key]["file_paths"].pop()
                                if os.path.exists(last_file["path"]):
                                    os.remove(last_file["path"])
                                if not self.store[key]["file_paths"]:
                                    del self.store[key]["file_paths"]
                                self.rebuild_indices()
                self.transaction_log = []
                self.transaction_active = False
                logging.info("Transaction rolled back")
                return "Transaction rolled back."
            except Exception as e:
                logging.error(f"Error during rollback: {e}")
                return f"Error rolling back transaction: {e}"
        finally:
            logging.info("Releasing lock for rollback")
            self.lock.release()

    def parse_value(self, value):
        logging.info(f"Parsing value '{value}'")
        try:
            parsed = json.loads(value)
            logging.info(f"Parsed value to {parsed}")
            if isinstance(parsed, dict):
                expected_fields = {'Name', 'Age', 'Grade', 'Class', 'Subjects'}
                if all(field in parsed for field in expected_fields):
                    if not isinstance(parsed['Name'], str):
                        logging.info("Validation failed: Name must be a string")
                        return value
                    if not isinstance(parsed['Age'], int):
                        logging.info("Validation failed: Age must be an integer")
                        return value
                    if not isinstance(parsed['Grade'], (int, str)):
                        logging.info("Validation failed: Grade must be an integer or string")
                        return value
                    if not isinstance(parsed['Class'], str):
                        logging.info("Validation failed: Class must be a string")
                        return value
                    if not isinstance(parsed['Subjects'], list) or not all(isinstance(s, str) for s in parsed['Subjects']):
                        logging.info("Validation failed: Subjects must be a list of strings")
                        return value
                    logging.info("Student data validation passed")
            return parsed
        except json.JSONDecodeError as e:
            logging.info(f"Value '{value}' not valid JSON: {e}. Treating as string")
            return value

    def create(self, key, value):
        logging.info("Attempting to acquire lock for create")
        if not self.lock.acquire(timeout=5):
            logging.error("Timeout acquiring lock for create")
            raise TimeoutError("Timeout acquiring lock for create")
        try:
            logging.info(f"Creating key '{key}' with value '{value}'")
            if not self.current_user:
                return "Error: Must be logged in to create a key"
            if key in self.store:
                logging.info(f"Key '{key}' already exists")
                return f"Error: Key '{key}' already exists."
            parsed_value = self.parse_value(value)
            logging.info(f"Parsed value: {parsed_value}")
            if self.transaction_active:
                self.transaction_log.append(("create", key, None))
                logging.info(f"Added create operation to transaction log for {key}")
            self.store[key] = parsed_value
            logging.info(f"Added {key} to store")
            value_key = json.dumps(parsed_value, sort_keys=True)
            self.value_index[value_key].append(key)
            logging.info(f"Added {key} to value_index with value_key {value_key}")
            value_str = str(parsed_value).lower()
            words = set(re.findall(r'\b\w+\b', value_str))
            logging.info(f"Extracted words for '{key}': {words}")
            for word in words:
                if word:
                    self.inverted_index[word].append(key)
                    logging.info(f"Added {key} to inverted_index for word '{word}'")
            if isinstance(parsed_value, (int, float)):
                self.btree_insert(key, parsed_value)
                logging.info(f"Added {key}:{parsed_value} to B-tree")
            if not self.transaction_active:
                logging.info("Calling save method")
                self.save()
            logging.info(f"Completed create for key '{key}'")
            return f"Inserted: {key} -> {json.dumps(parsed_value)}"
        finally:
            logging.info("Releasing lock for create")
            self.lock.release()

    def read(self, key):
        logging.info("Attempting to acquire lock for read")
        if not self.lock.acquire(timeout=5):
            logging.error("Timeout acquiring lock for read")
            raise TimeoutError("Timeout acquiring lock for read")
        try:
            logging.info(f"Reading key '{key}'")
            if not self.current_user:
                return "Error: Must be logged in to read a key"
            if key not in self.store:
                return f"Error: Key '{key}' not found."
            return json.dumps(self.store[key])
        finally:
            logging.info("Releasing lock for read")
            self.lock.release()

    def update(self, key, value):
        logging.info("Attempting to acquire lock for update")
        if not self.lock.acquire(timeout=5):
            logging.error("Timeout acquiring lock for update")
            raise TimeoutError("Timeout acquiring lock for update")
        try:
            logging.info(f"Updating key '{key}'")
            if not self.current_user:
                return "Error: Must be logged in to update a key"
            if key not in self.store:
                return f"Error: Key '{key}' not found."
            old_value = deepcopy(self.store[key])
            parsed_value = self.parse_value(value)
            if isinstance(old_value, dict) and "file_paths" in old_value:
                parsed_value["file_paths"] = old_value["file_paths"]
            if self.transaction_active:
                self.transaction_log.append(("update", key, old_value))
                logging.info(f"Added update operation to transaction log for {key}")
            self.store[key] = parsed_value
            logging.info(f"Updated store for {key}")
            old_value_key = json.dumps(old_value, sort_keys=True)
            if key in self.value_index[old_value_key]:
                self.value_index[old_value_key].remove(key)
                logging.info(f"Removed {key} from value_index for {old_value_key}")
                if not self.value_index[old_value_key]:
                    del self.value_index[old_value_key]
                    logging.info(f"Deleted empty value_index entry for {old_value_key}")
            value_key = json.dumps(parsed_value, sort_keys=True)
            self.value_index[value_key].append(key)
            logging.info(f"Added {key} to value_index with value_key {value_key}")
            old_value_str = str(old_value).lower()
            old_words = set(re.findall(r'\b\w+\b', old_value_str))
            for word in old_words:
                if word and key in self.inverted_index[word]:
                    self.inverted_index[word].remove(key)
                    if not self.inverted_index[word]:
                        del self.inverted_index[word]
            new_value_str = str(parsed_value).lower()
            new_words = set(re.findall(r'\b\w+\b', new_value_str))
            logging.info(f"Extracted words for '{key}': {new_words}")
            for word in new_words:
                if word:
                    self.inverted_index[word].append(key)
                    logging.info(f"Added {key} to inverted_index for word '{word}'")
            self.btree_root.keys = [(k, v) for k, v in self.btree_root.keys if k != key]
            logging.info(f"Removed {key} from B-tree")
            if isinstance(parsed_value, (int, float)):
                self.btree_insert(key, parsed_value)
                logging.info(f"Added {key}:{parsed_value} to B-tree")
            if not self.transaction_active:
                logging.info("Calling save method")
                self.save()
            logging.info(f"Completed update for key '{key}'")
            return f"Updated: {key} -> {json.dumps(parsed_value)}"
        finally:
            logging.info("Releasing lock for update")
            self.lock.release()

    def rebuild_indices(self):
        logging.info("Attempting to acquire lock for rebuild_indices")
        if not self.lock.acquire(timeout=5):
            logging.error("Timeout acquiring lock for rebuild_indices")
            raise TimeoutError("Timeout acquiring lock for rebuild_indices")
        try:
            logging.info("Rebuilding indices")
            self.value_index = defaultdict(list)
            self.inverted_index = defaultdict(list)
            self.btree_root = BTreeNode()
            numeric_pairs = []
            try:
                with self.timeout(30):
                    for key, value in self.store.items():
                        logging.info(f"Processing key '{key}' with value {value}")
                        try:
                            value_key = json.dumps(value, sort_keys=True)
                            self.value_index[value_key].append(key)
                            logging.info(f"Added {key} to value_index with value_key {value_key}")
                            value_str = str(value).lower()
                            logging.info(f"Tokenized string for '{key}': {value_str}")
                            words = set(re.findall(r'\b\w+\b', value_str))
                            logging.info(f"Extracted words for '{key}': {words}")
                            for word in words:
                                if word:
                                    self.inverted_index[word].append(key)
                                    logging.info(f"Added {key} to inverted_index for word '{word}'")
                            if isinstance(value, (int, float)):
                                numeric_pairs.append((key, value))
                                logging.info(f"Queued {key}:{value} for B-tree")
                        except Exception as e:
                            logging.error(f"Error processing key '{key}': {e}")
                            continue
                    if numeric_pairs:
                        logging.info("Performing batch B-tree insertion")
                        self.btree_root.keys.extend(numeric_pairs)
                        self.btree_root.keys.sort(key=lambda x: x[1])
                        logging.info(f"Inserted {len(numeric_pairs)} numeric pairs into B-tree")
                logging.info("Indices rebuilt")
            except TimeoutError:
                logging.error("Timeout while rebuilding indices")
                raise
            except Exception as e:
                logging.error(f"Error rebuilding indices: {e}")
                raise
        finally:
            logging.info("Releasing lock for rebuild_indices")
            self.lock.release()

    def btree_insert(self, key, value):
        logging.info("Attempting to acquire lock for btree_insert")
        if not self.lock.acquire(timeout=5):
            logging.error("Timeout acquiring lock for btree_insert")
            raise TimeoutError("Timeout acquiring lock for btree_insert")
        try:
            logging.info(f"Inserting {key}:{value} into B-tree")
            node = self.btree_root
            node.keys.append((key, value))
            node.keys.sort(key=lambda x: x[1])
            logging.info(f"Inserted {key}:{value} into B-tree")
        finally:
            logging.info("Releasing lock for btree_insert")
            self.lock.release()

    def btree_range_query(self, operator, query_value):
        logging.info("Attempting to acquire lock for btree_range_query")
        if not self.lock.acquire(timeout=5):
            logging.error("Timeout acquiring lock for btree_range_query")
            raise TimeoutError("Timeout acquiring lock for btree_range_query")
        try:
            logging.info(f"Performing B-tree range query with {operator} {query_value}")
            results = []
            for key, value in self.btree_root.keys:
                if (operator == ">" and value > query_value) or \
                   (operator == "<" and value < query_value):
                    results.append(key)
            logging.info(f"Range query results: {results}")
            return results
        finally:
            logging.info("Releasing lock for btree_range_query")
            self.lock.release()

    def get_sort_key(self, key, sort_field):
        value = self.store[key]
        if sort_field:
            if isinstance(value, dict) and sort_field in value:
                return value[sort_field]
            return float('-inf')
        return value if isinstance(value, (int, float, str)) else str(value)

    def find(self, query):
        logging.info("Attempting to acquire lock for find")
        if not self.lock.acquire(timeout=5):
            logging.error("Timeout acquiring lock for find")
            raise TimeoutError("Timeout acquiring lock for find")
        try:
            logging.info(f"Processing find query: {query}")
            if not self.current_user:
                return "Error: Must be logged in to perform a find query"
            parts = shlex.split(query)
            if len(parts) < 2:
                return "Invalid query. Use: = <value>, > <value>, < <value>, contains <value>, fulltext <value>, <field> = <value> [sortby <field>] [limit <n>]"
            sort_field = None
            limit = None
            main_query = parts[:]
            if "sortby" in parts:
                sort_idx = parts.index("sortby")
                if sort_idx + 1 < len(parts):
                    sort_field = parts[sort_idx + 1]
                    main_query = parts[:sort_idx] + parts[sort_idx + 2:]
            if "limit" in parts:
                limit_idx = parts.index("limit")
                if limit_idx + 1 < len(parts):
                    try:
                        limit = int(parts[limit_idx + 1])
                        if limit <= 0:
                            return "Error: Limit must be a positive integer"
                        main_query = parts[:limit_idx] + parts[limit_idx + 2:]
                    except ValueError:
                        return "Error: Limit must be a valid integer"
            field_or_op = main_query[0]
            query_value = " ".join(main_query[1:]) if len(main_query) > 1 else ""
            if field_or_op == "contains":
                parsed_query_value = query_value.strip('"\'')
                logging.info(f"Using raw string value '{parsed_query_value}' for contains query")
            elif field_or_op == "fulltext":
                parsed_query_value = query_value.strip('"\'')
                logging.info(f"Using raw string value '{parsed_query_value}' for fulltext query")
            else:
                parsed_query_value = self.parse_value(query_value)
            if field_or_op in ("=", ">", "<", "contains", "fulltext"):
                operator = field_or_op
                if operator == "=":
                    value_key = json.dumps(parsed_query_value, sort_keys=True)
                    results = self.value_index.get(value_key, [])
                elif operator in (">", "<"):
                    if not isinstance(parsed_query_value, (int, float)):
                        return "Error: Range queries only support numeric values."
                    results = self.btree_range_query(operator, parsed_query_value)
                elif operator == "contains":
                    if not isinstance(parsed_query_value, str):
                        return "Error: Contains queries only support string values."
                    results = []
                    for key, value in self.store.items():
                        value_str = str(value).lower()
                        logging.info(f"Checking key '{key}' with value_str '{value_str}' for substring '{parsed_query_value.lower()}'")
                        if parsed_query_value.lower() in value_str:
                            results.append(key)
                elif operator == "fulltext":
                    if not isinstance(parsed_query_value, str):
                        return "Error: Fulltext queries only support string values."
                    words = set(parsed_query_value.lower().split())
                    if not words:
                        return "Error: Fulltext query cannot be empty."
                    result_sets = [set(self.inverted_index[word]) for word in words if word in self.inverted_index]
                    logging.info(f"Inverted index for query terms: {[(word, self.inverted_index[word]) for word in words if word in self.inverted_index]}")
                    if not result_sets:
                        return "No keys found with the specified terms."
                    results = list(set.intersection(*result_sets))
                    logging.info(f"Fulltext query results: {results}")
                else:
                    return "Invalid operator"
            else:
                field = field_or_op
                if len(main_query) < 3 or main_query[1] != "=":
                    return "Invalid field query. Use: <field> = <value> [sortby <field>] [limit <n>]"
                parsed_query_value = self.parse_value(" ".join(main_query[2:]))
                results = [key for key, value in self.store.items() if isinstance(value, dict) and field in value and value[field] == parsed_query_value]
            if sort_field:
                try:
                    results.sort(key=lambda key: self.get_sort_key(key, sort_field))
                except Exception as e:
                    return f"Error sorting results: {e}"
            if limit is not None:
                results = results[:limit]
            return "Found keys: " + ", ".join(results) if results else "No keys found with the specified condition."
        finally:
            logging.info("Releasing lock for find")
            self.lock.release()

    def inspect_inverted_index(self, word=None):
        logging.info("Attempting to acquire lock for inspect_inverted_index")
        if not self.lock.acquire(timeout=5):
            logging.error("Timeout acquiring lock for inspect_inverted_index")
            raise TimeoutError("Timeout acquiring lock for inspect_inverted_index")
        try:
            logging.info("Inspecting inverted index")
            if not self.current_user:
                return "Error: Must be logged in to inspect inverted index"
            if word:
                return f"Inverted index for '{word}': {self.inverted_index.get(word.lower(), [])}"
            return "\n".join(f"Word '{w}': {keys}" for w, keys in self.inverted_index.items())
        finally:
            logging.info("Releasing lock for inspect_inverted_index")
            self.lock.release()

    def join(self, key1, key2, field=None):
        logging.info("Attempting to acquire lock for join")
        if not self.lock.acquire(timeout=5):
            logging.error("Timeout acquiring lock for join")
            raise TimeoutError("Timeout acquiring lock for join")
        try:
            logging.info(f"Processing join: key1={key1}, key2={key2}, field={field}")
            if not self.current_user:
                return "Error: Must be logged in to perform a join"
            if key1 not in self.store or key2 not in self.store:
                return f"Error: One or both keys not found: {key1}, {key2}"
            value1 = self.store[key1]
            value2 = self.store[key2]
            if field:
                if not (isinstance(value1, dict) and isinstance(value2, dict)):
                    return f"Error: Field-based join requires dictionary values for {key1} and {key2}."
                if field not in value1 or field not in value2:
                    return f"Error: Field '{field}' not found in one or both values."
                if value1[field] == value2[field]:
                    return f"Join result on field '{field}': {key1}={json.dumps(value1)}, {key2}={json.dumps(value2)}"
                return f"No match: {key1} and {key2} have different values for field '{field}'."
            else:
                if value1 == value2:
                    return f"Join result: {key1}={json.dumps(value1)}, {key2}={json.dumps(value2)}"
                return f"No match: {key1} and {key2} have different values."
        finally:
            logging.info("Releasing lock for join")
            self.lock.release()

    def max(self, key):
        logging.info("Attempting to acquire lock for max")
        if not self.lock.acquire(timeout=5):
            logging.error("Timeout acquiring lock for max")
            raise TimeoutError("Timeout acquiring lock for max")
        try:
            logging.info(f"Processing max for key '{key}'")
            if not self.current_user:
                return "Error: Must be logged in to perform max operation"
            if key not in self.store:
                return f"Error: Key '{key}' not found."
            value = self.store[key]
            if isinstance(value, (int, float)):
                return f"Max for {key}: {value}"
            elif isinstance(value, list) and all(isinstance(x, (int, float)) for x in value):
                return f"Max for {key}: {max(value)}"
            return f"Error: Max only supported for numbers or lists of numbers."
        finally:
            logging.info("Releasing lock for max")
            self.lock.release()

    def min(self, key):
        logging.info("Attempting to acquire lock for min")
        if not self.lock.acquire(timeout=5):
            logging.error("Timeout acquiring lock for min")
            raise TimeoutError("Timeout acquiring lock for min")
        try:
            logging.info(f"Processing min for key '{key}'")
            if not self.current_user:
                return "Error: Must be logged in to perform min operation"
            if key not in self.store:
                return f"Error: Key '{key}' not found."
            value = self.store[key]
            if isinstance(value, (int, float)):
                return f"Min for {key}: {value}"
            elif isinstance(value, list) and all(isinstance(x, (int, float)) for x in value):
                return f"Min for {key}: {min(value)}"
            return f"Error: Min only supported for numbers or lists of numbers."
        finally:
            logging.info("Releasing lock for min")
            self.lock.release()

    def sum(self, key):
        logging.info("Attempting to acquire lock for sum")
        if not self.lock.acquire(timeout=5):
            logging.error("Timeout acquiring lock for sum")
            raise TimeoutError("Timeout acquiring lock for sum")
        try:
            logging.info(f"Processing sum for key '{key}'")
            if not self.current_user:
                return "Error: Must be logged in to perform sum operation"
            if key not in self.store:
                return f"Error: Key '{key}' not found."
            value = self.store[key]
            if isinstance(value, (int, float)):
                return f"Sum for {key}: {value}"
            elif isinstance(value, list) and all(isinstance(x, (int, float)) for x in value):
                return f"Sum for {key}: {sum(value)}"
            return f"Error: Sum only supported for numbers or lists of numbers."
        finally:
            logging.info("Releasing lock for sum")
            self.lock.release()

    def avg(self, key):
        logging.info("Attempting to acquire lock for avg")
        if not self.lock.acquire(timeout=5):
            logging.error("Timeout acquiring lock for avg")
            raise TimeoutError("Timeout acquiring lock for avg")
        try:
            logging.info(f"Processing avg for key '{key}'")
            if not self.current_user:
                return "Error: Must be logged in to perform avg operation"
            if key not in self.store:
                return f"Error: Key '{key}' not found."
            value = self.store[key]
            if isinstance(value, (int, float)):
                return f"Average for {key}: {value}"
            elif isinstance(value, list) and all(isinstance(x, (int, float)) for x in value):
                return f"Average for {key}: {sum(value) / len(value)}"
            return f"Error: Average only supported for numbers or lists of numbers."
        finally:
            logging.info("Releasing lock for avg")
            self.lock.release()

    def list_all(self):
        logging.info("Attempting to acquire lock for list_all")
        if not self.lock.acquire(timeout=5):
            logging.error("Timeout acquiring lock for list_all")
            raise TimeoutError("Timeout acquiring lock for list_all")
        try:
            logging.info("Listing all key-value pairs")
            if not self.current_user:
                return "Error: Must be logged in to list all keys"
            if not self.store:
                return "Database is empty."
            return "\n".join(f"{key}: {json.dumps(value)}" for key, value in self.store.items())
        finally:
            logging.info("Releasing lock for list_all")
            self.lock.release()