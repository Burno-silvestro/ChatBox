import mysql.connector

class setupDB():

  def __init__(self):
    try:
      mydb = mysql.connector.connect(
        host="localhost",
        user="root",
        #password="password"
        database='ChatBox'
      )

      mycursor = mydb.cursor()
      #print('database esistente')

      try:
        # Crea la tabella users
        mycursor.execute("CREATE TABLE users (id INT AUTO_INCREMENT PRIMARY KEY, user_id VARCHAR(255), nickname VARCHAR(255), friend_list VARCHAR(255))")
        print('tabella creata')
      except Exception as errore:
        #print('tabella esistente', errore)
        pass
      
    except:
      mydb = mysql.connector.connect(
        host="localhost",
        user="root",
        #password="password"
      )

      mycursor = mydb.cursor()

      # Crea il database register
      mycursor.execute("CREATE DATABASE ChatBox")

      # Seleziona il database register
      mycursor.execute("USE ChatBox")

      # Crea la tabella users
      mycursor.execute("CREATE TABLE users (id INT AUTO_INCREMENT PRIMARY KEY, user_id VARCHAR(255), nickname VARCHAR(255) friend_list VARCHAR(255))")
      print('database creato')

  def remove(self):
    mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    #password="password",
    database="ChatBox"
    )

    mycursor = mydb.cursor()

    # Elimina il database mydatabase
    mycursor.execute("DROP DATABASE ChatBox")
    mydb.commit()

  def clear(self):
    db = mysql.connector.connect(
    host="localhost",
    user="root",
    #password="password",
    database="ChatBox"
    )

    mycursor = db.cursor()
    sql = "DELETE FROM users"
    mycursor.execute(sql)
    db.commit()