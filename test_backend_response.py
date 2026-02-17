import requests
import json

API_BASE_URL = 'http://localhost:5000'

# Test the /calculate endpoint
try:
    response = requests.post(
        f'{API_BASE_URL}/calculate',
        json={'storage_tb': 1, 'region': 'IN-WE'},
        timeout=10
    )
    print(f"Status Code: {response.status_code}")
    print(f"Response Body: {response.text}")
    print(f"Response JSON: {json.dumps(response.json(), indent=2)}")
except Exception as e:
    print(f"Error: {e}")
