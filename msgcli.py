import threading
import time
import sys
import mysql.connector

# Import the clean fixed operational backend boundaries cleanly
from chat_functions import *

db_lock = threading.Lock()

#CONFIG -> queries module
#CLIENT_LOGIN---------------------------------------------------------
print("1. Login")
print("2. Register")
choice = input("> ")

#REGISTRATION----------------------------------------------------------
if choice == "2":
    try:
        username = uname()
        phone = input("Phone Number > ")
        password = passw()
        reg_user(username, phone, password)
        print("Registration complete. Please restart script to log in.")
        sys.exit()
    except Exception as e:
        print("Registration error:", e)
        sys.exit()

#CONNECT---------------------------------------------------------------
user_session = uname()
pass_session = passw()

conn, cur = login(user_session, pass_session)
if not conn or not cur:
    print("Execution aborted due to invalid session parameters.")
    sys.exit()

print("Logged in as--------", user_session)

#CONTACT---------------------------------------------------------------
other = input("  Chat with user: ")

result = search_contact(cur, other)

if result:
    print(f"Connecting to ------------ {other}")
    add_contact(cur, conn, other)
else:
    print("  User does not exist.")
    logout(conn, cur)
    sys.exit()

# ================= RECEIVE MESSAGES =================
last_timestamp = "2026-01-01 00:00:00"
stop_signal = threading.Event()

def receive_messages():
    global last_timestamp
    while not stop_signal.is_set():
        try:
            with db_lock:
                messages = stream_txts(cur, other, last_timestamp)
                
            if messages:
                for msg in messages:
                    print(f"\n[{msg['dispatched_at']}] {msg['sender_username']}: {msg['body_text']}")
                    last_timestamp = str(msg['dispatched_at'])
            
            time.sleep(1.0)

        except Exception as e:
            time.sleep(2)

threading.Thread(target=receive_messages, daemon=True).start()

# ================= SEND MESSAGES =================
try:
    while True:
        message = input("> ")
    
        if not message:
            continue
            
        if message.strip().lower() == "exit":
            break
    
        with db_lock:
            send_txt(cur, conn, other, message)
            
except KeyboardInterrupt:
    pass

print("\nExit SIGNAL---------")
stop_signal.set()
time.sleep(0.2)

with db_lock:
    logout(conn, cur)

print(rt)
