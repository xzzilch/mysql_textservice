import sys
import threading
import time
import mysql.connector as my
from openports import *
from queries import *

# Define your database name variable (or pull this from your json config!)
DB_NAME = "text_service"

# SCRIPTS--------------------------------------------------------
script_template = '''
CREATE DATABASE IF NOT EXISTS {DB_NAME};
USE {DB_NAME};

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
    uuid INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL
);

DROP USER IF EXISTS 'guest'@'%';
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
        INSERT INTO users (user_id, username, password) 
        VALUES (NEW.uuid, NEW.username, NEW.password);
    END IF;
END;
'''

# CONNECT-----------------------------------------------------------
conn = server_connection()
try:
    cur = conn.cursor()
except my.Error as e:
    print('------------------ERROR\n', str(e).rjust(3))
    sys.exit(1)  # Stop execution if cursor fails

# CREATE_DB---------------------------------------------------------
try:
    # In version 9.2+, this handles the entire multi-statement string natively
    cur.execute(script, map_results=True)
    
    for statement, result_set in cur.fetchsets():
        print(f"Executed: {statement}\n\n", result_set)
    else:
        # Commit moved INSIDE the success block
        conn.commit()
        print("SCHEMA CREATED SUCCESSFULLY")
    
except my.Error as e:
    print("Error -> ", e, "\n\nRolling back...")
    conn.rollback()
    print("Done")

finally:
    cur.close()
    conn.close()
