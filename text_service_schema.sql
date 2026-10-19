#FUNCTIONS
#CAREFUL -FUNCTIONS HAVE VERTICAL_DEPENDENCE
rt = '| RETURNED\n------------------\n END OF TEST'
import sys
import os
import mysql.connector
import socket
from openports import *
import json

DB_CONFIG = {
    'host': 'localhost',
    'user': 'client_user',
    'password': 'AppSecureAccessPass2026!',
    'database': 'text_service_db'
}

###############################Functions###############################

#GET A OPEN PORT FROM USER______________________________________________________
def port(timeout= 1, ip='localhost'):
    while True:
        try:
            '''Query User for a port'''
            
            val = input('Port >')
            port = int(val) if val else 3306
            ps = portstatus(port, timeout, ip)
            print(ps)
            
            if ps == False:
                if input('Unable to connect retry? [y/n] > ') == 'n':
                    print('returning standard 3306')
                    return 3306
                else:
                    continue
            print('\n')
            return port
        except ValueError as e:
            print("Enter numbers only " , e)
#print(port(),rt)

#GET USER NAME FROM USER_________________________________________________________
def uname():
    '''Query User for a '''
    
    user = None
    while not user:
        user = input("Username: ")
    return user        
#print(uname(), rt)

#GET GOST ADDRESS FROM USER_____________________________________________________
def host():
    o = None
    while not o:
        o = input("hostip >")
    return o
#print(host(), rt)

#GET PASSWORD FROM USER_________________________________________________________
def passw():
    o = None
    while not o:
        o = input("password >")
    return o
#print(passw(), rt)

#RUN SCRIPTS FROM CWD____________________________________________________________________
def sqlscript(sql_script="text_service_schema.sql", json_cfg="DB_METADATA.json"):
    try:
        sql_script = os.path.join(os.getcwd(), sql_script.lstrip("/"))
        json_cfg = os.path.join(os.getcwd(), json_cfg.lstrip("/"))
        
        with open(json_cfg) as f:
            cfg = json.load(f)
            
        with open(sql_script) as f:
            return f.read().format(**cfg)
            
    except FileNotFoundError as e:
        print("SQL script missing...\n", e)
        return None
#print(sqlscript(), rt)

#SERVER CONNECTION_______________________________________________________________________
def server_connection(t=''):
    while True:
        try:   
            h = host()
            p = port(1, h)
            u = uname()
            ps = passw()
            if t == 'text_service' or t == 'text_service_guest':
                u = 'client_user'
                ps = 'AppSecureAccessPass2026!'
                t = 'text_service_db'

            print('Connect to server-----')
            
            connect_kwargs = {
                "host": h,
                "port": p,
                "user": u,
                "password": ps
            }
            if t:
                connect_kwargs["database"] = t

            o = mysql.connector.connect(**connect_kwargs)
            print('----------------------')
            if o:
                return o
        except mysql.connector.Error as e:
            print('-----------------------ERROR\n', str(e).rjust(3))
            if input('Retry database connection? [y/n] > ') == 'n':
                return None
        except KeyboardInterrupt as k:
            sys.exit('Exit Signal')
#print(server_connection(), rt)

#GET OPERATIONAL DB CONNECTION FROM CONFIG______________________________________________
def get_conn():
    return mysql.connector.connect(**DB_CONFIG)

#REGISTER NEW PROFILE IN SYSTEM_________________________________________________________
def reg_user(user, phone, pwd):
    conn = get_conn()
    cursor = conn.cursor()
    try:
        cursor.callproc('RegisterUser', [user, phone, pwd])
        conn.commit()
        print(f" Registered user: {user}")
        return True
    except mysql.connector.Error as err:
        print(f"❌ Registration failed for {user}: {err}")
        return False
    finally:
        cursor.close()
        conn.close()

#AUTHENTICATE USER AND ACQUIRE ACTIVE SESSION CONTEXT___________________________________
def login(user, pwd):
    conn = get_conn()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.callproc('UserLogin', [user, pwd])
        for res in cursor.stored_results():
            row = res.fetchone()
            if row and 'Login Successful!' in row.values():
                print(f"🔓 {user} logged in successfully.")
                return conn, cursor
        print(f"❌ Login failed for {user}: Invalid credentials.")
        conn.close()
        return None, None
    except mysql.connector.Error as err:
        print(f"❌ Login error for {user}: {err}")
        if conn.is_connected():
            conn.close()
        return None, None

#TERMINATE LOGGED IN SESSION AND CLOSE ASSETS___________________________________________
def logout(conn, cursor):
    if not conn or not conn.is_connected():
        return
    try:
        cursor.callproc('UserLogout')
        conn.commit()
        print("🔒 Logged out successfully.")
    except mysql.connector.Error as err:
        print(f"❌ Logout error: {err}")
    finally:
        cursor.close()
        conn.close()

#DISPATCH TEXT MESSAGE INTERACTION OVER SECURED LINE___________________________________
def send_txt(cursor, conn, receiver, text):
    try:
        cursor.callproc('SendText', [receiver, text])
        conn.commit()
        print(f"📩 Sent to {receiver}: '{text}'")
        return True
    except mysql.connector.Error as err:
        print(f"❌ Failed to send text to {receiver}: {err}")
        return False

#STREAM EXCHANGE FEED BETWEEN USERS SINCE HISTORICAL POINT______________________________
def stream_txts(cursor, target, timestamp):
    logs = []
    try:
        cursor.callproc('StreamNewTexts', [target, timestamp])
        for res in cursor.stored_results():
            logs.extend(res.fetchall())
        return logs
    except mysql.connector.Error as err:
        return []

#ADD MUTUAL LINK CONTACT RELATION MATRIX________________________________________________
def add_contact(cursor, conn, target):
    try:
        cursor.callproc('AddContactRelation', [target])
        conn.commit()
        print(f"🔗 Added {target} to contacts.")
        return True
    except mysql.connector.Error as err:
        print(f"❌ Failed to add contact {target}: {err}")
        return False

#SEARCH PUBLIC USERS TO VERIFY PROFILE RECORD___________________________________________
def search_contact(cursor, target):
    try:
        cursor.callproc('SearchContact', [target])
        for res in cursor.stored_results():
            row = res.fetchone()
            if row:
                return row
        return None
    except mysql.connector.Error:
        return None
