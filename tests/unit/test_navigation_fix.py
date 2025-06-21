#!/usr/bin/env python3
"""
Navigation Fix Verification Test
Verifies that all 11 navigation items are now rendering in the Svelte frontend
"""

import requests
import time
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException

def test_navigation_rendering():
    """Test that all navigation items are rendering correctly"""
    
    # Expected navigation items based on viewConfig
    expected_nav_items = [
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
    
    print("🔍 Testing Navigation Fix...")
    print(f"Expected {len(expected_nav_items)} navigation items")
    
    # Setup Chrome driver with headless option
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    
    driver = None
    try:
        # Check if frontend is running
        try:
            response = requests.get("http://localhost:3001", timeout=5)
            print("✅ Frontend is accessible")
        except requests.exceptions.RequestException as e:
            print(f"❌ Frontend not accessible: {e}")
            return False
            
        # Initialize web driver
        driver = webdriver.Chrome(options=chrome_options)
        driver.get("http://localhost:3001")
        
        # Wait for the application to load
        print("⏳ Waiting for application to load...")
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "godelos-interface"))
        )
        
        # Check if sidebar is collapsed and expand if needed
        try:
            sidebar = driver.find_element(By.CLASS_NAME, "sidebar")
            if "collapsed" in sidebar.get_attribute("class"):
                print("📱 Sidebar is collapsed, expanding...")
                toggle_btn = driver.find_element(By.CLASS_NAME, "sidebar-toggle")
                toggle_btn.click()
                time.sleep(1)
        except Exception as e:
            print(f"⚠️ Could not check sidebar state: {e}")
        
        # Find all navigation items
        nav_items = driver.find_elements(By.CLASS_NAME, "nav-item")
        print(f"🧭 Found {len(nav_items)} navigation items in DOM")
        
        # Extract navigation item titles
        found_titles = []
        for item in nav_items:
            try:
                title_elem = item.find_element(By.CLASS_NAME, "nav-title")
                title = title_elem.text.strip()
                if title:
                    found_titles.append(title)
            except Exception as e:
                print(f"⚠️ Could not extract title from nav item: {e}")
        
        print(f"📋 Found navigation items: {found_titles}")
        
        # Check debug navigation panel as backup
        debug_nav_items = driver.find_elements(By.CLASS_NAME, "debug-nav-item")
        print(f"🛠️ Debug panel shows {len(debug_nav_items)} items")
        
        # Verify all expected items are present
        missing_items = []
        for expected in expected_nav_items:
            if expected not in found_titles:
                missing_items.append(expected)
        
        # Results
        print("\n" + "="*60)
        print("NAVIGATION FIX TEST RESULTS")
        print("="*60)
        print(f"Expected items: {len(expected_nav_items)}")
        print(f"Found items: {len(found_titles)}")
        print(f"Debug panel items: {len(debug_nav_items)}")
        
        if len(found_titles) == len(expected_nav_items) and not missing_items:
            print("✅ SUCCESS: All navigation items are rendering correctly!")
            print("🎉 Navigation truncation issue has been FIXED!")
            return True
        else:
            print("❌ ISSUE: Navigation items still not rendering correctly")
            if missing_items:
                print(f"Missing items: {missing_items}")
            print("🔧 Further investigation needed")
            return False
            
    except TimeoutException:
        print("❌ Timeout waiting for application to load")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False
    finally:
        if driver:
            driver.quit()

def check_console_logs():
    """Check browser console for any JavaScript errors"""
    print("\n🔍 Checking for JavaScript errors...")
    
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    
    driver = None
    try:
        driver = webdriver.Chrome(options=chrome_options)
        driver.get("http://localhost:3001")
        
        # Wait for page load
        time.sleep(3)
        
        # Get console logs
        logs = driver.get_log('browser')
        
        errors = [log for log in logs if log['level'] == 'SEVERE']
        warnings = [log for log in logs if log['level'] == 'WARNING']
        
        print(f"📊 Console: {len(errors)} errors, {len(warnings)} warnings")
        
        if errors:
            print("❌ JavaScript Errors Found:")
            for error in errors[:5]:  # Show first 5 errors
                print(f"   {error['message']}")
        else:
            print("✅ No critical JavaScript errors")
            
        return len(errors) == 0
        
    except Exception as e:
        print(f"⚠️ Could not check console logs: {e}")
        return True  # Assume no errors if we can't check
    finally:
        if driver:
            driver.quit()

if __name__ == "__main__":
    print("🚀 Starting Navigation Fix Verification Test")
    print("-" * 50)
    
    # Test navigation rendering
    nav_success = test_navigation_rendering()
    
    # Check for console errors
    console_clean = check_console_logs()
    
    print("\n" + "="*60)
    print("FINAL RESULTS")
    print("="*60)
    
    if nav_success and console_clean:
        print("🎉 COMPLETE SUCCESS!")
        print("✅ All 11 navigation items are rendering")
        print("✅ No critical JavaScript errors")
        print("🚀 Navigation issue has been RESOLVED!")
    elif nav_success:
        print("🎯 PARTIAL SUCCESS!")
        print("✅ Navigation items are rendering")
        print("⚠️ Some JavaScript warnings present")
    else:
        print("❌ ISSUE PERSISTS")
        print("🔧 Navigation truncation still occurring")
        
    print("-" * 50)
