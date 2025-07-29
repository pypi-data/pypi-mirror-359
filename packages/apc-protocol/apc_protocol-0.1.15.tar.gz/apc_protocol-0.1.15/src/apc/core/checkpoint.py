"""
Advanced Checkpoint manager for APC.
Supports pluggable backends (in-memory, Redis, S3), checkpoint intervals, and recovery logic.
"""
import threading
import time
import json
from typing import Dict, Any, Optional, Callable, List
from abc import ABC, abstractmethod

class CheckpointBackend(ABC):
    """Abstract base class for checkpoint backends."""
    
    @abstractmethod
    def save(self, batch_id: str, state: Dict[str, Any]) -> None:
        """Save state for a batch."""
        pass
    
    @abstractmethod 
    def load(self, batch_id: str) -> Optional[Dict[str, Any]]:
        """Load state for a batch."""
        pass

class InMemoryBackend(CheckpointBackend):
    """In-memory checkpoint backend for development and testing."""
    
    def __init__(self):
        self._store: Dict[str, str] = {}
    
    def save(self, batch_id: str, state: Dict[str, Any]) -> None:
        self._store[batch_id] = json.dumps(state)
    
    def load(self, batch_id: str) -> Optional[Dict[str, Any]]:
        data = self._store.get(batch_id)
        return json.loads(data) if data else None
    
    def list_checkpoints(self) -> List[str]:
        return list(self._store.keys())

class RedisBackend(CheckpointBackend):
    """Redis checkpoint backend for distributed deployments."""
    
    def __init__(self, redis_client):
        self.redis = redis_client
    
    def save(self, batch_id: str, state: Dict[str, Any]) -> None:
        self.redis.set(batch_id, json.dumps(state))
    
    def load(self, batch_id: str) -> Optional[Dict[str, Any]]:
        data = self.redis.get(batch_id)
        return json.loads(data) if data else None

class S3Backend(CheckpointBackend):
    """S3 checkpoint backend for persistent storage."""
    
    def __init__(self, s3_client, bucket: str):
        self.s3 = s3_client
        self.bucket = bucket
    
    def save(self, batch_id: str, state: Dict[str, Any]) -> None:
        self.s3.put_object(
            Bucket=self.bucket, 
            Key=batch_id, 
            Body=json.dumps(state)
        )
    
    def load(self, batch_id: str) -> Optional[Dict[str, Any]]:
        try:
            obj = self.s3.get_object(Bucket=self.bucket, Key=batch_id)
            return json.loads(obj['Body'].read())
        except Exception:
            return None

class CheckpointManager:
    """Manages checkpoint operations with automatic interval-based saving."""
    
    def __init__(self, backend: Optional[CheckpointBackend] = None, interval: int = 60):
        self.backend = backend or InMemoryBackend()
        self.interval = interval  # seconds
        self._last_checkpoint: Dict[str, float] = {}
        self._lock = threading.Lock()
        self._stop = False
        self._thread: Optional[threading.Thread] = None

    def start_auto_checkpoint(self, batch_id: str, get_state_fn: Callable[[], Dict[str, Any]]) -> None:
        """Start automatic checkpointing for a batch."""
        def run():
            while not self._stop:
                state = get_state_fn()
                self.save_checkpoint(batch_id, state)
                time.sleep(self.interval)
        
        self._thread = threading.Thread(target=run, daemon=True)
        self._thread.start()

    def stop_auto_checkpoint(self) -> None:
        """Stop automatic checkpointing."""
        self._stop = True
        if self._thread:
            self._thread.join()
        self._thread = None
        self._stop = False

    def save_checkpoint(self, batch_id: str, state: Dict[str, Any], force: bool = False) -> None:
        """Save a checkpoint for a batch. If force=True, bypasses interval check."""
        with self._lock:
            now = time.time()
            last = self._last_checkpoint.get(batch_id, 0)
            if force or (now - last >= self.interval):
                self.backend.save(batch_id, state)
                self._last_checkpoint[batch_id] = now

    def load_checkpoint(self, batch_id: str) -> Optional[Dict[str, Any]]:
        """Load checkpoint for a batch."""
        with self._lock:
            return self.backend.load(batch_id)

    def last_checkpoint_time(self, batch_id: str) -> Optional[float]:
        """Get the timestamp of the last checkpoint for a batch."""
        with self._lock:
            return self._last_checkpoint.get(batch_id)

    def recover(self, batch_id: str, recovery_fn: Callable[[Dict[str, Any]], None], strict: bool = True) -> Optional[Dict[str, Any]]:
        """Load checkpoint and invoke recovery function to resume workflow."""
        state = self.load_checkpoint(batch_id)
        if state:
            recovery_fn(state)
        elif strict:
            raise RuntimeError(f"No checkpoint found for batch {batch_id}")
        return state

    def list_checkpoints(self) -> List[str]:
        """List all batch_ids with checkpoints (if supported by backend)."""
        if hasattr(self.backend, 'list_checkpoints'):
            return self.backend.list_checkpoints()
        if isinstance(self.backend, InMemoryBackend):
            return list(self.backend._store.keys())
        return []
