import requests
import json

API_BASE_URL = 'http://localhost:5000'

# Test storage size
STORAGE_GB = 100
STORAGE_TB = STORAGE_GB / 1024

# Different regions with their expected carbon intensity ranges
regions = [
    {"code": "IN-WE", "name": "India West", "expected_min": 400, "expected_max": 500},
    {"code": "FR", "name": "France", "expected_min": 30, "expected_max": 50},
    {"code": "US-CAL-CISO", "name": "California", "expected_min": 170, "expected_max": 200},
    {"code": "GB", "name": "Great Britain", "expected_min": 150, "expected_max": 250},
    {"code": "DE", "name": "Germany", "expected_min": 250, "expected_max": 350},
]

print("=" * 80)
print("🌍 REGION-SPECIFIC CARBON FOOTPRINT TEST")
print("=" * 80)
print(f"\nTest Configuration:")
print(f"  Storage Size: {STORAGE_GB} GB = {STORAGE_TB:.6f} TB")
print(f"  Backend URL: {API_BASE_URL}")
print(f"  Endpoint: POST /calculate")

print("\n" + "=" * 80)
print(f"{'Region':<25} {'Code':<12} {'Carbon Intensity':<20} {'Energy/Year':<15} {'Carbon/Year':<15}")
print("=" * 80)

for region in regions:
    try:
        response = requests.post(
            f'{API_BASE_URL}/calculate',
            json={'storage_tb': STORAGE_TB, 'region': region['code']},
            timeout=10
        )
        
        if response.status_code != 200:
            print(f"{region['name']:<25} {region['code']:<12} ❌ HTTP {response.status_code}")
            continue
        
        data = response.json()
        
        energy = data.get('energy_kwh_per_year', 0)
        carbon = data.get('carbon_kg_per_year', 0)
        
        # Calculate carbon intensity from the response
        # carbon = energy * (intensity / 1000) => intensity = carbon * 1000 / energy
        if energy > 0:
            calculated_intensity = (carbon * 1000) / energy
        else:
            calculated_intensity = 0
        
        # Check if within expected range
        status = "✅"
        if calculated_intensity < region['expected_min'] or calculated_intensity > region['expected_max']:
            status = f"⚠️  (expected {region['expected_min']}-{region['expected_max']})"
        
        print(f"{region['name']:<25} {region['code']:<12} {calculated_intensity:>6.0f} gCO2/kWh {status:<18} {energy:>14.2f} kWh  {carbon:>14.2f} kg")
        
    except requests.exceptions.ConnectionError:
        print(f"{region['name']:<25} {region['code']:<12} ❌ Connection refused (backend not running)")
        break
    except Exception as e:
        print(f"{region['name']:<25} {region['code']:<12} ❌ Error: {str(e)[:40]}")

print("\n" + "=" * 80)
print("✨ Test Summary:")
print("  • Same storage size = same energy (physics)")
print("  • Different regions = different carbon intensity")
print("  • Different regions = different carbon/cost (despite same storage & energy)")
print("=" * 80)
