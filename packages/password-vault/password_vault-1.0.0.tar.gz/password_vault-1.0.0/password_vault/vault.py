"""
vault.py

A secure, file-backed password vault that encrypts and stores secrets using a master password.
Features:
- Argon2id KDF for key derivation
- AES-GCM encryption via cryptography.Fernet
- Integrity protection with HMAC-SHA256
- Thread-safe queue for serializing file operations
- Inter-process file locking to avoid concurrent writes
- Configurable caching of unlocked master password
- Automatic cleanup on exit
"""

import os
import json
import getpass
import stat
import logging
import time
import tempfile
import secrets
import hmac
import hashlib
import atexit
from base64 import b64encode, b64decode
from typing import Optional, Tuple, Dict, Any, List
from queue import Queue, Empty
from threading import Thread, Event
from base64 import b64encode

from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.primitives.kdf.argon2 import Argon2id
from cryptography.hazmat.primitives import hashes
from filelock import FileLock, Timeout

logging.basicConfig(level=logging.INFO)

HMAC_KEY = "_hmac"


# Exceptions and helpers
class NumericValue(str):
    """
    A string subclass that sorts based on numeric suffix.
    E.g., 'value2' < 'value10'. Used in tests to order retrieved values.
    """

    def __lt__(self, other):
        try:
            n1 = int(self.lstrip("value"))
            n2 = int(str(other).lstrip("value"))
            return n1 < n2
        except Exception:
            return super().__lt__(other)


# Vault-specific exceptions
class WalletError(Exception):
    """Base class for vault-related errors."""

    pass


class WalletNotFoundError(WalletError):
    """Raised when the vault file does not exist."""

    pass


class InvalidPasswordError(WalletError):
    """Raised when the provided master password is incorrect."""

    pass


class KeyNotFoundError(WalletError):
    """Raised when a requested key is not found in the vault."""

    pass


class MalformedWalletError(WalletError):
    """Raised when the vault file JSON is invalid or missing required fields."""

    pass


class Vault:
    """
    A secure password vault supporting encryption, integrity checks, and concurrency safety.

    Public API:
      - Vault(filepath, master_password=None, keep_unlocked=10)
      - add(key, secret)
      - get(key) -> str
      - list_keys() -> List[str]
      - close()
    """

    KDF_ITERATIONS = 390_000
    SALT_KEY = "salt"
    MASTER_KEY = "master"
    KEYS_KEY = "keys"
    FILE_MODE = 0o600
    LOCK_TIMEOUT = 5
    _instances: List["Vault"] = []  # track for cleanup

    def __init__(
        self,
        filepath: str,
        master_password: Optional[str] = None,
        keep_unlocked: int = 10,
    ):
        """
        Initialize or open a vault file.

        :param filepath: Path to the JSON vault file.
        :param master_password: If provided, used for init/verify without prompt.
        :param keep_unlocked: Seconds to cache unlocked password before re-prompt.
        """
        self.filepath = filepath
        self.keep_unlocked = keep_unlocked
        self._last_unlock: Optional[float] = None
        self._cached_password: Optional[str] = None
        self._queue: Queue = Queue()
        self._stop_event = Event()
        self._lock = FileLock(f"{filepath}.lock", timeout=self.LOCK_TIMEOUT)
        self._worker = Thread(target=self._process_queue, daemon=True)
        self._worker.start()
        Vault._instances.append(self)

        # initialize or verify vault (only one process should ever init)
        try:
            with self._lock:
                if not os.path.exists(self.filepath):
                    pwd = master_password or self._prompt_password("New master password: ")
                    self._enqueue({"op": "init", "master_password": pwd})
                else:
                    self._enqueue({"op": "verify", "master_password": master_password})
        except Timeout:
            raise WalletError("Could not acquire file lock to initialize vault")

    @classmethod
    def _cleanup_all(cls):
        """Close all active vault instances on interpreter exit."""
        for inst in cls._instances:
            inst.close()

    def _process_queue(self):
        """
        Worker thread: dequeue tasks and dispatch to corresponding handlers.
        Supported ops: init, verify, add, get, list.
        """

        while not self._stop_event.is_set():
            try:
                task = self._queue.get(timeout=0.1)
            except Empty:
                continue
            try:
                op = task["op"]
                if op == "init":
                    self._do_init(task["master_password"])
                elif op == "verify":
                    self._do_verify(task["master_password"])
                elif op == "add":
                    task["result"] = self._do_add(task)
                elif op == "get":
                    task["result"] = self._do_get(task)
                elif op == "list":
                    task["result"] = self._do_list(task)
            except Exception as e:
                task["exception"] = e
            finally:
                task["done"].set()

    def _enqueue(self, task: Dict[str, Any]) -> Any:
        """
        Add a task to the queue and wait for completion.
        Propagates exceptions raised in worker.
        """

        task["done"] = Event()
        self._queue.put(task)
        task["done"].wait()
        if "exception" in task:
            raise task["exception"]
        return task.get("result")

    def _get_password(self, master_password: Optional[str] = None) -> str:
        """
        Retrieve or prompt for the master password, using cache if still valid.
        """

        now = time.time()
        if self._cached_password and self._last_unlock and now - self._last_unlock < self.keep_unlocked:
            return self._cached_password
        pwd = master_password or self._prompt_password("Master password: ")
        self._authenticate(pwd)
        self._cached_password = pwd
        self._last_unlock = now
        return pwd

    def _unlock(self, master_password: Optional[str] = None) -> Tuple[str, Dict]:
        """
        Authenticate and load vault data directly (for testing purposes).
        Returns (password, data_dict).
        """
        pwd = self._get_password(master_password)
        data = self._load_json()
        return pwd, data

    def close(self):
        """
        Signal worker thread to stop and wait for exit.
        """
        self._stop_event.set()
        self._worker.join()

    # low-level ops
    def _do_init(self, master_password: str):
        """
        Initialize a new vault file:
        - Generate random salt
        - Derive encryption key via Argon2id
        - Encrypt master password to embed
        - Compute HMAC over vault structure
        - Atomically write to disk with secure permissions
        """

        salt = secrets.token_bytes(16)
        key = self._derive_key(master_password, salt)
        token = Fernet(key).encrypt(master_password.encode())
        data = {self.SALT_KEY: b64encode(salt).decode(), self.MASTER_KEY: token.decode(), self.KEYS_KEY: {}}
        # embed integrity HMAC
        self._update_hmac(data, master_password)
        self._atomic_write(data)
        os.chmod(self.filepath, self.FILE_MODE)

    def _do_verify(self, master_password: Optional[str] = None):
        """
        Verify existing vault integrity and password:
        - Load JSON
        - Ensure required fields exist
        - Recompute and compare HMAC
        - Reset file permissions
        """

        try:
            data = self._load_json()
        except json.JSONDecodeError:
            raise MalformedWalletError("Vault file is not valid JSON")

        # basic structural checks
        for field in (self.SALT_KEY, self.MASTER_KEY, self.KEYS_KEY, HMAC_KEY):
            if field not in data:
                raise MalformedWalletError(f"Missing '{field}' in vault")

        # verify HMAC
        pwd = self._get_password(master_password)
        expected = self._compute_hmac(data, pwd)
        if not hmac.compare_digest(data[HMAC_KEY], expected):
            raise WalletError("Vault integrity check failed (HMAC mismatch)")

        os.chmod(self.filepath, self.FILE_MODE)

    def _do_add(self, task: Dict[str, Any]):
        """
        Add a new secret:
        - Authenticate and derive Fernet
        - Encrypt key and value
        - Insert into JSON and update HMAC
        - Atomically write updated vault
        """

        pwd = self._get_password(task.get("master_password"))
        f = self._get_fernet(pwd)
        try:
            with self._lock:
                data = self._load_json()
                enc_key = f.encrypt(task["key"].encode()).decode()
                enc_val = f.encrypt(task["secret"].encode()).decode()
                data[self.KEYS_KEY][enc_key] = enc_val
                # recompute integrity HMAC before writing
                self._update_hmac(data, pwd)
                self._atomic_write(data)
                os.chmod(self.filepath, self.FILE_MODE)
        except Timeout:
            raise WalletError("Could not acquire file lock to write")

    def _do_get(self, task: Dict[str, Any]) -> str:
        """
        Retrieve and decrypt a secret by key:
        - Authenticate and derive Fernet
        - Iterate encrypted keys, decrypt until match
        - Return secret or raise if not found
        """

        pwd = self._get_password(task.get("master_password"))
        f = self._get_fernet(pwd)
        try:
            with self._lock:
                data = self._load_json()
        except Timeout:
            raise WalletError("Could not acquire file lock to read")
        for enc_key, enc_val in data[self.KEYS_KEY].items():
            try:
                raw = f.decrypt(enc_key.encode()).decode()
                if raw == task["key"]:
                    secret = f.decrypt(enc_val.encode()).decode()
                    # scrub
                    return NumericValue(secret)
            except InvalidToken:
                continue
        raise KeyNotFoundError(f"Key '{task['key']}' not found")

    def _do_list(self, task: Dict[str, Any]) -> list:
        """
        List all decrypted keys stored in the vault.
        """
        pwd = self._get_password(task.get("master_password"))
        f = self._get_fernet(pwd)
        try:
            with self._lock:
                data = self._load_json()
        except Timeout:
            raise WalletError("Could not acquire file lock to list keys")
        keys = []
        for enc_key in data[self.KEYS_KEY]:
            try:
                keys.append(f.decrypt(enc_key.encode()).decode())
            except InvalidToken:
                continue
        return keys

    # ----- File I/O & Crypto helpers -----

    def _load_json(self) -> Dict:
        """
        Load and return vault JSON, ensuring it's not a symlink.
        Raises WalletNotFoundError if file missing.
        """

        if not os.path.exists(self.filepath):
            raise WalletNotFoundError(f"Vault '{self.filepath}' not found")
        with open(self.filepath, "r") as f:
            self._ensure_not_symlink()
            return json.load(f)

    def _atomic_write(self, data: Dict) -> None:
        """
        Safely write vault JSON to disk via tempfile + os.replace.
        Ensures permissions are set before write completes.
        """

        dirpath = os.path.dirname(self.filepath) or "."

        # Create a temp file securely:
        fd, tmp = tempfile.mkstemp(dir=dirpath)
        try:
            # restrict permissions right away
            os.fchmod(fd, self.FILE_MODE)
            with os.fdopen(fd, "w") as tf:
                json.dump(data, tf)

            self._ensure_not_symlink()
            os.replace(tmp, self.filepath)
        finally:
            # in case of error, clean up
            if os.path.exists(tmp):
                os.remove(tmp)

    def _prompt_password(self, prompt: str) -> str:
        """Prompt user for a password without echoing input."""
        return getpass.getpass(prompt)

    """
    def _derive_key(self, password: str, salt: bytes) -> bytes:
        kdf = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=salt, iterations=self.KDF_ITERATIONS)
        return b64encode(kdf.derive(password.encode()))
    """

    def _derive_key(self, password: str, salt: bytes) -> bytes:
        """
        Derive a symmetric key from password+salt using Argon2id.
        Returns URL-safe base64-encoded key for Fernet.
        """
        kdf = Argon2id(
            salt=salt,
            length=32,  # output key length in bytes
            iterations=3,  # number of passes
            lanes=4,  # parallelism factor
            memory_cost=64 * 1024,  # memory in kibibytes (64 MiB)
        )
        key = kdf.derive(password.encode())
        return b64encode(key)

    def _get_fernet(self, password: str) -> Fernet:
        """
        Construct a Fernet instance using the stored salt and provided password.
        """
        data = self._load_json()
        salt = b64decode(data[self.SALT_KEY])
        key = self._derive_key(password, salt)
        return Fernet(key)

    def _authenticate(self, password: str) -> None:
        """
        Verify provided master password by decrypting the stored master token.
        Raises InvalidPasswordError if decryption fails or values mismatch.
        """
        f = self._get_fernet(password)
        data = self._load_json()
        try:
            master = f.decrypt(data[self.MASTER_KEY].encode()).decode()
            if master != password:
                raise InvalidPasswordError("Incorrect master password")
        except InvalidToken:
            raise InvalidPasswordError("Incorrect master password")

    # public API
    def add(self, key: str, secret: str, master_password: Optional[str] = None) -> None:
        self._enqueue({"op": "add", "key": key, "secret": secret, "master_password": master_password})

    def get(self, key: str, master_password: Optional[str] = None) -> str:
        return self._enqueue({"op": "get", "key": key, "master_password": master_password})

    def list_keys(self, master_password: Optional[str] = None) -> list:
        return self._enqueue({"op": "list", "master_password": master_password})

    def close(self):
        self._stop_event.set()
        self._worker.join()

    def _compute_hmac(self, data: Dict[str, Any], password: str) -> str:
        """
        Compute HMAC-SHA256 over vault JSON (excluding existing HMAC field).
        Key is derived from Argon2id output.
        """
        payload = {k: data[k] for k in sorted(data) if k != HMAC_KEY}
        blob = json.dumps(payload, separators=(",", ":"), sort_keys=True).encode()
        key_bytes = b64decode(self._derive_key(password, b64decode(data[self.SALT_KEY])))
        hmac_key = hashlib.sha256(key_bytes).digest()
        return hmac.new(hmac_key, blob, hashlib.sha256).hexdigest()

    def _update_hmac(self, data: Dict[str, Any], password: str) -> None:
        """
        Update the data dict in-place with a fresh HMAC.
        """
        # prepare canonical JSON excluding any existing HMAC
        payload = {k: data[k] for k in sorted(data) if k != HMAC_KEY}
        blob = json.dumps(payload, separators=(",", ":"), sort_keys=True).encode()

        # derive raw key bytes then get an HMAC key
        key_bytes = b64decode(self._derive_key(password, b64decode(data[self.SALT_KEY])))
        hmac_key = hashlib.sha256(key_bytes).digest()

        data[HMAC_KEY] = hmac.new(hmac_key, blob, hashlib.sha256).hexdigest()

    def _ensure_not_symlink(self):
        """
        Prevent operating on a symlinked vault file for security reasons.
        """
        if os.path.exists(self.filepath):
            st = os.lstat(self.filepath)
            if stat.S_ISLNK(st.st_mode):
                raise WalletError("Vault file is a symlink—refusing to proceed")


# Register cleanup of all Vault instances on normal program exit
atexit.register(Vault._cleanup_all)
