#!/usr/bin/env python3
"""
Real Azure OpenAI Agents with APC Orchestration

A practical example showing how to use APC to coordinate multiple AI agents.
Tests real Azure OpenAI API calls with agent communication via gRPC.

Requirements:
- Azure OpenAI API key and endpoint in .env file
- pip install openai

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
from apc.transport import GRPCTransport
from apc.helpers.logging import get_logger
from apc.helpers.llms import AzureOpenAIStreamingClient

load_dotenv()
logger = get_logger(__name__)

# Check required environment variables
required_vars = ["AZURE_OPENAI_API_KEY", "AZURE_OPENAI_ENDPOINT", "AZURE_OPENAI_DEPLOYMENT_NAME"]
missing_vars = [var for var in required_vars if not os.getenv(var)]
if missing_vars:
    logger.error(f"Error: Missing environment variables: {missing_vars}")
    logger.error("Create .env file with Azure OpenAI credentials")
    exit(1)

# Initialize the APC Azure OpenAI streaming client
openai_client = AzureOpenAIStreamingClient()
logger.warning("🎨 Using APC streaming client with colored terminal output")

# Global data store for workflow
workflow_data = {}

class ResearchAgent:
    """Agent that performs research using Azure OpenAI."""
    
    def __init__(self):
        self.worker = Worker(
            worker_id="research_agent", 
            roles=["researcher", "analyzer", "reporter"]
        )
        
        self.transport = GRPCTransport(port=50052)
        self.worker.bind_transport(self.transport)
        
        # Register handlers
        self.worker.register_handler("research", self.do_research)
        self.worker.register_handler("analyze", self.do_analysis)
        self.worker.register_handler("report", self.create_report)
    
    async def do_research(self, params: dict) -> dict:
        """Research handler using real Azure OpenAI with streaming."""
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
        
        # Store in workflow data
        workflow_data["research"] = {
            "topic": topic,
            "findings": research_result,
            "timestamp": time.time()
        }
        
        logger.warning(f"✅ Research completed for topic: {topic}")
        
        return {"status": "completed", "research_length": len(research_result)}
    
    async def do_analysis(self, params: dict) -> dict:
        """Analysis handler using real Azure OpenAI with streaming."""
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
        
        # Store analysis
        workflow_data["analysis"] = {
            "insights": analysis_result,
            "based_on": research_data["topic"],
            "timestamp": time.time()
        }
        
        logger.warning(f"✅ Analysis completed for topic: {research_data['topic']}")
        
        return {"status": "completed", "insights_generated": True}
    
    async def create_report(self, params: dict) -> dict:
        """Report generation handler using real Azure OpenAI with streaming."""
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
        
        # Store final report
        workflow_data["report"] = {
            "content": report_result,
            "topic": research_data["topic"],
            "timestamp": time.time()
        }
        
        logger.warning(f"✅ Report generated for topic: {research_data['topic']}")
        
        return {"status": "completed", "report_generated": True}

async def main():
    """Main function to test APC with real Azure OpenAI agents."""
    logger.info("Testing APC with real Azure OpenAI agents...")
    
    # Create conductor with persistent checkpointing
    # Uses default "./checkpoints" directory for consistency across all examples
    conductor = Conductor(
        conductor_id="azure_research_conductor",
        checkpoint_manager=Conductor.create_file_checkpoint_manager("./checkpoints", interval=30),
        enable_auto_recovery=True
    )
    
    # Start research agent in background
    agent = ResearchAgent()
    
    # Use a try-finally pattern to ensure proper cleanup
    try:
        # Start agent and conductor
        await agent.worker.start()
        task1 = asyncio.create_task(agent.transport.start_server())
        await asyncio.sleep(2)  # Give server time to start
        
        conductor.bind_transport(GRPCTransport())
        await conductor.start()
        
        # Check for existing checkpoints
        checkpoints = conductor.list_available_checkpoints()
        if checkpoints:
            logger.info(f"Found {len(checkpoints)} existing checkpoint(s)")
        
        # Create workflow
        workflow = conductor.create_workflow("azure_openai_research")
        
        # Add workflow steps
        workflow.add_step(
            name="research",
            required_role="researcher",
            params={"topic": "Artificial Intelligence in Healthcare 2024"},
            timeout=60  # Reduced timeout
        )
        
        workflow.add_step(
            name="analyze",
            required_role="analyzer", 
            dependencies=["research"],
            timeout=45  # Reduced timeout
        )
        
        workflow.add_step(
            name="report",
            required_role="reporter",
            dependencies=["analyze"],
            timeout=60  # Reduced timeout
        )
        
        # Execute workflow
        batch_id = f"azure_research_{int(time.time())}"
        logger.info(f"Executing workflow with batch_id: {batch_id}")
        
        # Set a reasonable overall timeout
        result = await asyncio.wait_for(
            conductor.execute_workflow(workflow, batch_id=batch_id),
            timeout=180  # 3 minutes max
        )
        
        if result["status"] == "completed":
            logger.info(f"Workflow completed in {result['duration']:.1f} seconds")
            
            # Display results
            if "research" in workflow_data:
                logger.info(f"Research completed: {len(workflow_data['research']['findings'])} characters")
            
            if "analysis" in workflow_data:
                logger.info(f"Analysis completed: {len(workflow_data['analysis']['insights'])} characters")
            
            if "report" in workflow_data:
                logger.info(f"Report completed: {len(workflow_data['report']['content'])} characters")
                
                # Save report to organized reports directory
                report_path = f"reports/azure_research_report_{batch_id}.txt"
                os.makedirs("reports", exist_ok=True)
                with open(report_path, "w") as f:
                    f.write(workflow_data['report']['content'])
                logger.info(f"Report saved to {report_path}")
            
            # Check checkpoint
            checkpoint_info = conductor.get_checkpoint_info(batch_id)
            if checkpoint_info:
                logger.info(f"Checkpoint saved at {time.ctime(checkpoint_info['checkpoint_time'])}")
        
        else:
            logger.error(f"Workflow failed: {result}")
    
    except asyncio.TimeoutError:
        logger.error("Workflow execution timed out")
    except Exception as e:
        logger.error(f"Error: {e}")
    
    finally:
        # Proper cleanup
        try:
            await conductor.stop()
        except Exception as e:
            logger.error(f"Error stopping conductor: {e}")
        try:
            await agent.transport.stop_server()
        except Exception as e:
            logger.error(f"Error stopping agent transport: {e}")
        try:
            await agent.worker.stop()
        except Exception as e:
            logger.error(f"Error stopping agent worker: {e}")

if __name__ == "__main__":
    asyncio.run(main())
