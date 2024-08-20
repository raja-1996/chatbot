import pandas as pd
import sqlite3, os

db_path = 'db/chatbot.db'

# Connect to SQLite database (creates it if it doesn't exist)
conn = sqlite3.connect(db_path)

c = conn.cursor()
c.execute("""select * from messages""")


conn.commit()

# Close the connection
conn.close()

