<div align="center">

[![TaskMan - Your Personal Task Manager](https://img.shields.io/badge/TaskMan-Your%20Personal%20Task%20Manager-blue?style=for-the-badge&logo=python&logoColor=white)](https://github.com/tahadnan/To-do-list-manager)

[![Pypi](https://badge.fury.io/py/taskman-cli.svg)](https://badge.fury.io/py/taskman-cli)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

</div>

# Project Status

Dear users and visitors, this project development is **COMPLETED** and no further development, from the creator's part, is expected in the foreseen future, but feel free to fork the project on [Github](https://github.com/tahadnan/TaskMan-CLI-PyPi) and build upon it, or improve it in any way. The latest stable release by the creator is [v1.0.0](https://pypi.org/project/taskman-cli/), thanks for your support, keep learning and contributing !  

## 📝 Description

TaskMan CLI is a powerful and user-friendly task management application built with Python. It offers a seamless command-line interface for efficiently managing your daily tasks, helping you boost productivity and stay organized.  

**Important Note: As of 01/19/2025, [TaskMan CLI](https://github.com/tahadnan/TaskMan-CLI.git) repo was archived and now this is the main TaskMan CLI repo, the '-PyPi' will remain due to the existence of [TaskMan CLI](https://github.com/tahadnan/TaskMan-CLI.git).**

## ✨ Features

- 📌 **Add Tasks and Specify their Priorities**: Easily add new tasks with priorities to your to-do list
- 🗑️ **Remove Tasks**: Remove tasks from your to-do list
- ✅ **Mark Tasks as Completed**: Move tasks to a "done" list when completed
- 👀 **View Current State**: See all your tasks, both pending and completed
- 🧹 **Clear Lists**: Clean up your to-do and done lists with a single command
- 💾 **Data Persistence**: Your tasks are saved automatically, so you never lose your progress
- 📊 **Generate Reports**: Create daily task reports to track your productivity

## 🚀 Installation

You can install TaskMan CLI using pip:

```bash
pip install taskman-cli
```

## 🛠️ Usage

After installation, you can start TaskMan CLI by running:

```bash
taskman
```

Once launched, you'll see the TaskMan welcome screen. Type `help` to see available commands:

```
TaskMan > help
```

Use the various commands to manage your tasks. Here are some examples:

```
TaskMan > add Buy groceries | Call mom:high | Finish report
TaskMan > list-todo
TaskMan > mark-as-done Buy groceries
TaskMan > list-both
```

## 📚 Available Commands

- `add [task1:priority] | [task2] | ...`: Add one or more tasks with their priorities
- `remove [task1] | [task2] | ...`: Remove one or more tasks
- `mark-as-done / mad [task1]...`: Mark one or more tasks as completed
- `list-both / lb`: Show all tasks (to-do and done)
- `list-todo / ltd`: Show pending tasks
- `list-done / ld`: Show completed tasks
- `clear-todo / cltd`: Clear all pending tasks
- `clear-done / cld`: Clear all completed tasks
- `reset`: Clear all tasks (both to-do and done)
- `report [name]`: Generate a report (optional custom name, defaults to ```current_date.txt```)
- `save`: Save current state to file
- `help`: Show the help message
- `clear / Ctrl+l`: Clear the screen
- `exit`: Exit the program

## 📶 Available Priorities
The available task priorities are:
+ high
+ medium (default one)
+ low

## 💡 Tips

- Use the up and down arrow keys to navigate through your command history.
- TaskMan supports auto-completion. Start typing a command and press Tab to complete it.
- If a task is passed without specifying the priority (e.g: ```add code```) the priority will default to medium 
- Your tasks can be saved, so you can safely exit with saving the current state and resume your work later.

## 🤝 Contributing

Contributions are welcome! Here's how you can contribute:

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Inspired by the ZTM Python course by Andrei Neagoie
- Built for learning purposes using Python, [ttask_manager](https://github.com/tahadnan/ttask-manager)[prompt_toolkit](https://github.com/prompt-toolkit/python-prompt-toolkit)
