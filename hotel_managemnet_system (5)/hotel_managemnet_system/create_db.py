import mysql.connector

# Create connection without specifying a database
cnx = mysql.connector.connect(
    user='root',
    password='Khamlesh@1234',
    host='localhost'
)

cursor = cnx.cursor()

# Create the database
cursor.execute("CREATE DATABASE IF NOT EXISTS HotelManagementNew")

print("Database created successfully!")

# Close the connection
cnx.close() 