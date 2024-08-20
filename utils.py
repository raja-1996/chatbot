import sqlite3, time, json

db_path = "db/graph.db"

from langgraph.checkpoint.sqlite import SqliteSaver

import sqlite3

conn = sqlite3.connect(db_path, check_same_thread=False)


def get_chats():
    try:
        c = conn.cursor()
        c.execute(f"SELECT thread_id, checkpoint FROM checkpoints order by thread_id, checkpoint_id  ")

        rows = c.fetchall()

        chats = []
        last_chat_id = None
        for chat_id, message in rows:
            if chat_id == last_chat_id:
                continue
            last_chat_id = chat_id
            message = json.loads(message)["channel_values"]["__start__"]["messages"][0][1]
            chats.append([chat_id, message])

        # conn.close()
        print("Done retrieving chats")
        return chats[::-1]
    except:
        return []
