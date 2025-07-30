#!/usr/bin/env python3
"""
🎯 APC Protocol Value Demonstration: Multi-Agent Supply Chain Management with Azure OpenAI

BEFORE YOU RUN: This example clearly shows what problems APC solves and why it's essential.

❌ WITHOUT APC (Traditional Approach):
1. Manual agent coordination - complex custom orchestration code
2. Custom communication protocols - reinvent messaging for every project  
3. Dependency management nightmare - manually track what runs when
4. Error handling chaos - custom retry logic for every interaction
5. No service discovery - agents can't find each other
6. Resource coordination headaches - prevent conflicts and deadlocks

✅ WITH APC (This Example):
1. ✅ Define workflow steps with dependencies → APC handles orchestration
2. ✅ Role-based agent routing → APC automatically routes tasks to right agents
3. ✅ Built-in dependency management → Steps run in correct order automatically
4. ✅ Standardized gRPC communication → No custom protocols needed
5. ✅ Built-in error handling & timeouts → Robust failure recovery
6. ✅ Service discovery → Agents find each other automatically

ARCHITECTURE: 3-Agent Supply Chain Pipeline
Demand Forecasting Agent → Inventory Optimization Agent → Procurement Planning Agent
(Each step depends on the previous, APC manages the entire flow)
"""

import asyncio
import json
import os
from typing import Dict, Any
from dotenv import load_dotenv

# APC imports
from apc import Worker, Conductor
from apc.transport import GRPCTransport
from apc.logging import get_logger, StructuredLogger

# Load environment variables
load_dotenv()

# Enhanced APC logging - automatically colorized and structured
logger = StructuredLogger(get_logger(__name__))

# Azure OpenAI imports
try:
    from openai import AzureOpenAI
except ImportError:
    logger.error(
        "Azure OpenAI library not installed", 
        solution="Run: pip install openai",
        required_library="openai"
    )
    exit(1)

class AzureOpenAIClient:
    """Azure OpenAI client for agent communication."""
    
    def __init__(self):
        self.client = AzureOpenAI(
            api_key=os.getenv("AZURE_OPENAI_API_KEY"),
            api_version=os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-15-preview"),
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
        )
        self.deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", "gpt-35-turbo")
    
    def chat_completion(self, messages: list, max_tokens: int = 800) -> str:
        """Get completion from Azure OpenAI."""
        try:
            response = self.client.chat.completions.create(
                model=self.deployment,
                messages=messages,
                max_tokens=max_tokens,
                temperature=0.7
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            logger.error(
                "Azure OpenAI API error",
                error=str(e),
                model=self.deployment,
                operation="chat_completion"
            )
            return f"Error: {str(e)}"

# Shared storage for multi-agent workflow (in production, use Redis/database)
supply_chain_data = {}
openai_client = AzureOpenAIClient()

class SupplyChainWorker:
    """Multi-role worker demonstrating APC orchestration benefits for supply chain management."""
    
    def __init__(self):
        # Create worker with multiple roles (could be separate workers in production)
        self.worker = Worker(
            worker_id="supply_chain_worker", 
            roles=["demand_forecaster", "inventory_optimizer", "procurement_planner"]
        )
        
        # Bind transport (APC handles all gRPC communication)
        self.transport = GRPCTransport(port=50055)
        self.worker.bind_transport(self.transport)
        
        # Register handlers for each workflow step
        self.worker.register_handler("forecast_demand", self.forecast_demand)
        self.worker.register_handler("optimize_inventory", self.optimize_inventory)
        self.worker.register_handler("plan_procurement", self.plan_procurement)
    
    async def forecast_demand(self, params: dict) -> dict:
        """Step 1: Demand Forecasting Agent - Predict future demand patterns."""
        
        print("\n" + "📊" + "="*70)
        print("📊 STEP 1: DEMAND FORECASTING AGENT EXECUTING")
        print("🎯 APC BENEFIT: Role-based routing automatically sent this to 'demand_forecaster'")
        print("📊" + "="*70)
        
        product_category = params.get("product_category", "Electronics")
        time_horizon = params.get("time_horizon", "Q1 2025")
        historical_data = params.get("historical_data", "2022-2024 sales data")
        
        print(f"📋 Forecasting demand for: {product_category}")
        print(f"📅 Time horizon: {time_horizon}")
        print(f"📈 Using historical data: {historical_data}")
        print("⚡ APC BENEFIT: Built-in error handling - failures handled gracefully")
        
        # Demand forecasting prompt for Azure OpenAI
        messages = [
            {"role": "system", "content": "You are a demand forecasting expert. Analyze market trends and historical data to predict future demand patterns."},
            {"role": "user", "content": f"""Forecast demand for {product_category} in {time_horizon} based on {historical_data}.
            
            Analyze:
            1. Historical sales patterns and trends
            2. Seasonal variations and cyclical patterns
            3. Market factors affecting demand
            4. Economic indicators and consumer behavior
            5. Competitive landscape impact
            6. Demand forecast by month with confidence intervals
            
            Provide a detailed demand forecast report."""}
        ]
        
        # Get forecasting results
        demand_forecast = openai_client.chat_completion(messages, max_tokens=800)
        
        # Store for next workflow step
        print("📡 APC BENEFIT: Seamless data sharing - storing for next workflow step")
        supply_chain_data["demand_forecast"] = demand_forecast
        supply_chain_data["product_category"] = product_category
        supply_chain_data["time_horizon"] = time_horizon
        supply_chain_data["historical_data"] = historical_data
        
        print("✅ Demand forecasting completed - APC will automatically trigger next step")
        logger.info(
            "Demand forecasting completed",
            product_category=product_category,
            forecast_length=len(demand_forecast),
            time_horizon=time_horizon,
            step="demand_forecasting"
        )
        
        return {
            "status": "completed",
            "forecast_data": demand_forecast,
            "product_category": product_category,
            "step": "demand_forecast"
        }
    
    async def optimize_inventory(self, params: dict) -> dict:
        """Step 2: Inventory Optimization Agent - Optimize inventory levels based on demand forecast."""
        
        print("\n" + "📦" + "="*70)
        print("📦 STEP 2: INVENTORY OPTIMIZATION AGENT EXECUTING")
        print("🎯 APC BENEFIT: Dependency management - only runs AFTER demand forecasting completes")
        print("📦" + "="*70)
        
        # Get forecast from previous step
        demand_forecast = supply_chain_data.get("demand_forecast", "")
        product_category = supply_chain_data.get("product_category", "unknown")
        time_horizon = supply_chain_data.get("time_horizon", "Q1 2025")
        
        if not demand_forecast:
            print("❌ No demand forecast data available")
            return {"status": "failed", "error": "No demand forecast data"}
        
        print(f"📦 Optimizing inventory for: {product_category}")
        print(f"📊 Using demand forecast ({len(demand_forecast)} characters)")
        print("🔄 APC BENEFIT: Perfect data flow - no custom messaging protocols needed")
        
        # Inventory optimization prompt
        messages = [
            {"role": "system", "content": "You are an inventory optimization specialist. Design optimal inventory strategies based on demand forecasts and operational constraints."},
            {"role": "user", "content": f"""Optimize inventory levels for {product_category} in {time_horizon} based on this demand forecast:

            DEMAND FORECAST:
            {demand_forecast}
            
            Create an inventory optimization plan including:
            1. Optimal stock levels by month
            2. Safety stock calculations
            3. Reorder points and quantities
            4. ABC analysis and prioritization
            5. Inventory turnover targets
            6. Storage and handling requirements
            7. Cost optimization strategies
            
            Provide a detailed inventory optimization report."""}
        ]
        
        # Get optimization results
        inventory_plan = openai_client.chat_completion(messages, max_tokens=800)
        
        # Store for final step
        print("📡 APC BENEFIT: Automatic result propagation to next workflow step")
        supply_chain_data["inventory_plan"] = inventory_plan
        
        print("✅ Inventory optimization completed - APC will automatically trigger final step")
        logger.info(
            "Inventory optimization completed",
            plan_length=len(inventory_plan),
            product_category=supply_chain_data.get("product_category", "unknown"),
            step="inventory_optimization"
        )
        
        return {
            "status": "completed",
            "inventory_data": inventory_plan,
            "step": "inventory_optimization"
        }
    
    async def plan_procurement(self, params: dict) -> dict:
        """Step 3: Procurement Planning Agent - Create comprehensive procurement strategy."""
        
        print("\n" + "🛒" + "="*70)
        print("🛒 STEP 3: PROCUREMENT PLANNING AGENT EXECUTING")
        print("🎯 APC BENEFIT: Final step - waits for ALL dependencies to complete")
        print("🛒" + "="*70)
        
        # Get data from all previous steps
        demand_forecast = supply_chain_data.get("demand_forecast", "")
        inventory_plan = supply_chain_data.get("inventory_plan", "")
        product_category = supply_chain_data.get("product_category", "unknown")
        time_horizon = supply_chain_data.get("time_horizon", "Q1 2025")
        
        if not demand_forecast or not inventory_plan:
            print("❌ Missing data from previous steps")
            return {"status": "failed", "error": "Incomplete supply chain data"}
        
        print(f"🛒 Creating procurement plan for: {product_category}")
        print("🏗️ APC BENEFIT: All workflow data automatically available")
        print("📊 No complex coordination - APC handled everything!")
        
        # Procurement planning prompt
        messages = [
            {"role": "system", "content": "You are a procurement planning expert. Develop comprehensive procurement strategies based on demand forecasts and inventory optimization plans."},
            {"role": "user", "content": f"""Create a procurement plan for {product_category} in {time_horizon} using this information:

            DEMAND FORECAST:
            {demand_forecast}
            
            INVENTORY OPTIMIZATION PLAN:
            {inventory_plan}
            
            Develop a comprehensive procurement strategy including:
            1. Supplier selection criteria and evaluation
            2. Purchase order scheduling and quantities
            3. Contract negotiation strategies
            4. Risk mitigation and contingency plans
            5. Cost optimization and budget allocation
            6. Quality assurance and compliance requirements
            7. Performance metrics and KPIs
            8. Implementation timeline and milestones
            
            Format as a complete procurement strategy document."""}
        ]
        
        # Generate final procurement plan
        procurement_plan = openai_client.chat_completion(messages, max_tokens=1000)
        
        # Store final result
        supply_chain_data["procurement_plan"] = procurement_plan
        
        print("✅ Procurement planning completed - Workflow finished successfully!")
        logger.info(
            "Procurement planning completed",
            plan_length=len(procurement_plan),
            product_category=supply_chain_data.get("product_category", "unknown"),
            step="procurement_planning"
        )
        
        return {
            "status": "completed",
            "procurement_plan": procurement_plan,
            "step": "procurement_planning"
        }

async def demonstrate_apc_supply_chain():
    """Demonstrate the clear value of APC protocol for multi-agent supply chain management."""
    
    print("🚀" + "="*80)
    print("🚀 APC PROTOCOL DEMONSTRATION: Multi-Agent Supply Chain Management")
    print("🚀" + "="*80)
    print("📦 Supply Chain Focus: 'Smart Home Devices - Q2 2025 planning'")
    print("🏗️  Architecture: Demand Forecast → Inventory Optimization → Procurement Planning")
    print("⚡ APC handles: routing, dependencies, communication, error handling")
    print("="*82)
    
    # Initialize the multi-role worker
    worker = SupplyChainWorker()
    
    # Start worker and transport
    await worker.worker.start()
    await worker.transport.start_server()
    await asyncio.sleep(2)  # Let server initialize
    
    # Create conductor for workflow orchestration
    conductor = Conductor(conductor_id="supply_chain_conductor")
    conductor.bind_transport(GRPCTransport())
    
    # Clear any previous data
    supply_chain_data.clear()
    
    try:
        print("\n🏗️ CREATING SUPPLY CHAIN WORKFLOW WITH APC...")
        print("⚡ APC BENEFIT: Simple workflow definition replaces complex orchestration code")
        
        # Create workflow (this is ALL the orchestration code needed!)
        workflow = conductor.create_workflow("supply_chain_management_workflow")
        
        # Step 1: Demand forecasting (no dependencies)
        workflow.add_step(
            name="forecast_demand",
            required_role="demand_forecaster",
            params={
                "product_category": "Smart Home Devices",
                "time_horizon": "Q2 2025",
                "historical_data": "2022-2024 smart device sales and market data"
            },
            timeout=60
        )
        
        # Step 2: Inventory optimization (depends on demand forecast)
        workflow.add_step(
            name="optimize_inventory",
            required_role="inventory_optimizer", 
            dependencies=["forecast_demand"],  # APC ensures this runs AFTER forecasting
            timeout=60
        )
        
        # Step 3: Procurement planning (depends on inventory optimization)
        workflow.add_step(
            name="plan_procurement",
            required_role="procurement_planner",
            dependencies=["optimize_inventory"],  # APC ensures this runs AFTER optimization
            timeout=60
        )
        
        print("✅ Supply chain workflow defined! APC will handle all orchestration automatically.")
        print("\n🚀 EXECUTING MULTI-AGENT SUPPLY CHAIN MANAGEMENT...")
        
        # Execute workflow (APC does ALL the hard work!)
        result = await conductor.execute_workflow(workflow)
        
        if result["status"] == "completed":
            # Show the dramatic difference APC makes
            print("\n" + "🎯" + "="*80)
            print("🎯 APC PROTOCOL VALUE DEMONSTRATION - PROBLEMS SOLVED!")
            print("🎯" + "="*80)
            print("❌ WITHOUT APC (traditional approach):")
            print("   💻 ~200+ lines of custom orchestration code needed")
            print("   🔧 Custom message passing between supply chain agents")
            print("   ⏰ Manual timeout and error handling")
            print("   🔄 Complex dependency tracking and execution order")
            print("   🔍 Service discovery and agent registration")
            print("   🛠️  Custom retry logic and failure recovery")
            print("   📡 Protocol design and implementation")
            print("   🚨 Resource coordination and deadlock prevention")
            print("")
            print("✅ WITH APC (this example):")
            print("   ⚡ ~15 lines to define workflow steps and dependencies")
            print("   🤖 Automatic role-based routing and execution")
            print("   🛡️  Built-in timeout, error handling, and retries")
            print("   📋 Dependency management handled automatically")
            print("   🔍 Service discovery built into the protocol") 
            print("   📡 Standardized gRPC communication")
            print("   ✨ Just focus on your agent logic - APC handles the rest!")
            print("="*82)
            
            # Display the actual results
            print("\n📋 SUPPLY CHAIN MANAGEMENT RESULTS:")
            print("="*50)
            
            print("\n📊 DEMAND FORECAST:")
            print("-" * 30)
            forecast = supply_chain_data.get("demand_forecast", "No data")
            print(forecast[:300] + "..." if len(forecast) > 300 else forecast)
            
            print("\n📦 INVENTORY OPTIMIZATION:")
            print("-" * 30)
            inventory = supply_chain_data.get("inventory_plan", "No data")
            print(inventory[:300] + "..." if len(inventory) > 300 else inventory)
            
            print("\n🛒 PROCUREMENT STRATEGY:")
            print("-" * 30)
            procurement = supply_chain_data.get("procurement_plan", "No data")
            print(procurement[:400] + "..." if len(procurement) > 400 else procurement)
            
            print("\n🎉 SUCCESS! APC orchestrated 3 supply chain agents seamlessly!")
            print("💡 This would require 200+ lines of custom code without APC!")
            
        else:
            print(f"❌ Workflow failed: {result}")
            print("🛡️ APC BENEFIT: Even failures are handled gracefully with detailed error info")
    
    except Exception as e:
        logger.error(
            "Supply chain workflow execution failed",
            error=str(e),
            workflow_type="supply_chain_management"
        )
        print("🛡️ APC BENEFIT: Built-in exception handling prevents system crashes")
        import traceback
        traceback.print_exc()
    
    finally:
        # Cleanup
        print("\n🧹 Cleaning up resources...")
        try:
            await worker.transport.stop_server()
            await worker.worker.stop()
        except:
            pass

if __name__ == "__main__":
    # Environment validation
    required_vars = ["AZURE_OPENAI_API_KEY", "AZURE_OPENAI_ENDPOINT"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"❌ Missing environment variables: {missing_vars}")
        print("📋 Setup instructions:")
        print("   1. Copy .env.example to .env")
        print("   2. Add your Azure OpenAI credentials")
        print("   3. Run the example again")
        exit(1)
    
    print("✅ Environment check passed")
    print("🚀 Starting APC Protocol supply chain demonstration...")
    
    # Run the demonstration
    asyncio.run(demonstrate_apc_supply_chain())
