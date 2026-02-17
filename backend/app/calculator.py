CARBON_PRICE_PER_TON = 30

def calculate_emissions(energy_kwh, carbon_intensity):
    carbon_kg = energy_kwh * (carbon_intensity / 1000)
    carbon_cost = (carbon_kg / 1000) * CARBON_PRICE_PER_TON
    return carbon_kg, carbon_cost
