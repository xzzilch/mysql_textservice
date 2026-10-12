import threading
import time
import openports
from queries import *
import sys

#CONFIG -> queries module

#CONNECT---------------------------------------------------------------
db = database_connection()
cur = db.cursor()
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
        
#FETCH_USER-------------------------------------------------------------        
cur.execute(
    "SELECT user_id FROM users WHERE username=%s AND password=%s",
    (username, password)
)

result = cur.fetchone()

if not result:
    print("Invalid username or password.")
    exit()

user_id = result[0]
db.close()

print("Logged in as", username)

#CONTACT---------------------------------------------------------------
other = input("Chat with user: ")

db = database_connection()
cur = db.cursor()

cur.execute(
    "SELECT user_id FROM users WHERE username=%s",
    (other,)
)

result = cur.fetchone()

if not result:
    print("User does not exist.")
    exit()

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

db.close()

print("\nConnected to", other)
print("Type messages below. Ctrl+C to quit.\n")


# ================= RECEIVE MESSAGES =================
last_message = 0


def receive_messages():
    global last_message

    while True:
        try:
            db = database_connection()
            cur = db.cursor()

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

            db.close()
            time.sleep(0.5)

        except Exception as e:
            print("\nConnection error:", e)
            time.sleep(2)


threading.Thread(target=receive_messages, daemon=True).start()


# ================= SEND MESSAGES =================

while True:
    message = input("> ")

    if not message:
        continue

    db = database_connection()
    cur = db.cursor()

    cur.execute("""
    INSERT INTO messages (session_id, sender_id, message)
    VALUES (%s, %s, %s)
    """, (session_id, user_id, message))

    db.commit()
    db.close()

