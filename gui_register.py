import wx
from gui_database import register_user_in_db

class RegistrationFrame(wx.Frame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.Maximize(True)
        self.SetSize(400, 450)
        self.SetTitle("User Registration")
        panel = wx.Panel(self)

        # Form Fields
        wx.StaticText(panel, label="Username:", pos=(20, 30))
        self.username_input = wx.TextCtrl(panel, pos=(150, 30), size=(200, -1))

        wx.StaticText(panel, label="Password:", pos=(20, 70))
        self.password_input = wx.TextCtrl(panel, pos=(150, 70), size=(200, -1), style=wx.TE_PASSWORD)

        wx.StaticText(panel, label="Confirm Password:", pos=(20, 110))
        self.confirm_password_input = wx.TextCtrl(panel, pos=(150, 110), size=(200, -1), style=wx.TE_PASSWORD)

        # Checkbox for Admin Role
        self.admin_checkbox = wx.CheckBox(panel, label="Register as Admin", pos=(150, 150))

        # Dropdown for Designation
        wx.StaticText(panel, label="Designation:", pos=(20, 190))
        self.designation_dropdown = wx.Choice(panel, pos=(150, 190), size=(200, -1),
                                              choices=["None", "Manager", "Team Lead", "Developer", "Intern"])

        # Register Button
        register_btn = wx.Button(panel, label="Register", pos=(150, 240))
        register_btn.Bind(wx.EVT_BUTTON, self.on_register)

        # Go to Main Menu Button
        main_menu_btn = wx.Button(panel, label="Go to Main Menu", pos=(150, 290))
        main_menu_btn.Bind(wx.EVT_BUTTON, self.go_to_main_menu)

    def on_register(self, event):
        username = self.username_input.GetValue()
        password = self.password_input.GetValue()
        confirm_password = self.confirm_password_input.GetValue()
        role = "Admin" if self.admin_checkbox.GetValue() else "Employee"
        designation = self.designation_dropdown.GetStringSelection()

        # Validate Inputs
        if not username or not password or not confirm_password:
            wx.MessageBox("All fields are required.", "Error", wx.OK | wx.ICON_ERROR)
            return

        # Check if passwords match
        if password != confirm_password:
            wx.MessageBox("Passwords do not match. Please try again.", "Error", wx.OK | wx.ICON_ERROR)
            return

        # Salary Map
        salary_map = {
            "Manager": 100000,
            "Team Lead": 80000,
            "Developer": 60000,
            "Intern": 20000,
            "None": 0
        }
        salary = salary_map.get(designation, 0)

        # Register User
        user_id, error = register_user_in_db(username, password, role, designation)

        if error:
            wx.MessageBox(error, "Error", wx.OK | wx.ICON_ERROR)
        else:
            wx.MessageBox(f"Registration successful! Your User ID is: {user_id}", "Success", wx.OK | wx.ICON_INFORMATION)
            self.Close()

    def go_to_main_menu(self, event):
        self.Close()
        main_menu = MainMenuFrame(None, title="Main Menu")
        main_menu.Show()
