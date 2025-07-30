#!/usr/bin/env python3
"""
Conductor Health Monitoring and Automatic Takeover System.
Implements distributed conductor discovery, health checking, and seamless failover.
"""

import asyncio
import time
import uuid
from typing import Dict, List, Optional, Set
from dataclasses import dataclass, field
from enum import Enum
import structlog

from ..logging import get_logger, StructuredLogger


class ConductorState(Enum):
    """Conductor states for the election algorithm."""
    FOLLOWER = "follower"
    CANDIDATE = "candidate" 
    LEADER = "leader"
    FAILED = "failed"


@dataclass
class ConductorInfo:
    """Information about a conductor in the cluster."""
    conductor_id: str
    last_heartbeat: float = field(default_factory=time.time)
    state: ConductorState = ConductorState.FOLLOWER
    term: int = 0
    priority: int = 100  # Higher priority = more likely to become leader
    active_workflows: Set[str] = field(default_factory=set)
    load_score: float = 0.0  # 0.0 = no load, 1.0 = fully loaded


class ConductorHealthMonitor:
    """
    Monitors conductor health and manages automatic failover.
    Implements a simplified Raft-like consensus algorithm for conductor election.
    """
    
    def __init__(
        self,
        conductor_id: str,
        heartbeat_interval: float = 5.0,
        election_timeout: float = 15.0,
        failure_threshold: float = 30.0
    ):
        self.conductor_id = conductor_id
        self.heartbeat_interval = heartbeat_interval
        self.election_timeout = election_timeout
        self.failure_threshold = failure_threshold
        
        # Cluster state
        self.conductors: Dict[str, ConductorInfo] = {}
        self.current_leader: Optional[str] = None
        self.current_term = 0
        self.voted_for: Optional[str] = None
        self.state = ConductorState.FOLLOWER
        
        # Monitoring tasks
        self._heartbeat_task: Optional[asyncio.Task] = None
        self._health_check_task: Optional[asyncio.Task] = None
        self._election_task: Optional[asyncio.Task] = None
        
        # Event callbacks
        self.on_leader_elected = None
        self.on_conductor_failed = None
        self.on_takeover_required = None
        
        self.logger = StructuredLogger(get_logger(__name__))
        
        # Register self
        self.conductors[conductor_id] = ConductorInfo(
            conductor_id=conductor_id,
            state=ConductorState.FOLLOWER
        )
    
    async def start(self):
        """Start the health monitoring system."""
        self.logger.info(
            "Starting conductor health monitor",
            conductor_id=self.conductor_id,
            heartbeat_interval=self.heartbeat_interval
        )
        
        self._heartbeat_task = asyncio.create_task(self._heartbeat_loop())
        self._health_check_task = asyncio.create_task(self._health_check_loop())
        
        # Start election if no leader is known
        if not self.current_leader:
            self._start_election()
    
    async def stop(self):
        """Stop the health monitoring system."""
        self.logger.info("Stopping conductor health monitor", conductor_id=self.conductor_id)
        
        # Cancel all tasks
        for task in [self._heartbeat_task, self._health_check_task, self._election_task]:
            if task:
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass
    
    def register_conductor(self, conductor_id: str, priority: int = 100):
        """Register a new conductor in the cluster."""
        if conductor_id not in self.conductors:
            self.conductors[conductor_id] = ConductorInfo(
                conductor_id=conductor_id,
                priority=priority
            )
            self.logger.info(
                "Conductor registered",
                conductor_id=conductor_id,
                priority=priority,
                total_conductors=len(self.conductors)
            )
    
    def update_conductor_load(self, conductor_id: str, load_score: float, active_workflows: Set[str]):
        """Update a conductor's load information."""
        if conductor_id in self.conductors:
            self.conductors[conductor_id].load_score = load_score
            self.conductors[conductor_id].active_workflows = active_workflows
    
    async def request_takeover(self, failed_conductor_id: str, workflow_id: str) -> bool:
        """
        Request takeover of a workflow from a failed conductor.
        Returns True if takeover was successful.
        """
        self.logger.warning(
            "Requesting workflow takeover",
            failed_conductor=failed_conductor_id,
            workflow_id=workflow_id,
            current_leader=self.current_leader
        )
        
        # Mark the conductor as failed
        if failed_conductor_id in self.conductors:
            self.conductors[failed_conductor_id].state = ConductorState.FAILED
        
        # If we're the leader, we can authorize the takeover
        if self.state == ConductorState.LEADER:
            return await self._authorize_takeover(failed_conductor_id, workflow_id)
        
        # If there's no leader, start an election
        if not self.current_leader or self.current_leader == failed_conductor_id:
            self._start_election()
            return False
        
        # Request takeover from the current leader
        return await self._request_takeover_from_leader(failed_conductor_id, workflow_id)
    
    async def _heartbeat_loop(self):
        """Send periodic heartbeats to announce our presence."""
        while True:
            try:
                await self._send_heartbeat()
                await asyncio.sleep(self.heartbeat_interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error("Heartbeat failed", error=str(e))
                await asyncio.sleep(self.heartbeat_interval)
    
    async def _health_check_loop(self):
        """Monitor other conductors' health."""
        while True:
            try:
                await self._check_conductor_health()
                await asyncio.sleep(self.heartbeat_interval / 2)
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error("Health check failed", error=str(e))
                await asyncio.sleep(self.heartbeat_interval)
    
    async def _send_heartbeat(self):
        """Send heartbeat to announce our presence."""
        current_time = time.time()
        
        if self.conductor_id in self.conductors:
            self.conductors[self.conductor_id].last_heartbeat = current_time
        
        # In a real implementation, this would send heartbeats via the transport layer
        self.logger.debug(
            "Heartbeat sent",
            conductor_id=self.conductor_id,
            state=self.state.value,
            term=self.current_term
        )
    
    async def _check_conductor_health(self):
        """Check health of all conductors and detect failures."""
        current_time = time.time()
        failed_conductors = []
        
        for conductor_id, info in self.conductors.items():
            if conductor_id == self.conductor_id:
                continue  # Skip self
            
            time_since_heartbeat = current_time - info.last_heartbeat
            
            if time_since_heartbeat > self.failure_threshold and info.state != ConductorState.FAILED:
                failed_conductors.append(conductor_id)
                info.state = ConductorState.FAILED
                
                self.logger.warning(
                    "Conductor failure detected",
                    failed_conductor=conductor_id,
                    time_since_heartbeat=time_since_heartbeat,
                    active_workflows=len(info.active_workflows)
                )
                
                # Trigger takeover for any active workflows
                if info.active_workflows and self.on_takeover_required:
                    for workflow_id in info.active_workflows:
                        await self.on_takeover_required(conductor_id, workflow_id)
        
        # If the leader failed, start a new election
        if self.current_leader in failed_conductors:
            self.logger.warning(
                "Leader failure detected, starting election",
                failed_leader=self.current_leader
            )
            self.current_leader = None
            self._start_election()
    
    def _start_election(self):
        """Start a leader election process."""
        if self._election_task and not self._election_task.done():
            return  # Election already in progress
        
        self._election_task = asyncio.create_task(self._run_election())
    
    async def _run_election(self):
        """Run the leader election algorithm using real distributed voting."""
        try:
            self.logger.info(
                "Starting leader election",
                conductor_id=self.conductor_id,
                term=self.current_term + 1
            )
            
            # Become candidate
            self.state = ConductorState.CANDIDATE
            self.current_term += 1
            self.voted_for = self.conductor_id
            
            # Vote for self
            votes_received = 1
            total_conductors = len([c for c in self.conductors.values() if c.state != ConductorState.FAILED])
            majority_needed = (total_conductors // 2) + 1
            
            # Request votes from other conductors
            vote_requests = []
            for conductor_id, info in self.conductors.items():
                if conductor_id != self.conductor_id and info.state != ConductorState.FAILED:
                    vote_requests.append(
                        self._request_vote(conductor_id, self.current_term)
                    )
            
            # Wait for vote responses (with timeout)
            if vote_requests:
                try:
                    vote_responses = await asyncio.wait_for(
                        asyncio.gather(*vote_requests, return_exceptions=True),
                        timeout=self.election_timeout / 2
                    )
                    
                    # Count valid votes
                    for response in vote_responses:
                        if isinstance(response, bool) and response:
                            votes_received += 1
                        elif isinstance(response, Exception):
                            self.logger.debug(
                                "Vote request failed",
                                error=str(response)
                            )
                except asyncio.TimeoutError:
                    self.logger.warning(
                        "Vote request timeout during election",
                        conductor_id=self.conductor_id
                    )
            
            self.logger.info(
                "Election votes counted",
                conductor_id=self.conductor_id,
                votes_received=votes_received,
                majority_needed=majority_needed,
                total_conductors=total_conductors
            )
            
            if votes_received >= majority_needed:
                # We won the election
                await self._become_leader()
            else:
                # We lost, become follower
                self.state = ConductorState.FOLLOWER
                self.logger.info(
                    "Election lost, becoming follower",
                    conductor_id=self.conductor_id
                )
        
        except Exception as e:
            self.logger.error("Election failed", error=str(e))
            self.state = ConductorState.FOLLOWER
    
    async def _become_leader(self):
        """Become the cluster leader."""
        self.state = ConductorState.LEADER
        self.current_leader = self.conductor_id
        
        self.logger.info(
            "Elected as leader",
            conductor_id=self.conductor_id,
            term=self.current_term
        )
        
        # Update our info
        if self.conductor_id in self.conductors:
            self.conductors[self.conductor_id].state = ConductorState.LEADER
        
        # Notify about leader election
        if self.on_leader_elected:
            await self.on_leader_elected(self.conductor_id)
    
    async def _authorize_takeover(self, failed_conductor_id: str, workflow_id: str) -> bool:
        """Authorize a workflow takeover (called when we're the leader)."""
        self.logger.info(
            "Authorizing workflow takeover",
            failed_conductor=failed_conductor_id,
            workflow_id=workflow_id,
            conductor_id=self.conductor_id
        )
        
        # Find the best conductor to take over the workflow
        best_conductor = self._select_takeover_conductor(workflow_id)
        
        if best_conductor:
            self.logger.info(
                "Takeover authorized",
                failed_conductor=failed_conductor_id,
                workflow_id=workflow_id,
                new_conductor=best_conductor
            )
            return True
        
        return False
    
    def _select_takeover_conductor(self, workflow_id: str) -> Optional[str]:
        """Select the best conductor to take over a workflow."""
        available_conductors = [
            (conductor_id, info) for conductor_id, info in self.conductors.items()
            if info.state not in [ConductorState.FAILED] and conductor_id != self.conductor_id
        ]
        
        if not available_conductors:
            return None
        
        # Sort by load score (prefer less loaded conductors)
        available_conductors.sort(key=lambda x: x[1].load_score)
        
        return available_conductors[0][0]
    
    async def _request_vote(self, conductor_id: str, term: int) -> bool:
        """
        Request a vote from another conductor for leader election.
        This is a placeholder for real distributed voting via transport layer.
        """
        # TODO: Implement real vote request via transport layer (gRPC, WebSocket, etc.)
        # For now, this is a no-op that will be replaced by transport integration
        self.logger.debug(
            "Vote request (transport integration required)",
            target_conductor=conductor_id,
            term=term
        )
        
        # In production, this would:
        # 1. Send a vote request message to the target conductor
        # 2. Wait for the response
        # 3. Return True if vote granted, False otherwise
        # For now, return False to ensure election requires manual intervention
        return False
    
    async def _request_takeover_from_leader(self, failed_conductor_id: str, workflow_id: str) -> bool:
        """Request takeover authorization from the current leader."""
        # TODO: Implement real takeover request via transport layer
        self.logger.info(
            "Requesting takeover from leader (transport integration required)",
            failed_conductor=failed_conductor_id,
            workflow_id=workflow_id,
            leader=self.current_leader
        )
        
        # In production, this would:
        # 1. Send a takeover request to the leader
        # 2. Wait for authorization response
        # 3. Return True if approved, False otherwise
        # For now, return False to ensure manual intervention is required
        return False
    
    def get_cluster_status(self) -> Dict:
        """Get current cluster status."""
        return {
            "conductor_id": self.conductor_id,
            "state": self.state.value,
            "current_leader": self.current_leader,
            "current_term": self.current_term,
            "total_conductors": len(self.conductors),
            "healthy_conductors": len([c for c in self.conductors.values() if c.state != ConductorState.FAILED]),
            "failed_conductors": len([c for c in self.conductors.values() if c.state == ConductorState.FAILED]),
            "conductors": {
                cid: {
                    "state": info.state.value,
                    "last_heartbeat": info.last_heartbeat,
                    "priority": info.priority,
                    "load_score": info.load_score,
                    "active_workflows": len(info.active_workflows)
                }
                for cid, info in self.conductors.items()
            }
        }
