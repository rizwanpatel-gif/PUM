import sqlite3

conn = sqlite3.connect('pum.db')
cursor = conn.cursor()

cursor.execute("SELECT id, block_number, transaction_hash, event_type, timestamp, network_id FROM blockchain_events ORDER BY timestamp DESC LIMIT 10")
rows = cursor.fetchall()

print("Latest 10 blockchain events:")
for row in rows:
    print(row)

conn.close() 