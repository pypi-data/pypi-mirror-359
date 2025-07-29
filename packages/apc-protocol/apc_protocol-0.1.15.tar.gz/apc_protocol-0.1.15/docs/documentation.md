# APC Documentation

Welcome to the official documentation for the Agent Protocol Conductor (APC)!

---

## Table of Contents
- [Introduction](#introduction)
- [Design Rationale & Goals](#design-rationale--goals)
- [Architecture Overview](#architecture-overview)
- [Message Schemas](#message-schemas)
- [State Machines](#state-machines)
- [Checkpointing & Failover](#checkpointing--failover)
- [Transport Adapters](#transport-adapters)
- [Security & Policy](#security--policy)
- [Registry & Discovery](#registry--discovery)
- [SDK Usage](#sdk-usage)
- [Examples](#examples)
- [FAQ](#faq)

---

## Introduction
APC is a decentralized orchestration protocol for heterogeneous AI agent ecosystems. It enables dynamic leadership hand-off, sequenced task execution, checkpointing, failover, and auditability—all without centralized control.

---

## Design Rationale & Goals
- **Decentralized Leadership**: No single point of failure; any agent can become conductor.
- **Dynamic Sequencing**: Workflows defined at runtime, supporting evolving subtask lists.
- **Resilience & Checkpointing**: Recover from agent failures via checkpoints and takeover.
- **Interoperability**: Protobuf/JSON schemas for cross-language support.
- **Extensibility & Security**: Add new message types, mTLS/JWT, and policy enforcement.

---

## Architecture Overview

<img alt="APC Architecture" src="https://raw.githubusercontent.com/deepfarkade/apc-protocol/main/docs/images/apc-architecture.png">

🔧 **APC Protocol – High-Level Architecture Summary**
This diagram showcases the core runtime structure of the APC (Agent Protocol for Choreography) system.

- **Conductor Agent:** The central orchestrator that assigns tasks to Worker Agents based on a known plan. It maintains execution state and error recovery logic.
- **gRPC/WebSocket Layer:** A communication backbone that enables bidirectional, low-latency messaging between Conductor and Worker Agents.
- **Worker Agent:** These agents perform domain-specific subtasks. They respond to commands from the Conductor and return results or status updates.
- **Checkpoint Store:** A persistent storage layer used by the Conductor to save execution state. On system failure, it allows the Conductor to recover seamlessly without restarting the entire flow.

This modular setup enables dynamic, scalable, and fault-tolerant agent workflows where control is coordinated yet loosely coupled through standardized message passing and recovery mechanisms.

---

## Message Schemas
- Defined in [proto/apc.proto](../proto/apc.proto)
- Protobuf v3 for cross-language support
- Core messages: `ProposeTask`, `Accept`, `Reject`, `Completed`, `Failed`, `TakeOver`, etc.

---

## State Machines
- **Conductor**: Handles batch goals, proposes tasks, sequences steps, manages failover.
- **Worker**: Accepts/rejects tasks, executes, reports completion/failure.
- **CheckpointManager**: Saves and restores state for resilience.

---

## Checkpointing & Failover
- Pluggable backends: In-memory, Redis, S3
- Auto-checkpointing and recovery logic
- TakeOver messages for dynamic leadership

---

## Transport Adapters
- gRPC: High-performance, strongly-typed
- WebSocket: Lightweight, browser-friendly
- Easily extendable for other transports

---

## Security & Policy
- mTLS: X.509 certificate-based mutual authentication
- JWT: Role/scopes encoded in tokens
- Policy engine for compliance and data sensitivity

---

## Registry & Discovery
- Optional: Register, discover, and load-balance agents
- Example: `registerAgent()`, `discoverAgents(filter)`

---

## SDK Usage
- See [examples/](../examples/) for sample agents
- Install via `pip install apc-protocol`
- Subclass `Conductor` or `Worker` and implement your logic
- Integrate LLMs or custom business logic as needed

### Basic Usage
```python
from apc import Worker, Conductor
from apc.transport import GRPCTransport

# Create a worker
worker = Worker("my-worker", roles=["processor"])

@worker.register_handler("my_task")
async def handle_task(batch_id, step_name, params):
    return {"result": "completed"}

# Setup transport
transport = GRPCTransport(port=50051)
worker.bind_transport(transport)
await transport.start_server()
```

---

## Examples
- [Basic gRPC Example](../examples/basic/simple_grpc.py)
- [LLM Agent Integration](../examples/agents/llm_agent.py)
- [Data Processing Pipeline](../examples/agents/data_processor.py)

### Quick Start Example
```python
# Install: pip install apc-protocol
from apc import Worker
import asyncio

async def main():
    worker = Worker("demo-worker", roles=["demo"])
    
    @worker.register_handler("demo_task")
    async def demo_handler(batch_id, step_name, params):
        return {"message": "Hello from APC!", "data": params}
    
    print("Worker ready!")
    # Add your transport setup here

asyncio.run(main())
```

---

## FAQ
**Q: Can I use APC with Node.js, Go, or Java?**
A: Yes! Use the Protobuf schema to generate SDKs for any language.

**Q: How do I add a new message type?**
A: Extend the Protobuf schema and regenerate code.

**Q: How do I contribute?**
A: Fork the repo, branch, and submit a PR!

---

## 🧠 Why APC? (The Evolutionary Backdrop)

**MCP (Message-Centered Protocol)** gave agents a common language for basic send/receive—everyone could talk, but only at the lowest level.

**A2A (Agent-to-Agent)** enabled direct peer-to-peer links, letting Agent A push subtasks straight to Agent B. This improved speed, but made systems brittle at scale.

**ACP (Agent Control Protocol)** introduced a central orchestrator to sequence tasks and enforce policies. This fixed deadlocks, but reintroduced a single point of failure and made most agents passive workers.

All three advanced the field, but none provided a flexible, fault-tolerant way for agents to coordinate and think for themselves in complex, branching workflows.

---

## 🚀 Why APC Is the Next Leap

- **Distributed “Conductors”**: Any agent can temporarily assume the conductor role for a workflow, enabling sequencing, dependency checks, and deadlock avoidance—without a heavy, central master.
- **Plug-and-Play Orchestration**: Agents register their orchestration capabilities and load. If one goes offline, another takes over automatically.
- **Context-Aware Scheduling**: Conductors probe agent readiness, context, and load before launching subtasks, avoiding mid-pipeline failures.
- **Graceful Preemption & Handoffs**: When priorities shift, conductors checkpoint running subtasks and offer them to peers—no more “hung” workflows.

---

## 🌟 The Transformative Impact

- **Elastic Workflows**: Agents can dynamically lead or follow, adapting to changing needs.
- **No Orchestration Silos**: Get the governance of ACP without the latency or single-point-of-failure risk.
- **Simplified Developer Experience**: Define tasks and dependencies once—APC’s conductor handshakes handle the rest.

**In short:** APC doesn’t just mediate “who talks to whom”; it embeds a living, breathing conductor in every agent ecosystem—unlocking true multi-agent creativity, resilience, and scale. That’s why APC is the next flagship protocol for Gen-AI agents.

---

## More Real-World Scenarios & Diagrams

### 📦 Scenario 1: Multi‑Stage Data Pipeline

<img alt="Multi‑Stage Data Pipeline APC Architecture" src="https://raw.githubusercontent.com/deepfarkade/apc-protocol/main/docs/images/Scenerio-1.png">

**APC in Action:**

- **Dynamic Conductor Claim:** Agent X volunteers as conductor for this ETL batch.
- **Sequenced Proposals:** X “PROPOSE_TASK: Extract” → Y; on completion, “PROPOSE_TASK: Transform” → Z; then “PROPOSE_TASK: Load” → W.
- **Checkpointing:** After each subtask, X records progress (e.g. raw data, cleaned data) in the checkpoint store.
- **Failover:** If Y times out or fails, X issues a TAKE_OVER and re‑proposes extract to Y2.
- **Completion:** Once W reports “COMPLETED,” X closes the batch.

---

### 💬 Scenario 2: LLM‑Driven Multi‑Agent Chat

<img alt="LLM‑Driven Multi‑Agent Chat APC Architecture" src="https://raw.githubusercontent.com/deepfarkade/apc-protocol/main/docs/images/Scenerio-2.png">

**APC in Action:**

- **Orchestration Start:** M receives a new user message and becomes conductor for that turn.
- **LLM Call:** M “PROPOSE_TASK: Generate” → N; N returns the text response.
- **Tool Execution:** M then “PROPOSE_TASK: ToolCall” → O (e.g., fetch weather API); O returns results.
- **Resilience:** If N fails to reply, M “TAKE_OVER” and sends generate request to N2.
- **Unified Flow:** M aggregates both responses, then sends back to the user—all under one batch ID.

---

### 🖼️ Scenario 3: Distributed Image Processing

<img alt="Distributed Image Processing APC Architecture" src="https://raw.githubusercontent.com/deepfarkade/apc-protocol/main/docs/images/Scenerio-3.png">

**APC in Action:**

- **Initiation:** P kicks off the image batch, claiming conductor duties.
- **Preprocessing:** P → Q to resize/normalize; upon “COMPLETED,” P → R to classify.
- **Annotation:** After labels arrive, P → S to overlay annotations.
- **Checkpointing & Recovery:** P checkpoints image states after each stage. If Q fails, P hands off to Q2, which resumes from last checkpoint.
- **End‑to‑End Audit:** All message exchanges and checkpoint snapshots are logged for traceability.

---

### 🚚 Scenario 4: Autonomous Fleet Coordination

<img alt="Autonomous Fleet Coordination APC Architecture" src="https://raw.githubusercontent.com/deepfarkade/apc-protocol/main/docs/images/Scenerio-4.png">

**APC in Action:**

- **Task Assignment:** F as conductor proposes “Deliver” to G and H in parallel (two drones).
- **Status Aggregation:** Each drone reports back “COMPLETED” when the package is dropped.
- **Last‑Mile Handoff:** F then “PROPOSE_TASK: Last Mile” → I (ground robot).
- **Fault Tolerance:** If G fails mid‑flight, F uses TAKE_OVER to reassign its route to G2 with the same mission parameters.
- **Coordinated Finish:** F collects all completions and closes the delivery workflow.

---

For more, see the [README](../README.md) or use the provided Mermaid code in a compatible viewer. Each scenario demonstrates APC's ability to coordinate, recover, and audit complex, distributed agent workflows in real-world domains.
