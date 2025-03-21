import wx
from gui_database import get_connection

class ProfileFrame(wx.Frame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.Maximize(True)
        self.SetSize(400, 300)
        panel = wx.Panel(self)

        # Go to Main Menu Button
        main_menu_btn = wx.Button(panel, label="Go to Main Menu", pos=(150, 250))
        main_menu_btn.Bind(wx.EVT_BUTTON, self.go_to_main_menu)

        # Form Fields
        wx.StaticText(panel, label="User ID:", pos=(20, 30))
        self.user_id_input = wx.TextCtrl(panel, pos=(100, 30), size=(150, -1))

        view_btn = wx.Button(panel, label="View Profile", pos=(100, 70))
        view_btn.Bind(wx.EVT_BUTTON, self.on_view_profile)

    def on_view_profile(self, event):
        user_id = self.user_id_input.GetValue()

        conn = get_connection()
        if not conn:
            wx.MessageBox("Database connection error!", "Error", wx.OK | wx.ICON_ERROR)
            return

        cursor = conn.cursor()
        try:
            # Fetch user details
            cursor.execute('''
                SELECT username, registration_date
                FROM Users
                WHERE user_id = ?
            ''', (user_id,))
            user = cursor.fetchone()

            if user:
                wx.MessageBox(f"User: {user[0]}\nRegistered On: {user[1]}", "Profile", wx.OK | wx.ICON_INFORMATION)
            else:
                wx.MessageBox("No profile found for the given User ID.", "Error", wx.OK | wx.ICON_ERROR)

        except Exception as e:
            wx.MessageBox(f"Error: {e}", "Error", wx.OK | wx.ICON_ERROR)
        finally:
            cursor.close()
            conn.close()

    def go_to_main_menu(self, event):
        self.Close()
        main_menu = MainMenuFrame(None, title="Main Menu")
        main_menu.Show()