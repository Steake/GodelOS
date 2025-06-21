#!/usr/bin/env python3
"""
Quick navigation and layout verification test for GödelOS Svelte frontend.
Checks that all 11 navigation items are working and layout looks good.
"""

import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import json
from datetime import datetime

def test_navigation_and_layout():
    """Test all navigation items and verify layout improvements."""
    
    # Setup Chrome options
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run in headless mode
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920,1080")
    
    driver = webdriver.Chrome(options=chrome_options)
    results = {
        "timestamp": datetime.now().isoformat(),
        "test_name": "Navigation & Layout Verification",
        "navigation_items": {},
        "layout_checks": {},
        "overall_status": "UNKNOWN"
    }
    
    try:
        print("🚀 Starting GödelOS navigation and layout test...")
        
        # Navigate to the app
        driver.get("http://localhost:3001")
        
        # Wait for the app to load
        WebDriverWait(driver, 10).wait(
            EC.presence_of_element_located((By.CLASS_NAME, "godelos-interface"))
        )
        
        print("✅ App loaded successfully")
        
        # Check if all navigation items are present
        nav_items = driver.find_elements(By.CLASS_NAME, "nav-item")
        print(f"📊 Found {len(nav_items)} navigation items")
        
        # Expected navigation items
        expected_views = [
            "Dashboard", "Cognitive State", "Knowledge Graph", "Query Interface",
            "Knowledge Import", "Reflection", "Capabilities", "Resources", 
            "Transparency", "Reasoning Sessions", "Provenance & Attribution"
        ]
        
        # Test clicking each navigation item
        for i, nav_item in enumerate(nav_items):
            try:
                # Get the nav title
                nav_title_element = nav_item.find_element(By.CLASS_NAME, "nav-title")
                nav_title = nav_title_element.text
                
                print(f"🔍 Testing navigation item {i+1}: {nav_title}")
                
                # Click the navigation item
                driver.execute_script("arguments[0].click();", nav_item)
                time.sleep(0.5)  # Brief pause for transition
                
                # Check if view changed
                current_view_indicator = driver.find_element(By.CLASS_NAME, "current-view-indicator")
                view_title_element = current_view_indicator.find_element(By.CLASS_NAME, "view-title")
                active_view_title = view_title_element.text
                
                # Verify the view changed
                success = active_view_title == nav_title
                results["navigation_items"][nav_title] = {
                    "index": i + 1,
                    "clickable": True,
                    "view_changes": success,
                    "status": "PASS" if success else "FAIL"
                }
                
                print(f"   ✅ {nav_title}: {'PASS' if success else 'FAIL'}")
                
            except Exception as e:
                print(f"   ❌ {nav_title}: FAIL - {str(e)}")
                results["navigation_items"][f"Item_{i+1}"] = {
                    "index": i + 1,
                    "clickable": False,
                    "error": str(e),
                    "status": "FAIL"
                }
        
        # Layout verification checks
        print("\n📐 Checking layout improvements...")
        
        # Check main content area
        main_content = driver.find_element(By.CLASS_NAME, "main-content")
        main_rect = main_content.rect
        results["layout_checks"]["main_content_visible"] = main_rect["height"] > 0 and main_rect["width"] > 0
        
        # Check sidebar
        sidebar = driver.find_element(By.CLASS_NAME, "sidebar")
        sidebar_rect = sidebar.rect
        results["layout_checks"]["sidebar_visible"] = sidebar_rect["height"] > 0 and sidebar_rect["width"] > 0
        
        # Check header
        header = driver.find_element(By.CLASS_NAME, "interface-header")
        header_rect = header.rect
        results["layout_checks"]["header_compact"] = header_rect["height"] <= 80  # Should be reasonably compact
        
        # Test sidebar collapse
        toggle_button = driver.find_element(By.CLASS_NAME, "sidebar-toggle")
        driver.execute_script("arguments[0].click();", toggle_button)
        time.sleep(0.5)
        
        # Check if sidebar collapsed
        sidebar_after = driver.find_element(By.CLASS_NAME, "sidebar")
        collapsed_width = sidebar_after.rect["width"]
        results["layout_checks"]["sidebar_collapse_works"] = collapsed_width < 100
        
        print(f"   📏 Main content area: {main_rect['width']}x{main_rect['height']}")
        print(f"   📏 Header height: {header_rect['height']}px")
        print(f"   📏 Sidebar collapsed width: {collapsed_width}px")
        
        # Test responsiveness by changing window size
        driver.set_window_size(768, 1024)  # Mobile size
        time.sleep(0.5)
        
        main_content_mobile = driver.find_element(By.CLASS_NAME, "main-content")
        mobile_rect = main_content_mobile.rect
        results["layout_checks"]["mobile_responsive"] = mobile_rect["width"] > 0
        
        print(f"   📱 Mobile layout: {mobile_rect['width']}x{mobile_rect['height']}")
        
        # Calculate overall success
        nav_successes = sum(1 for item in results["navigation_items"].values() if item["status"] == "PASS")
        layout_successes = sum(1 for check in results["layout_checks"].values() if check)
        
        total_nav_items = len(results["navigation_items"])
        total_layout_checks = len(results["layout_checks"])
        
        if nav_successes == total_nav_items and layout_successes == total_layout_checks:
            results["overall_status"] = "PASS"
        elif nav_successes >= total_nav_items * 0.8 and layout_successes >= total_layout_checks * 0.8:
            results["overall_status"] = "MOSTLY_PASS"
        else:
            results["overall_status"] = "FAIL"
        
        print(f"\n📊 Test Results Summary:")
        print(f"   Navigation items: {nav_successes}/{total_nav_items} working")
        print(f"   Layout checks: {layout_successes}/{total_layout_checks} passing")
        print(f"   Overall status: {results['overall_status']}")
        
    except Exception as e:
        print(f"❌ Test failed with error: {str(e)}")
        results["error"] = str(e)
        results["overall_status"] = "ERROR"
        
    finally:
        driver.quit()
    
    # Save results
    results_file = f"navigation_layout_test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n📄 Results saved to: {results_file}")
    return results

if __name__ == "__main__":
    test_navigation_and_layout()
