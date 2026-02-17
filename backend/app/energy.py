PUE = 1.4
POWER_PER_TB_WATTS = 8

def calculate_energy(storage_tb):
    return (storage_tb * POWER_PER_TB_WATTS * 24 * 365 * PUE) / 1000
