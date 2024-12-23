import mysql.connector
import datetime

# Connect to the MySQL server
mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Vamsi@18",
    database="test"
)

# Create a cursor to interact with the database
mycursor = mydb.cursor()

# Execute a query to show all databases


# Create another cursor for your insert operation
query = "INSERT INTO fert (user_id, date, input, prediction, rating, review) VALUES (%s, %s, %s, %s, %s, %s)"
values = (1, datetime.datetime.now(), "hi", "p", None, None)

mycursor.execute(query, values)
mydb.commit()

