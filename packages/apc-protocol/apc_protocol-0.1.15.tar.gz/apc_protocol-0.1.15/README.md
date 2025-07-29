# ![APC Logo](https://raw.githubusercontent.com/deepfarkade/apc-protocol/main/docs/images/apc-logo.png)

# APC: Agent Protocol Conductor

[![PyPI version](https://img.shields.io/pypi/v/apc-protocol?color=blue)](https://pypi.org/project/apc-protocol/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Build Status](https://img.shields.io/github/actions/workflow/status/deepfarkade/apc-protocol/ci.yml?branch=main)](https://github.com/deepfarkade/apc-protocol/actions)
[![Docs](https://img.shields.io/badge/docs-online-blue)](docs/documentation.md)

A protocol for decentralized, resilient, and auditable orchestration of heterogeneous AI agent ecosystems.

[Documentation](docs/documentation.md) | [Specification](proto/apc.proto) | [Examples](examples/) | [PyPI Package](https://pypi.org/project/apc-protocol/)

---

APC (Agent Protocol Conductor) is an open protocol and SDK designed to orchestrate distributed AI agents in a truly decentralized, resilient, and auditable way. With APC, you can build intelligent systems where multiple agents—each with their own roles and capabilities—work together to accomplish complex tasks, adapt to failures, and recover automatically, all without relying on a central controller.

Key features include:
- **Dynamic Leadership:** Any agent can become the conductor, coordinating workflows and handing off control as needed.
- **Sequenced Task Execution:** Define and manage multi-step processes, with each agent performing specialized subtasks.
- **Checkpointing & Failover:** Progress is saved at every step, so if an agent fails, another can seamlessly take over from the last checkpoint—no lost work, no manual intervention.
- **Interoperability:** Built on Protobuf schemas, APC supports cross-language agent ecosystems (Python, TypeScript, Java, and more).
- **Extensibility & Security:** Easily add new message types, enforce security with mTLS/JWT, and integrate custom business logic or LLMs.

APC is production-ready and ideal for both classic automation and advanced AI-powered workflows. Whether you’re building ETL pipelines, LLM chatbots, or autonomous fleets, APC gives you the tools to create robust, scalable, and future-proof agent systems.

---

## 🚀 Quick Start

```sh
# Install from PyPI
pip install apc-protocol

# Or from source
git clone https://github.com/deepfarkade/apc-protocol.git
cd apc-protocol
python setup.py
```

## 🧑‍� Basic Usage

```python
from apc import Worker, Conductor
from apc.transport import GRPCTransport

# Create worker with specific roles
worker = Worker("my-worker", roles=["data-processor"])

# Register task handlers
@worker.register_handler("process_data")
async def handle_data(batch_id: str, step_name: str, params: dict):
    # Your processing logic here
    return {"processed": params["data"], "status": "completed"}

# Set up transport and start
transport = GRPCTransport(port=50051)
worker.bind_transport(transport)
await transport.start_server()
```

## 🛠️ Key Features

- **Protobuf-based message schemas** for cross-language interoperability
- **Pluggable checkpoint manager** (in-memory, Redis, S3)
- **State machine engine** for conductor and worker agents
- **gRPC and WebSocket transport adapters**
- **Dynamic Leadership**: Any agent can become the conductor
- **Fault Tolerance**: Automatic failover and recovery
- **Cross-Language Support**: Python, TypeScript, Java, and more
- **Checkpointing**: Save progress and resume from failures
- **Security Ready**: mTLS, JWT authentication support

---

## 🏗️ Architecture Overview

![APC Architecture](docs/images/apc-architecture.png)

APC Protocol enables decentralized agent coordination with:

- **Conductor Agent**: The orchestrator that assigns tasks to Worker Agents based on a workflow plan. Maintains execution state and error recovery logic.
- **Worker Agent**: Domain-specific agents that perform specialized subtasks. They respond to commands from Conductors and return results.
- **gRPC/WebSocket Layer**: Communication backbone that enables bidirectional, low-latency messaging between agents.
- **Checkpoint Store**: Persistent storage layer used to save execution state. Enables seamless recovery without restarting entire workflows.

This modular setup enables dynamic, scalable, and fault-tolerant agent workflows where control is coordinated yet loosely coupled through standardized message passing.

---

## 📚 Learn More
- **[Usage Guide](docs/USAGE_GUIDE.md)** - Complete tutorials and examples
- **[Examples](examples/)** - Working code you can run
- **[Protocol Spec](proto/apc.proto)** - Technical details

---

## 🤝 Contributing

We welcome contributions! Here's how to get started:

### Development Setup
```sh
git clone https://github.com/deepfarkade/apc-protocol.git
cd apc-protocol
python setup.py
python scripts/test_package.py
```

### Key Files
- [`proto/apc.proto`](proto/apc.proto) - Protocol definitions
- [`src/apc/`](src/apc/) - Core Python SDK
- [`examples/`](examples/) - Usage examples
- [`docs/`](docs/) - Documentation

### Testing
```sh
# Run tests
python scripts/test_package.py

# Run demo
python scripts/demo.py

# Test examples
python examples/basic/simple_grpc.py
```

---

## 📦 Release Information

- **Current Release:** v0.1.x (Alpha)
- See [Releases](https://github.com/deepfarkade/apc-protocol/releases) for changelogs and version history.
- This is the first public alpha release of the APC protocol and SDK.

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

## **Example: Document Processing Workflow with APC**

Imagine a real-world scenario where you need to process a batch of scanned documents:

- `Agent A` (Conductor): Orchestrates the workflow.
- `Agent B` (Worker: OCR): Extracts text from images.
- `Agent C` (Worker: Summarizer): Summarizes the extracted text.

**Workflow:**
1. `Agent A` receives a new batch and proposes the first step to `Agent B` (OCR).
2. `Agent B` accepts, processes the images, and sends back the extracted text.
3. `Agent A` checkpoints the result, then proposes the next step to `Agent C` (Summarization).
4. `Agent C` summarizes the text and returns the summary to `Agent A`.
5. If `Agent B` fails or disconnects, APC's checkpointing and takeover logic allow another eligible OCR agent to resume from the last checkpoint—no data loss, no manual intervention.
6. Every step, hand-off, and result is auditable and interoperable across languages and platforms.

---

## 📊 More Real-World Scenarios & Diagrams

For advanced diagrams and multi-agent workflow scenarios, see the [full documentation](docs/documentation.md).

---

## 🛡️ License
MIT
