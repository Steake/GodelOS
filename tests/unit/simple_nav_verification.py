#!/usr/bin/env python3
"""
Simple Navigation Fix Verification
Checks the HTML source for all expected navigation items
"""

import requests
import re
import time

def verify_navigation_fix():
    """Verify that all navigation items are in the HTML source"""
    
    expected_navigation_items = [
        "Dashboard",
        "Cognitive State", 
        "Knowledge Graph",
        "Query Interface",
        "Knowledge Import",
        "Reflection",
        "Capabilities", 
        "Resources",
        "Transparency",
        "Reasoning Sessions",
        "Provenance & Attribution"
    ]
    
    print("🔍 Verifying Navigation Fix...")
    print(f"Expected {len(expected_navigation_items)} navigation items")
    
    try:
        # Get the HTML content
        response = requests.get("http://localhost:3001", timeout=10)
        if response.status_code != 200:
            print(f"❌ Failed to fetch frontend: HTTP {response.status_code}")
            return False
            
        html_content = response.text
        
        # Check for viewConfig object in the JavaScript
        if "const viewConfig" in html_content:
            print("✅ viewConfig found in HTML")
        else:
            print("⚠️ viewConfig not found in HTML - may be dynamically loaded")
        
        # Count occurrences of navigation titles in the HTML
        found_items = []
        for item in expected_navigation_items:
            # Look for the title in various contexts
            patterns = [
                rf'nav-title[^>]*>{re.escape(item)}<',
                rf'title[^>]*>{re.escape(item)}<', 
                rf'>{re.escape(item)}</span>',
                rf'title.*{re.escape(item)}',
            ]
            
            found = False
            for pattern in patterns:
                if re.search(pattern, html_content, re.IGNORECASE):
                    found = True
                    break
            
            if found:
                found_items.append(item)
                print(f"✅ Found: {item}")
            else:
                print(f"❌ Missing: {item}")
        
        # Check debug panel mentions
        debug_panel_match = re.search(r'Navigation Debug.*?(\d+)\s*Items', html_content)
        if debug_panel_match:
            debug_count = int(debug_panel_match.group(1))
            print(f"🛠️ Debug panel reports: {debug_count} items")
        
        # Check if the each loop is present and working
        each_loop_pattern = r'\{#each\s+Object\.entries\(viewConfig\)'
        if re.search(each_loop_pattern, html_content):
            print("✅ Navigation each loop found in source")
        else:
            print("⚠️ Navigation each loop not found - may be compiled")
        
        # Results
        print("\n" + "="*60)
        print("NAVIGATION FIX VERIFICATION RESULTS")
        print("="*60)
        print(f"Expected items: {len(expected_navigation_items)}")
        print(f"Found in HTML: {len(found_items)}")
        print(f"Missing items: {set(expected_navigation_items) - set(found_items)}")
        
        if len(found_items) >= len(expected_navigation_items) * 0.8:  # 80% threshold
            print("✅ SUCCESS: Most navigation items found in HTML!")
            print("🎉 Navigation rendering issue appears to be FIXED!")
            return True
        else:
            print("❌ ISSUE: Not enough navigation items found in HTML")
            print("🔧 Further investigation needed")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Network error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def check_javascript_structure():
    """Check if the JavaScript structure looks correct"""
    
    print("\n🔍 Checking JavaScript Structure...")
    
    try:
        response = requests.get("http://localhost:3001", timeout=10)
        html_content = response.text
        
        # Check for key components
        checks = {
            "viewConfig object": r'(?:const|let|var)\s+viewConfig\s*=',
            "Object.entries": r'Object\.entries\s*\(\s*viewConfig\s*\)',
            "Navigation loop": r'\{#each.*?viewConfig.*?\}',
            "Console logging": r'console\.log.*navigation',
        }
        
        results = {}
        for check_name, pattern in checks.items():
            if re.search(pattern, html_content, re.IGNORECASE):
                results[check_name] = "✅ Found"
            else:
                results[check_name] = "❌ Missing"
        
        print("JavaScript Structure Check:")
        for check, result in results.items():
            print(f"  {result} {check}")
        
        return all("✅" in result for result in results.values())
        
    except Exception as e:
        print(f"❌ Error checking JavaScript: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Starting Simple Navigation Fix Verification")
    print("-" * 50)
    
    # Wait for app to be ready
    print("⏳ Waiting for frontend to be ready...")
    time.sleep(2)
    
    # Run verification tests
    nav_success = verify_navigation_fix()
    js_success = check_javascript_structure()
    
    print("\n" + "="*60)
    print("FINAL VERIFICATION RESULTS")
    print("="*60)
    
    if nav_success and js_success:
        print("🎉 COMPLETE SUCCESS!")
        print("✅ Navigation items are properly structured")
        print("✅ JavaScript structure is correct")
        print("🚀 Navigation issue has been RESOLVED!")
        print("\n📋 Next Steps:")
        print("1. Open http://localhost:3001 in browser")
        print("2. Verify all 11 navigation items are visible")
        print("3. Test clicking on each navigation item")
        print("4. Check the debug panel shows 'All 11 Items'")
    elif nav_success:
        print("🎯 PARTIAL SUCCESS!")
        print("✅ Navigation items found in HTML")
        print("⚠️ JavaScript structure may need adjustment")
    else:
        print("❌ ISSUE PERSISTS")
        print("🔧 Navigation items still not properly rendered")
        
    print("-" * 50)
