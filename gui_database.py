import wx
import pyodbc
import bcrypt
from datetime import datetime, timedelta

# Connection string for SQL Server
CONNECTION_STRING = r'Driver={ODBC Driver 17 for SQL Server};Server=MSI\SQLEXPRESS;Database=EmployeeManagement;Trusted_Connection=yes;'

# Function to establish a database connection
def get_connection():
    try:
        conn = pyodbc.connect(CONNECTION_STRING, autocommit=False)  # Explicitly disable autocommit
        return conn
    except pyodbc.Error as ex:
        print(f"Database connection error: {ex}")
        return None

#Function for register the new user.
def register_user_in_db(username, password, role, designation):
    conn = get_connection()
    if not conn:
        return None, "Database connection error!"

    cursor = conn.cursor()
    try:
        conn.autocommit = False  # Explicitly disable autocommit for transaction handling

        # Check if the username already exists
        cursor.execute("SELECT COUNT(*) FROM Users WHERE username = ?", (username,))
        if cursor.fetchone()[0] > 0:
            return None, "Username already exists. Please choose a different username."

        # Ensure only one admin can exist
        if role == "Admin":
            cursor.execute("SELECT COUNT(*) FROM Users WHERE role = 'Admin'")
            if cursor.fetchone()[0] > 0:
                return None, "An admin already exists."

        # Hash the password using bcrypt
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

        # Insert the new user into the Users table and capture the inserted user_id
        cursor.execute('''
            INSERT INTO Users (username, password, role, designation, is_approved)
            VALUES (?, ?, ?, ?, ?);
        ''', (username, hashed_password, role, designation, 0))

        # Use IDENT_CURRENT to get the last identity value for the Users table
        cursor.execute("SELECT IDENT_CURRENT('Users')")
        result = cursor.fetchone()
        if result is None or result[0] is None:
            conn.rollback()
            return None, "Failed to retrieve the new user ID."
        
        user_id = int(result[0])

        # Commit the transaction
        conn.commit()

        return user_id, None
    except Exception as e:
        conn.rollback()
        return None, f"Error: {e}"
    finally:
        cursor.close()
        conn.close()

# Function to validate user login
def validate_login(username, password):
    conn = get_connection()
    if not conn:
        return False, "Database connection error!"

    cursor = conn.cursor()
    try:
        # Fetch hashed password for the given username
        cursor.execute("SELECT password, is_approved FROM Users WHERE username = ?", (username,))
        result = cursor.fetchone()

        if not result:
            return False, "Username not found."

        hashed_password, is_approved = result

        # Ensure the user is approved by the admin
        if not is_approved:
            return False, "Your account is not yet approved by the admin."

        # Verify the password using bcrypt
        if bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8')):
            return True, None  # Login successful
        else:
            return False, "Invalid password."
    except Exception as e:
        return False, f"Error: {e}"
    finally:
        cursor.close()
        conn.close()

# Function to fetch user profile data
def fetch_user_profile(user_id):
    conn = get_connection()
    if not conn:
        return None, "Database connection error!"

    cursor = conn.cursor()
    try:
        # Fetch user profile data
        cursor.execute('''
            SELECT username, registration_date, designation
            FROM Users
            WHERE user_id = ?
        ''', (user_id,))
        user = cursor.fetchone()

        if user:
            return user, None  # Return user data and no error
        else:
            return None, "User ID not found."
    except Exception as e:
        return None, f"Error: {e}"
    finally:
        cursor.close()
        conn.close()

# Function to fetch notifications for the admin
def fetch_notifications(role=None, user_id=None):
    """
    Fetch notifications based on user role or ID.
    Admins see all notifications; Employees see their own.
    """
    conn = get_connection()
    if not conn:
        return None, "Database connection error!"

    cursor = conn.cursor()
    try:
        if role == "Admin":
            # Admin sees all notifications
            cursor.execute("""
                SELECT notification_id, user_id, message, created_at
                FROM Notifications
                ORDER BY created_at DESC
            """)
        elif user_id:
            # Employees see only their notifications
            cursor.execute("""
                SELECT notification_id, user_id, message, created_at
                FROM Notifications
                WHERE user_id = ?
                ORDER BY created_at DESC
            """, (user_id,))
        else:
            return None, "Invalid role or user ID."

        return cursor.fetchall(), None
    except Exception as e:
        return None, f"Error: {e}"
    finally:
        cursor.close()
        conn.close()

# Function to approve a new employee
def approve_employee(user_id):
    conn = get_connection()
    if not conn:
        return False, "Database connection error!"

    cursor = conn.cursor()
    try:
        # Approve the employee
        cursor.execute("UPDATE Users SET is_approved = 1 WHERE user_id = ?", (user_id,))
        if cursor.rowcount == 0:
            return False, "Employee not found."

        # Mark the notification as resolved (optional: add a resolved column to Notifications table)
        cursor.execute("""
            UPDATE Notifications
            SET message = CONCAT(message, ' (Approved)')
            WHERE user_id = ?;
        """, (user_id,))
        conn.commit()

        return True, None
    except Exception as e:
        conn.rollback()
        return False, f"Error: {e}"
    finally:
        cursor.close()
        conn.close()

# Function to fetch all attendance records
def fetch_attendance(user_id):
    conn = get_connection()
    if not conn:
        return None, "Database connection error!"

    cursor = conn.cursor()
    try:
        # Fetch attendance records for the given user
        cursor.execute('''
            SELECT attendance_date, status
            FROM Attendance
            WHERE user_id = ?
            ORDER BY attendance_date DESC
        ''', (user_id,))
        return cursor.fetchall(), None
    except Exception as e:
        return None, f"Error: {e}"
    finally:
        cursor.close()
        conn.close()


def validate_admin(user_id, username, password):
    conn = get_connection()
    if not conn:
        return False, "Database connection error!"

    cursor = conn.cursor()
    try:
        # Debug statement to log user_id and username
        print(f"Validating Admin: User ID: {user_id}, Username: {username}")

        # Check if the admin ID and username exist and fetch the hashed password
        cursor.execute("SELECT role, password FROM Users WHERE user_id = ? AND username = ? AND role = 'Admin'", (user_id, username))
        result = cursor.fetchone()

        # Debug statement to log the result of the query
        print(f"Query Result: {result}")

        if not result:
            return False, "Invalid Admin User ID or Username."

        role, hashed_password = result

        # Debug statement to log the retrieved role and hashed_password
        print(f"Retrieved Role: {role}, Retrieved Hashed Password: {hashed_password}")

        # Verify the entered password against the stored hash
        if bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8')):
            return True, None  # Admin authentication successful
        else:
            return False, "Incorrect password."
    except Exception as e:
        return False, f"Error: {e}"
    finally:
        cursor.close()
        conn.close()



def update_weekly_salary(user_id, designation):
    conn = get_connection()
    if not conn:
        wx.MessageBox("Database connection error!", "Error", wx.OK | wx.ICON_ERROR)
        return
    
    cursor = conn.cursor()
    try:
        # Weekly Salary for Each Designation
        salary_mapping = {
            "developer": 15000,
            "intern": 5000,
            "team lead": 20000,
            "manager": 25000
        }
        
        weekly_salary = salary_mapping.get(designation.lower(), 0)
        per_day_salary = weekly_salary / 5  # Weekly salary divided by 5 workdays
        
        # Calculate Weekly Attendance (Monday to Sunday)
        today = datetime.now().date()
        start_of_week = today - timedelta(days=today.weekday())  # Get Monday
        end_of_week = start_of_week + timedelta(days=6)  # Get Sunday

        # Fetch attendance records for the week
        cursor.execute("""
            SELECT COUNT(*) FROM Attendance 
            WHERE user_id = ? AND attendance_date BETWEEN ? AND ? AND status = 'Present'
        """, (user_id, start_of_week, end_of_week))  # Use 'Present' instead of 1
        present_days = cursor.fetchone()[0]

        # Calculate absent days
        absent_days = 5 - present_days

        # Calculate weekly salary adjustment
        if absent_days == 0:
            salary_to_add = weekly_salary
        else:
            salary_to_add = weekly_salary - (per_day_salary * absent_days)

        # Update total salary in Salary Table
        cursor.execute("""
            UPDATE Salary 
            SET amount = amount + ? 
            WHERE user_id = ?
        """, (salary_to_add, user_id))
        conn.commit()

    except Exception as e:
        wx.MessageBox(f"Error updating salary: {e}", "Error", wx.OK | wx.ICON_ERROR)
    finally:
        cursor.close()
        conn.close()
