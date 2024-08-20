
import sqlite3, time
db_path = 'db/chatbot.db'


def get_chats():
    conn = sqlite3.connect(db_path)

    c = conn.cursor()
    c.execute(f"SELECT id, message message FROM messages where message_id=1 order by id desc ")

    rows = c.fetchall()
    conn.close()
    return rows

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
        