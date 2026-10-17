
#from queries import *
import threading
import time
from openports import *
from queries import *
import sys
import mysql.connector as my

#Create database and tables
#HOSTONLY

#SCRIPTS--------------------------------------------------------
script = '''

'''

#CONNECT-----------------------------------------------------------
db = server_connection()
try:
    cur = db.cursor()
except mysql.connector.Error as e:
    print('------------------ERROR\n', str(e).rjust(3))

#CREATE_DB---------------------------------------------------------
cur.execute(script)
db.commit()
db.close()

#______________________________________________________________________________________________
