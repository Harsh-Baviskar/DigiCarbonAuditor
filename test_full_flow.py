import requests
import json

API_BASE_URL = 'http://localhost:5000'

# Test with 100 GB
print("Testing backend with 100 GB storage size...")
try:
    response = requests.post(
        f'{API_BASE_URL}/calculate',
        json={'storage_tb': 100/1024, 'region': 'IN-WE'},  # 100 GB = 0.0977 TB
        timeout=10
    )
    print(f"Status Code: {response.status_code}")
    data = response.json()
    print(f"Response JSON:\n{json.dumps(data, indent=2)}")
    
    # Check if values are non-zero
    energy = data.get('energy_kwh_per_year', 0)
    carbon = data.get('carbon_kg_per_year', 0)
    cost = data.get('carbon_cost_estimate', 0)
    
    print(f"\n--- Extracted Values ---")
    print(f"Energy: {energy} kWh/year")
    print(f"Carbon: {carbon} kg/year")
    print(f"Cost: ${cost}/year")
    
    if energy == 0 or carbon == 0 or cost == 0:
        print("\n⚠️ WARNING: One or more values are zero!")
    else:
        print("\n✅ All values are non-zero")
        
except Exception as e:
    print(f"Error: {e}")

# Test with 1 TB
print("\n" + "="*50)
print("Testing backend with 1 TB storage size...")
try:
    response = requests.post(
        f'{API_BASE_URL}/calculate',
        json={'storage_tb': 1, 'region': 'IN-WE'},
        timeout=10
    )
    print(f"Status Code: {response.status_code}")
    data = response.json()
    print(f"Response JSON:\n{json.dumps(data, indent=2)}")
    
    # Check if values are non-zero
    energy = data.get('energy_kwh_per_year', 0)
    carbon = data.get('carbon_kg_per_year', 0)
    cost = data.get('carbon_cost_estimate', 0)
    
    print(f"\n--- Extracted Values ---")
    print(f"Energy: {energy} kWh/year")
    print(f"Carbon: {carbon} kg/year")
    print(f"Cost: ${cost}/year")
        
except Exception as e:
    print(f"Error: {e}")
