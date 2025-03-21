import wx
from gui_database import fetch_notifications, approve_employee, get_connection


class AdminFrame(wx.Frame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.Maximize(True)
        self.SetSize(600, 600)
        self.SetTitle("Admin Dashboard")
        panel = wx.Panel(self)

        # Go to Main Menu Button
        main_menu_btn = wx.Button(panel, label="Go to Main Menu", pos=(150, 250))
        main_menu_btn.Bind(wx.EVT_BUTTON, self.go_to_main_menu)

        # Notifications Panel
        wx.StaticText(panel, label="Notifications:", pos=(20, 20))
        self.notifications_list = wx.ListCtrl(
            panel, pos=(20, 50), size=(550, 200), style=wx.LC_REPORT | wx.BORDER_SUNKEN
        )
        self.notifications_list.InsertColumn(0, "Notification ID", width=100)
        self.notifications_list.InsertColumn(1, "Message", width=300)
        self.notifications_list.InsertColumn(2, "Created At", width=150)

        # Users Panel
        wx.StaticText(panel, label="Users:", pos=(20, 270))
        self.users_list = wx.ListCtrl(
            panel, pos=(20, 300), size=(550, 200), style=wx.LC_REPORT | wx.BORDER_SUNKEN
        )
        self.users_list.InsertColumn(0, "User ID", width=100)
        self.users_list.InsertColumn(1, "Username", width=200)
        self.users_list.InsertColumn(2, "Designation", width=150)

        # Buttons for Admin Actions
        view_notifications_btn = wx.Button(panel, label="Refresh Notifications", pos=(20, 520))
        view_notifications_btn.Bind(wx.EVT_BUTTON, self.view_notifications)

        approve_employee_btn = wx.Button(panel, label="Approve Selected Employee", pos=(180, 520))
        approve_employee_btn.Bind(wx.EVT_BUTTON, self.approve_selected_employee)

        refresh_users_btn = wx.Button(panel, label="Refresh Users", pos=(340, 520))
        refresh_users_btn.Bind(wx.EVT_BUTTON, self.view_users)

        delete_user_btn = wx.Button(panel, label="Delete Selected User", pos=(460, 520))
        delete_user_btn.Bind(wx.EVT_BUTTON, self.delete_selected_user)

        # Load Notifications and Users on Start
        self.view_notifications(None)
        self.view_users(None)

    def view_notifications(self, event):
        # Clear the existing list
        self.notifications_list.DeleteAllItems()

        # Fetch notifications from the database for Admin
        notifications, error = fetch_notifications(role="Admin")

        if error:
            wx.MessageBox(error, "Error", wx.OK | wx.ICON_ERROR)
            return

        # Populate the notifications list
        for notification in notifications:
            index = self.notifications_list.InsertItem(
                self.notifications_list.GetItemCount(), str(notification[0])
            )
            self.notifications_list.SetItem(index, 1, notification[2])  # Message
            self.notifications_list.SetItem(index, 2, str(notification[3]))  # Created At

    def view_users(self, event):
        # Clear the existing users list
        self.users_list.DeleteAllItems()

        # Fetch users from the database
        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT user_id, username, designation FROM Users")
            users = cursor.fetchall()

            for user in users:
                index = self.users_list.InsertItem(self.users_list.GetItemCount(), str(user[0]))
                self.users_list.SetItem(index, 1, user[1])
                self.users_list.SetItem(index, 2, user[2])

        except Exception as e:
            wx.MessageBox(f"Error: {e}", "Error", wx.OK | wx.ICON_ERROR)
        finally:
            cursor.close()
            conn.close()

    def approve_selected_employee(self, event):
        # Get the selected notification
        selected_item = self.notifications_list.GetFirstSelected()
        if selected_item == -1:
            wx.MessageBox("Please select a notification.", "Error", wx.OK | wx.ICON_ERROR)
            return

        # Extract Notification ID and Message
        notification_id = self.notifications_list.GetItemText(selected_item, 0)
        notification_message = self.notifications_list.GetItemText(selected_item, 1)

        # Extract Username from the Notification Message
        if "registered:" in notification_message:
            username = notification_message.split("registered: ")[1]
        else:
            wx.MessageBox("Invalid notification format.", "Error", wx.OK | wx.ICON_ERROR)
            return

        # Get User Details from the database
        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                "SELECT user_id, designation FROM Users WHERE username = ?", (username,)
            )
            result = cursor.fetchone()

            if result:
                user_id, designation = result
                # Show confirmation dialog with username and designation
                confirmation = wx.MessageBox(
                    f"Do you want to approve the user '{username}' with the designation '{designation}'?",
                    "Approve User",
                    wx.YES_NO | wx.ICON_QUESTION,
                )
                if confirmation == wx.YES:
                    # Approve the user
                    success, error = approve_employee(user_id)
                    if success:
                        # Delete the notification after successful approval
                        cursor.execute(
                            "DELETE FROM Notifications WHERE notification_id = ?",
                            (notification_id,),
                        )
                        conn.commit()
                        wx.MessageBox(
                            f"User '{username}' ({designation}) approved successfully!",
                            "Success",
                            wx.OK | wx.ICON_INFORMATION,
                        )
                        self.view_notifications(None)  # Refresh the list
                    else:
                        wx.MessageBox(error, "Error", wx.OK | wx.ICON_ERROR)
            else:
                wx.MessageBox("User not found.", "Error", wx.OK | wx.ICON_ERROR)
        except Exception as e:
            wx.MessageBox(f"Error: {e}", "Error", wx.OK | wx.ICON_ERROR)
        finally:
            cursor.close()
            conn.close()

    def delete_selected_user(self, event):
        # Get the selected user
        selected_item = self.users_list.GetFirstSelected()
        if selected_item == -1:
            wx.MessageBox("Please select a user to delete.", "Error", wx.OK | wx.ICON_ERROR)
            return

        # Extract User ID and Username
        user_id = self.users_list.GetItemText(selected_item, 0)
        username = self.users_list.GetItemText(selected_item, 1)

        # Confirm deletion
        confirmation = wx.MessageBox(
            f"Are you sure you want to delete the user '{username}' and all their associated details?",
            "Confirm Deletion",
            wx.YES_NO | wx.ICON_WARNING,
        )
        if confirmation != wx.YES:
            return

        # Delete user and associated data
        conn = get_connection()
        cursor = conn.cursor()
        try:
            # Delete user's data from related tables
            cursor.execute("DELETE FROM Attendance WHERE user_id = ?", (user_id,))
            cursor.execute("DELETE FROM Salary WHERE user_id = ?", (user_id,))
            cursor.execute(
                "DELETE FROM Notifications WHERE message LIKE ?", (f"%{username}%",)
            )
            cursor.execute("DELETE FROM Users WHERE user_id = ?", (user_id,))
            conn.commit()

            wx.MessageBox(
                f"User '{username}' and all associated details deleted successfully.",
                "Success",
                wx.OK | wx.ICON_INFORMATION,
            )
            self.view_users(None)  # Refresh the users list
        except Exception as e:
            wx.MessageBox(f"Error: {e}", "Error", wx.OK | wx.ICON_ERROR)
        finally:
            cursor.close()
            conn.close()

    def go_to_main_menu(self, event):
        self.Close()
        main_menu = MainMenuFrame(None, title="Main Menu")
        main_menu.Show()