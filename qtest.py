from UserHandler import UserHandler
from QuestionHandler import QuestionHandler
from windows import display_main_menu,say_goodbye,display_data_window,display_practise_window,get_topic,display_test_window
from helper_functions import extract_window_id
import constants as c

"""Main function:
    - has two parts:
        Startup - load user db, user login, load question db
        Window event loop - assign first window event and then do the event loop until quit
    - designed as a window event loop, 
    - each window event is an action message returned from each method/function and identifies:
        - the next window to be called (anything called c.WINDOW_XXX)
        - the next action to be performed (anything called c.EVENT_XXX)
"""
def main():
    users = UserHandler(c.USER_CSVFILE_NAME,10,70)
    if users.user_login() == False:
        say_goodbye()
        return
    questions = QuestionHandler(c.DEFAULT_TEST_CSVFILE,10,130)

    window_event = c.WINDOW_MAIN_MENU + c.EVENT_VIEW_ITEMS
    while True:
        match extract_window_id(window_event):
            case c.WINDOW_TOPICS:
                window_event = get_topic(questions)
            case c.WINDOW_MAIN_MENU:
                window_event = display_main_menu(users.current_user_role,questions.data_rows)
            case c.WINDOW_USERS:
                window_event = display_data_window(users,window_event,users.current_user)
            case c.WINDOW_QMANAGER:
                window_event = display_data_window(questions,window_event,users.current_user)
            case c.WINDOW_PRACTISE:
                window_event = display_practise_window(questions,users.current_user)
            case c.WINDOW_TEST:
                window_event = display_test_window(questions,users.current_user)
            case c.WINDOW_STATS:
                window_event = display_data_window(questions,window_event,users.current_user)
            case c.WINDOW_QUIT_PROGRAM:
                window_event = say_goodbye()
            case c.BREAK_OUT_OF_JAIL:
                break


if __name__ == "__main__":
    main()
