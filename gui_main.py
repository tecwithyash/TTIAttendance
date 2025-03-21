import wx
from gui_register import RegistrationFrame
from gui_login import LoginFrame
from gui_profile import ProfileFrame
from gui_admin import AdminFrame
from gui_dashboard import UserDashboardFrame
from gui_database import validate_admin


class MainApp(wx.Frame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.Maximize(True)
        self.SetTitle("Employee Management System")
        self.SetSize(400, 350)

        panel = wx.Panel(self)

        # Create a vertical box sizer to hold heading and buttons
        vbox = wx.BoxSizer(wx.VERTICAL)

        # Add Heading
        heading = wx.StaticText(panel, label="Welcome to Employee Attendance System")
        heading_font = wx.Font(14, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)
        heading.SetFont(heading_font)
        heading.SetForegroundColour("white")  # Optional: Make the heading stand out
        heading.SetBackgroundColour("black")  # Optional: Background color
        heading.Wrap(-1)  # Prevent line-breaking
        vbox.Add(heading, 0, wx.ALL | wx.ALIGN_CENTER_HORIZONTAL, 20)

        # Buttons for the main menu
        button_size = (250, 40)  # Define a uniform size for all buttons

        register_btn = wx.Button(panel, label="Register", size=button_size)
        login_btn = wx.Button(panel, label="Mark Your Attendance", size=button_size)
        profile_btn = wx.Button(panel, label="View Profile", size=button_size)
        dashboard_btn = wx.Button(panel, label="View Dashboard", size=button_size)
        admin_btn = wx.Button(panel, label="Admin Options", size=button_size)
        exit_btn = wx.Button(panel, label="Exit", size=button_size)

        # Bind button events to their respective methods
        register_btn.Bind(wx.EVT_BUTTON, self.open_registration)
        login_btn.Bind(wx.EVT_BUTTON, self.open_login)
        profile_btn.Bind(wx.EVT_BUTTON, self.open_profile)
        dashboard_btn.Bind(wx.EVT_BUTTON, self.open_dashboard)
        admin_btn.Bind(wx.EVT_BUTTON, self.open_admin)
        exit_btn.Bind(wx.EVT_BUTTON, self.on_exit)

        # Add buttons to the sizer with spacing
        vbox.Add(register_btn, 0, wx.ALL | wx.ALIGN_CENTER_HORIZONTAL, 10)
        vbox.Add(login_btn, 0, wx.ALL | wx.ALIGN_CENTER_HORIZONTAL, 10)
        vbox.Add(profile_btn, 0, wx.ALL | wx.ALIGN_CENTER_HORIZONTAL, 10)
        vbox.Add(dashboard_btn, 0, wx.ALL | wx.ALIGN_CENTER_HORIZONTAL, 10)
        vbox.Add(admin_btn, 0, wx.ALL | wx.ALIGN_CENTER_HORIZONTAL, 10)
        vbox.Add(exit_btn, 0, wx.ALL | wx.ALIGN_CENTER_HORIZONTAL, 10)

        # Set the sizer for the panel
        panel.SetSizer(vbox)

    def on_exit(self, event):
        """Closes the application."""
        self.Close()

    def open_registration(self, event):
        frame = RegistrationFrame(None, title="User Registration")
        frame.Show()

    def open_login(self, event):
        frame = LoginFrame(None, title="User Login")
        frame.Show()

    def open_profile(self, event):
        frame = ProfileFrame(None, title="View Profile")
        frame.Show()

    def open_dashboard(self, event):
        user_id = wx.GetTextFromUser("Enter your User ID:", "View Dashboard")
        if not user_id.isdigit():
            wx.MessageBox("Invalid User ID.", "Error", wx.OK | wx.ICON_ERROR)
            return

        frame = UserDashboardFrame(None, title="User Dashboard", user_id=int(user_id))
        frame.Show()

    def open_admin(self, event):
        user_id = wx.GetTextFromUser("Enter your Admin User ID:", "Admin Authentication")
        if not user_id or not user_id.isdigit():
            wx.MessageBox("Invalid Admin User ID. Please enter a numeric ID.", "Error", wx.OK | wx.ICON_ERROR)
            return

        username = wx.GetTextFromUser("Enter your Admin Username:", "Admin Authentication")
        if not username:
            wx.MessageBox("Username is required.", "Error", wx.OK | wx.ICON_ERROR)
            return

        password = wx.GetPasswordFromUser("Enter your password:", "Admin Authentication")
        if not password:
            wx.MessageBox("Password is required.", "Error", wx.OK | wx.ICON_ERROR)
            return

        is_admin, error_message = validate_admin(int(user_id), username, password)
        if not is_admin:
            if error_message:
                wx.MessageBox(f"Error: {error_message}", "Error", wx.OK | wx.ICON_ERROR)
            else:
                wx.MessageBox("Invalid Admin User ID, Username, or Password.", "Error", wx.OK | wx.ICON_ERROR)
            return

        frame = AdminFrame(None, title="Admin Options")
        frame.Show()


if __name__ == "__main__":
    app = wx.App(False)
    frame = MainApp(None)
    frame.Show()
    app.MainLoop()
