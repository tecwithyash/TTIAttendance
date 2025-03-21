import wx
from gui_database import get_connection

class UserDashboardFrame(wx.Frame):
    def __init__(self, *args, user_id, **kwargs):
        super().__init__(*args, **kwargs)
        self.Maximize(True)
        self.SetSize(600, 400)
        self.user_id = user_id
        panel = wx.Panel(self)

        # Go to Main Menu Button
        main_menu_btn = wx.Button(panel, label="Go to Main Menu", pos=(150, 250))
        main_menu_btn.Bind(wx.EVT_BUTTON, self.go_to_main_menu)

        # User Details Section
        wx.StaticText(panel, label="User Details:", pos=(20, 20))
        self.user_details = wx.TextCtrl(panel, pos=(20, 50), size=(550, 100), style=wx.TE_MULTILINE | wx.TE_READONLY)

        # Attendance History Section
        wx.StaticText(panel, label="Attendance History:", pos=(20, 170))
        self.attendance_list = wx.ListCtrl(panel, pos=(20, 200), size=(550, 150),
                                           style=wx.LC_REPORT | wx.BORDER_SUNKEN)
        self.attendance_list.InsertColumn(0, "Date", width=200)
        self.attendance_list.InsertColumn(1, "Status", width=100)

        # Load Dashboard Data
        self.load_dashboard()

    def load_dashboard(self):
        conn = get_connection()
        if not conn:
            wx.MessageBox("Database connection error!", "Error", wx.OK | wx.ICON_ERROR)
            return

        cursor = conn.cursor()
        try:
            # Fetch User Details
            cursor.execute('''
                SELECT username, designation, registration_date
                FROM Users
                WHERE user_id = ?
            ''', (self.user_id,))
            user = cursor.fetchone()

            if not user:
                wx.MessageBox("User not found.", "Error", wx.OK | wx.ICON_ERROR)
                return

            username, designation, registration_date = user

            # Fetch Total Salary
            cursor.execute('''
                SELECT SUM(amount) AS total_salary
                FROM Salary
                WHERE user_id = ?
            ''', (self.user_id,))
            salary_result = cursor.fetchone()
            total_salary = salary_result[0] if salary_result and salary_result[0] else 0

            # Display User Details
            details = (f"User ID: {self.user_id}\n"
                       f"Username: {username}\n"
                       f"Designation: {designation}\n"
                       f"Registration Date: {registration_date}\n"
                       f"Total Salary: {total_salary}")
            self.user_details.SetValue(details)

            # Fetch Attendance History
            cursor.execute('''
                SELECT attendance_date, status
                FROM Attendance
                WHERE user_id = ?
                ORDER BY attendance_date DESC
            ''', (self.user_id,))
            attendance_records = cursor.fetchall()

            # Populate Attendance List
            self.attendance_list.DeleteAllItems()
            for record in attendance_records:
                index = self.attendance_list.InsertItem(self.attendance_list.GetItemCount(), str(record[0]))
                self.attendance_list.SetItem(index, 1, record[1])

        except Exception as e:
            wx.MessageBox(f"Error: {e}", "Error", wx.OK | wx.ICON_ERROR)
        finally:
            cursor.close()
            conn.close()

    def go_to_main_menu(self, event):
        self.Close()
        main_menu = MainMenuFrame(None, title="Main Menu")
        main_menu.Show()