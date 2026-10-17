#Config--------------------------------------------------------------
DB_PORT = 3306
DB_NAME = "text_service"
DB_HOST = 'localhost'
#---------------------------------------------------------------------

def cfg():
  print(f'''
  Defaults--------------
  PORT : {DB_PORT}
  HOST : {DB_HOST}
  ----------------------
  ''')

if __name__ == '__main__':
  print(globals())
