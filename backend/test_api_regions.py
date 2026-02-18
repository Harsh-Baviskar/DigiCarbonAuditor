#!/usr/bin/env python3
"""
Test script for ElectricityMap API integration
Tests the /calculate endpoint with different regions to verify real carbon intensity data
"""

import requests
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

API_BASE = "http://127.0.0.1:5000"
API_KEY = os.getenv("ELECTRICITYMAP_API_KEY")

# Test regions with different carbon intensities
TEST_REGIONS = [
    ("IN-WE", "India - Western Grid", "High carbon intensity"),
    ("US-CA", "California, USA", "Lower carbon intensity (renewable heavy)"),
    ("DE", "Germany", "Medium-high carbon intensity"),
    ("NO", "Norway", "Very low (hydroelectric)"),
    ("US-TX", "Texas, USA", "Wind + gas mix"),
    ("FR", "France", "Very low (nuclear)"),
    ("MX-BC", "Baja California, Mexico", "Mix of renewables"),
]

def test_calculate_endpoint(storage_gb=100, region="IN-WE"):
    """Test the /calculate endpoint with a given region"""
    print(f"\n{'='*70}")
    print(f"Testing /calculate with {storage_gb}GB storage in region: {region}")
    print('='*70)
    
    # Test GET endpoint
    try:
        url = f"{API_BASE}/calculate?data_size={storage_gb}&region={region}"
        print(f"📡 GET Request: {url}")
        
        response = requests.get(url)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("\n✅ Success! Real API Response:")
            print(json.dumps(data, indent=2))
            
            # Extract key values
            carbon_intensity = data.get('carbon_intensity_gco2_per_kwh', 'N/A')
            carbon_kg = data.get('carbon_kg_per_year', 0)
            energy_kwh = data.get('energy_kwh_per_year', 0)
            cost = data.get('carbon_cost_estimate', 0)
            
            print(f"\n📊 Summary for {region}:")
            print(f"   Carbon Intensity: {carbon_intensity} gCO2/kWh")
            print(f"   Energy/Year: {energy_kwh} kWh")
            print(f"   CO2 Emissions/Year: {carbon_kg} kg")
            print(f"   Est. Carbon Cost/Year: ${cost}")
            print(f"   Calculation Method: {data.get('calculation_method', 'unknown')}")
            
            return data
        else:
            print(f"\n❌ Error: {response.status_code}")
            print(f"Response: {response.text}")
            return None
    
    except requests.exceptions.ConnectionError:
        print(f"\n❌ Connection Error: Backend not running at {API_BASE}")
        print("Start the Flask backend with: python app.py (in backend/app directory)")
        return None
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        return None


def compare_regions():
    """Compare carbon footprint across different regions"""
    print("\n\n" + "="*70)
    print("COMPARING CARBON INTENSITY ACROSS REGIONS")
    print("="*70)
    
    storage_gb = 100  # Fixed storage for comparison
    results = {}
    
    for region_code, region_name, description in TEST_REGIONS:
        print(f"\n🌍 {region_code}: {region_name} ({description})")
        data = test_calculate_endpoint(storage_gb, region_code)
        
        if data:
            results[region_code] = {
                'name': region_name,
                'carbon_intensity': data.get('carbon_intensity_gco2_per_kwh'),
                'carbon_kg': data.get('carbon_kg_per_year'),
                'cost': data.get('carbon_cost_estimate')
            }
    
    # Print comparison table
    if results:
        print("\n\n" + "="*70)
        print(f"COMPARISON TABLE ({storage_gb}GB Storage)")
        print("="*70)
        print(f"{'Region':<12} {'Carbon Intensity':<20} {'CO2/Year':<15} {'Cost/Year':<12}")
        print("-"*70)
        
        for region_code, data in sorted(results.items(), key=lambda x: x[1]['carbon_intensity'] or 0, reverse=True):
            intensity = f"{data['carbon_intensity']} gCO2/kWh" if data['carbon_intensity'] else "N/A"
            carbon = f"{data['carbon_kg']} kg" if data['carbon_kg'] else "N/A"
            cost = f"${data['cost']}" if data['cost'] else "N/A"
            print(f"{region_code:<12} {intensity:<20} {carbon:<15} {cost:<12}")
        
        # Find highest and lowest
        sorted_results = [(r, d) for r, d in results.items() if d['carbon_intensity']]
        if sorted_results:
            sorted_results.sort(key=lambda x: x[1]['carbon_intensity'], reverse=True)
            highest = sorted_results[0]
            lowest = sorted_results[-1]
            
            print("\n" + "="*70)
            print(f"🔴 HIGHEST Carbon Intensity: {highest[0]} ({highest[1]['carbon_intensity']} gCO2/kWh)")
            print(f"🟢 LOWEST Carbon Intensity: {lowest[0]} ({lowest[1]['carbon_intensity']} gCO2/kWh)")
            
            if lowest[1]['carbon_intensity'] > 0:
                ratio = highest[1]['carbon_intensity'] / lowest[1]['carbon_intensity']
                print(f"⚖️  Difference: {ratio:.1f}x higher emissions in highest vs lowest")


def test_post_endpoint(storage_tb=0.1, region="US-CA"):
    """Test the POST /calculate endpoint"""
    print("\n\n" + "="*70)
    print("TESTING POST /calculate ENDPOINT")
    print("="*70)
    
    try:
        url = f"{API_BASE}/calculate"
        payload = {
            "storage_tb": storage_tb,
            "region": region
        }
        
        print(f"📡 POST Request to: {url}")
        print(f"Payload: {json.dumps(payload, indent=2)}")
        
        response = requests.post(url, json=payload)
        print(f"\nStatus Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("\n✅ Success! Response:")
            print(json.dumps(data, indent=2))
            
            carbon_intensity = data.get('carbon_intensity_gco2_per_kwh', 'N/A')
            carbon_kg = data.get('carbon_kg_per_year', 0)
            
            print(f"\n📊 POST Test Summary:")
            print(f"   Storage: {storage_tb} TB = {storage_tb * 1024} GB")
            print(f"   Region: {region}")
            print(f"   Carbon Intensity: {carbon_intensity} gCO2/kWh")
            print(f"   CO2/Year: {carbon_kg} kg")
            
            return data
        else:
            print(f"\n❌ Error: {response.status_code}")
            print(f"Response: {response.text}")
            return None
    
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        return None


def main():
    print("\n" + "="*70)
    print("DIGITAL CARBON AUDITOR - API TEST SUITE")
    print("Testing ElectricityMap API Integration")
    print("="*70)
    
    print(f"\n🔑 API Key Status: {'✅ Configured' if API_KEY else '❌ Missing'}")
    print(f"🌐 Backend URL: {API_BASE}")
    
    # Test 1: Single region GET
    print("\n\n▶️  TEST 1: Single Region Query (GET)")
    test_calculate_endpoint(100, "IN-WE")
    
    # Test 2: Compare regions
    print("\n\n▶️  TEST 2: Regional Comparison")
    compare_regions()
    
    # Test 3: POST endpoint
    print("\n\n▶️  TEST 3: POST Endpoint")
    test_post_endpoint(0.1, "US-CA")
    
    print("\n\n" + "="*70)
    print("✅ API TEST COMPLETE")
    print("="*70)


if __name__ == "__main__":
    main()
