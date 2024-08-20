import pandas as pd
import sqlite3, os

db_path = 'db/chatbot.db'
if os.path.exists(db_path):
    os.system(f"rm -r {db_path}")

# Connect to SQLite database (creates it if it doesn't exist)
conn = sqlite3.connect(db_path)

c = conn.cursor()
c.execute("""CREATE TABLE IF NOT EXISTS  messages (
            id INTEGER,
            message_id INTEGER,
            timestamp INTEGER,
            role text,
            message text
            )""")


conn.commit()

# Close the connection
conn.close()

