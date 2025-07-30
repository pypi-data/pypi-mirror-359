#!/usr/bin/env python3
"""
🎯 APC Protocol Value Demonstration: Multi-Agent Financial Analysis with Google Gemini

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

ARCHITECTURE: 3-Agent Financial Analysis Pipeline
Market Research Agent → Risk Analysis Agent → Investment Report Agent
(Each step depends on the previous, APC manages the entire flow)
"""

import asyncio
import json
import logging
import os
from typing import Dict, Any
from dotenv import load_dotenv

# APC imports
from apc import Worker, Conductor
from apc.transport import GRPCTransport

# Load environment variables
load_dotenv()

# Configure logging to show APC orchestration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Google Gemini imports
try:
    import google.generativeai as genai
except ImportError:
    logger.error("❌ Google Generative AI library not installed. Run: pip install google-generativeai")
    exit(1)

class GeminiClient:
    """Google Gemini client for agent communication."""
    
    def __init__(self):
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            logger.error("Missing GOOGLE_API_KEY environment variable")
            exit(1)
            
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(os.getenv("GEMINI_MODEL", "gemini-1.5-flash"))
    
    def chat_completion(self, prompt: str, max_tokens: int = 800) -> str:
        """Get completion from Google Gemini."""
        try:
            response = self.model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    max_output_tokens=max_tokens,
                    temperature=0.7
                )
            )
            return response.text.strip()
        except Exception as e:
            logger.error(f"Gemini API error: {e}")
            return f"Error: {str(e)}"

# Shared storage for multi-agent workflow (in production, use Redis/database)
financial_data = {}
gemini_client = GeminiClient()

class FinancialAnalysisWorker:
    """Multi-role worker demonstrating APC orchestration benefits for financial analysis."""
    
    def __init__(self):
        # Create worker with multiple roles (could be separate workers in production)
        self.worker = Worker(
            worker_id="financial_analysis_worker", 
            roles=["market_researcher", "risk_analyst", "investment_advisor"]
        )
        
        # Bind transport (APC handles all gRPC communication)
        self.transport = GRPCTransport(port=50054)
        self.worker.bind_transport(self.transport)
        
        # Register handlers for each workflow step
        self.worker.register_handler("research_market", self.research_market)
        self.worker.register_handler("analyze_risks", self.analyze_risks)
        self.worker.register_handler("create_investment_report", self.create_investment_report)
    
    async def research_market(self, params: dict) -> dict:
        """Step 1: Market Research Agent - Research market trends and opportunities."""
        
        print("\n" + "📈" + "="*70)
        print("📈 STEP 1: MARKET RESEARCH AGENT EXECUTING")
        print("🎯 APC BENEFIT: Role-based routing automatically sent this to 'market_researcher'")
        print("📈" + "="*70)
        
        sector = params.get("sector", "Technology")
        timeframe = params.get("timeframe", "Q4 2024")
        investment_amount = params.get("investment_amount", "$50,000")
        
        print(f"📋 Researching market: {sector} sector")
        print(f"📅 Timeframe: {timeframe}")
        print(f"💰 Investment amount: {investment_amount}")
        print("⚡ APC BENEFIT: Built-in error handling - failures handled gracefully")
        
        # Market research prompt for Gemini
        prompt = f"""As an expert market researcher, analyze the {sector} sector for {timeframe}. 
        
        Research Focus:
        - Market trends and growth patterns
        - Key players and competitive landscape
        - Emerging opportunities and technologies
        - Market size and potential returns
        - Economic factors affecting the sector
        
        Investment Context: {investment_amount} investment
        
        Provide a comprehensive market research report with data-driven insights."""
        
        # Get research results
        research_results = gemini_client.chat_completion(prompt, max_tokens=800)
        
        # Store for next workflow step
        print("📡 APC BENEFIT: Seamless data sharing - storing for next workflow step")
        financial_data["market_research"] = research_results
        financial_data["sector"] = sector
        financial_data["timeframe"] = timeframe
        financial_data["investment_amount"] = investment_amount
        
        print("✅ Market research completed - APC will automatically trigger next step")
        logger.info(f"Market research completed for '{sector}' ({len(research_results)} characters)")
        
        return {
            "status": "completed",
            "research_data": research_results,
            "sector": sector,
            "step": "market_research"
        }
    
    async def analyze_risks(self, params: dict) -> dict:
        """Step 2: Risk Analysis Agent - Analyze investment risks and mitigation strategies."""
        
        print("\n" + "⚠️" + "="*70)
        print("⚠️ STEP 2: RISK ANALYSIS AGENT EXECUTING")
        print("🎯 APC BENEFIT: Dependency management - only runs AFTER market research completes")
        print("⚠️" + "="*70)
        
        # Get research from previous step
        market_research = financial_data.get("market_research", "")
        sector = financial_data.get("sector", "unknown")
        investment_amount = financial_data.get("investment_amount", "$50,000")
        timeframe = financial_data.get("timeframe", "Q4 2024")
        
        if not market_research:
            print("❌ No market research data available")
            return {"status": "failed", "error": "No market research data"}
        
        print(f"⚠️ Analyzing risks for: {sector} sector")
        print(f"📊 Using market research ({len(market_research)} characters)")
        print("🔄 APC BENEFIT: Perfect data flow - no custom messaging protocols needed")
        
        # Risk analysis prompt
        prompt = f"""As a risk analysis expert, evaluate the investment risks for {sector} sector with {investment_amount} investment in {timeframe}.

        MARKET RESEARCH DATA:
        {market_research}
        
        Analyze:
        1. Market risks (volatility, competition, regulation)
        2. Financial risks (liquidity, credit, operational)
        3. Economic risks (inflation, interest rates, recession)
        4. Sector-specific risks and challenges
        5. Risk mitigation strategies
        6. Risk scoring and probability assessment
        
        Provide a comprehensive risk analysis report with actionable insights."""
        
        # Get risk analysis results
        risk_analysis = gemini_client.chat_completion(prompt, max_tokens=800)
        
        # Store for final step
        print("📡 APC BENEFIT: Automatic result propagation to next workflow step")
        financial_data["risk_analysis"] = risk_analysis
        
        print("✅ Risk analysis completed - APC will automatically trigger final step")
        logger.info(f"Risk analysis completed ({len(risk_analysis)} characters)")
        
        return {
            "status": "completed",
            "risk_data": risk_analysis,
            "step": "risk_analysis"
        }
    
    async def create_investment_report(self, params: dict) -> dict:
        """Step 3: Investment Advisor Agent - Create comprehensive investment recommendation."""
        
        print("\n" + "💼" + "="*70)
        print("💼 STEP 3: INVESTMENT ADVISOR EXECUTING")
        print("🎯 APC BENEFIT: Final step - waits for ALL dependencies to complete")
        print("💼" + "="*70)
        
        # Get data from all previous steps
        market_research = financial_data.get("market_research", "")
        risk_analysis = financial_data.get("risk_analysis", "")
        sector = financial_data.get("sector", "unknown")
        investment_amount = financial_data.get("investment_amount", "$50,000")
        timeframe = financial_data.get("timeframe", "Q4 2024")
        
        if not market_research or not risk_analysis:
            print("❌ Missing data from previous steps")
            return {"status": "failed", "error": "Incomplete financial analysis data"}
        
        print(f"💼 Creating investment report for: {sector} sector")
        print("🏗️ APC BENEFIT: All workflow data automatically available")
        print("📊 No complex coordination - APC handled everything!")
        
        # Investment report generation prompt
        prompt = f"""As a senior investment advisor, create a comprehensive investment recommendation for {sector} sector with {investment_amount} investment in {timeframe}.

        MARKET RESEARCH:
        {market_research}
        
        RISK ANALYSIS:
        {risk_analysis}
        
        Create a detailed investment report including:
        1. Executive Summary and Recommendation
        2. Market Analysis Summary
        3. Risk Assessment and Mitigation
        4. Investment Strategy and Allocation
        5. Expected Returns and Timeline
        6. Specific Investment Targets (companies/funds)
        7. Exit Strategy and Performance Metrics
        8. Action Plan and Next Steps
        
        Format as a professional investment advisory report."""
        
        # Generate final investment report
        investment_report = gemini_client.chat_completion(prompt, max_tokens=1000)
        
        # Store final result
        financial_data["investment_report"] = investment_report
        
        print("✅ Investment report completed - Workflow finished successfully!")
        logger.info(f"Investment report generation completed ({len(investment_report)} characters)")
        
        return {
            "status": "completed",
            "investment_report": investment_report,
            "step": "investment_report"
        }

async def demonstrate_apc_financial_analysis():
    """Demonstrate the clear value of APC protocol for multi-agent financial analysis."""
    
    print("🚀" + "="*80)
    print("🚀 APC PROTOCOL DEMONSTRATION: Multi-Agent Financial Analysis Workflow")
    print("🚀" + "="*80)
    print("📈 Investment Focus: 'Renewable Energy Sector - $75,000 investment'")
    print("🏗️  Architecture: Market Research → Risk Analysis → Investment Report (3 coordinated agents)")
    print("⚡ APC handles: routing, dependencies, communication, error handling")
    print("="*82)
    
    # Initialize the multi-role worker
    worker = FinancialAnalysisWorker()
    
    # Start worker and transport
    await worker.worker.start()
    await worker.transport.start_server()
    await asyncio.sleep(2)  # Let server initialize
    
    # Create conductor for workflow orchestration
    conductor = Conductor(conductor_id="financial_conductor")
    conductor.bind_transport(GRPCTransport())
    
    # Clear any previous data
    financial_data.clear()
    
    try:
        print("\n🏗️ CREATING FINANCIAL ANALYSIS WORKFLOW WITH APC...")
        print("⚡ APC BENEFIT: Simple workflow definition replaces complex orchestration code")
        
        # Create workflow (this is ALL the orchestration code needed!)
        workflow = conductor.create_workflow("financial_analysis_workflow")
        
        # Step 1: Market research (no dependencies)
        workflow.add_step(
            name="research_market",
            required_role="market_researcher",
            params={
                "sector": "Renewable Energy",
                "timeframe": "2025 Q1-Q2",
                "investment_amount": "$75,000"
            },
            timeout=60
        )
        
        # Step 2: Risk analysis (depends on market research)
        workflow.add_step(
            name="analyze_risks",
            required_role="risk_analyst", 
            dependencies=["research_market"],  # APC ensures this runs AFTER research
            timeout=60
        )
        
        # Step 3: Investment report (depends on risk analysis)
        workflow.add_step(
            name="create_investment_report",
            required_role="investment_advisor",
            dependencies=["analyze_risks"],  # APC ensures this runs AFTER risk analysis
            timeout=60
        )
        
        print("✅ Financial workflow defined! APC will handle all orchestration automatically.")
        print("\n🚀 EXECUTING MULTI-AGENT FINANCIAL ANALYSIS...")
        
        # Execute workflow (APC does ALL the hard work!)
        result = await conductor.execute_workflow(workflow)
        
        if result["status"] == "completed":
            # Show the dramatic difference APC makes
            print("\n" + "🎯" + "="*80)
            print("🎯 APC PROTOCOL VALUE DEMONSTRATION - PROBLEMS SOLVED!")
            print("🎯" + "="*80)
            print("❌ WITHOUT APC (traditional approach):")
            print("   💻 ~200+ lines of custom orchestration code needed")
            print("   🔧 Custom message passing between financial agents")
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
            print("\n📋 FINANCIAL ANALYSIS RESULTS:")
            print("="*50)
            
            print("\n📈 MARKET RESEARCH:")
            print("-" * 30)
            research = financial_data.get("market_research", "No data")
            print(research[:300] + "..." if len(research) > 300 else research)
            
            print("\n⚠️ RISK ANALYSIS:")
            print("-" * 30)
            risks = financial_data.get("risk_analysis", "No data")
            print(risks[:300] + "..." if len(risks) > 300 else risks)
            
            print("\n💼 INVESTMENT RECOMMENDATION:")
            print("-" * 30)
            report = financial_data.get("investment_report", "No data")
            print(report[:400] + "..." if len(report) > 400 else report)
            
            print("\n🎉 SUCCESS! APC orchestrated 3 financial agents seamlessly!")
            print("💡 This would require 200+ lines of custom code without APC!")
            
        else:
            print(f"❌ Workflow failed: {result}")
            print("🛡️ APC BENEFIT: Even failures are handled gracefully with detailed error info")
    
    except Exception as e:
        logger.error(f"Financial workflow execution failed: {e}")
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
    required_vars = ["GOOGLE_API_KEY"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"❌ Missing environment variables: {missing_vars}")
        print("📋 Setup instructions:")
        print("   1. Copy .env.example to .env")
        print("   2. Add your Google API key: GOOGLE_API_KEY=your_key_here")
        print("   3. Run the example again")
        exit(1)
    
    print("✅ Environment check passed")
    print("🚀 Starting APC Protocol financial analysis demonstration...")
    
    # Run the demonstration
    asyncio.run(demonstrate_apc_financial_analysis())
