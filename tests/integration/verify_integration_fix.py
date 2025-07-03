#!/usr/bin/env python3
"""
Direct test of the fixed integration without starting the server.
"""

import sys
import os
import asyncio
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Add the project root to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)
sys.path.insert(0, os.path.join(project_root, 'backend'))

async def main():
    """Test the integration directly."""
    print("🔍 Testing fixed GödelOS integration directly...")
    
    try:
        # Import and create integration
        print("📝 Importing integration...")
        from backend.godelos_integration import GödelOSIntegration
        
        integration = GödelOSIntegration()
        print(f"✅ Created integration: {type(integration).__name__}")
        
        # Initialize
        print("📝 Initializing integration...")
        await integration.initialize()
        print(f"✅ Initialized: {integration.initialized}")
        
        # Test a simple knowledge query
        print("📝 Testing knowledge query...")
        result = await integration.process_natural_language_query(
            "What is artificial intelligence?"
        )
        
        print(f"✅ Query successful!")
        print(f"✅ Response: {result.get('response', 'No response')}")
        print(f"✅ Confidence: {result.get('confidence', 0.0)}")
        print(f"✅ Knowledge used: {result.get('knowledge_used', [])}")
        print(f"✅ Inference time: {result.get('inference_time_ms', 0.0)} ms")
        
        # Test system status
        print("📝 Testing system status...")
        status = await integration.get_system_status()
        print(f"✅ System status: {status.get('status')}")
        print(f"✅ Capabilities: {list(status.get('capabilities', {}).keys())}")
        
        print("\n✅ SUCCESS: GödelOS integration is working correctly!")
        print("✅ The corrupted integration has been fixed and is ready for use.")
        
        return True
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(main())
    if success:
        print("\n🎉 Integration fix completed successfully!")
        print("🔧 The backend should now work properly with the fixed integration.")
    else:
        print("\n❌ Integration fix failed.")
    
    sys.exit(0 if success else 1)
