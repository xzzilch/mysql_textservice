#FUNCTIONS
#CAREFUL -FUNCTIONS HAVE VERTICAL_DEPENDENCE
rt = '| RETURNED'
import sys
import mysql.connector
import socket
from openports import *

#Config--------------------------------------------------------------
DB_PORT = 3306
DB_NAME = "text_service"
DB_HOST = 'localhost'

print(f'''
Defaults--------------
PORT : {DB_PORT}
HOST : {DB_HOST}
----------------------
''')
#---------------------------------------------------------------------

###############################Functions###############################

def port(timeout= 1, ip='localhost'):
    while True:
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
def exec(self, script = 'SELECT NULL AS null_set;'):
    try:
        self._connection.consume_results()
        for curs in self.execute(script, multi=True):
            print(curs.statement, '\nEXECUTED\n')
            if curs.with_rows:
                print(curs.fetchall())
    except mysql.connector.Error as e:
        print('ERROR ->\t', str(e).rjust(10))
#exec()
#__________________________________________________________________________
def server_connection(t = ''):
    while True:
        try:   
            h = host()
            print('Connect to server-----')
            o = mysql.connector.connect(
                host = h,
                port = port(h, 1),
                user = uname(),
                password = input('Enter password') or '',
                database=t
            )
            print('----------------------')
            if o:
                return o
        except mysql.connector.Error as e:
            print('-----------------------ERROR\n', str(e).rjust(3))
        except KeyboardInterrupt as k:
            sys.exit('Exit Signal')
            
    


