import os
from taskman_cli.helper_functions import get_necessary_files,print_welcome_message, print_help_message
from ttask_manager import TaskManager
from prompt_toolkit import prompt, HTML
from prompt_toolkit import print_formatted_text as print
from prompt_toolkit.styles import Style
from prompt_toolkit.shortcuts import confirm
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory

def main():
    def clear_screen():
        if os.name == 'nt':
            os.system('cls')             
        else:
            os.system('clear')
    binding = KeyBindings()
    @binding.add('c-l')
    def _(event):
        clear_screen()

    report_dir, json_data_file, history_file = get_necessary_files()     

    def save():
        save = confirm(HTML("<ansicyan>Wanna save the current state: </ansicyan>"),suffix="[y/N]" )
        if save:    
            print(to_do_list.save_current_state(json_data_file))
        else:
            print('Data not saved.')        

    print_welcome_message()

    commands = ['add','remove','mark-as-done','mad','list-both','lb','list-todo','ltd','list done','ld','clear-todo','cltd','clear-done','cld','reset','report','save','help','clear','exit']
    completer = WordCompleter(commands  , ignore_case=True)
    stylesheet = Style.from_dict({
        'positive' : '#4CAF50',
        'negative' : '#FF3333',
        'message'  : '#008080'
    })

    to_do_list = TaskManager()
    print(to_do_list.load_state(json_data_file))

    while True:
        try:
            command = prompt(HTML("<b fg='#FFA500'><i>TaskMan > </i></b>"), completer=completer, history=history_file, auto_suggest=AutoSuggestFromHistory()).strip()            
            if not command:
                print(HTML("<negative>Invalid option,the input cannot be blank,try 'help' to get more info on how to use this CLI.</negative>"), style=stylesheet)

            elif command.lower() == 'clear' :
                clear_screen()
                continue

            elif command.lower() == 'help':
                print_help_message()

            elif command.lower() == 'exit':
                save()
                break
                
            elif command.lower() == 'save':
                to_do_list.save_current_state(json_data_file)

            elif command.lower().startswith('add'):
                try:
                    tasks_input = command.split(maxsplit=1)[1].split('|')
                    tasks = []

                    for task_str in tasks_input:
                        task_str = task_str.strip()
                        if not task_str:
                            continue

                        if ':' in task_str:
                            task, priority = map(str.strip, task_str.split(':',1))
                            tasks.append((task,priority))
                        else:
                            tasks.append(task_str)
                    to_do_list.add_task(*tasks)
                except IndexError:
                    print(HTML("<ansired>You need to pass tasks to the commands !</ansired>"))

            elif command.lower().startswith('remove') or command.lower().startswith('rm') :
                try:
                    tasks_tobe_removed = [task.strip() for task in command.split(maxsplit=1)[1].split('|') if task.strip()]
                    to_do_list.remove_task(*tasks_tobe_removed)
                except IndexError:
                    print(HTML("<ansired>You need to pass tasks to the commands !</ansired>"))

            elif command.lower().startswith('mark-as-done') or command.lower().startswith('mad'):
                try:
                    tasks_tobe_mad = [task.strip() for task in command.split(maxsplit=1)[1].split('|') if task.strip()]
                    to_do_list.task_done(*tasks_tobe_mad)
                except IndexError:
                    print(HTML("<ansired>You need to pass tasks to the commands !</ansired>"))

            elif command.lower().startswith('list-both') or command.lower().startswith('lb'):
                to_do_list.current_state('both')

            elif command.lower().startswith('list-todo') or command.lower().startswith('ltd'):
                to_do_list.current_state('to-do')

            elif command.lower().startswith('list-done') or command.lower().startswith('ld') :
                to_do_list.current_state('done')

            elif command.lower().startswith('clear-todo') or command.lower().startswith('cltd'):
                to_do_list.clear('todo')

            elif command.lower().startswith('clear-done') or command.lower().startswith('cld'):
                to_do_list.clear('done')

            elif command.lower().startswith('report'):
                report_name = command[len('report'):].strip()
                if report_name and '\n' not in report_name:
                    print(to_do_list.report(report_dir,f"{report_name}.txt",report_content='all'))
                else:
                    to_do_list.report(report_dir)

            elif command.lower().startswith('reset'):
                to_do_list.clear('both')
            else:
                print(HTML("<negative>Invalid option, try 'help' to get more info on how to use this CLI.</negative>"),style=stylesheet)

        except KeyboardInterrupt:
            print(HTML("<negative>\nKeyboardInterrupt detected.Exiting... </negative>"),style=stylesheet)
            save()
            break   
            
        except EOFError:
            print(HTML("<negative>\nEOF detected. Exiting...</negative>"), style=stylesheet)
            save()
            break

        except Exception as e:
            print(HTML(f"<negative>An unexpected error occurred: {e}</negative>"), style=stylesheet)
            print(HTML("<message>Please try again or type 'help' to see available commands or 'exit' to quit.</message>"),style=stylesheet)

    print(HTML("<ansigreen>Thank you for using TaskMan CLI. Goodbye!</ansigreen>"))

if __name__ == '__main__':
    main()
