#!/usr/bin/env python3

import sys
import os
import json
import requests

def test_full_api():
    """Test the full API with actual NayaPay data"""
    
    print("🔍 Testing Full API with NayaPay Data")
    print("=" * 50)
    
    API_BASE = 'http://127.0.0.1:8000'
    
    # Test if API is running
    try:
        response = requests.get(f"{API_BASE}/")
        print(f"✅ API is running: {response.json()}")
    except Exception as e:
        print(f"❌ API not running: {e}")
        print("💡 Start the API with: cd backend && python main.py")
        return
    
    # Load the template to verify it's correct
    try:
        response = requests.get(f"{API_BASE}/template/NayaPay_Enhanced_Template")
        if response.status_code == 200:
            config = response.json()['config']
            print(f"✅ Template loaded: {len(config.get('categorization_rules', []))} rules")
            
            # Check for key rules
            rule_names = [rule['rule_name'] for rule in config.get('categorization_rules', [])]
            if 'Surraiya Riaz Transactions' in rule_names:
                print("✅ Surraiya Riaz rule found")
            if 'Ride Hailing Services' in rule_names:
                print("✅ Ride Hailing rule found")
        else:
            print(f"❌ Failed to load template: {response.status_code}")
    except Exception as e:
        print(f"❌ Template load error: {e}")
    
    print("\n🎯 Template validation complete!")
    print("\n💡 To test with real data:")
    print("   1. Start the frontend: cd frontend && npm start")
    print("   2. Upload m032025.csv")
    print("   3. Check that small Raast Out transactions get categorized as Travel/Ride Hailing")
    print("   4. Check that Surraiya Riaz transactions get titled 'Zunayyara Quran'")

if __name__ == "__main__":
    test_full_api()
