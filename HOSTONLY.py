import sys
import time
import mysql.connector as my
from openports import *
from chat_functions import *  # Contains your server_connection and sqlscript definitions

# Define your database name variable (or pull this from your json config!)
DB_NAME = "text_service"

# SCRIPTS--------------------------------------------------------
# Read dynamic multi-statement parameters out of local config files
script_payload = sqlscript(sql_script="text_service_schema.sql", json_cfg="DB_METADATA.json")

if not script_payload:
    print("Schema installation terminated: SQL script source string empty.")
    sys.exit(1)

# CONNECT-----------------------------------------------------------
conn = server_connection()
try:
    cur = conn.cursor()
except my.Error as e:
    print('------------------ERROR\n', str(e).rjust(3))
    sys.exit(1)  # Stop execution if cursor fails

# CREATE_DB---------------------------------------------------------
try:
    print("Initializing multi-statement database provisioning sequence...")
    
    # Utilizing MySQL Connector 9.2+ native unified batch execution mode
    cur.execute(script_payload, map_results=True)
    
    # Loop through the modern generator returning (statement, result_set) tuples
    for statement, result_set in cur.fetchsets():
        # Flush each underlying statement result out of the pipeline buffer
        if result_set:
            pass
            
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
