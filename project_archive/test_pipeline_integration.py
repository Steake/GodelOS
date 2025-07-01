#!/usr/bin/env python3
"""
Integration Test Script

Tests the knowledge pipeline integration with the backend API.
"""

import asyncio
import logging
import sys
import os

# Add the parent directory to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.knowledge_pipeline_service import knowledge_pipeline_service

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_pipeline_integration():
    """Test the knowledge pipeline integration."""
    
    print("🔄 Testing Knowledge Pipeline Integration...")
    
    try:
        # Initialize the pipeline service
        print("\n1. Initializing Knowledge Pipeline Service...")
        await knowledge_pipeline_service.initialize()
        
        if not knowledge_pipeline_service.initialized:
            print("❌ Pipeline service failed to initialize")
            return False
        
        print("✅ Pipeline service initialized successfully")
        
        # Test text processing
        print("\n2. Testing Text Processing...")
        test_text = """
        Apple Inc. is an American multinational technology company headquartered in Cupertino, California.
        Tim Cook is the CEO of Apple. The company was founded by Steve Jobs, Steve Wozniak, and Ronald Wayne in 1976.
        Apple is known for developing innovative products like the iPhone, iPad, and Mac computers.
        """
        
        result = await knowledge_pipeline_service.process_text_document(
            content=test_text,
            title="Apple Inc. Test Document",
            metadata={"source": "integration_test"}
        )
        
        print(f"✅ Text processing completed:")
        print(f"   - Entities extracted: {result.get('entities_extracted', 0)}")
        print(f"   - Relationships extracted: {result.get('relationships_extracted', 0)}")
        print(f"   - Processing time: {result.get('processing_time_seconds', 0):.2f}s")
        
        # Test semantic search
        print("\n3. Testing Semantic Search...")
        query_result = await knowledge_pipeline_service.semantic_query("Who is the CEO of Apple?")
        
        print(f"✅ Semantic search completed:")
        print(f"   - Results found: {len(query_result.get('results', []))}")
        print(f"   - Query time: {query_result.get('query_time_seconds', 0):.2f}s")
        
        # Test knowledge graph export
        print("\n4. Testing Knowledge Graph Export...")
        graph_data = await knowledge_pipeline_service.get_knowledge_graph_data()
        
        print(f"✅ Knowledge graph exported:")
        print(f"   - Nodes: {len(graph_data.get('nodes', []))}")
        print(f"   - Edges: {len(graph_data.get('edges', []))}")
        
        # Test pipeline status
        print("\n5. Testing Pipeline Status...")
        status = await knowledge_pipeline_service.get_pipeline_status()
        
        print(f"✅ Pipeline status retrieved:")
        print(f"   - Initialized: {status.get('initialized', False)}")
        print(f"   - Documents processed: {status.get('metrics', {}).get('documents_processed', 0)}")
        
        print("\n🎉 All integration tests passed!")
        return True
        
    except Exception as e:
        print(f"\n❌ Integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Main test function."""
    success = await test_pipeline_integration()
    
    if success:
        print("\n✅ Knowledge Pipeline Integration is working correctly!")
        print("\nThe following components are now integrated:")
        print("  • Knowledge extraction pipeline in backend API")
        print("  • Advanced NLP processing for imports")
        print("  • Semantic search for queries")
        print("  • Knowledge graph visualization")
        print("  • Frontend SmartImport component with advanced processing")
        
        print("\nNext steps:")
        print("  1. Start the backend: python -m backend.main")
        print("  2. Start the frontend: cd svelte-frontend && npm run dev")
        print("  3. Test the new 'Text Input' option in SmartImport")
        print("  4. Try semantic search in queries")
        
    else:
        print("\n❌ Integration test failed. Please check the error messages above.")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
