#FUNCTIONS
#CAREFUL -FUNCTIONS HAVE VERTICAL_DEPENDENCE
rt = '| RETURNED\n------------------\n END OF TEST'
import sys
import os
import mysql.connector
import socket
from openports import *
import json



###############################Functions###############################

#GET A OPEN PORT FROM USER______________________________________________________
def port(timeout= 1, ip='localhost'):
    while True:
        try:
            '''Query User for a port'''
            
            port = int(input('Port >') or 3306)
            ps = portstatus(port, timeout, ip)
            print(ps[1])
            
            if ps[0] == False:
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
        # Use .lstrip("/") to prevent the absolute path slash trap we discussed
        sql_script = os.path.join(os.getcwd(), sql_script.lstrip("/"))
        json_cfg = os.path.join(os.getcwd(), json_cfg.lstrip("/"))
        
        with open(json_cfg) as f:
            cfg = json.load(f)
            
        with open(sql_script) as f:
            return f.read().format(**cfg)
            
    except FileNotFoundError as e:
        print("SQL script missing...\n", e)
        return None # Explicitly return None if a load fails
#print(sqlscript(), rt)

#SERVER CONNECTION_______________________________________________________________________
def server_connection(t=''):
    while True:
        try:   
            h = host()
            p = port(1, h)
            u = uname()
            ps = passw()
            if t == 'text_service_guest':
                u = 'guest'
                ps = ''

            print('Connect to server-----')
            
            # Change: If database parameter 't' is empty, do NOT pass it to connector.
            # This allows you to connect to raw MySQL to run a "CREATE DATABASE" query.
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
        except KeyboardInterrupt as k:
            sys.exit('Exit Signal')
#print(server_connection(), rt)

            
    


