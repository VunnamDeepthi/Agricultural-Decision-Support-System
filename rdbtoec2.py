pip install mysql-connector-python
import mysql.connector
from mysql.connector import Error

# Database connection configuration
db_config = {
    'host': 'database-2.cercrmi7ai1b.us-west-1.rds.amazonaws.com',     # Replace with your MySQL host
    'user': 'admin',     # Replace with your MySQL user
    'password': 'admin123',  # Replace with your MySQL password
    'database': 'test',
    'raise_on_warnings': True
}

# Function to establish a connection to MySQL
def create_connection():
    connection = None
    try:
        connection = mysql.connector.connect(**db_config)
        if connection.is_connected():
            print(f"Connected to MySQL Server version {connection.get_server_info()}")
        return connection
    except Error as e:
        print(f"Error: {e}")
        return None

# Function to create a sample table
def create_sample_table(connection):
    create_table_query = """
        CREATE TABLE IF NOT EXISTS sample_table (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(255),
            age INT
        )
    """
    try:
        cursor = connection.cursor()
        cursor.execute(create_table_query)
        print("Sample table created successfully.")
        cursor.close()
    except Error as e:
        print(f"Error: {e}")

# Function to insert data into the sample table
def insert_data(connection, name, age):
    insert_query = "INSERT INTO sample_table (name, age) VALUES (%s, %s)"
    data = (name, age)
    try:
        cursor = connection.cursor()
        cursor.execute(insert_query, data)
        connection.commit()
        print("Data inserted successfully.")
        cursor.close()
    except Error as e:
        print(f"Error: {e}")

# Function to update data in the sample table
def update_data(connection, user_id, new_age):
    update_query = "UPDATE sample_table SET age = %s WHERE id = %s"
    data = (new_age, user_id)
    try:
        cursor = connection.cursor()
        cursor.execute(update_query, data)
        connection.commit()
        print("Data updated successfully.")
        cursor.close()
    except Error as e:
        print(f"Error: {e}")

# Function to delete data from the sample table
def delete_data(connection, user_id):
    delete_query = "DELETE FROM sample_table WHERE id = %s"
    data = (user_id,)
    try:
        cursor = connection.cursor()
        cursor.execute(delete_query, data)
        connection.commit()
        print("Data deleted successfully.")
        cursor.close()
    except Error as e:
        print(f"Error: {e}")

# Function to select and display all data from the sample table
def select_all_data(connection):
    select_query = "SELECT * FROM sample_table"
    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute(select_query)
        rows = cursor.fetchall()
        if rows:
            for row in rows:
                print(f"ID: {row['id']}, Name: {row['name']}, Age: {row['age']}")
        else:
            print("No data found.")
        cursor.close()
    except Error as e:
        print(f"Error: {e}")

# Main function
def main():
    connection = create_connection()
    if connection:
        create_sample_table(connection)

        # Insert sample data
        insert_data(connection, 'John Doe', 25)
        insert_data(connection, 'Jane Doe', 30)

        # Display initial data
        print("\nInitial Data:")
        select_all_data(connection)

        # Update data
        update_data(connection, 1, 26)

        # Display updated data
        print("\nUpdated Data:")
        select_all_data(connection)

        # Delete data
        delete_data(connection, 2)

        # Display final data
        print("\nFinal Data:")
        select_all_data(connection)

        # Close the connection
        connection.close()

if __name__ == "__main__":
    main()
