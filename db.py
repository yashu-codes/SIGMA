import mysql.connector

connection = mysql.connector.connect(
    host="localhost",
    user="root",
    password="yashusql@cse16",
    database="mineguard_nexus"
)

print("MySQL connected successfully!")

connection.close()