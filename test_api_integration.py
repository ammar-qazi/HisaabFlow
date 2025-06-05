#!/usr/bin/env python3
"""
Test the template loading and column mapping through the API
to diagnose the frontend issue
"""

import requests
import json

def test_template_api():
    print("🔍 Testing Template API Integration")
    print("=" * 50)
    
    base_url = "http://127.0.0.1:8000"
    
    # Test 1: List available templates
    print(f"\n1. Testing template listing...")
    try:
        response = requests.get(f"{base_url}/templates")
        if response.status_code == 200:
            templates = response.json()
            print(f"✅ Templates available: {templates}")
        else:
            print(f"❌ Failed to list templates: {response.status_code}")
            return
    except Exception as e:
        print(f"❌ Error listing templates: {e}")
        return
    
    # Test 2: Load NayaPay template
    print(f"\n2. Testing NayaPay template loading...")
    try:
        response = requests.get(f"{base_url}/template/NayaPay_Enhanced_Template")
        if response.status_code == 200:
            template_data = response.json()
            print(f"✅ Template loaded successfully")
            print(f"📋 Template config: {json.dumps(template_data, indent=2)}")
            
            # Check column mapping specifically
            if 'config' in template_data and 'column_mapping' in template_data['config']:
                column_mapping = template_data['config']['column_mapping']
                print(f"\n🗺️ Column Mapping in Template:")
                for target, source in column_mapping.items():
                    print(f"   {target} → {source}")
            else:
                print(f"❌ No column mapping found in template")
        else:
            print(f"❌ Failed to load template: {response.status_code}")
            print(f"Response: {response.text}")
    except Exception as e:
        print(f"❌ Error loading template: {e}")

def test_file_parsing_api():
    print(f"\n🔍 Testing File Parsing API")
    print("=" * 50)
    
    # This would require uploading a file first, but let's see what we can check
    # We can test the detection endpoint if we have a file uploaded
    
    # For now, let's just check if the server is running
    try:
        response = requests.get("http://127.0.0.1:8000/")
        if response.status_code == 200:
            server_info = response.json()
            print(f"✅ Server is running: {server_info}")
        else:
            print(f"❌ Server not responding properly: {response.status_code}")
    except Exception as e:
        print(f"❌ Cannot connect to server: {e}")
        print(f"💡 Make sure the backend is running: python backend/main.py")

if __name__ == "__main__":
    test_template_api()
    test_file_parsing_api()
