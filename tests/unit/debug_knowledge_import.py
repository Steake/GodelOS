#!/usr/bin/env python3
"""
Debug Knowledge Import Processing

This script will help us debug why the knowledge import processing is not working.
"""

import asyncio
import aiohttp
import json
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BASE_URL = "http://localhost:8000/api"

async def test_import_and_debug():
    """Test knowledge import and debug the processing."""
    
    async with aiohttp.ClientSession() as session:
        # Import some simple knowledge
        logger.info("Importing test knowledge...")
        
        payload = {
            "content": "Logic is the systematic study of the principles of valid inference and correct reasoning.",
            "title": "Logic Definition Debug Test",
            "category": "philosophy"
        }
        
        async with session.post(f"{BASE_URL}/knowledge/import/text", json=payload) as response:
            if response.status == 200:
                result = await response.json()
                import_id = result.get('import_id')
                logger.info(f"✅ Import queued: {import_id}")
                
                # Wait and check progress
                for i in range(10):
                    await asyncio.sleep(2)
                    
                    # Check progress
                    async with session.get(f"{BASE_URL}/knowledge/import/progress/{import_id}") as prog_response:
                        if prog_response.status == 200:
                            progress = await prog_response.json()
                            logger.info(f"Progress check {i+1}: {progress}")
                            
                            if progress.get('status') == 'completed':
                                logger.info("✅ Import completed!")
                                break
                            elif progress.get('status') == 'failed':
                                logger.error(f"❌ Import failed: {progress.get('error_message')}")
                                break
                        else:
                            logger.warning(f"Could not check progress: {prog_response.status}")
                
                # Test query after import
                logger.info("Testing query after import...")
                
                query_payload = {
                    "query": "What is logic?",
                    "include_reasoning": True
                }
                
                async with session.post(f"{BASE_URL}/query", json=query_payload) as query_response:
                    if query_response.status == 200:
                        query_result = await query_response.json()
                        logger.info(f"Query result: {query_result}")
                    else:
                        error_text = await query_response.text()
                        logger.error(f"Query failed: {query_response.status} - {error_text}")
                        
            else:
                error_text = await response.text()
                logger.error(f"Import failed: {response.status} - {error_text}")

if __name__ == "__main__":
    asyncio.run(test_import_and_debug())
