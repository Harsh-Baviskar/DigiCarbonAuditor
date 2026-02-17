import sqlite3

def init_db():
    conn = sqlite3.connect("carbon.db")
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS emissions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        storage_tb REAL,
        energy_kwh REAL,
        carbon_kg REAL,
        carbon_cost REAL,
        region TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    conn.commit()
    conn.close()


def insert_record(storage_tb, energy, carbon_kg, carbon_cost, region):
    conn = sqlite3.connect("carbon.db")
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO emissions (storage_tb, energy_kwh, carbon_kg, carbon_cost, region)
    VALUES (?, ?, ?, ?, ?)
    """, (storage_tb, energy, carbon_kg, carbon_cost, region))

    conn.commit()
    conn.close()
