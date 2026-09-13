import mysql.connector

connection = mysql.connector.connect(
    host="localhost",
    user="root",
    password="your_actual_password",
    database="mineguard_nexus"
)

print("MySQL connected successfully!")

connection.close()
