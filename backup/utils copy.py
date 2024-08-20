
import sqlite3, time, json
db_path = 'memory.db'


def get_chats():
    try:
        conn = sqlite3.connect(db_path)

        c = conn.cursor()
        c.execute(f"SELECT session_id, message FROM message_store order by id asc ")

        rows = c.fetchall()

        chats = []
        last_chat_id = None
        for chat_id, message in rows:
            if chat_id == last_chat_id:
                continue
            last_chat_id = chat_id
            message = json.loads(message)['data']['content']
            chats.append([chat_id, message])
                                                    
        conn.close()
        return chats[::-1]
    except:
        return []

def get_messages(id):
    conn = sqlite3.connect(db_path)

    c = conn.cursor()
    c.execute(f"SELECT id, message_id, timestamp, role, message FROM messages where id={id}")

    rows = c.fetchall()
    conn.close()
    return rows

def insert_message(id, role, message, message_id):
    timestamp = int(time.time())

    data =[[id, message_id, timestamp, role, message]]
    conn = sqlite3.connect(db_path)

    c = conn.cursor()
    sql='''
    INSERT INTO messages (id, message_id, timestamp, role, message)
    VALUES (?, ?, ?, ?, ?)
    '''
    c.executemany(sql, data)
    conn.commit()
    conn.close()



def parse_messages(messages):
    # print(messages)
    messages1 = []
    for message in messages:
        messages1.append({"role": message[3], "content": message[4]})
    return messages1
        