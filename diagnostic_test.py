"""
Test API to diagnose zero values issue
"""
import requests
import json

print('=== Testing Backend API ===\n')

# Test 1: Check backend status
print('Test 1: Check if backend is running')
try:
    response = requests.get('http://localhost:5000/carbon-forecast?zone=IN-WE', timeout=5)
    if response.status_code == 200:
        print('✅ Backend is running')
    else:
        print(f'❌ Backend returned status {response.status_code}')
except Exception as e:
    print(f'❌ Backend not responding: {e}')

print('\n' + '='*60 + '\n')

# Test 2: Test calculate endpoint
print('Test 2: Test /calculate endpoint (1 TB, India West)')
try:
    response = requests.post('http://localhost:5000/calculate', 
        json={'storage_tb': 1.0, 'region': 'IN-WE'},
        timeout=10
    )
    print(f'Status Code: {response.status_code}')
    data = response.json()
    print(f'Response:')
    print(json.dumps(data, indent=2))
    
    # Check for zeros
    print('\nValue Check:')
    energy = data.get('energy_kwh_per_year', 0)
    carbon = data.get('carbon_kg_per_year', 0)
    cost = data.get('carbon_cost_estimate', 0)
    
    print(f'  Energy: {energy} kWh/year {"❌ ZERO" if energy == 0 else "✅ OK"}')
    print(f'  Carbon: {carbon} kg/year {"❌ ZERO" if carbon == 0 else "✅ OK"}')
    print(f'  Cost: ${cost}/year {"❌ ZERO" if cost == 0 else "✅ OK"}')
    
except Exception as e:
    print(f'❌ Error: {e}')

print('\n' + '='*60 + '\n')

# Test 3: Check ElectricityMap API
print('Test 3: Test ElectricityMap API directly')
api_key = 'PYEaCUKNg2MVDqBDw1pm'
try:
    url = 'https://api.electricitymaps.com/v3/carbon-intensity/latest?zone=IN-WE'
    response = requests.get(url, headers={'auth-token': api_key}, timeout=10)
    print(f'Status Code: {response.status_code}')
    
    if response.status_code == 200:
        data = response.json()
        print('✅ API key is valid')
        print(f'Response: {json.dumps(data, indent=2)[:300]}...')
    else:
        print(f'❌ API Error: {response.status_code}')
        print(f'Response: {response.text[:300]}')
except Exception as e:
    print(f'❌ Connection Error: {e}')

print('\n' + '='*60 + '\n')
print('Diagnosis Summary:')
print('- If backend shows 0 values but API call works --> Energy calculation issue')
print('- If API call fails --> API key or network issue')
print('- If backend is not running --> Start backend: python app.py')
