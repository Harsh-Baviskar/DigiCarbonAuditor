"""
Test the /waste-detect endpoint
"""
import requests
import json
import os

def test_waste_detect_endpoint():
    """Test the /waste-detect endpoint with a real folder"""
    
    backend_url = 'http://127.0.0.1:5000'
    
    # Test with the backend directory itself
    test_path = os.path.dirname(os.path.abspath(__file__))
    
    print("Testing Waste Detect Endpoint")
    print("=" * 50)
    print(f"Backend URL: {backend_url}")
    print(f"Test Path: {test_path}")
    print(f"Path Exists: {os.path.exists(test_path)}")
    print(f"Is Directory: {os.path.isdir(test_path)}")
    print("-" * 50)
    
    try:
        # Test the endpoint
        response = requests.post(
            f'{backend_url}/waste-detect',
            json={'path': test_path},
            headers={'Content-Type': 'application/json'}
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        print("-" * 50)
        
        data = response.json()
        print(f"Response JSON:\n{json.dumps(data, indent=2)}")
        
        if response.status_code == 200:
            print("\n✅ Endpoint working correctly!")
            print(f"Scan Status: {data.get('scanStatus')}")
            print(f"Total Files: {data.get('summary', {}).get('totalFiles')}")
            print(f"Duplicates: {data.get('summary', {}).get('duplicateFilesCount')}")
        else:
            print(f"\n❌ Endpoint returned error: {data.get('detail')}")
        
        return response.status_code == 200
        
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to backend. Make sure Flask is running:")
        print("   cd backend")
        print("   python -m flask --app app.app run")
        return False
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

if __name__ == '__main__':
    success = test_waste_detect_endpoint()
    exit(0 if success else 1)
