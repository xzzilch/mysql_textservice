import threading
import time
import openports
from queries import *
import sys

#CONFIG -> queries module
#CLIENT_LOGIN---------------------------------------------------------
print("1. Login")
print("2. Register")
choice = input("> ")
#REGISTRATION----------------------------------------------------------
if choice == "2":
    try:
        connection = server_connection('text_service_guest')
        db = connection['conn']
        cur = connection['cursor']
        username = connection['username']
        password = input('Once chance to enter password good luck')
        cur.execute(
            "INSERT INTO users (username, password) VALUES (%s, %s)",
            (username, password)
        )
        db.commit()
        print("Account created.-----------\n")
        
        cur.close()
        db.close()
    except mysql.connector.IntegrityError:
        print("Username already exists.")
        exit()
#CONNECT---------------------------------------------------------------
connection = server_connection('text_service')
db = connection['conn']
cur = connection['cursor']
username = connection['username']
print("Logged in as--------", username)

#CONTACT---------------------------------------------------------------
other = input("  Chat with user: ")
cur.execute(
    "SELECT user_id FROM users WHERE username=%s",
    (other,)
)

result = cur.fetchone()

if result:
    print(f"Connecting to ------------ {other}")
    other_id = result[0]
else:
    print("  User does not exist.")
    

#GET_SESSION---------------------------------------------------------

#later

# ================= RECEIVE MESSAGES =================
last_message = 0
stop_signal = threading.Event()

def receive_messages():
    global last_message
    thread_conn = server_connection("text_service")
    thread_cur = thread_conn["cursor"]
    while not stop_signal.is_set():
        try:
            thread_cur.execute("""
            SELECT message_id, sender_id, message, sent_at
            FROM messages
            WHERE session_id=%s
              AND message_id>%s
            ORDER BY message_id
            """, (session_id, last_message))

            rows = thread_cur.fetchall()

            for message_id, sender_id, message, sent_at in rows:
                last_message = message_id

                if sender_id != user_id:
                    print(f"\n{other}: {message}")
            time.sleep(0.1)

        except Exception as e:
            print("\nConnection error:\n", e)
            time.sleep(2)
    
    thread_cur.close()
    thread_conn["conn"].close()

threading.Thread(target=receive_messages, daemon=True).start()

# ================= SEND MESSAGES =================
try:
    while True:
        message = input("> ")
    
        if not message:
            continue
    
        cur.execute("""
        INSERT INTO messages (session_id, sender_id, message)
        VALUES (%s, %s, %s)
        """, (session_id, user_id, message))
except KeyboardInterrupt:
    stop_signal.set()
    print("Exit SIGNAL---------")
    pass

db.commit()
cur.close()
db.close()

