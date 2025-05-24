import sys
import os
import mysql.connector
from getpass import getpass

def connect_to_db():
    """Connect to the MySQL database using credentials"""
    print("Enter your MySQL credentials:")
    username = input("Username (default 'root'): ") or "root"
    password = getpass("Password: ")
    host = input("Host (default 'localhost'): ") or "localhost"
    db_name = input("Database name (default 'HotelManagementNew'): ") or "HotelManagementNew"
    
    try:
        connection = mysql.connector.connect(
            host=host,
            user=username,
            password=password,
            database=db_name
        )
        print("Connected to MySQL database!")
        return connection
    except mysql.connector.Error as err:
        print(f"Error connecting to MySQL: {err}")
        sys.exit(1)

def add_priority_column(connection):
    """Add the Priority column to the Maintenance table"""
    cursor = connection.cursor()
    
    try:
        # Check if the column already exists
        cursor.execute("SHOW COLUMNS FROM Maintenance LIKE 'Priority'")
        if cursor.fetchone():
            print("Priority column already exists in Maintenance table.")
            return
        
        # Add the Priority column
        cursor.execute("""
            ALTER TABLE Maintenance 
            ADD COLUMN Priority VARCHAR(20) NULL DEFAULT 'Medium'
        """)
        connection.commit()
        print("Priority column added to Maintenance table successfully!")
        
        # Update existing records to extract priority from Issue_Reported
        cursor.execute("SELECT Maintenance_ID, Issue_Reported FROM Maintenance")
        maintenance_records = cursor.fetchall()
        
        for maintenance_id, issue_reported in maintenance_records:
            priority = 'Medium'  # Default
            
            if issue_reported:
                if 'Priority: Emergency' in issue_reported:
                    priority = 'Emergency'
                elif 'Priority: High' in issue_reported:
                    priority = 'High'
                elif 'Priority: Medium' in issue_reported:
                    priority = 'Medium'
                elif 'Priority: Low' in issue_reported:
                    priority = 'Low'
            
            cursor.execute(
                "UPDATE Maintenance SET Priority = %s WHERE Maintenance_ID = %s",
                (priority, maintenance_id)
            )
        
        connection.commit()
        print(f"Updated priority values for {len(maintenance_records)} maintenance records.")
        
    except mysql.connector.Error as err:
        print(f"Error adding Priority column: {err}")
        connection.rollback()
    finally:
        cursor.close()

def check_customer_ids(connection):
    """Check which customers exist in the database"""
    cursor = connection.cursor()
    
    try:
        cursor.execute("SELECT Customer_ID, First_Name, Last_Name, Email FROM Customer")
        customers = cursor.fetchall()
        
        print("\nCustomers in database:")
        print("----------------------")
        for customer in customers:
            print(f"ID: {customer[0]}, Name: {customer[1]} {customer[2]}, Email: {customer[3]}")
            
        print("\nIf you're having issues with a specific user account, make note of their Customer_ID.")
        
    except mysql.connector.Error as err:
        print(f"Error checking customers: {err}")
    finally:
        cursor.close()

def check_maintenance_table(connection):
    """Check the structure of the Maintenance table"""
    cursor = connection.cursor()
    
    try:
        cursor.execute("DESCRIBE Maintenance")
        columns = cursor.fetchall()
        
        print("\nMaintenance Table Structure:")
        print("----------------------------")
        for column in columns:
            print(f"Column: {column[0]}, Type: {column[1]}, Null: {column[2]}, Key: {column[3]}, Default: {column[4]}")
        
    except mysql.connector.Error as err:
        print(f"Error checking Maintenance table: {err}")
    finally:
        cursor.close()

def main():
    """Main function to run the migration"""
    print("This script will add the Priority column to the Maintenance table.")
    connection = connect_to_db()
    
    try:
        check_maintenance_table(connection)
        check_customer_ids(connection)
        add_priority_column(connection)
        print("\nMigration completed successfully!")
    finally:
        if connection.is_connected():
            connection.close()
            print("Database connection closed.")

if __name__ == "__main__":
    main() 