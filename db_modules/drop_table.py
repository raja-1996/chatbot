import sqlite3

# Connect to the database (or create it if it doesn't exist)
db_path = 'db/chatbot.db'
conn = sqlite3.connect(db_path)

# Create a cursor object to interact with the database
cursor = conn.cursor()

# Define the table name to delete
table_name = 'messages'

# Execute the DROP TABLE statement
cursor.execute(f"DROP TABLE IF EXISTS {table_name}")

# Commit the changes
conn.commit()

# Close the connection
conn.close()
