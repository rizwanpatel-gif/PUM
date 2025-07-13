import sqlite3

conn = sqlite3.connect('pum.db')
cursor = conn.cursor()
cursor.execute('DELETE FROM blockchain_events;')
conn.commit()
print('All events deleted from blockchain_events table.')
conn.close() 