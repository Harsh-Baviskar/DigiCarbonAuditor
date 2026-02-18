"""
Test the /select-folder endpoint
"""
import requests
import json

def test_select_folder_endpoint():
    """Test the /select-folder endpoint"""
    
    backend_url = 'http://127.0.0.1:5000'
    
    print("Testing Select Folder Endpoint")
    print("=" * 50)
    print(f"Backend URL: {backend_url}")
    print("-" * 50)
    
    try:
        # Test the endpoint
        response = requests.get(f'{backend_url}/select-folder')
        
        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        print("-" * 50)
        
        data = response.json()
        print(f"Response JSON:\n{json.dumps(data, indent=2)}")
        
        if data.get('path'):
            print(f"\n✅ Path received: {data.get('path')}")
        else:
            print(f"\n⚠️  No path returned (user might have canceled)")
            print(f"This is normal if the dialog was canceled")
        
        return True
        
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to backend. Make sure Flask is running:")
        print("   cd backend")
        print("   python -m flask --app app.app run")
        return False
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

if __name__ == '__main__':
    success = test_select_folder_endpoint()
    exit(0 if success else 1)
