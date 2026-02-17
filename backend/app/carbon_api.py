import httpx
import os

API_KEY = os.getenv("ELECTRICITYMAP_API_KEY")

async def get_carbon_intensity(region="IN-WE"):
    """Fetch carbon intensity from ElectricityMaps API.
    Returns gCO2/kWh for the region, or 500 as default if unavailable.
    """
    url = f"https://api.electricitymaps.com/v3/carbon-intensity/latest?zone={region}"
    headers = {"auth-token": API_KEY}

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            data = response.json()
        
        carbon_intensity = data.get("carbonIntensity")
        
        if carbon_intensity is None:
            print(f"Warning: No carbonIntensity in response for {region}. Using default 500 gCO2/kWh")
            return 500
        
        return carbon_intensity
    except Exception as e:
        print(f"Error fetching carbon intensity for {region}: {str(e)}")
        return 500  # Default fallback value in gCO2/kWh
