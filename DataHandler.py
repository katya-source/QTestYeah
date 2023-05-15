import csv
import math
import datetime
import sys
from abc import ABC,abstractmethod
from collections import OrderedDict
import constants as c

"""DataHandler: Abstract class
This program manages data as follows:
- data is read from a csv file into an OrderedDict (data)
- data manipulation is done to the OrderedDict
- data is saved by overwriting the csv file with the OrderedDict
This class handles the file operations and the data record operations with the OrderedDict.
It also prescribes some abstract properties and methods so that these can be referenced in other 
functions (e.g. display_data_window) by "DataHandler." instead of <object name.>.
There are also some window handling functions in the end which are used by all subclasses. So I 
put them here. :)
"""

class DataHandler(ABC):
    def __init__(self, file_name, rows_per_page):
        self.data_file_name = file_name
        self.rows_per_page = rows_per_page
        self.read_file()
        self.current_page = 1

# abstract attributes
# This is needed so that in windows functions these property can be accessed using DataHandler.<attribute name>
# Each subclass has to implement these getters and setters.
# window_size: the horizontal size of the window in number of characters
    @property
    @abstractmethod
    def window_size(self):
        pass

    @window_size.setter
    @abstractmethod
    def window_size(self,size):
        pass
    @property
    @abstractmethod
    def max_id(self):
        pass

    @max_id.setter
    @abstractmethod
    def max_id(self, id):
        pass

# abstract methods to be implemented by all subclasses
# paint_data_window: print a new screen specific to window and action
# ask_action: ui for user to choose an action (add, edit, next page etc.)
# add_item, edit_item, toggle_item_flag: ui for user to input data; calls corresponding data record operation
    @abstractmethod
    def paint_data_window(self,mode):
        pass

    @abstractmethod
    def ask_action(self):
        pass

    @abstractmethod
    def add_item(self):
        pass

    @abstractmethod
    def edit_item(self):
        pass

    @abstractmethod
    def toggle_item_flag(self):
        pass

# attributes    
# data_file_name has its .csv extension stripped so that it can be used to print the file name as topic name.
# max_id is responsible for creating unique record IDs.
# save_flag keeps track if the user made changes to the OrderedDict so we know if we need to write stuff back to disk.
# data_rows holds the number of records.
# current_page,total_pages is used for paging through the data on-screen.
    @property
    def data_file_name(self):
        return self._data_file_name

    @data_file_name.setter
    def data_file_name(self,file_name):
        self._data_file_name = file_name

    @property
    def save_flag(self):
        return self._save_flag
   
    @save_flag.setter
    def save_flag(self,flag):
        self._save_flag = flag

    @property
    def current_page(self):
        return self._current_page
    
    @current_page.setter
    def current_page(self,page):
        self._current_page = 0 if self.data_rows == 0 else page

    @property
    def total_pages(self):
        return math.ceil(self.data_rows/self.rows_per_page)

    @property
    def data_rows(self):
        return len(self.data)

# File handling
    def read_file(self):
        self.max_id = 0
        self.save_flag = False
        self.data = OrderedDict()
        file_name = f"Data/{self.data_file_name}.csv"
        with open(file_name, "r") as csvfile:
            reader = csv.DictReader(csvfile,delimiter=c.CSV_FILE_DELIMITER)
            self.data_headers = reader.fieldnames
            try:
                temp_list = list(next(reader).values())
                self.max_id,self.file_time_stamp,self.file_user = int(temp_list[0]), temp_list[1],temp_list[2]
            except ValueError:
                self.max_id,self.file_time_stamp,self.file_user = 0,"never","no one"
            for record in reader:
                self.read_record_from_file(record)

    def save_file(self,user_name,silently = False):
# loops thru OrderedDict and overwrites file
# if called with silently = True it will not prompt the user for anything
        if silently == False:
            if self.save_flag == False:
                input(f"{c.COLOR_HEADER}There is nothing to save. Press enter to continue.{c.COLOR_NORMAL}")
                self.current_page = 1
                return True
            
            while True:
                answer = input(f"{c.COLOR_INPUT}Do you want to save changes? y/n or c to cancel:{c.COLOR_NORMAL} ").lower() 
                if answer == "n":
                    self.read_file()
                    self.current_page = 1
                    return True
                if answer == "c":
                    return False
                if answer == "y":
                    break
                print(f"{c.COLOR_INPUT}Please make up your mind! :){c.COLOR_NORMAL}")

        file_name = f"Data/{self.data_file_name}.csv"
        with open(file_name, "w", newline="") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=self.data_headers,delimiter=c.CSV_FILE_DELIMITER)
            writer.writeheader()
            data_settings = [self.max_id, datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), user_name] + ['Unused']*(len(self.data_headers)-3)
            writer.writerow(dict(zip(self.data_headers, data_settings)))
            to_delete = []
            for key, record in self.data.items():
                if record["Status"] == c.REC_STATUS_DELETED:
                    to_delete.append(key)
                    continue
                temp_record = record.copy()
                temp_record["ID"] = key
                del temp_record["Status"]
                if "Score" in temp_record:
                    del temp_record["Score"]
                writer.writerow(temp_record)
                record["Status"] = c.REC_STATUS_ACTIVE
            for key in to_delete:
                del self.data[key]

        self.save_flag = False
        self.current_page = 1
        if silently == False:
            input(f"{c.COLOR_HEADER}Data saved to file. Press enter to continue.{c.COLOR_NORMAL}")
        return True

    def read_record_from_file(self,record):
        try:
            record_id = int(record.pop("ID"))
            record["Status"] = c.REC_STATUS_ACTIVE
            self.data[record_id] = record
            self.max_id = record_id
        except Exception as e:
            print(f"{c.COLOR_WARNING}There was an error reading this record:{c.COLOR_NORMAL}")
            print("Exception occurred:", type(e))
            print(self.data_headers)     
            print(record)
            if input(f"{c.COLOR_INPUT}Do you want to continue reading this file or abort the program? c/a:{c.COLOR_NORMAL} ").lower() == "a":
                sys.exit(1)

# Data record handling
# These functions add, update, delete and find records in the data list in memory. 
# The values in the records are prepared in the subclasses and passed to these functions.
# These functions also take care of save_flag and max_id handling.
    def add_record(self,in_record):
        self.max_id = self.max_id + 1
        in_record["Status"] = c.REC_STATUS_NEW
        self.data[self.max_id] = in_record
        self.save_flag = True

# delete_record here actually is designed habing in mind only the user database as we never ever plan to delete 
# questions from questions database. It look inconsistent, I know. :)
    def delete_record(self,parent_window):
        record_id = self.ask_for_id()
        if record_id == None:
            return parent_window + c.EVENT_VIEW_ITEMS
        if record_id == 1:
            input(f"{c.COLOR_WARNING}Felicia is stronger than you. You cannot simply delete her! :){c.COLOR_NORMAL}")
            return parent_window + c.EVENT_VIEW_ITEMS
        if input(f"{c.COLOR_INPUT}Do you really want to delete user nr. {record_id}? (y/n):{c.COLOR_NORMAL} ").lower() == "y":
            self.data[record_id]["Status"] = c.REC_STATUS_DELETED
            self.save_flag = True
        return parent_window + c.EVENT_VIEW_ITEMS
        
    def update_record(self,record_id,record):
        if record_id in self.data:
            record["Status"] = c.REC_STATUS_UPDATED
            self.data[record_id] = record
            self.save_flag = True
            return
        print(f"{c.COLOR_WARNING}ERROR: Record to be updated not found.{c.COLOR_NORMAL}")

    def fetch_record_by_key(self,key_name,key_value):
        for key,record in self.data.items():
            if record[key_name] == key_value:
                return key,record
        return 0,None

    def ask_for_id(self):
        while True:
            str = input(f"{c.COLOR_INPUT}Enter ID:{c.COLOR_NORMAL} ")
            if str.lower() == "q":
                return None
            try:
                record_id = int(str)
            except ValueError:
                print(f"{c.COLOR_WARNING}Please enter a valid ID.{c.COLOR_NORMAL}")
                continue
            if record_id in self.data:
                return record_id
            print(f"{c.COLOR_WARNING}ID does not exist.{c.COLOR_NORMAL}")

# Some window handling stuff
    def step_to_page(self,step):
        if self.current_page + step > self.total_pages:
            self.current_page = self.total_pages
        elif self.current_page + step < 1:
            self.current_page = 0 if self.data_rows == 0 else 1
        else:
            self.current_page = self.current_page + step

    def print_empty_rows(self,rows):
        if rows == 0:
            return
        for idx in range(rows):
            print(f"│ " + " " * (self.window_size - 3) + "│")

# This is the ui action handler. It's here because it looks (almost) the same for any object.
# It returns the window event combination:
# - the window we are currently in, e.g. Questions manager, Users, and
# - the action we want to perform next (add,edit, delete etc.)
    def ask_action(self,parent_window,valid_keys):
        while True:
            str = input(f"{c.COLOR_INPUT}Input action key:{c.COLOR_NORMAL} ").upper()
            if str not in valid_keys.upper():
                print(f"{c.COLOR_WARNING}Please enter a valid action key.{c.COLOR_NORMAL}")
                continue
            match str:
                case "A":
                    return parent_window + c.EVENT_ADD_ITEM
                case "E":
                    return parent_window + c.EVENT_EDIT_ITEM
                case "D":
                    return parent_window + c.EVENT_DELETE_ITEM
                case "X":
                    return parent_window + c.EVENT_CHANGE_ITEM_STATUS
                case "N":
                    self.step_to_page(1)
                    return parent_window + c.EVENT_VIEW_ITEMS
                case "P":
                    self.step_to_page(-1)
                    return parent_window + c.EVENT_VIEW_ITEMS
                case "F":
                    self.current_page = 1
                    return parent_window + c.EVENT_VIEW_ITEMS
                case "L":
                    self.current_page = self.total_pages
                    return parent_window + c.EVENT_VIEW_ITEMS
                case "S":
                    return parent_window + c.EVENT_SAVE_ITEMS
                case "Q":
                    if self.save_flag == False:
                        self.current_page = 1
                        return c.WINDOW_MAIN_MENU + c.EVENT_VIEW_ITEMS
                    return parent_window + c.EVENT_SAVE_ITEMS
