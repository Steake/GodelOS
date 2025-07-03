#!/usr/bin/env python3
"""
Debug script to test backend processing directly
"""

import asyncio
import aiohttp
import json

async def debug_backend():
    """Test backend and check for debug logs."""
    
    api_base = "http://localhost:8000"
    
    print("🔧 Debug Backend Processing")
    print("=" * 30)
    
    try:
        async with aiohttp.ClientSession() as session:
            # Test Wikipedia import
            print("1. Submitting Wikipedia import...")
            
            wikipedia_data = {
                "source": {
                    "source_type": "wikipedia",
                    "source_identifier": "Test Article",
                    "metadata": {"source": "debug_test"}
                },
                "page_title": "Test Article",
                "language": "en",
                "include_references": True,
                "section_filter": []
            }
            
            async with session.post(f"{api_base}/api/knowledge/import/wikipedia", 
                                  json=wikipedia_data) as response:
                result = await response.json()
                
                print(f"Response Status: {response.status}")
                print(f"Response Body: {json.dumps(result, indent=2)}")
                
                if response.status == 200:
                    import_id = result.get('import_id')
                    print(f"✅ Import started with ID: {import_id}")
                    
                    # Wait and check status
                    print("2. Waiting 10 seconds for processing...")
                    await asyncio.sleep(10)
                    
                    # Check import status
                    print("3. Checking import status...")
                    async with session.get(f"{api_base}/api/knowledge/import/{import_id}") as status_response:
                        if status_response.status == 200:
                            status_result = await status_response.json()
                            print(f"Import Status: {json.dumps(status_result, indent=2)}")
                        else:
                            print(f"Failed to get status: {status_response.status}")
                    
                else:
                    print(f"❌ Import failed: {result}")
                    
        print("\n" + "=" * 50)
        print("💡 Check backend logs for debug messages starting with '🔍 DEBUG:'")
        print("   Look for messages about:")
        print("   - websocket_manager exists")
        print("   - has_connections")
        print("   - Broadcasting progress event")
        print("   - Exception details if any")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(debug_backend())