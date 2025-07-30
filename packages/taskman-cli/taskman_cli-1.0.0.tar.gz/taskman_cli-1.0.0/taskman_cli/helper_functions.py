import os
from prompt_toolkit import HTML, print_formatted_text as print
import platformdirs
from prompt_toolkit.history import FileHistory

def get_necessary_files():
    app_data_root = platformdirs.user_data_dir(appname="TaskMan-CLI", appauthor='TYA')
    if not os.path.exists(app_data_root):
        os.makedirs(app_data_root)

    report_dir = os.path.join(app_data_root, 'Reports')

    if not os.path.exists(report_dir):
        os.makedirs(report_dir)

    json_data_file = os.path.join(app_data_root, 'data.json')
    history_file = FileHistory(os.path.join(app_data_root, '.hist'))
    return report_dir, json_data_file, history_file

def print_welcome_message():
    print(HTML("""<ansiyellow>
    ╔═══════════════════════════════════════════════════════════════════════════╗
    ║                                                                           ║
    ║   ████████╗ █████╗ ███████╗██╗  ██╗    ███╗   ███╗ █████╗ ███╗   ██╗      ║
    ║   ╚══██╔══╝██╔══██╗██╔════╝██║ ██╔╝    ████╗ ████║██╔══██╗████╗  ██║      ║
    ║      ██║   ███████║███████╗█████╔╝     ██╔████╔██║███████║██╔██╗ ██║      ║
    ║      ██║   ██╔══██║╚════██║██╔═██╗     ██║╚██╔╝██║██╔══██║██║╚██╗██║      ║
    ║      ██║   ██║  ██║███████║██║  ██╗    ██║ ╚═╝ ██║██║  ██║██║ ╚████║      ║
    ║      ╚═╝   ╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝    ╚═╝     ╚═╝╚═╝  ╚═╝╚═╝  ╚═══╝      ║
    ║                                                                           ║
    ║              Welcome to TaskMan - Your Personal Task Manager!             ║
    ║                                                                           ║
    ║        Manage your tasks efficiently with simple CLI commands.            ║
    ║        Type 'help' to see available commands or 'exit' to quit.           ║
    ║                                                                           ║
    ║                     Let's boost your productivity!                        ║
    ╚═══════════════════════════════════════════════════════════════════════════╝
    </ansiyellow>
    """))

def print_help_message():
    print(HTML("""<ansiyellow>
        ╔═════════════════════════════════════════════════════════════════════════════════════╗
        ║                              TaskMan CLI Commands                                   ║
        ╠═════════════════════════════════════════════════════════════════════════════════════╣
        ║  add [task1] | [task2] | ...         : Add one or more tasks                        ║
        ║    - Format: task:priority           : Add task with specific priority              ║
        ║  remove / rm [task1] | [task2] | ... : Remove one or more tasks                     ║
        ║  mark-as-done / mad [task1]...       : Mark one or more tasks as completed          ║
        ║  list-both / lb                      : Show all tasks (to-do and done)              ║
        ║  list-todo / ltd                     : Show pending tasks                           ║
        ║  list-done / ld                      : Show completed tasks                         ║
        ║  clear-todo / cltd                   : Clear all pending tasks                      ║
        ║  clear-done / cld                    : Clear all completed tasks                    ║
        ║  reset                               : Clear all tasks (both to-do and done)        ║
        ║  report [name(optional)]             : Generate a report (optional custom name)     ║
        ║  save                                : Save current state to file                   ║
        ║  help                                : Show this help message                       ║
        ║  clear / Ctrl+l                      : Clear the screen                             ║
        ║  exit                                : Exit the program                             ║
        ╠═════════════════════════════════════════════════════════════════════════════════════╣
        ║  Notes:                                                                             ║
        ║  - Use '|' to separate multiple tasks in 'add', 'remove', or 'mad' commands.        ║
        ║  - Tasks can be saved on exit, if the user agrees to do so, and loaded on startup,  ║
        ║    if any were saved in a previous session.                                         ║
        ║  - Priority levels: high, medium, low (default: medium)                             ║
        ╚═════════════════════════════════════════════════════════════════════════════════════╝
        </ansiyellow>
    """))