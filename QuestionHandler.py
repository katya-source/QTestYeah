import random
from collections import OrderedDict
from DataHandler import DataHandler
from helper_functions import flag_to_str, score_to_str
import constants as c

"""QuestionHandler: subclass of DataHandler
Manages the questions.
Implements properties and methods prescribed by DataHandler:
- paint_data_window - is used in two different modes:
        (A)- manages table of questions
        (B)- shows statistics
- does the ui stuff for adding, editing, disabling/enabling questions for (A)
- read_file is inherited and extended with specific stuff
- specific stuff at the end
"""

class QuestionHandler(DataHandler):
    def __init__(self, file_name, rows_per_page, window_size):
        super().__init__(file_name, rows_per_page)
        self._window_size = window_size

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
        if mode == c.WINDOW_STATS:
            print(f"{c.COLOR_HEADER}Statistics for: {c.COLOR_INPUT}{self.data_file_name}{c.COLOR_NORMAL}")
            print("┌" + "─" * (self.window_size - 2) + "┐")
            print("│  Rank ID   Question" + " " * (self.window_size-43) + f"Score / total {self.current_page:2d}/{self.total_pages:2d}  │")
        else:
            print(f"{c.COLOR_HEADER}Questions manager for: {c.COLOR_INPUT}{self.data_file_name}{c.COLOR_NORMAL} (last updated {self.file_time_stamp} by {self.file_user})")
            print("┌" + "─" * (self.window_size - 2) + "┐")
            print("│  ID  Type  Question" + " " * (self.window_size-39) + f"Flag       {self.current_page:2d}/{self.total_pages:2d} │")
        print("├" + "─" * (self.window_size - 2) + "┤")
        if self.current_page == 0:
            self.print_empty_rows(self.rows_per_page)
            return
        start_row = (self.current_page - 1) * self.rows_per_page
        end_row = self.current_page * self.rows_per_page
        if end_row > self.data_rows:
            end_row = self.data_rows    
        if mode == c.WINDOW_STATS:
            sorted_keys = self.get_sorted_key_list()
            for rank, key in enumerate(sorted_keys[start_row:end_row]):
                record = self.data[key]
                this_flag = "enabled " if record["Flag"] == c.FLAG_ENABLED else "disabled"
                this_score = score_to_str(record["Answered"],record["Asked"])
                print(f"│ {rank+1:3d}. [{key:3d}] {record['Question'].ljust(self.window_size - 39)} " + f"{this_score}".rjust(8) + f" / {record['Asked']}".ljust(5) + f" {this_flag}  │")
        else:
            for key, record in list(self.data.items())[start_row:end_row]:
                this_type = "Free" if record["Type"] == "f" else "Mult"
                this_flag = "enabled " if record["Flag"] == c.FLAG_ENABLED else "disabled"
                print(f"│ {key:3d}. {this_type}  {record['Question'].ljust(self.window_size - 33)}  {this_flag} {record['Status'].ljust(7)} │")
        self.print_empty_rows(self.rows_per_page - (end_row - start_row))

    def add_item(self):       
        record=self.input_question(c.EDIT_MODE_NEW,{})
        if record == None:
            return c.WINDOW_QMANAGER + c.EVENT_VIEW_ITEMS

        if input(f"{c.COLOR_INPUT}Review question and decide if you want to save it (y/n):{c.COLOR_NORMAL} ").lower() == "y":
            record["Status"] = c.REC_STATUS_NEW
            record["Flag"] = c.FLAG_ENABLED
            record["Asked"]=0
            record["Answered"]=0
            record["Score"] = score_to_str(0,0)
            self.add_record(record)
            self.current_page = self.total_pages
        return c.WINDOW_QMANAGER + c.EVENT_VIEW_ITEMS

    def edit_item(self):
        record_id = self.ask_for_id()
        if record_id == None:
            return c.WINDOW_QMANAGER + c.EVENT_VIEW_ITEMS
        record = self.data[record_id]

        record = self.input_question(c.EDIT_MODE_EDIT,record)
        if record == None:
            return c.WINDOW_QMANAGER + c.EVENT_VIEW_ITEMS

        if input(f"{c.COLOR_INPUT}Do you really want to update this question? (y/n):{c.COLOR_NORMAL} ").lower() == "y":
            record["Status"] = c.REC_STATUS_UPDATED
            self.update_record(record_id,record)
        return c.WINDOW_QMANAGER + c.EVENT_VIEW_ITEMS

    def toggle_item_flag(self):
        record_id = self.ask_for_id()
        if record_id == None:
            return c.WINDOW_QMANAGER + c.EVENT_VIEW_ITEMS
        record = self.data[record_id]

        if record["Flag"] == c.FLAG_ENABLED:
            if input(f"{c.COLOR_INPUT}Do you want to disable question nr. {record_id}? (y/n):{c.COLOR_NORMAL} ").lower() == "y":
                record["Flag"] = c.FLAG_DISABLED
                self.update_record(record_id,record)
        else:
            if input(f"{c.COLOR_INPUT}Do you want to enable question nr. {record_id}? (y/n):{c.COLOR_NORMAL} ").lower() == "y":
                record["Flag"] = c.FLAG_ENABLED
                self.update_record(record_id,record)

        return c.WINDOW_QMANAGER + c.EVENT_VIEW_ITEMS

# DataHandler has a generic read_file for users and questions database. 
# But questions has more fields which are handled here after super().read_file()
    def read_file(self):
        super().read_file()
        for key, record in self.data.items():
            try:
                record["Flag"] = int(record["Flag"])
            except:
                record["Flag"] = int(0)
            try:
                record["Asked"] = int(record["Answered"])
            except:
                record["Asked"] = int(0)
            try:
                record["Answered"] = int(record["Answered"])
            except:
                record["Answered"] = int(0)
            record["Score"] = score_to_str(record["Answered"],record["Asked"])

#Stuff created by and used in this class
# ui stuff used in add_item and edit_item
    def input_question(self,mode,record):
        if mode == c.EDIT_MODE_EDIT:
            this_type = "free" if record['Type']=='f' else "multiple choice"
            print(f"{c.COLOR_HEADER}Current question type:{c.COLOR_NORMAL} {this_type}", end=" - ")
        while True:
            answer = input(f"{c.COLOR_INPUT}Set the answer type - free-form or multiple choice? f/m:{c.COLOR_NORMAL} ").lower()
            if answer == "q":
                return None
            if answer == "":
                break
            if answer in ["f","m"]:
                record["Type"] = answer
                break

        if mode == c.EDIT_MODE_EDIT:
            print(f"{c.COLOR_HEADER}Current question text:{c.COLOR_NORMAL} {record['Question']}")
        answer = input(f"{c.COLOR_INPUT}Question text:{c.COLOR_NORMAL} ")
        if answer.lower() == "q":
            return None
        if answer != "":
            record["Question"] = answer

        if record["Type"] == 'f':
            record["Answer_A"], record["Answer_B"], record["Answer_C"],record["Answer_D"] = ("","","","")
        else:
            for letter in ["A","B","C","D"]:
                key_name = f"Answer_{letter}"
                if mode == c.EDIT_MODE_EDIT:
                    print(f"{c.COLOR_HEADER}Current text for choice {letter}:{c.COLOR_NORMAL} {record[key_name]}",end=" - ")
                answer = input(f"{c.COLOR_INPUT}Set text for choice {letter}:{c.COLOR_NORMAL} ")
                if answer.lower() == "q":
                    return None
                if answer != "":
                    record[key_name] = answer
        if mode == c.EDIT_MODE_EDIT:
            print(f"{c.COLOR_HEADER}Current correct answer:{c.COLOR_NORMAL} {record['Correct']}",end=" - ")
        while True:
            record["Correct"] = input(f"{c.COLOR_INPUT}Set correct answer:{c.COLOR_NORMAL} ").upper()
            if record["Correct"] == "Q":
                return None
            if record["Correct"] in "ABCD" or record["Type"] == "f":
                break

        return record
 
 # 3 methods to get questions for Practise, Test your knowledge and Statistics
    def get_random_weighted_record_id(self):
        weights = []
        keys = []
        for key, record in self.data.items():
            if record["Flag"] == 0:
                continue
            keys.append(key)
            if int(record["Asked"]) > 0:
                weight = 1 - int(record["Answered"]) / int(record["Asked"])
            else:
                weight = 1
            weights.append(weight)

        if sum(weights) > 0:
            return random.choices(keys, weights=weights, k=1)[0]
        return random.choice(keys)


    def get_random_key_sample(self,cnt):
        enabled_keys = [key for key in self.data.keys() if self.data[key]['Flag'] == c.FLAG_ENABLED]
        return random.sample(enabled_keys, cnt)

    def get_sorted_key_list(self):
        return sorted(self.data.keys(), key=lambda x: ((0 if self.data[x]["Asked"] == 0 else -self.data[x]["Answered"]/self.data[x]["Asked"]), -self.data[x]["Asked"]))
