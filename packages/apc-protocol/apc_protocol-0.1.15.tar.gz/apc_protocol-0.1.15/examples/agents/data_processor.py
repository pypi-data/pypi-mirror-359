"""
Data Processing Agent Example
Demonstrates a specialized agent for data processing tasks.
"""
import asyncio
import json
import pandas as pd
from typing import Dict, Any, List
from apc import Worker
from apc.transport import GRPCTransport

class DataProcessorAgent:
    """
    Specialized agent for data processing operations.
    
    Capabilities:
    - CSV data processing
    - Data validation and cleaning
    - Statistical analysis
    - Format conversion
    """
    
    def __init__(self, worker_id: str = "data-processor-001"):
        self.worker = Worker(
            worker_id=worker_id,
            roles=["data-processor", "data-cleaner", "data-analyst"]
        )
        self.transport = GRPCTransport(port=50053)
        self.worker.bind_transport(self.transport)
        
        # Register handlers
        self._register_handlers()
    
    def _register_handlers(self):
        """Register all data processing handlers."""
        
        @self.worker.register_handler("load_csv")
        async def load_csv(params: Dict[str, Any]) -> Dict[str, Any]:
            """Load and validate CSV data."""
            file_path = params.get("file_path")
            if not file_path:
                raise ValueError("file_path parameter is required")
            
            try:
                df = pd.read_csv(file_path)
                return {
                    "status": "success",
                    "rows": len(df),
                    "columns": list(df.columns),
                    "sample": df.head().to_dict('records')
                }
            except Exception as e:
                raise RuntimeError(f"Failed to load CSV: {str(e)}")
        
        @self.worker.register_handler("clean_data")
        async def clean_data(params: Dict[str, Any]) -> Dict[str, Any]:
            """Clean and validate data."""
            data = params.get("data")
            if not data:
                raise ValueError("data parameter is required")
            
            # Simulate data cleaning
            await asyncio.sleep(0.5)
            
            cleaned_rows = len(data) if isinstance(data, list) else 1
            return {
                "status": "success",
                "cleaned_rows": cleaned_rows,
                "removed_duplicates": 5,
                "filled_nulls": 12
            }
        
        @self.worker.register_handler("analyze_data")
        async def analyze_data(params: Dict[str, Any]) -> Dict[str, Any]:
            """Perform statistical analysis on data."""
            data = params.get("data")
            columns = params.get("columns", [])
            
            # Simulate analysis
            await asyncio.sleep(1.0)
            
            return {
                "status": "success",
                "summary_stats": {
                    "mean": 42.5,
                    "median": 40.0,
                    "std_dev": 15.2
                },
                "correlations": {
                    "feature1_feature2": 0.85
                },
                "outliers_detected": 3
            }
        
        @self.worker.register_handler("export_data")
        async def export_data(params: Dict[str, Any]) -> Dict[str, Any]:
            """Export processed data to various formats."""
            format_type = params.get("format", "json").lower()
            output_path = params.get("output_path")
            
            # Simulate export
            await asyncio.sleep(0.3)
            
            return {
                "status": "success",
                "format": format_type,
                "output_path": output_path,
                "size_bytes": 1024 * 1024
            }
    
    async def start(self):
        """Start the data processor agent."""
        print("🔧 Starting Data Processor Agent...")
        await self.worker.start()
        await self.transport.start_server()
        print(f"✅ Data Processor Agent running on port 50053")
        print(f"📊 Available capabilities: {list(self.worker.roles)}")
    
    async def stop(self):
        """Stop the data processor agent."""
        await self.transport.stop_server()
        await self.worker.stop()
        print("🛑 Data Processor Agent stopped")

async def main():
    """Run the data processor agent."""
    agent = DataProcessorAgent()
    
    try:
        await agent.start()
        
        # Keep running
        print("💡 Agent is ready to receive tasks...")
        print("   Ctrl+C to stop")
        while True:
            await asyncio.sleep(1)
            
    except KeyboardInterrupt:
        print("\n⏹️  Shutting down...")
    finally:
        await agent.stop()

if __name__ == "__main__":
    asyncio.run(main())
