#!/usr/bin/env python3
"""
Enhanced Frontend Navigation Test - Debug UI Component Accessibility
"""

import requests
import json
import time
from pathlib import Path
import subprocess
import os

def test_component_accessibility():
    """Test each specific component's accessibility"""
    print("🧩 Testing individual component accessibility...")
    
    # Test navigation endpoint (if exists)
    test_endpoints = [
        "/api/health",
        "/api/transparency/statistics", 
        "/api/cognitive/state",
        "/api/knowledge/graph",
        "/api/import/status"
    ]
    
    backend_accessible = []
    backend_failed = []
    
    for endpoint in test_endpoints:
        try:
            response = requests.get(f"http://localhost:8000{endpoint}", timeout=3)
            if response.status_code == 200:
                backend_accessible.append(endpoint)
            else:
                backend_failed.append(f"{endpoint} ({response.status_code})")
        except Exception as e:
            backend_failed.append(f"{endpoint} (error: {str(e)[:50]})")
    
    print(f"✅ Backend accessible endpoints: {backend_accessible}")
    print(f"❌ Backend failed endpoints: {backend_failed}")
    
    return len(backend_accessible) > 0

def check_frontend_javascript_errors():
    """Use curl to check frontend and look for JavaScript errors in browser console"""
    print("\n🔍 Checking frontend JavaScript execution...")
    
    try:
        # Get frontend HTML
        response = requests.get("http://localhost:3001", timeout=5)
        html_content = response.text
        
        # Check for common error indicators
        error_indicators = [
            'script error',
            'uncaught',
            'undefined',
            'cannot read property',
            'is not a function'
        ]
        
        has_errors = any(indicator in html_content.lower() for indicator in error_indicators)
        
        print(f"📄 Frontend HTML length: {len(html_content)} chars")
        print(f"🚨 Error indicators found: {has_errors}")
        
        # Check if main.js is accessible
        try:
            js_response = requests.get("http://localhost:3001/src/main.js", timeout=3)
            print(f"📜 Main.js accessible: {js_response.status_code == 200}")
        except:
            print("📜 Main.js accessibility: Failed")
        
        return not has_errors
        
    except Exception as e:
        print(f"❌ Frontend check failed: {e}")
        return False

def test_navigation_items():
    """Test specific navigation functionality"""
    print("\n🧭 Testing navigation item accessibility...")
    
    # Create a simple test by checking if the navigation config is correct
    app_svelte_path = Path("/Users/oli/code/GödelOS.md/svelte-frontend/src/App.svelte")
    
    if not app_svelte_path.exists():
        print("❌ App.svelte file not found")
        return False
    
    content = app_svelte_path.read_text()
    
    # Check for navigation configuration
    nav_items = {
        'knowledge': 'Knowledge Graph',
        'import': 'Knowledge Import', 
        'transparency': 'Transparency',
        'reasoning': 'Reasoning Sessions',
        'provenance': 'Provenance'
    }
    
    found_items = {}
    for key, title in nav_items.items():
        if f"'{key}'" in content and title in content:
            found_items[key] = "✅ Found"
        else:
            found_items[key] = "❌ Missing"
    
    print("📋 Navigation items in App.svelte:")
    for key, status in found_items.items():
        print(f"   {key}: {status}")
    
    # Check for component imports
    components = [
        'KnowledgeGraph',
        'SmartImport', 
        'TransparencyDashboard',
        'ReasoningSessionViewer',
        'ProvenanceTracker'
    ]
    
    found_components = {}
    for comp in components:
        if f"import {comp}" in content or f"from './{comp}" in content:
            found_components[comp] = "✅ Imported"
        else:
            found_components[comp] = "❌ Not imported"
    
    print("\n🧩 Component imports in App.svelte:")
    for comp, status in found_components.items():
        print(f"   {comp}: {status}")
    
    return len([v for v in found_items.values() if "✅" in v]) >= 3

def check_component_files():
    """Enhanced component file check"""
    print("\n📁 Enhanced component file check...")
    
    frontend_path = Path("/Users/oli/code/GödelOS.md/svelte-frontend")
    
    critical_files = {
        "src/App.svelte": "Main application",
        "src/main.js": "Entry point",
        "src/components/knowledge/KnowledgeGraph.svelte": "Knowledge visualization",
        "src/components/knowledge/SmartImport.svelte": "Knowledge import",
        "src/components/transparency/TransparencyDashboard.svelte": "Transparency UI",
        "src/stores/cognitive.js": "State management"
    }
    
    all_exist = True
    for file_path, description in critical_files.items():
        full_path = frontend_path / file_path
        if full_path.exists():
            size = full_path.stat().st_size
            print(f"✅ {file_path} ({size} bytes) - {description}")
        else:
            print(f"❌ {file_path} - MISSING - {description}")
            all_exist = False
    
    return all_exist

def run_debug_test():
    """Run comprehensive debug test"""
    print("🦉 GödelOS Frontend Navigation Debug Test")
    print("=" * 60)
    
    # Test results
    results = {
        'files_ok': check_component_files(),
        'backend_ok': test_component_accessibility(),
        'frontend_ok': check_frontend_javascript_errors(),
        'navigation_ok': test_navigation_items()
    }
    
    print("\n" + "=" * 60)
    print("🔍 DEBUG RESULTS:")
    for test, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {test}: {status}")
    
    # Overall assessment
    if all(results.values()):
        print("\n🎉 All tests passed - Navigation should be accessible")
        print("💡 If you still can't see navigation, check browser console for JS errors")
    else:
        print("\n🚨 Some tests failed - Navigation accessibility issues detected")
        
        # Provide specific guidance
        if not results['files_ok']:
            print("   → Fix: Ensure all component files exist")
        if not results['backend_ok']:
            print("   → Fix: Start/restart the backend server")
        if not results['frontend_ok']:
            print("   → Fix: Check browser console for JavaScript errors")
        if not results['navigation_ok']:
            print("   → Fix: Verify navigation configuration in App.svelte")
    
    print(f"\n🔗 Frontend URL: http://localhost:3001")
    print(f"🔗 Backend URL: http://localhost:8000")
    
    return all(results.values())

if __name__ == "__main__":
    run_debug_test()
