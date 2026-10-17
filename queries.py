#FUNCTIONS
#CAREFUL -FUNCTIONS HAVE VERTICAL_DEPENDENCE
rt = '| RETURNED'
import sys
import mysql.connector
import socket
from openports import *



###############################Functions###############################

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

#________________________________________________________________________
def uname():
    '''Query User for a '''
    
    user = None
    while not user:
        user = input("Username: ")
    return user        
#print(uname(), rt)

#_________________________________________________________________________
def host():
    o = None
    while not o:
        o = input("hostip >")
    return o
#print(host(), rt)

#_________________________________________________________________________
def passw():
    o = None
    while not o:
        o = input("password >")
    return o
#print(passw(), rt)

#__________________________________________________________________________
def server_connection(t = ''):
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
            o = mysql.connector.connect(
                host = h,
                port = p,
                user = u,
                password = ps,
                database=t
            )
            print('----------------------')
            if o:
                return o
        except mysql.connector.Error as e:
            print('-----------------------ERROR\n', str(e).rjust(3))
        except KeyboardInterrupt as k:
            sys.exit('Exit Signal')
            
    


