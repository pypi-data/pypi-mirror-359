#!/usr/bin/env python3
"""
Real Azure OpenAI Agents with APC Orchestration (WebSocket Transport)

A practical example showing how to use APC to coordinate multiple AI agents using WebSocket transport.
Tests real Azure OpenAI API calls with agent communication via WebSocket.

Requirements:
- Azure OpenAI API key and endpoint in .env file
- pip install openai websockets python-dotenv

Architecture:
Research Agent → Analysis Agent → Report Agent
"""

import asyncio
import json
import os
import time
from typing import Dict, Any
from dotenv import load_dotenv

from apc import Worker, Conductor
from apc.transport.websocket import WebSocketTransport
from apc.helpers.logging import get_logger
from apc.helpers.llms import AzureOpenAIStreamingClient
from conductor_ws_server import ConductorWebSocketServer

load_dotenv()
logger = get_logger(__name__)

# Azure OpenAI imports and client setup
try:
    from apc.helpers.llms import AzureOpenAIStreamingClient
    # Use APC's enhanced Azure OpenAI client with streaming
    openai_client = AzureOpenAIStreamingClient()
    logger.warning("🎨 Using APC streaming client with colored terminal output")
except ImportError:
    logger.error("APC streaming client not available")
    exit(1)

# Check required environment variables
required_vars = ["AZURE_OPENAI_API_KEY", "AZURE_OPENAI_ENDPOINT", "AZURE_OPENAI_DEPLOYMENT_NAME"]
missing_vars = [var for var in required_vars if not os.getenv(var)]
if missing_vars:
    logger.error(f"Missing environment variables: {missing_vars}")
    logger.error("Create .env file with Azure OpenAI credentials")
    exit(1)

workflow_data = {}

class ResearchAgent:
    """Agent that performs research using Azure OpenAI."""
    def __init__(self):
        self.worker = Worker(
            worker_id="research_agent_ws",
            roles=["researcher", "analyzer", "reporter"]
        )
        self.transport = WebSocketTransport(port=8765)
        self.worker.bind_transport(self.transport)
        self.worker.register_handler("research", self.do_research)
        self.worker.register_handler("analyze", self.do_analysis)
        self.worker.register_handler("report", self.create_report)
    async def do_research(self, params: dict) -> dict:
        topic = params.get("topic", "AI research")
        logger.warning(f"🔬 Starting research task for topic: {topic}")
        
        messages = [
            {"role": "system", "content": "You are a research assistant. Provide factual, comprehensive research."},
            {"role": "user", "content": f"Research the topic: {topic}. Provide key findings, current trends, and important statistics."}
        ]
        
        # Use streaming with colored output
        research_result = openai_client.chat_completion_streaming(
            agent_name="Research Agent",
            messages=messages, 
            max_tokens=400
        )
        
        workflow_data["research"] = {
            "topic": topic,
            "findings": research_result,
            "timestamp": time.time()
        }
        logger.warning(f"✅ Research completed for topic: {topic}")
        return {"status": "completed", "research_length": len(research_result)}
    async def do_analysis(self, params: dict) -> dict:
        research_data = workflow_data.get("research", {})
        if not research_data:
            logger.error("No research data available for analysis")
            return {"status": "failed", "error": "No research data available"}
        
        logger.warning(f"🧠 Starting analysis for topic: {research_data['topic']}")
        
        messages = [
            {"role": "system", "content": "You are a data analyst. Analyze research findings and identify key insights."},
            {"role": "user", "content": f"Analyze this research data and identify the top 3 key insights and implications:\n\n{research_data['findings']}"}
        ]
        
        # Use streaming with colored output
        analysis_result = openai_client.chat_completion_streaming(
            agent_name="Analysis Agent",
            messages=messages, 
            max_tokens=350
        )
        
        workflow_data["analysis"] = {
            "insights": analysis_result,
            "based_on": research_data["topic"],
            "timestamp": time.time()
        }
        logger.warning(f"✅ Analysis completed for topic: {research_data['topic']}")
        return {"status": "completed", "insights_generated": True}
    async def create_report(self, params: dict) -> dict:
        research_data = workflow_data.get("research", {})
        analysis_data = workflow_data.get("analysis", {})
        if not research_data or not analysis_data:
            logger.error("Missing research or analysis data for report generation")
            return {"status": "failed", "error": "Missing research or analysis data"}
        
        logger.warning(f"📝 Starting report generation for topic: {research_data['topic']}")
        
        messages = [
            {"role": "system", "content": "You are a report writer. Create clear, professional reports."},
            {"role": "user", "content": f"Create a comprehensive report based on:\n\nRESEARCH: {research_data['findings']}\n\nANALYSIS: {analysis_data['insights']}\n\nProvide a structured report with executive summary, key findings, and recommendations."}
        ]
        
        # Use streaming with colored output
        report_result = openai_client.chat_completion_streaming(
            agent_name="Report Agent",
            messages=messages, 
            max_tokens=500
        )
        
        workflow_data["report"] = {
            "content": report_result,
            "topic": research_data["topic"],
            "timestamp": time.time()
        }
        logger.warning(f"✅ Report generated for topic: {research_data['topic']}")
        return {"status": "completed", "report_generated": True}

async def main():
    logger.warning("Testing APC with real Azure OpenAI agents (WebSocket transport, bidirectional)...")
    # Create conductor with persistent checkpointing
    # Uses default "./checkpoints" directory for consistency across all examples
    conductor = Conductor(
        conductor_id="azure_research_conductor_ws",
        checkpoint_manager=Conductor.create_file_checkpoint_manager("./checkpoints", interval=30),
        enable_auto_recovery=True
    )
    agent = ResearchAgent()
    conductor_ws_server = ConductorWebSocketServer(conductor, port=8766)
    try:
        await agent.worker.start()
        task1 = asyncio.create_task(agent.transport.start_server())
        task2 = asyncio.create_task(conductor_ws_server.start())
        await asyncio.sleep(2)
        conductor.bind_transport(WebSocketTransport(port=8766))
        await conductor.start()
        workflow = conductor.create_workflow("azure_openai_research_ws")
        workflow.add_step(
            name="research",
            required_role="researcher",
            params={"topic": "Artificial Intelligence in Healthcare 2024"},
            timeout=60
        )
        workflow.add_step(
            name="analyze",
            required_role="analyzer",
            dependencies=["research"],
            timeout=45
        )
        workflow.add_step(
            name="report",
            required_role="reporter",
            dependencies=["analyze"],
            timeout=60
        )
        batch_id = f"azure_research_ws_{int(time.time())}"
        logger.warning(f"Executing workflow with batch_id: {batch_id}")
        result = await asyncio.wait_for(
            conductor.execute_workflow(workflow, batch_id=batch_id),
            timeout=180
        )
        if result["status"] == "completed":
            logger.warning(f"Workflow completed in {result['duration']:.1f} seconds")
            if "research" in workflow_data:
                logger.warning(f"Research completed: {len(workflow_data['research']['findings'])} characters")
            if "analysis" in workflow_data:
                logger.warning(f"Analysis completed: {len(workflow_data['analysis']['insights'])} characters")
            if "report" in workflow_data:
                logger.warning(f"Report completed: {len(workflow_data['report']['content'])} characters")
                # Save report to organized reports directory
                report_path = f"reports/azure_research_report_{batch_id}.txt"
                os.makedirs("reports", exist_ok=True)
                with open(report_path, "w") as f:
                    f.write(workflow_data['report']['content'])
                logger.warning(f"Report saved to {report_path}")
            checkpoint_info = conductor.get_checkpoint_info(batch_id)
            if checkpoint_info:
                logger.warning(f"Checkpoint saved at {time.ctime(checkpoint_info['checkpoint_time'])}")
            # Print summary to terminal in bold yellow
            print("\033[1;33m\n==== APC WORKFLOW SUMMARY ====")
            print(f"Batch ID: {batch_id}")
            print(f"Duration: {result['duration']:.1f} seconds")
            print(f"Report file: reports/azure_research_report_{batch_id}.txt")
            print("==============================\033[0m\n")
        else:
            logger.error(f"Workflow failed: {result}")
    except asyncio.TimeoutError:
        logger.error("Workflow execution timed out")
    except Exception as e:
        logger.error(f"Error: {e}")
    finally:
        # Stop agent and transport first, then conductor, then ws server
        try:
            await agent.worker.stop()
        except Exception as e:
            logger.error(f"Error stopping agent worker: {e}")
        try:
            await agent.transport.stop_server()
        except Exception as e:
            logger.error(f"Error stopping agent transport: {e}")
        try:
            await conductor.stop()
        except Exception as e:
            logger.error(f"Error stopping conductor: {e}")
        try:
            await conductor_ws_server.stop()
        except Exception as e:
            logger.error(f"Error stopping conductor WebSocket server: {e}")

if __name__ == "__main__":
    asyncio.run(main())
