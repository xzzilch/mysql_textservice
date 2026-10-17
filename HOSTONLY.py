
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
CREATE DATABASE IF NOT EXISTS {DB_NAME};

CREATE TABLE IF NOT EXISTS users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL
);

CREATE TABLE IF NOT EXISTS sessions (
    session_id INT AUTO_INCREMENT PRIMARY KEY,
    user1_id INT NOT NULL,
    user2_id INT NOT NULL,
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS messages (
    message_id INT AUTO_INCREMENT PRIMARY KEY,
    session_id INT NOT NULL,
    sender_id INT NOT NULL,
    message TEXT NOT NULL,
    sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS guests (
    uuid INT AUTO_INTCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL
);

CREATE USER 'guest'@'%';
GRANT SELECT ON {DB_NAME}.guests TO 'guest'@'%';
FLUSH PRIVILEGES;

CREATE TRIGGER before_guests_insert 
BEFORE INSERT ON guests 
FOR EACH ROW
BEGIN 
    IF EXISTS (SELECT 1 FROM users WHERE username = NEW.username) THEN
        SIGNAL SQLSTATE '45000' 
        SET MESSAGE_TEXT = 'Error: Username is already taken!';
    ELSE
        INSERT INTO users (uuid, username, password) 
        VALUES (NEW.uuid, NEW.username, NEW.password);
    END IF;
END
'''

#CONNECT-----------------------------------------------------------
db = server_connection()
try:
    cur = db.cursor()
except mysql.connector.Error as e:
    print('------------------ERROR\n', str(e).rjust(3))

#CREATE_DB---------------------------------------------------------
try:
    cur.execute(script, map_results = True)
    
    for statement, result_set in cur.fetchsets():
        print(f"Executed: {statement}\n\n", result_set)
except mysql.connector.Error as e:
    print("Error -> ", e)
        
db.commit()
db.close()

#______________________________________________________________________________________________
