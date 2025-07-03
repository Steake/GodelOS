#!/usr/bin/env python3
"""
Comprehensive End-to-End Test Suite for GödelOS Backend API

This test suite maps all backend API endpoints and identifies gaps between
backend capabilities and frontend implementation.
"""

import asyncio
import json
import logging
import time
from dataclasses import dataclass
from typing import Dict, List, Optional, Any, Set
import requests
import websockets
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class EndpointTest:
    """Test case for a backend endpoint"""
    endpoint: str
    method: str
    description: str
    expected_status: int = 200
    payload: Optional[Dict] = None
    requires_auth: bool = False
    category: str = "general"
    frontend_component: Optional[str] = None
    implemented_in_frontend: bool = False

@dataclass
class TestResult:
    """Result of an endpoint test"""
    endpoint: str
    method: str
    status_code: int
    success: bool
    response_data: Optional[Dict] = None
    error_message: Optional[str] = None
    response_time: float = 0.0

@dataclass
class GapAnalysis:
    """Analysis of gaps between backend and frontend"""
    missing_frontend_components: List[str]
    unused_backend_endpoints: List[str]
    frontend_components_without_backend: List[str]
    recommendations: List[str]

class GödelOSE2ETester:
    """Comprehensive end-to-end tester for GödelOS system"""
    
    def __init__(self, backend_url: str = "http://localhost:8000", frontend_url: str = "http://localhost:3001"):
        self.backend_url = backend_url
        self.frontend_url = frontend_url
        self.test_results: List[TestResult] = []
        
    def define_test_endpoints(self) -> List[EndpointTest]:
        """Define all backend endpoints to test"""
        return [
            # Core API Endpoints
            EndpointTest("/", "GET", "Root endpoint", frontend_component="App.svelte", implemented_in_frontend=True),
            EndpointTest("/health", "GET", "Health check", frontend_component="App.svelte", implemented_in_frontend=True),
            EndpointTest("/api/health", "GET", "API health check", frontend_component="App.svelte", implemented_in_frontend=True),
            
            # Query Processing
            EndpointTest("/api/query", "POST", "Natural language query processing", 
                        payload={"query": "What is consciousness?", "include_reasoning": True}, 
                        frontend_component="QueryInterface.svelte", implemented_in_frontend=True, category="query"),
            EndpointTest("/api/simple-test", "GET", "Simple test endpoint", category="testing"),
            
            # Knowledge Management - Basic
            EndpointTest("/api/knowledge", "GET", "Get knowledge base", 
                        frontend_component="KnowledgeGraph.svelte", implemented_in_frontend=True, category="knowledge"),
            EndpointTest("/api/knowledge", "POST", "Add knowledge", 
                        payload={"concept": "test_concept", "definition": "test definition", "category": "test"}, 
                        frontend_component="SmartImport.svelte", implemented_in_frontend=True, category="knowledge"),
            EndpointTest("/api/knowledge/{item_id}", "GET", "Get specific knowledge item", 
                        frontend_component="KnowledgeGraph.svelte", implemented_in_frontend=False, category="knowledge"),
            
            # Knowledge Management - Advanced
            EndpointTest("/api/knowledge/graph", "GET", "Get knowledge graph", 
                        frontend_component="KnowledgeGraph.svelte", implemented_in_frontend=True, category="knowledge"),
            EndpointTest("/api/knowledge/evolution", "GET", "Get knowledge evolution", 
                        frontend_component="ConceptEvolution.svelte", implemented_in_frontend=True, category="knowledge"),
            EndpointTest("/api/knowledge/search", "GET", "Search knowledge base", 
                        frontend_component="KnowledgeGraph.svelte", implemented_in_frontend=False, category="knowledge"),
            
            # Knowledge Import Endpoints
            EndpointTest("/api/knowledge/import/url", "POST", "Import from URL", 
                        payload={"url": "https://example.com", "category": "web"}, 
                        frontend_component="SmartImport.svelte", implemented_in_frontend=True, category="import"),
            EndpointTest("/api/knowledge/import/wikipedia", "POST", "Import from Wikipedia", 
                        payload={"topic": "artificial intelligence", "category": "encyclopedia"}, 
                        frontend_component="SmartImport.svelte", implemented_in_frontend=True, category="import"),
            EndpointTest("/api/knowledge/import/text", "POST", "Import text content", 
                        payload={"content": "Sample text content", "title": "Test Document", "category": "document"}, 
                        frontend_component="SmartImport.svelte", implemented_in_frontend=True, category="import"),
            EndpointTest("/api/knowledge/import/batch", "POST", "Batch import", 
                        payload={"sources": [{"type": "text", "content": "Test content"}]}, 
                        frontend_component="SmartImport.svelte", implemented_in_frontend=False, category="import"),
            EndpointTest("/api/knowledge/import/progress/{import_id}", "GET", "Get import progress", 
                        frontend_component="SmartImport.svelte", implemented_in_frontend=False, category="import"),
            EndpointTest("/api/knowledge/import/{import_id}", "DELETE", "Cancel import", 
                        frontend_component="SmartImport.svelte", implemented_in_frontend=False, category="import"),
            
            # Cognitive State
            EndpointTest("/api/cognitive-state", "GET", "Get cognitive state", 
                        frontend_component="CognitiveStateMonitor.svelte", implemented_in_frontend=True, category="cognitive"),
            
            # Cognitive Transparency API - Configuration
            EndpointTest("/api/transparency/configure", "POST", "Configure transparency", 
                        payload={"transparency_level": "detailed", "session_specific": False}, 
                        frontend_component="ProcessInsight.svelte", implemented_in_frontend=False, category="transparency"),
            
            # Cognitive Transparency API - Reasoning Sessions
            EndpointTest("/api/transparency/session/start", "POST", "Start reasoning session", 
                        payload={"query": "Test reasoning", "transparency_level": "detailed"}, 
                        frontend_component="ReflectionVisualization.svelte", implemented_in_frontend=False, category="transparency"),
            EndpointTest("/api/transparency/session/{session_id}/complete", "POST", "Complete reasoning session", 
                        frontend_component="ReflectionVisualization.svelte", implemented_in_frontend=False, category="transparency"),
            EndpointTest("/api/transparency/session/{session_id}/trace", "GET", "Get reasoning trace", 
                        frontend_component="ReflectionVisualization.svelte", implemented_in_frontend=False, category="transparency"),
            EndpointTest("/api/transparency/sessions/active", "GET", "Get active sessions", 
                        frontend_component="ProcessInsight.svelte", implemented_in_frontend=False, category="transparency"),
            EndpointTest("/api/transparency/statistics", "GET", "Get transparency statistics", 
                        frontend_component="ResourceAllocation.svelte", implemented_in_frontend=False, category="transparency"),
            EndpointTest("/api/transparency/session/{session_id}/statistics", "GET", "Get session statistics", 
                        frontend_component="ResourceAllocation.svelte", implemented_in_frontend=False, category="transparency"),
            
            # Cognitive Transparency API - Knowledge Graph
            EndpointTest("/api/transparency/knowledge-graph/node", "POST", "Add knowledge graph node", 
                        payload={"concept": "test_node", "node_type": "concept"}, 
                        frontend_component="KnowledgeGraph.svelte", implemented_in_frontend=False, category="transparency"),
            EndpointTest("/api/transparency/knowledge-graph/relationship", "POST", "Add knowledge graph relationship", 
                        payload={"source": "node1", "target": "node2", "relationship_type": "related_to"}, 
                        frontend_component="KnowledgeGraph.svelte", implemented_in_frontend=False, category="transparency"),
            EndpointTest("/api/transparency/knowledge-graph/export", "GET", "Export knowledge graph", 
                        frontend_component="KnowledgeGraph.svelte", implemented_in_frontend=False, category="transparency"),
            EndpointTest("/api/transparency/knowledge-graph/statistics", "GET", "Get knowledge graph statistics", 
                        frontend_component="KnowledgeGraph.svelte", implemented_in_frontend=False, category="transparency"),
            EndpointTest("/api/transparency/knowledge-graph/discover/{concept}", "GET", "Discover knowledge concepts", 
                        frontend_component="KnowledgeGraph.svelte", implemented_in_frontend=False, category="transparency"),
            EndpointTest("/api/transparency/knowledge/categories", "GET", "Get knowledge categories", 
                        frontend_component="KnowledgeGraph.svelte", implemented_in_frontend=False, category="transparency"),
            EndpointTest("/api/transparency/knowledge/statistics", "GET", "Get knowledge statistics", 
                        frontend_component="KnowledgeGraph.svelte", implemented_in_frontend=False, category="transparency"),
            
            # Cognitive Transparency API - Provenance
            EndpointTest("/api/transparency/provenance/query", "POST", "Query provenance", 
                        payload={"query_type": "attribution", "target_id": "test_target"}, 
                        frontend_component=None, implemented_in_frontend=False, category="transparency"),
            EndpointTest("/api/transparency/provenance/attribution/{target_id}", "GET", "Get attribution", 
                        frontend_component=None, implemented_in_frontend=False, category="transparency"),
            EndpointTest("/api/transparency/provenance/confidence-history/{target_id}", "GET", "Get confidence history", 
                        frontend_component=None, implemented_in_frontend=False, category="transparency"),
            EndpointTest("/api/transparency/provenance/statistics", "GET", "Get provenance statistics", 
                        frontend_component=None, implemented_in_frontend=False, category="transparency"),
            EndpointTest("/api/transparency/provenance/snapshot", "POST", "Create provenance snapshot", 
                        payload={"description": "Test snapshot"}, 
                        frontend_component=None, implemented_in_frontend=False, category="transparency"),
            EndpointTest("/api/transparency/provenance/rollback/{snapshot_id}", "GET", "Rollback to snapshot", 
                        frontend_component=None, implemented_in_frontend=False, category="transparency"),
        ]
    
    async def test_endpoint(self, test: EndpointTest) -> TestResult:
        """Test a single endpoint"""
        start_time = time.time()
        
        try:
            # Handle parameterized endpoints
            endpoint = test.endpoint
            if "{item_id}" in endpoint:
                endpoint = endpoint.replace("{item_id}", "test_item")
            if "{session_id}" in endpoint:
                endpoint = endpoint.replace("{session_id}", "test_session")
            if "{import_id}" in endpoint:
                endpoint = endpoint.replace("{import_id}", "test_import")
            if "{target_id}" in endpoint:
                endpoint = endpoint.replace("{target_id}", "test_target")
            if "{concept}" in endpoint:
                endpoint = endpoint.replace("{concept}", "consciousness")
            if "{snapshot_id}" in endpoint:
                endpoint = endpoint.replace("{snapshot_id}", "test_snapshot")
            
            url = f"{self.backend_url}{endpoint}"
            
            # Make HTTP request
            if test.method == "GET":
                response = requests.get(url, timeout=10)
            elif test.method == "POST":
                response = requests.post(url, json=test.payload, timeout=10)
            elif test.method == "PUT":
                response = requests.put(url, json=test.payload, timeout=10)
            elif test.method == "DELETE":
                response = requests.delete(url, timeout=10)
            else:
                raise ValueError(f"Unsupported method: {test.method}")
            
            response_time = time.time() - start_time
            
            # Parse response
            try:
                response_data = response.json()
            except:
                response_data = {"raw_response": response.text}
            
            success = (200 <= response.status_code < 300) or response.status_code == test.expected_status
            
            return TestResult(
                endpoint=test.endpoint,
                method=test.method,
                status_code=response.status_code,
                success=success,
                response_data=response_data,
                response_time=response_time
            )
            
        except Exception as e:
            response_time = time.time() - start_time
            return TestResult(
                endpoint=test.endpoint,
                method=test.method,
                status_code=0,
                success=False,
                error_message=str(e),
                response_time=response_time
            )
    
    async def test_websocket_endpoints(self) -> List[TestResult]:
        """Test WebSocket endpoints"""
        websocket_results = []
        
        # Test cognitive stream WebSocket
        try:
            uri = f"ws://localhost:8000/ws/cognitive-stream"
            async with websockets.connect(uri) as websocket:
                # Send a test message
                await websocket.send(json.dumps({"type": "subscribe", "events": ["cognitive_state"]}))
                
                # Wait for response
                response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                response_data = json.loads(response)
                
                websocket_results.append(TestResult(
                    endpoint="/ws/cognitive-stream",
                    method="WebSocket",
                    status_code=200,
                    success=True,
                    response_data=response_data
                ))
                
        except Exception as e:
            websocket_results.append(TestResult(
                endpoint="/ws/cognitive-stream",
                method="WebSocket",
                status_code=0,
                success=False,
                error_message=str(e)
            ))
        
        return websocket_results
    
    async def run_comprehensive_tests(self) -> Dict[str, Any]:
        """Run all tests and generate comprehensive report"""
        logger.info("🚀 Starting comprehensive end-to-end tests...")
        
        test_endpoints = self.define_test_endpoints()
        results = []
        
        # Test HTTP endpoints
        for test in test_endpoints:
            logger.info(f"Testing {test.method} {test.endpoint}: {test.description}")
            result = await self.test_endpoint(test)
            results.append(result)
            
            if result.success:
                logger.info(f"✅ {test.endpoint} - {result.status_code} ({result.response_time:.2f}s)")
            else:
                logger.warning(f"❌ {test.endpoint} - {result.status_code} - {result.error_message}")
        
        # Test WebSocket endpoints
        logger.info("Testing WebSocket endpoints...")
        websocket_results = await self.test_websocket_endpoints()
        results.extend(websocket_results)
        
        self.test_results = results
        
        # Generate analysis
        analysis = self.analyze_gaps(test_endpoints)
        
        return {
            "test_results": results,
            "gap_analysis": analysis,
            "summary": self.generate_summary(results, test_endpoints)
        }
    
    def analyze_gaps(self, test_endpoints: List[EndpointTest]) -> GapAnalysis:
        """Analyze gaps between backend and frontend"""
        
        # Frontend components that exist
        existing_frontend_components = {
            "App.svelte", "QueryInterface.svelte", "CognitiveStateMonitor.svelte",
            "ResponseDisplay.svelte", "KnowledgeGraph.svelte", "ConceptEvolution.svelte",
            "SmartImport.svelte", "ReflectionVisualization.svelte", "ResourceAllocation.svelte",
            "ProcessInsight.svelte", "CapabilityDashboard.svelte", "ArchitectureTimeline.svelte",
            "Modal.svelte", "EnhancedDashboard.svelte"
        }
        
        # Backend endpoints that work
        working_endpoints = [r.endpoint for r in self.test_results if r.success]
        
        # Backend endpoints that don't work
        failing_endpoints = [r.endpoint for r in self.test_results if not r.success]
        
        # Find missing frontend components
        missing_components = []
        unused_endpoints = []
        
        for test in test_endpoints:
            # Find corresponding result for this test
            test_result = None
            for result in self.test_results:
                if result.endpoint == test.endpoint and result.method == test.method:
                    test_result = result
                    break
            
            if test_result and test_result.success and not test.implemented_in_frontend:
                if test.frontend_component:
                    if test.frontend_component not in existing_frontend_components:
                        missing_components.append(f"{test.frontend_component} for {test.endpoint}")
                else:
                    unused_endpoints.append(f"{test.method} {test.endpoint} - {test.description}")
        
        # Generate recommendations
        recommendations = []
        
        # Group by category for better analysis
        categories = {}
        for test in test_endpoints:
            if test.category not in categories:
                categories[test.category] = []
            categories[test.category].append(test)
        
        # Transparency category analysis
        transparency_tests = categories.get("transparency", [])
        transparency_implemented = sum(1 for t in transparency_tests if t.implemented_in_frontend)
        if transparency_implemented < len(transparency_tests) * 0.5:
            recommendations.append("Implement comprehensive cognitive transparency UI components")
        
        # Import category analysis
        import_tests = categories.get("import", [])
        import_implemented = sum(1 for t in import_tests if t.implemented_in_frontend)
        if import_implemented < len(import_tests) * 0.7:
            recommendations.append("Enhance knowledge import interface with progress tracking and batch operations")
        
        # Knowledge category analysis
        knowledge_tests = categories.get("knowledge", [])
        knowledge_implemented = sum(1 for t in knowledge_tests if t.implemented_in_frontend)
        if knowledge_implemented < len(knowledge_tests) * 0.8:
            recommendations.append("Add knowledge search and detailed item views to the knowledge graph")
        
        return GapAnalysis(
            missing_frontend_components=missing_components,
            unused_backend_endpoints=unused_endpoints,
            frontend_components_without_backend=[],  # Would need frontend analysis for this
            recommendations=recommendations
        )
    
    def generate_summary(self, results: List[TestResult], test_endpoints: List[EndpointTest]) -> Dict[str, Any]:
        """Generate test summary statistics"""
        total_tests = len(results)
        successful_tests = sum(1 for r in results if r.success)
        failed_tests = total_tests - successful_tests
        
        # Category breakdown
        categories = {}
        for test in test_endpoints:
            if test.category not in categories:
                categories[test.category] = {"total": 0, "success": 0, "implemented": 0}
            categories[test.category]["total"] += 1
            if test.implemented_in_frontend:
                categories[test.category]["implemented"] += 1
        
        for result in results:
            for test in test_endpoints:
                if test.endpoint == result.endpoint and test.method == result.method:
                    if result.success:
                        categories[test.category]["success"] += 1
                    break
        
        # Frontend implementation coverage
        total_endpoints = len(test_endpoints)
        implemented_endpoints = sum(1 for t in test_endpoints if t.implemented_in_frontend)
        coverage_percentage = (implemented_endpoints / total_endpoints) * 100
        
        return {
            "total_tests": total_tests,
            "successful_tests": successful_tests,
            "failed_tests": failed_tests,
            "success_rate": (successful_tests / total_tests) * 100,
            "frontend_coverage": coverage_percentage,
            "category_breakdown": categories,
            "average_response_time": sum(r.response_time for r in results if r.response_time) / len([r for r in results if r.response_time])
        }
    
    def generate_detailed_report(self, report_data: Dict[str, Any]) -> str:
        """Generate a detailed markdown report"""
        
        summary = report_data["summary"]
        gap_analysis = report_data["gap_analysis"]
        results = report_data["test_results"]
        
        report = f"""# GödelOS Backend-Frontend Gap Analysis Report
Generated on: {time.strftime('%Y-%m-%d %H:%M:%S')}

## Executive Summary

- **Total Endpoints Tested**: {summary['total_tests']}
- **Success Rate**: {summary['success_rate']:.1f}%
- **Frontend Implementation Coverage**: {summary['frontend_coverage']:.1f}%
- **Average Response Time**: {summary['average_response_time']:.3f}s

## Test Results by Category

"""
        
        for category, stats in summary["category_breakdown"].items():
            success_rate = (stats["success"] / stats["total"]) * 100 if stats["total"] > 0 else 0
            impl_rate = (stats["implemented"] / stats["total"]) * 100 if stats["total"] > 0 else 0
            
            report += f"""### {category.title()} Category
- **Endpoints**: {stats['total']}
- **Success Rate**: {success_rate:.1f}%
- **Frontend Implementation**: {impl_rate:.1f}%

"""
        
        report += """## Gap Analysis

### Missing Frontend Components
"""
        
        if gap_analysis.missing_frontend_components:
            for component in gap_analysis.missing_frontend_components:
                report += f"- {component}\n"
        else:
            report += "- No missing components identified\n"
        
        report += """
### Unused Backend Endpoints
"""
        
        if gap_analysis.unused_backend_endpoints:
            for endpoint in gap_analysis.unused_backend_endpoints:
                report += f"- {endpoint}\n"
        else:
            report += "- All endpoints have frontend implementations\n"
        
        report += """
### Recommendations
"""
        
        for recommendation in gap_analysis.recommendations:
            report += f"- {recommendation}\n"
        
        report += """
## Detailed Test Results

| Endpoint | Method | Status | Success | Response Time | Frontend Component | Implemented |
|----------|--------|--------|---------|---------------|-------------------|-------------|
"""
        
        # Find test endpoint info for each result
        test_lookup = {}
        for test in self.define_test_endpoints():
            test_lookup[f"{test.method}:{test.endpoint}"] = test
        
        for result in results:
            test_key = f"{result.method}:{result.endpoint}"
            test_info = test_lookup.get(test_key, None)
            
            component = test_info.frontend_component if test_info else "Unknown"
            implemented = "✅" if test_info and test_info.implemented_in_frontend else "❌"
            success_icon = "✅" if result.success else "❌"
            
            report += f"| {result.endpoint} | {result.method} | {result.status_code} | {success_icon} | {result.response_time:.3f}s | {component or 'None'} | {implemented} |\n"
        
        report += """
## Implementation Priority Matrix

### High Priority (Core Functionality Gaps)
"""
        
        high_priority = [
            "Knowledge search interface",
            "Import progress tracking",
            "Detailed knowledge item views",
            "Transparency session management"
        ]
        
        for item in high_priority:
            report += f"- {item}\n"
        
        report += """
### Medium Priority (Enhanced Features)
"""
        
        medium_priority = [
            "Batch import operations",
            "Provenance tracking UI",
            "Advanced knowledge graph statistics",
            "Session-based transparency controls"
        ]
        
        for item in medium_priority:
            report += f"- {item}\n"
        
        report += """
### Low Priority (Future Enhancements)
"""
        
        low_priority = [
            "Knowledge graph export functionality",
            "Advanced provenance queries",
            "Snapshot management",
            "Real-time confidence tracking"
        ]
        
        for item in low_priority:
            report += f"- {item}\n"
        
        return report

async def main():
    """Main test execution"""
    logger.info("🎯 GödelOS Comprehensive End-to-End Testing")
    
    tester = GödelOSE2ETester()
    
    # Check if backend is running
    try:
        response = requests.get(f"{tester.backend_url}/health", timeout=5)
        if response.status_code != 200:
            logger.error("❌ Backend not responding properly")
            return
    except Exception as e:
        logger.error(f"❌ Backend not accessible: {e}")
        return
    
    # Run comprehensive tests
    report_data = await tester.run_comprehensive_tests()
    
    # Generate and save report
    report_content = tester.generate_detailed_report(report_data)
    
    report_path = Path("backend_frontend_gap_analysis.md")
    with open(report_path, "w") as f:
        f.write(report_content)
    
    logger.info(f"📊 Report saved to: {report_path}")
    
    # Print summary
    summary = report_data["summary"]
    print(f"\n🎯 TEST SUMMARY")
    print(f"Success Rate: {summary['success_rate']:.1f}%")
    print(f"Frontend Coverage: {summary['frontend_coverage']:.1f}%")
    print(f"Total Tests: {summary['total_tests']}")
    print(f"Failed Tests: {summary['failed_tests']}")
    
    if summary['failed_tests'] > 0:
        print(f"\n❌ FAILING ENDPOINTS:")
        for result in report_data["test_results"]:
            if not result.success:
                print(f"  - {result.method} {result.endpoint}: {result.error_message or f'Status {result.status_code}'}")
    
    # Save raw results as JSON for further analysis
    json_path = Path("test_results.json")
    with open(json_path, "w") as f:
        # Convert results to serializable format
        serializable_results = []
        for result in report_data["test_results"]:
            serializable_results.append({
                "endpoint": result.endpoint,
                "method": result.method,
                "status_code": result.status_code,
                "success": result.success,
                "response_data": result.response_data,
                "error_message": result.error_message,
                "response_time": result.response_time
            })
        
        json.dump({
            "summary": summary,
            "results": serializable_results,
            "timestamp": time.time()
        }, f, indent=2)
    
    logger.info(f"📊 Raw results saved to: {json_path}")

if __name__ == "__main__":
    asyncio.run(main())
