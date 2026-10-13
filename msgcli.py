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
        cur.execute(
            "INSERT INTO users (username, password) VALUES (%s, %s)",
            (username, password)
        )
        db.commit()
        print("Account created.")
    except mysql.connector.IntegrityError:
        print("Username already exists.")
        exit()
#CONNECT---------------------------------------------------------------
db = database_connection()
cur = db.cursor()
print("Logged in as--------", username)

#CONTACT---------------------------------------------------------------
other = input("  Chat with user: ")
cur.execute(
    "SELECT user_id FROM users WHERE username=%s",
    (other,)
)

result = cur.fetchone()

if not result:
    print("  User does not exist.")

other_id = result[0]

#GET_SESSION---------------------------------------------------------
cur.execute("""
SELECT session_id
FROM sessions
WHERE (user1_id=%s AND user2_id=%s)
   OR (user1_id=%s AND user2_id=%s)
LIMIT 1
""", (user_id, other_id, other_id, user_id))

result = cur.fetchone()

if result:
    session_id = result[0]
else:
    cur.execute(
        "INSERT INTO sessions (user1_id, user2_id) VALUES (%s, %s)",
        (user_id, other_id)
    )
    db.commit()
    session_id = cur.lastrowid

#db.close()

print("\nConnected to", other)
print("Type messages below. Ctrl+C to quit.\n")

# ================= RECEIVE MESSAGES =================
last_message = 0

def receive_messages(cur):
    global last_message
    while True:
        try:
            cur.execute("""
            SELECT message_id, sender_id, message, sent_at
            FROM messages
            WHERE session_id=%s
              AND message_id>%s
            ORDER BY message_id
            """, (session_id, last_message))

            rows = cur.fetchall()

            for message_id, sender_id, message, sent_at in rows:
                last_message = message_id

                if sender_id != user_id:
                    print(f"\n{other}: {message}")
            time.sleep(0.1)

        except Exception as e:
            print("\nConnection error:\n", e)
            time.sleep(2)

stop_signal = threading.Event()
threading.Thread(target=receive_messages(cur), args = (cur,), daemon=True).start()


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
    t.join(timeout=3)
    print("Exit SIGNAL---------")
    pass

db.commit()
db.close()

