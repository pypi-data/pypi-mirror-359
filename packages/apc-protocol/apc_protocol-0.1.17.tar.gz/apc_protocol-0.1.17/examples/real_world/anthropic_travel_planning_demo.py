#!/usr/bin/env python3
"""
🎯 APC Protocol Value Demonstration: Multi-Agent Travel Planning with Anthropic Claude

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

ARCHITECTURE: 3-Agent Travel Planning Pipeline
Travel Research Agent → Accommodation Agent → Itinerary Agent
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

# Anthropic imports
try:
    import anthropic
except ImportError:
    logger.error("❌ Anthropic library not installed. Run: pip install anthropic")
    exit(1)

class AnthropicClient:
    """Anthropic Claude client for agent communication."""
    
    def __init__(self):
        self.client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        self.model = os.getenv("ANTHROPIC_MODEL", "claude-3-sonnet-20240229")
    
    def chat_completion(self, system_prompt: str, user_prompt: str, max_tokens: int = 800) -> str:
        """Get completion from Anthropic Claude."""
        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=max_tokens,
                system=system_prompt,
                messages=[{"role": "user", "content": user_prompt}]
            )
            return response.content[0].text.strip()
        except Exception as e:
            logger.error(f"Anthropic API error: {e}")
            return f"Error: {str(e)}"

# Shared storage for multi-agent workflow (in production, use Redis/database)
travel_data = {}
anthropic_client = AnthropicClient()

class TravelPlanningWorker:
    """Multi-role worker demonstrating APC orchestration benefits for travel planning."""
    
    def __init__(self):
        # Create worker with multiple roles (could be separate workers in production)
        self.worker = Worker(
            worker_id="travel_planning_worker", 
            roles=["travel_researcher", "accommodation_finder", "itinerary_planner"]
        )
        
        # Bind transport (APC handles all gRPC communication)
        self.transport = GRPCTransport(port=50053)
        self.worker.bind_transport(self.transport)
        
        # Register handlers for each workflow step
        self.worker.register_handler("research_destination", self.research_destination)
        self.worker.register_handler("find_accommodations", self.find_accommodations)
        self.worker.register_handler("create_itinerary", self.create_itinerary)
    
    async def research_destination(self, params: dict) -> dict:
        """Step 1: Travel Research Agent - Research destination and activities."""
        
        print("\n" + "🔍" + "="*70)
        print("🔍 STEP 1: TRAVEL RESEARCH AGENT EXECUTING")
        print("🎯 APC BENEFIT: Role-based routing automatically sent this to 'travel_researcher'")
        print("🔍" + "="*70)
        
        destination = params.get("destination", "Paris, France")
        budget = params.get("budget", "$3000")
        duration = params.get("duration", "7 days")
        
        print(f"📋 Researching destination: {destination}")
        print(f"💰 Budget: {budget} for {duration}")
        print("⚡ APC BENEFIT: Built-in error handling - failures handled gracefully")
        
        # Research prompt for Anthropic Claude
        system_prompt = "You are a travel research expert. Provide comprehensive information about destinations, including attractions, culture, weather, and travel tips."
        user_prompt = f"""Research {destination} for a {duration} trip with a {budget} budget. Provide:
        
        1. Top attractions and must-see places
        2. Local culture and customs
        3. Best time to visit and weather considerations
        4. Transportation options
        5. Food and dining recommendations
        6. Budget considerations and cost estimates
        
        Format as a detailed travel research report."""
        
        # Get research results
        research_results = anthropic_client.chat_completion(system_prompt, user_prompt, max_tokens=800)
        
        # Store for next workflow step
        print("📡 APC BENEFIT: Seamless data sharing - storing for next workflow step")
        travel_data["research_results"] = research_results
        travel_data["destination"] = destination
        travel_data["budget"] = budget
        travel_data["duration"] = duration
        
        print("✅ Travel research completed - APC will automatically trigger next step")
        logger.info(f"Travel research completed for '{destination}' ({len(research_results)} characters)")
        
        return {
            "status": "completed",
            "research_data": research_results,
            "destination": destination,
            "step": "research"
        }
    
    async def find_accommodations(self, params: dict) -> dict:
        """Step 2: Accommodation Agent - Find suitable accommodations."""
        
        print("\n" + "🏨" + "="*70)
        print("🏨 STEP 2: ACCOMMODATION AGENT EXECUTING")
        print("🎯 APC BENEFIT: Dependency management - only runs AFTER research completes")
        print("🏨" + "="*70)
        
        # Get research from previous step
        research_data = travel_data.get("research_results", "")
        destination = travel_data.get("destination", "unknown")
        budget = travel_data.get("budget", "$3000")
        duration = travel_data.get("duration", "7 days")
        
        if not research_data:
            print("❌ No research data available")
            return {"status": "failed", "error": "No research data"}
        
        print(f"🏨 Finding accommodations in: {destination}")
        print(f"📊 Using research data ({len(research_data)} characters)")
        print("🔄 APC BENEFIT: Perfect data flow - no custom messaging protocols needed")
        
        # Accommodation prompt
        system_prompt = "You are an accommodation specialist. Recommend suitable hotels, hostels, or other accommodations based on destination research and budget."
        user_prompt = f"""Based on this travel research for {destination}, recommend accommodations for a {duration} trip with {budget} budget:

        RESEARCH DATA:
        {research_data}
        
        Provide:
        1. 3-5 accommodation recommendations (different price ranges)
        2. Location advantages and nearby attractions
        3. Amenities and features
        4. Estimated costs per night
        5. Booking tips and best practices
        
        Format as a detailed accommodation guide."""
        
        # Get accommodation results
        accommodation_results = anthropic_client.chat_completion(system_prompt, user_prompt, max_tokens=800)
        
        # Store for final step
        print("📡 APC BENEFIT: Automatic result propagation to next workflow step")
        travel_data["accommodation_results"] = accommodation_results
        
        print("✅ Accommodation search completed - APC will automatically trigger final step")
        logger.info(f"Accommodation search completed ({len(accommodation_results)} characters)")
        
        return {
            "status": "completed",
            "accommodation_data": accommodation_results,
            "step": "accommodation"
        }
    
    async def create_itinerary(self, params: dict) -> dict:
        """Step 3: Itinerary Agent - Create comprehensive travel itinerary."""
        
        print("\n" + "📅" + "="*70)
        print("📅 STEP 3: ITINERARY PLANNER EXECUTING")
        print("🎯 APC BENEFIT: Final step - waits for ALL dependencies to complete")
        print("📅" + "="*70)
        
        # Get data from all previous steps
        research_data = travel_data.get("research_results", "")
        accommodation_data = travel_data.get("accommodation_results", "")
        destination = travel_data.get("destination", "unknown")
        duration = travel_data.get("duration", "7 days")
        budget = travel_data.get("budget", "$3000")
        
        if not research_data or not accommodation_data:
            print("❌ Missing data from previous steps")
            return {"status": "failed", "error": "Incomplete travel data"}
        
        print(f"📅 Creating itinerary for: {destination}")
        print("🏗️ APC BENEFIT: All workflow data automatically available")
        print("📊 No complex coordination - APC handled everything!")
        
        # Itinerary generation prompt
        system_prompt = "You are a professional travel itinerary planner. Create detailed, day-by-day travel itineraries combining destination research and accommodation information."
        user_prompt = f"""Create a comprehensive {duration} itinerary for {destination} with {budget} budget, using this information:

        DESTINATION RESEARCH:
        {research_data}
        
        ACCOMMODATION OPTIONS:
        {accommodation_data}
        
        Create a detailed day-by-day itinerary including:
        1. Daily activities and attractions
        2. Recommended accommodation from the research
        3. Transportation between locations
        4. Meal suggestions and dining
        5. Budget breakdown by day
        6. Travel tips and important notes
        
        Format as a complete travel itinerary guide."""
        
        # Generate final itinerary
        final_itinerary = anthropic_client.chat_completion(system_prompt, user_prompt, max_tokens=1000)
        
        # Store final result
        travel_data["final_itinerary"] = final_itinerary
        
        print("✅ Travel itinerary completed - Workflow finished successfully!")
        logger.info(f"Itinerary generation completed ({len(final_itinerary)} characters)")
        
        return {
            "status": "completed",
            "final_itinerary": final_itinerary,
            "step": "itinerary"
        }

async def demonstrate_apc_travel_planning():
    """Demonstrate the clear value of APC protocol for multi-agent travel planning."""
    
    print("🚀" + "="*80)
    print("🚀 APC PROTOCOL DEMONSTRATION: Multi-Agent Travel Planning Workflow")
    print("🚀" + "="*80)
    print("✈️  Travel Destination: 'Tokyo, Japan - 10 day cultural adventure'")
    print("🏗️  Architecture: Research → Accommodation → Itinerary (3 coordinated agents)")
    print("⚡ APC handles: routing, dependencies, communication, error handling")
    print("="*82)
    
    # Initialize the multi-role worker
    worker = TravelPlanningWorker()
    
    # Start worker and transport
    await worker.worker.start()
    await worker.transport.start_server()
    await asyncio.sleep(2)  # Let server initialize
    
    # Create conductor for workflow orchestration
    conductor = Conductor(conductor_id="travel_conductor")
    conductor.bind_transport(GRPCTransport())
    
    # Clear any previous data
    travel_data.clear()
    
    try:
        print("\n🏗️ CREATING TRAVEL WORKFLOW WITH APC...")
        print("⚡ APC BENEFIT: Simple workflow definition replaces complex orchestration code")
        
        # Create workflow (this is ALL the orchestration code needed!)
        workflow = conductor.create_workflow("travel_planning_workflow")
        
        # Step 1: Research destination (no dependencies)
        workflow.add_step(
            name="research_destination",
            required_role="travel_researcher",
            params={
                "destination": "Tokyo, Japan",
                "budget": "$4000",
                "duration": "10 days"
            },
            timeout=60
        )
        
        # Step 2: Find accommodations (depends on research)
        workflow.add_step(
            name="find_accommodations",
            required_role="accommodation_finder", 
            dependencies=["research_destination"],  # APC ensures this runs AFTER research
            timeout=60
        )
        
        # Step 3: Create itinerary (depends on accommodations)
        workflow.add_step(
            name="create_itinerary",
            required_role="itinerary_planner",
            dependencies=["find_accommodations"],  # APC ensures this runs AFTER accommodations
            timeout=60
        )
        
        print("✅ Travel workflow defined! APC will handle all orchestration automatically.")
        print("\n🚀 EXECUTING MULTI-AGENT TRAVEL PLANNING...")
        
        # Execute workflow (APC does ALL the hard work!)
        result = await conductor.execute_workflow(workflow)
        
        if result["status"] == "completed":
            # Show the dramatic difference APC makes
            print("\n" + "🎯" + "="*80)
            print("🎯 APC PROTOCOL VALUE DEMONSTRATION - PROBLEMS SOLVED!")
            print("🎯" + "="*80)
            print("❌ WITHOUT APC (traditional approach):")
            print("   💻 ~200+ lines of custom orchestration code needed")
            print("   🔧 Custom message passing between travel agents")
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
            print("\n📋 TRAVEL PLANNING RESULTS:")
            print("="*50)
            
            print("\n🔍 DESTINATION RESEARCH:")
            print("-" * 30)
            research = travel_data.get("research_results", "No data")
            print(research[:300] + "..." if len(research) > 300 else research)
            
            print("\n🏨 ACCOMMODATION RECOMMENDATIONS:")
            print("-" * 30)
            accommodations = travel_data.get("accommodation_results", "No data")
            print(accommodations[:300] + "..." if len(accommodations) > 300 else accommodations)
            
            print("\n📅 COMPLETE TRAVEL ITINERARY:")
            print("-" * 30)
            itinerary = travel_data.get("final_itinerary", "No data")
            print(itinerary[:400] + "..." if len(itinerary) > 400 else itinerary)
            
            print("\n🎉 SUCCESS! APC orchestrated 3 travel agents seamlessly!")
            print("💡 This would require 200+ lines of custom code without APC!")
            
        else:
            print(f"❌ Workflow failed: {result}")
            print("🛡️ APC BENEFIT: Even failures are handled gracefully with detailed error info")
    
    except Exception as e:
        logger.error(f"Travel workflow execution failed: {e}")
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
    required_vars = ["ANTHROPIC_API_KEY"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"❌ Missing environment variables: {missing_vars}")
        print("📋 Setup instructions:")
        print("   1. Copy .env.example to .env")
        print("   2. Add your Anthropic API key: ANTHROPIC_API_KEY=your_key_here")
        print("   3. Run the example again")
        exit(1)
    
    print("✅ Environment check passed")
    print("🚀 Starting APC Protocol travel planning demonstration...")
    
    # Run the demonstration
    asyncio.run(demonstrate_apc_travel_planning())
