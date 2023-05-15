import os
import re
from collections import OrderedDict
from DataHandler import DataHandler
import constants as c

"""UserHandler: subclass of DataHandler
Manages the user database.
Implements properties and methods prescribed by DataHandler:
- paint_data_window: prints user table
- does the ui stuff for adding, editing, deleting users
- does the user login and holds the info (name, role, id) of the user to be used in other places
"""

class UserHandler(DataHandler):
    def __init__(self, file_name, rows_per_page, window_size):
        super().__init__(file_name, rows_per_page)
        self.window_size = window_size

#Implemented abstract attributes and methods from DataHandler
    @property
    def window_size(self):
        return self._window_size

    @window_size.setter
    def window_size(self,size):
        self._window_size = size

    @property
    def max_id(self):
        return self._max_id

    @max_id.setter
    def max_id(self, id):
        try:
            if self._max_id < id:
                self._max_id = id
        except:
            self._max_id = 0

    def paint_data_window(self,mode):
        print(f"{c.COLOR_HEADER}Users{c.COLOR_NORMAL} (last updated {self.file_time_stamp} by {self.file_user})")
        print("┌" + "─" * (self.window_size - 2) + "┐")
        print("│  ID  User name                    User type    Status".ljust(self.window_size - 8) + f" {self.current_page:2d}/{self.total_pages:2d} │")
        print("├" + "─" * (self.window_size - 2) + "┤")
        if self.current_page == 0:
            self.print_empty_rows(self.rows_per_page)
            return
        start_row = (self.current_page - 1) * self.rows_per_page
        end_row = self.current_page * self.rows_per_page
        if end_row > self.data_rows:
            end_row = self.data_rows
        for key, record in list(self.data.items())[start_row:end_row]:
            print(f"│ {key:3d}. {record['Name'].ljust(29)}{record['Type'].ljust(13)}{record['Status'].ljust(self.window_size - 51)} │")
        self.print_empty_rows(self.rows_per_page - (end_row - start_row))

    def add_item(self):
        record={}
        while True:
            record["Name"] = input(f"{c.COLOR_INPUT}User name: {c.COLOR_NORMAL} ")
            if record["Name"].lower() == "q":
                return c.WINDOW_USERS + c.EVENT_VIEW_ITEMS
            test_id, test_record = self.fetch_record_by_key("Name", record["Name"])
            if test_record != None:
                print(f"{c.COLOR_WARNING}This user name already exists.{c.COLOR_NORMAL}")
            elif self.validate_user_name(record["Name"]):
                break

        while True:
            record["Type"] = input(f"{c.COLOR_INPUT}Set user type - admin or user - a/u:{c.COLOR_NORMAL} ").lower()
            if record["Type"] == "q":
                return c.WINDOW_USERS + c.EVENT_VIEW_ITEMS
            if record["Type"] in ["a","admin"]:
                record["Type"] = c.USER_TYPE_ADMIN
                break
            if record["Type"] in ["u","user"]:
                record["Type"] = c.USER_TYPE_USER
                break

        if input(f"{c.COLOR_INPUT}Do you really want to add user {record['Name']}? (y/n):{c.COLOR_NORMAL} ").lower() == "y":
            self.add_record(record)
            self.current_page = self.total_pages
        
        return c.WINDOW_USERS + c.EVENT_VIEW_ITEMS

    def edit_item(self):
        record_id = self.ask_for_id()
        if record_id == None:
            return c.WINDOW_USERS + c.EVENT_VIEW_ITEMS
        record = self.data[record_id]

        while True:
            str = input(f"{c.COLOR_INPUT}Enter new user name or press enter to leave it unchanged:{c.COLOR_NORMAL} ")
            if str.lower() == "q":
                return c.WINDOW_USERS + c.EVENT_VIEW_ITEMS
            if str == "":
                break
            if self.validate_user_name(str):
                record["Name"] = str
                break

        while True:
            str = input(f"{c.COLOR_INPUT}Set user type - admin or user - a/u:{c.COLOR_NORMAL} ").lower()
            if str == "q":
                return c.WINDOW_USERS + c.EVENT_VIEW_ITEMS
            if str in ["a","admin"]:
                record["Type"] = c.USER_TYPE_ADMIN
                break
            if str in ["u","user"]:
                record["Type"] = c.USER_TYPE_USER
                break

        if input(f"{c.COLOR_INPUT}Do you really want to update user {self.data[record_id]['Name']}? (y/n):{c.COLOR_NORMAL} ").lower() == "y":
            self.update_record(record_id,record)
        return c.WINDOW_USERS + c.EVENT_VIEW_ITEMS
      
    def toggle_item_flag(self):
# We have nothing to toggle in user. Nor anybody to tickle. :)
        pass

# Stuff created by this class
# Attributes
    @property
    def current_user(self):
        return self._current_user
    
    @current_user.setter
    def current_user(self,user_name):
        self._current_user = user_name

    @property
    def current_user_id(self):
        return self._current_user_id
    
    @current_user_id.setter
    def current_user_id(self,user_id):
        self._current_user_id = user_id

    @property
    def current_user_role(self):
        return self._current_user_role
    
    @current_user_role.setter
    def current_user_role(self,user_role):
        self._current_user_role = user_role

# Methods        
    def user_login(self):
        os.system('cls' if os.name == 'nt' else 'clear')
        cnt = 0
        print(f"{c.COLOR_HEADER}Welcome to our Quizz Machine!{c.COLOR_NORMAL}\n\nPlease log in and train your brain.\n\n")
        while cnt < 3:
            user_name = input(f"{c.COLOR_INPUT}Enter your user name (or q + enter to cancel):{c.COLOR_NORMAL} ")
            if user_name.lower() == "q":
                break
            record_id, record = self.fetch_record_by_key("Name",user_name)
            if record == None:
                cnt += 1
                print(f"{c.COLOR_WARNING}Login failed.{c.COLOR_NORMAL}")
                continue
            self.current_user = record["Name"]
            self.current_user_role = record["Type"]
            self.current_user_ID = record_id
            return True
        return False

    def validate_user_name(self,user_name):
        pattern = r"\W"
        if re.search(pattern,user_name):
            print(f"{c.COLOR_WARNING}You can only use letters, numbers and underscore in a user name.{c.COLOR_NORMAL}")
            return False
        if len(user_name) > 10:
            print(f"{c.COLOR_WARNING}A user name cannot be longer than 10 characters.{c.COLOR_NORMAL}")
            return False
        return True
