"""
Advanced Checkpoint manager for APC.
Supports pluggable backends (in-memory, file, Redis, S3), checkpoint intervals, and recovery logic.
"""
import threading
import time
import json
import os
import glob
from pathlib import Path
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

class FileBackend(CheckpointBackend):
    """File-based checkpoint backend for persistent storage."""
    
    def __init__(self, checkpoint_dir: str = "./checkpoints"):
        self.checkpoint_dir = Path(checkpoint_dir)
        self.checkpoint_dir.mkdir(parents=True, exist_ok=True)
        self._lock = threading.Lock()
    
    def _get_filepath(self, batch_id: str) -> Path:
        """Get the filepath for a batch checkpoint."""
        # Sanitize batch_id for filesystem
        safe_batch_id = "".join(c for c in batch_id if c.isalnum() or c in ('-', '_', '.'))
        return self.checkpoint_dir / f"{safe_batch_id}.json"
    
    def save(self, batch_id: str, state: Dict[str, Any]) -> None:
        """Save checkpoint to file with atomic write."""
        filepath = self._get_filepath(batch_id)
        temp_filepath = filepath.with_suffix('.tmp')
        
        with self._lock:
            try:
                # Write to temp file first for atomic operation
                with open(temp_filepath, 'w', encoding='utf-8') as f:
                    json.dump(state, f, indent=2, ensure_ascii=False)
                
                # Atomic move
                if os.name == 'nt':  # Windows
                    if filepath.exists():
                        filepath.unlink()
                    temp_filepath.rename(filepath)
                else:  # Unix-like
                    temp_filepath.rename(filepath)
                    
            except Exception as e:
                # Cleanup temp file on error
                if temp_filepath.exists():
                    temp_filepath.unlink()
                raise e
    
    def load(self, batch_id: str) -> Optional[Dict[str, Any]]:
        """Load checkpoint from file."""
        filepath = self._get_filepath(batch_id)
        
        with self._lock:
            try:
                if filepath.exists():
                    with open(filepath, 'r', encoding='utf-8') as f:
                        return json.load(f)
            except (json.JSONDecodeError, IOError):
                # If checkpoint is corrupted, return None
                pass
        
        return None
    
    def list_checkpoints(self) -> List[str]:
        """List all available checkpoint batch IDs."""
        with self._lock:
            checkpoint_files = glob.glob(str(self.checkpoint_dir / "*.json"))
            return [
                Path(f).stem for f in checkpoint_files
                if not f.endswith('.tmp')
            ]
    
    def delete_checkpoint(self, batch_id: str) -> bool:
        """Delete a checkpoint file."""
        filepath = self._get_filepath(batch_id)
        
        with self._lock:
            try:
                if filepath.exists():
                    filepath.unlink()
                    return True
            except OSError:
                pass
        
        return False
    
    def cleanup_old_checkpoints(self, max_age_hours: int = 24) -> int:
        """Remove checkpoint files older than max_age_hours."""
        cutoff_time = time.time() - (max_age_hours * 3600)
        removed_count = 0
        
        with self._lock:
            for filepath in self.checkpoint_dir.glob("*.json"):
                try:
                    if filepath.stat().st_mtime < cutoff_time:
                        filepath.unlink()
                        removed_count += 1
                except OSError:
                    continue
        
        return removed_count

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
    """Manages checkpoint operations with automatic interval-based saving and recovery."""
    
    def __init__(self, backend: Optional[CheckpointBackend] = None, interval: int = 60, auto_recovery: bool = True):
        self.backend = backend or FileBackend()  # Default to persistent file backend
        self.interval = interval  # seconds
        self.auto_recovery = auto_recovery
        self._last_checkpoint: Dict[str, float] = {}
        self._lock = threading.Lock()
        self._stop = False
        self._auto_checkpoint_threads: Dict[str, threading.Thread] = {}

    def start_auto_checkpoint(self, batch_id: str, get_state_fn: Callable[[], Dict[str, Any]]) -> None:
        """Start automatic checkpointing for a batch."""
        def run():
            while not self._stop and batch_id in self._auto_checkpoint_threads:
                try:
                    state = get_state_fn()
                    self.save_checkpoint(batch_id, state)
                    time.sleep(self.interval)
                except Exception as e:
                    # Log error but continue checkpointing
                    print(f"Auto-checkpoint error for {batch_id}: {e}")
                    time.sleep(self.interval)
        
        if batch_id not in self._auto_checkpoint_threads:
            thread = threading.Thread(target=run, daemon=True, name=f"checkpoint-{batch_id}")
            self._auto_checkpoint_threads[batch_id] = thread
            thread.start()

    def stop_auto_checkpoint(self, batch_id: Optional[str] = None) -> None:
        """Stop automatic checkpointing for a specific batch or all batches."""
        if batch_id:
            # Stop specific batch
            thread = self._auto_checkpoint_threads.pop(batch_id, None)
            if thread and thread.is_alive():
                thread.join(timeout=5)
        else:
            # Stop all auto-checkpointing
            self._stop = True
            threads = list(self._auto_checkpoint_threads.values())
            self._auto_checkpoint_threads.clear()
            
            for thread in threads:
                if thread.is_alive():
                    thread.join(timeout=5)
            
            self._stop = False

    def save_checkpoint(self, batch_id: str, state: Dict[str, Any], force: bool = False) -> None:
        """Save a checkpoint for a batch. If force=True, bypasses interval check."""
        with self._lock:
            now = time.time()
            last = self._last_checkpoint.get(batch_id, 0)
            if force or (now - last >= self.interval):
                # Add metadata to the checkpoint
                checkpoint_data = {
                    "checkpoint_time": now,
                    "batch_id": batch_id,
                    "apc_version": "1.0.0",  # Can be made dynamic
                    "state": state
                }
                self.backend.save(batch_id, checkpoint_data)
                self._last_checkpoint[batch_id] = now

    def load_checkpoint(self, batch_id: str) -> Optional[Dict[str, Any]]:
        """Load checkpoint for a batch."""
        with self._lock:
            checkpoint_data = self.backend.load(batch_id)
            if checkpoint_data:
                # Return the actual state, not the wrapper
                return checkpoint_data.get("state", checkpoint_data)
            return None

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

    def discover_checkpoints(self) -> List[Dict[str, Any]]:
        """Discover all available checkpoints with metadata."""
        checkpoints = []
        for batch_id in self.list_checkpoints():
            with self._lock:
                checkpoint_data = self.backend.load(batch_id)
                if checkpoint_data:
                    checkpoints.append({
                        "batch_id": batch_id,
                        "checkpoint_time": checkpoint_data.get("checkpoint_time", 0),
                        "has_state": "state" in checkpoint_data,
                        "apc_version": checkpoint_data.get("apc_version", "unknown")
                    })
        return sorted(checkpoints, key=lambda x: x["checkpoint_time"], reverse=True)

    def auto_recover_workflows(self, recovery_fn: Callable[[str, Dict[str, Any]], None]) -> List[str]:
        """
        Automatically discover and recover all available workflows.
        Returns list of recovered batch IDs.
        """
        if not self.auto_recovery:
            return []
        
        recovered = []
        for batch_id in self.list_checkpoints():
            try:
                state = self.load_checkpoint(batch_id)
                if state:
                    recovery_fn(batch_id, state)
                    recovered.append(batch_id)
            except Exception as e:
                print(f"Failed to auto-recover workflow {batch_id}: {e}")
        
        return recovered

    def list_checkpoints(self) -> List[str]:
        """List all batch_ids with checkpoints (if supported by backend)."""
        if hasattr(self.backend, 'list_checkpoints'):
            return self.backend.list_checkpoints()
        if isinstance(self.backend, InMemoryBackend):
            return list(self.backend._store.keys())
        return []

    def delete_checkpoint(self, batch_id: str) -> bool:
        """Delete a checkpoint."""
        with self._lock:
            if hasattr(self.backend, 'delete_checkpoint'):
                return self.backend.delete_checkpoint(batch_id)
            elif isinstance(self.backend, InMemoryBackend):
                return self.backend._store.pop(batch_id, None) is not None
        return False

    def cleanup_old_checkpoints(self, max_age_hours: int = 24) -> int:
        """Clean up old checkpoints."""
        if hasattr(self.backend, 'cleanup_old_checkpoints'):
            return self.backend.cleanup_old_checkpoints(max_age_hours)
        return 0

    def get_checkpoint_info(self, batch_id: str) -> Optional[Dict[str, Any]]:
        """Get metadata about a checkpoint without loading the full state."""
        with self._lock:
            checkpoint_data = self.backend.load(batch_id)
            if checkpoint_data:
                return {
                    "batch_id": batch_id,
                    "checkpoint_time": checkpoint_data.get("checkpoint_time", 0),
                    "apc_version": checkpoint_data.get("apc_version", "unknown"),
                    "has_state": "state" in checkpoint_data,
                    "last_local_checkpoint": self._last_checkpoint.get(batch_id)
                }
        return None
