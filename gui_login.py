import wx
from gui_database import get_connection, update_weekly_salary
from datetime import datetime
import bcrypt


class LoginFrame(wx.Frame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.Maximize(True)
        self.SetSize(300, 200)
        panel = wx.Panel(self)

        # Go to Main Menu Button
        main_menu_btn = wx.Button(panel, label="Go to Main Menu", pos=(150, 250))
        main_menu_btn.Bind(wx.EVT_BUTTON, self.go_to_main_menu)

        # Form Fields
        wx.StaticText(panel, label="Username:", pos=(20, 30))
        self.username_input = wx.TextCtrl(panel, pos=(100, 30), size=(150, -1))

        wx.StaticText(panel, label="Password:", pos=(20, 70))
        self.password_input = wx.TextCtrl(panel, pos=(100, 70), size=(150, -1), style=wx.TE_PASSWORD)

        # Login Button
        login_btn = wx.Button(panel, label="Mark Present", pos=(100, 120))
        login_btn.Bind(wx.EVT_BUTTON, self.on_login)

    def on_login(self, event):
        username = self.username_input.GetValue()
        password = self.password_input.GetValue()

        conn = get_connection()
        if not conn:
            wx.MessageBox("Database connection error!", "Error", wx.OK | wx.ICON_ERROR)
            return

        cursor = conn.cursor()
        try:
            # Validate user credentials
            cursor.execute("SELECT user_id, password, designation, is_approved FROM Users WHERE username = ?", (username,))
            result = cursor.fetchone()

            if not result:
                wx.MessageBox("Username not found.", "Error", wx.OK | wx.ICON_ERROR)
                return

            user_id, hashed_password, designation, is_approved = result

            # Check approval status
            if not is_approved:
                wx.MessageBox("Your account is not yet approved by the admin.", "Error", wx.OK | wx.ICON_ERROR)
                return

            # Verify password
            if not bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8')):
                wx.MessageBox("Invalid password.", "Error", wx.OK | wx.ICON_ERROR)
                return

            # Check if the user has already logged in today
            today = datetime.now().date()
            cursor.execute("""
                SELECT COUNT(*) FROM Attendance 
                WHERE user_id = ? AND attendance_date = ?
            """, (user_id, today))
            login_count = cursor.fetchone()[0]

            if login_count > 0:
                wx.MessageBox("You have already logged in today.", "Error", wx.OK | wx.ICON_ERROR)
                return

            # Mark attendance for today
            cursor.execute("""
                INSERT INTO Attendance (user_id, attendance_date, status) 
                VALUES (?, ?, 'Present')
            """, (user_id, today))
            conn.commit()

            # Update weekly salary
            update_weekly_salary(user_id, designation)

            wx.MessageBox("Login successful!", "Success", wx.OK | wx.ICON_INFORMATION)
            self.Close()

        except Exception as e:
            wx.MessageBox(f"Error: {e}", "Error", wx.OK | wx.ICON_ERROR)
        finally:
            cursor.close()
            conn.close()

    def go_to_main_menu(self, event):
        self.Close()
        main_menu = MainMenuFrame(None, title="Main Menu")
        main_menu.Show()