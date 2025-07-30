# Real-World APC Protocol Examples

This directory contains **clear, working examples** that demonstrate **why APC is essential** for multi-agent systems. Each example explicitly shows what problems APC solves and how it simplifies multi-agent orchestration.

## 🎯 **Why These Examples Matter**

❌ **WITHOUT APC:** Building multi-agent systems requires ~200+ lines of custom orchestration code, manual dependency management, custom protocols, and complex error handling.

✅ **WITH APC:** Just define workflow steps and dependencies - APC handles everything else automatically!

## 🚀 **Quick Start Examples**

## 📋 Available Demonstrations

| Demo | Description | API Required | Perfect For |
|------|-------------|--------------|-------------|
| `apc_simple_demo.py` | Data processing pipeline (simulated) | ❌ None | ⭐ Beginners - No setup needed! |
| `simple_azure_openai_demo.py` | Research → Analysis → Report | ✅ Azure OpenAI | 🔥 Most Popular - Real AI workflow |
| `anthropic_travel_planning_demo.py` | Travel planning workflow | ✅ Anthropic | ✈️ Claude AI demonstration |
| `gemini_financial_analysis_demo.py` | Financial analysis pipeline | ✅ Google Gemini | 📊 Gemini AI demonstration |
| `azureopenai_supply_chain_demo.py` | Supply chain management | ✅ Azure OpenAI | 🏭 Business process automation |

## � **Setup Instructions**

### Prerequisites
```bash
# Install APC and dependencies
pip install -r requirements.txt

# Copy environment template
cp .env.example .env
```

### Environment Variables
Add your API keys to `.env`:

```env
# Azure OpenAI (for Azure demos)
AZURE_OPENAI_API_KEY=your_azure_openai_api_key_here
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4
AZURE_OPENAI_API_VERSION=2024-02-15-preview

# Anthropic (for Claude demos)
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# Google (for Gemini demos)
GOOGLE_API_KEY=your_google_api_key_here
```

### Run Examples
```bash
# Start with the main demo (Azure OpenAI)
python simple_azure_openai_demo.py

# Try other providers
python anthropic_travel_planning_demo.py
python gemini_financial_analysis_demo.py
python azureopenai_supply_chain_demo.py
```

## 🎯 **What You'll See**

Each demo explicitly shows:

```
🎯 APC PROTOCOL VALUE DEMONSTRATION - PROBLEMS SOLVED!
❌ WITHOUT APC (traditional approach):
   💻 ~200+ lines of custom orchestration code needed
   🔧 Custom message passing between agents
   ⏰ Manual timeout and error handling
   🔄 Complex dependency tracking and execution order
   🔍 Service discovery and agent registration
   🛠️  Custom retry logic and failure recovery

✅ WITH APC (this example):
   ⚡ ~15 lines to define workflow steps and dependencies
   🤖 Automatic role-based routing and execution
   🛡️  Built-in timeout, error handling, and retries
   📋 Dependency management handled automatically
   🔍 Service discovery built into the protocol
   📡 Standardized gRPC communication
   ✨ Just focus on your agent logic - APC handles the rest!
```

## 🏗️ **Architecture Pattern**

All examples follow the same proven pattern:

```
Agent 1 (Role A) → Agent 2 (Role B) → Agent 3 (Role C)
       ↓                ↓                ↓
    [Step 1]         [Step 2]         [Step 3]
       ↓                ↓                ↓
  Dependencies:     Depends on:      Depends on:
     None            Step 1           Step 2
```

**APC automatically handles:**
- ✅ Role-based routing (right agent gets right task)
- ✅ Dependency management (steps run in correct order)
- ✅ Data flow (results pass between agents seamlessly)
- ✅ Error handling (failures managed gracefully)
- ✅ Communication (standardized gRPC protocol)

## � **Expected Output**

Each demo shows clear step-by-step execution:

```
🚀 APC PROTOCOL DEMONSTRATION: Multi-Agent Workflow
🔍 STEP 1: RESEARCH AGENT EXECUTING
🎯 APC BENEFIT: Role-based routing sent this to 'researcher'
📊 STEP 2: ANALYSIS AGENT EXECUTING  
🎯 APC BENEFIT: Dependency management - only runs AFTER research
� STEP 3: REPORT AGENT EXECUTING
🎯 APC BENEFIT: Final step - waits for ALL dependencies
🎉 SUCCESS! APC orchestrated 3 agents seamlessly!
```

## � **Customization**

Each demo is designed for easy modification:

1. **Change Topics:** Modify the research topics or business scenarios
2. **Add Agents:** Extend workflows with additional specialized agents  
3. **Switch Providers:** Swap between Azure OpenAI, Anthropic, or Gemini
4. **Custom Logic:** Add your own business logic to agent handlers
5. **Scale Up:** Run agents on separate machines using APC's distributed nature

## 🎯 **Next Steps**

After running these demos:

1. **Understand the Value:** See how APC eliminates orchestration complexity
2. **Build Your Own:** Use these patterns for your specific use cases
3. **Production Ready:** Add persistence, monitoring, and scaling
4. **Contribute:** Share your agent implementations with the community

---

**💡 Pro Tip:** Start with `simple_azure_openai_demo.py` - it's the clearest demonstration of APC's value and easiest to understand!
