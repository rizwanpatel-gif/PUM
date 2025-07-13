import sqlite3

DB_PATH = "pum.db"

index_statements = [
    "CREATE INDEX IF NOT EXISTS idx_protocolupgrade_protocol_id ON protocol_upgrades(protocol_id);",
    "CREATE INDEX IF NOT EXISTS idx_riskassessment_upgrade_id ON risk_assessments(upgrade_id);",
    "CREATE INDEX IF NOT EXISTS idx_volatilityprediction_upgrade_id ON volatility_predictions(upgrade_id);"
]

def main():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    for stmt in index_statements:
        print(f"Executing: {stmt}")
        cursor.execute(stmt)
    conn.commit()
    conn.close()
    print("Indexes created successfully.")

if __name__ == "__main__":
    main() 