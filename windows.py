import os
import random
import datetime
import constants as c
from helper_functions import score_to_str,extract_event_id

"""Window functions
These are functions which print various windows without requiring full-scale database management.
- get_topic: ui to choose topic, hands data_file_name over to questions and makes it read that file into OrderedDict
- say_goodbye says goodbye
- display_main_menu - main menu ui and action handling
- display_data_window - prints the whole screen of data tables with header, data table, shortkey bar
- display_practise_window - does the whole practise thing, visuals and ui (ugly solution, didn't have time. Sorry!)
- display_test_window - does the whole test thing, visuals and ui, writes score to results.txt (another ugly solution, 
  didn't have time. Sorry! Again!)
- print_footer is used in other functions here to print the footer. Yes. :)
"""

def get_topic(questions):
    os.system('cls' if os.name == 'nt' else 'clear')
    print(f"{c.COLOR_HEADER}These are our topics:{c.COLOR_NORMAL}")
    topics = {}
    id = 0
    for file_name in os.listdir(c.DATA_FOLDER):
        if file_name.endswith(".csv") and file_name != f"{c.USER_CSVFILE_NAME}.csv":
            id += 1
            topics[id] = file_name.replace(".csv","")
            print(f"{id} - {topics[id]}")

    while True:
        topic_id = input(f"{c.COLOR_INPUT}Enter topic ID (or q to cancel):{c.COLOR_NORMAL} ").lower()
        if topic_id == "q":
            break
        try:
            topic_id = int(topic_id)
        except:
            print(f"{c.COLOR_WARNING}Please choose a valid topic ID.{c.COLOR_NORMAL}")
        else:
            if 1 <= topic_id <= id:
                questions.data_file_name = f"{topics[topic_id]}"
                questions.read_file()
                break
            print(f"{c.COLOR_WARNING}Please choose a valid topic ID.{c.COLOR_NORMAL}")
    return c.WINDOW_MAIN_MENU + c.EVENT_VIEW_ITEMS

def say_goodbye():
    os.system('cls' if os.name == 'nt' else 'clear')
    print(f"{c.COLOR_HEADER}Thank you and goodbye!{c.COLOR_NORMAL}")

def display_main_menu(current_user_role,number_of_questions):
    os.system('cls' if os.name == 'nt' else 'clear')
    print(f"{c.COLOR_HEADER}Main menu{c.COLOR_NORMAL}")
    print("┌────────────────────────────────┐")
    print("│ C - Choose a topic             │")
    print("│ P - Practise                   │")
    print("│ T - Test your knowledge        │")
    print("│ S - Statistics                 │")
    print("│ M - Manage questions           │")
    print("│ U - User profiles              │")
    print("│ Q - Quit program               │")
    print("└────────────────────────────────┘")

    while True:
        str = input(f"{c.COLOR_INPUT}Input action key:{c.COLOR_NORMAL} ").upper()
        if str in "PTS" and number_of_questions < c.MINIMUM_NUMBER_OF_ENABLED_ITEMS:
            input(f"{c.COLOR_WARNING}You cannot use this feature as there are too few questions available.{c.COLOR_NORMAL}")
            return c.WINDOW_MAIN_MENU + c.EVENT_VIEW_ITEMS
        if str in "MU" and current_user_role != c.USER_TYPE_ADMIN:
            input(f"{c.COLOR_WARNING}You have no permission to use this feature. Press enter to continue.{c.COLOR_NORMAL}")
            return c.WINDOW_MAIN_MENU + c.EVENT_VIEW_ITEMS
        match str:
            case "C":
                return c.WINDOW_TOPICS + c.EVENT_VIEW_ITEMS
            case "P":
                return c.WINDOW_PRACTISE + c.EVENT_VIEW_ITEMS
            case "T":
                return c.WINDOW_TEST + c.EVENT_VIEW_ITEMS
            case "S":
                return c.WINDOW_STATS + c.EVENT_VIEW_ITEMS
            case "M":
                return c.WINDOW_QMANAGER + c.EVENT_VIEW_ITEMS
            case "U":
                return c.WINDOW_USERS + c.EVENT_VIEW_ITEMS
            case "Q":
                if input(f"{c.COLOR_INPUT}Do you really want to quit the program? y/n:{c.COLOR_NORMAL} ").lower() == "y":
                    return c.WINDOW_QUIT_PROGRAM + c.EVENT_VIEW_ITEMS
                else:
                    return c.WINDOW_MAIN_MENU + c.EVENT_VIEW_ITEMS
        print(f"{c.COLOR_WARNING}Please enter a valid action key.{c.COLOR_NORMAL}")

def display_data_window(DataHandler,window_event,current_user):
    os.system('cls' if os.name == 'nt' else 'clear')
    DataHandler.paint_data_window(window_event // c.WINDOW_EXTRACTOR * c.WINDOW_EXTRACTOR)
    match extract_event_id(window_event):
        case c.EVENT_VIEW_ITEMS:
            if window_event // c.WINDOW_EXTRACTOR * c.WINDOW_EXTRACTOR == c.WINDOW_USERS:
                print_footer(DataHandler.window_size,"A - Add | E - Edit | D - Delete | S - Save changes | Q - Quit",True)
                return DataHandler.ask_action(c.WINDOW_USERS,"AEDSQNPLF")
            elif window_event // c.WINDOW_EXTRACTOR * c.WINDOW_EXTRACTOR == c.WINDOW_QMANAGER:
                print_footer(DataHandler.window_size,"A - Add | E - Edit | X - Enable/disable | S - Save changes | Q - Quit",True)
                return DataHandler.ask_action(c.WINDOW_QMANAGER,"AEXSQNPLF")
            elif window_event // c.WINDOW_EXTRACTOR * c.WINDOW_EXTRACTOR == c.WINDOW_STATS:
                print_footer(DataHandler.window_size,"Q - Quit",True)
                return DataHandler.ask_action(c.WINDOW_STATS,"QNPLF")
        case c.EVENT_ADD_ITEM:
            print_footer(DataHandler.window_size,"Adding record (Press \"Q\" + Enter in any field to cancel)",False)
            return DataHandler.add_item()
        case c.EVENT_EDIT_ITEM:
            print_footer(DataHandler.window_size,"Editing record (Press \"Q\" + Enter in any field to cancel)",False)
            return DataHandler.edit_item()
        case c.EVENT_DELETE_ITEM:
            if window_event // c.WINDOW_EXTRACTOR * c.WINDOW_EXTRACTOR == c.WINDOW_USERS:
                print_footer(DataHandler.window_size,"Deleting record (Press \"Q\" + Enter to cancel)",False)
                return DataHandler.delete_record(c.WINDOW_USERS)
        case c.EVENT_CHANGE_ITEM_STATUS:
            if window_event // c.WINDOW_EXTRACTOR * c.WINDOW_EXTRACTOR == c.WINDOW_QMANAGER:
                print_footer(DataHandler.window_size,"Disable/enable record (Press \"Q\" + Enter to cancel)",False)
                return DataHandler.toggle_item_flag()
        case c.EVENT_SAVE_ITEMS:
            print_footer(DataHandler.window_size,"Saving changes",False)
            if DataHandler.save_file(current_user) == True:
                return c.WINDOW_MAIN_MENU + c.EVENT_VIEW_ITEMS
            else:
                return window_event // c.WINDOW_EXTRACTOR * c.WINDOW_EXTRACTOR + c.EVENT_VIEW_ITEMS
 
def display_practise_window(questions,current_user):
    cnt = 0
    score = 0
    while True:
        print_header(questions.window_size,f"Practise test: {questions.data_file_name}",score,cnt)

        record_id = questions.get_random_weighted_record_id()
        print(f"Question: {questions.data[record_id]['Question']}.")
        if questions.data[record_id]["Type"] == "m":
            print(f"(A) {questions.data[record_id]['Answer_A']}")
            print(f"(B) {questions.data[record_id]['Answer_B']}")
            print(f"(C) {questions.data[record_id]['Answer_C']}")
            print(f"(D) {questions.data[record_id]['Answer_D']}")
        print("─" * questions.window_size)

        if questions.data[record_id]['Flag'] == "m":
            while True:
                answer = input(f"{c.COLOR_INPUT}Choose A, B, C or D, (or q to quit):{c.COLOR_NORMAL} ").lower()
                if answer in ["q","a","b","c","d"]:
                    break
        else:
            answer = input(f"{c.COLOR_INPUT}Your answer (or q to quit):{c.COLOR_NORMAL} ").lower()

        if answer == "q":
            break
        
        cnt += 1
        questions.data[record_id]["Asked"] = int(questions.data[record_id]["Asked"]) + 1
        if answer == questions.data[record_id]["Correct"].lower():
            score += 1
            questions.data[record_id]["Answered"] = int(questions.data[record_id]["Answered"]) + 1
            questions.data[record_id]["Score"] = float(questions.data[record_id]["Answered"]/questions.data[record_id]["Asked"])
            if input(f"Correct answer. Congrats!\n{c.COLOR_INPUT}Press Enter to continue or q to quit.{c.COLOR_NORMAL}").lower() == "q":
                break
            continue
        if input(f"Wrong!!! Yikes!\n{c.COLOR_INPUT}Press Enter to continue or q to quit.{c.COLOR_NORMAL}").lower() == "q":
            break

    print_header(questions.window_size,f"Practise test: {questions.data_file_name}")
    input(f"Your final score is: {score} of {cnt} = {score_to_str(score,cnt)} answered correctly.")
    questions.save_flag = True
    questions.save_file(current_user,True)
    return c.WINDOW_MAIN_MENU + c.EVENT_VIEW_ITEMS

def display_test_window(questions,current_user):
    print_header(questions.window_size,f"Test: {questions.data_file_name}")

    while True:
        print(f"{c.COLOR_INPUT}How many test questions do you want to include?")
        str = input(f"Please choose between 1 and {questions.data_rows} or q + enter to quit:{c.COLOR_NORMAL} ").lower()
        if str == "q":
            return c.WINDOW_MAIN_MENU + c.EVENT_VIEW_ITEMS
        try:
            cnt = int(str)
        except ValueError:
            print(f"{c.COLOR_WARNING}Please choose between 1 and {questions.data_rows} or q + enter to quit:{c.COLOR_NORMAL} ")
        else:
            if 1 <= cnt <= questions.data_rows:
                break
            print(f"{c.COLOR_WARNING}Please choose between 1 and {questions.data_rows} or q + enter to quit:{c.COLOR_NORMAL} ")

    random_keys = questions.get_random_key_sample(cnt)

    score = 0
    for question_counter in range(1,cnt + 1):
        print_header(questions.window_size,f"Test: {questions.data_file_name} (question nr. {question_counter})",score,cnt)
        record_id = random_keys.pop()
        print(f"Question {question_counter}: {questions.data[record_id]['Question']}.")
        if questions.data[record_id]["Type"] == "m":
            print(f"(A) {questions.data[record_id]['Answer_A']}")
            print(f"(B) {questions.data[record_id]['Answer_B']}")
            print(f"(C) {questions.data[record_id]['Answer_C']}")
            print(f"(D) {questions.data[record_id]['Answer_D']}")
        print("─" * questions.window_size)
        answer = input(f"{c.COLOR_INPUT}Your answer:{c.COLOR_NORMAL} ").lower()
        questions.data[record_id]["Asked"] = int(questions.data[record_id]["Asked"]) + 1
        if answer == questions.data[record_id]["Correct"].lower():
            score += 1
            print("Correct.")
        else:
            print("Wrong.")
        input("Press Enter to continue.")

    with open(c.RESULTS_FILENAME, "a") as result_file:
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        result_file.write(f"{timestamp} {questions.data_file_name.ljust(30)} {current_user.ljust(10)}" + f" {score}".rjust(6) + f" {cnt}".rjust(6) + f" {score*100/cnt:.1f} %".rjust(7) + "\n")

    print_header(questions.window_size,f"Practise test: {questions.data_file_name}")
    input(f"Your final score is: {score} of {cnt} = {score_to_str(score,cnt)} answered correctly.")
    return c.WINDOW_MAIN_MENU + c.EVENT_VIEW_ITEMS

# helper functions for the display_ functions
def print_footer(window_size, description,set_page_bar):
    print("├" + "─" * (window_size - 2) + "┤")
    print(f"│ {description.ljust(window_size-4)} │")
    if set_page_bar == True:
        print("│ N - next page | P - previous page | F - First page | L - Last page".ljust(window_size-2) + " │")
    print("└" + "─" * (window_size - 2) + "┘")

def print_header(window_size,head_line, score = -1, cnt = 0):
    os.system('cls' if os.name == 'nt' else 'clear')
    print(f"{c.COLOR_HEADER}{head_line}{c.COLOR_NORMAL}")
    if score != -1:
        print(f"Current score: {score} of {cnt} = {score_to_str(score,cnt)}")
    print("─" * window_size)
