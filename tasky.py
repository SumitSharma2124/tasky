#!/usr/bin/env python3
import curses, json, os
from datetime import datetime

TASKS_FILE = "tasks.json"

def load_tasks():
    if os.path.exists(TASKS_FILE):
        try:
            with open(TASKS_FILE, "r") as f:
                content = f.read().strip()
                if not content:
                    return []
                return json.loads(content)
        except json.JSONDecodeError:
            return []
    return []

def save_tasks(tasks):
    with open(TASKS_FILE, "w") as f:
        json.dump(tasks, f, indent=4)

def main(stdscr):
    curses.curs_set(0)
    tasks = load_tasks()
    current_row = 0
    show_completed_only = False

    curses.start_color()
    curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLACK)

    def get_visible_tasks():
        return [t for t in tasks if (not show_completed_only or t["done"])]

    def print_menu():
        stdscr.clear()
        visible = get_visible_tasks()
        stdscr.addstr(0, 0, f"Task List ({'Completed Only' if show_completed_only else 'All'})")
        for idx, task in enumerate(visible):
            mark = "[*]" if task["done"] else "[ ]"
            title = f"{mark} ~~{task['title']}~~ ({task['created']})" if task["done"] else f"{mark} {task['title']} ({task['created']})"
            pointer = "→" if idx == current_row else " "
            stdscr.addstr(idx + 1, 0, pointer)
            if idx == current_row:
                stdscr.attron(curses.A_REVERSE)
                stdscr.addstr(idx + 1, 2, title, curses.color_pair(2) if task["done"] else curses.color_pair(1))
                stdscr.attroff(curses.A_REVERSE)
            else:
                stdscr.addstr(idx + 1, 2, title, curses.color_pair(2) if task["done"] else curses.color_pair(1))
        pointer = "→" if current_row == len(visible) else " "
        stdscr.addstr(len(visible) + 2, 0, f"{pointer} Add New Task: (press Enter here)")
        stdscr.addstr(len(visible) + 4, 0, "Keys: ↑↓ move | Enter toggle/add | d delete | f filter | Esc quit")
        stdscr.refresh()

    while True:
        visible = get_visible_tasks()
        print_menu()
        key = stdscr.getch()

        if key == curses.KEY_UP and current_row > 0:
            current_row -= 1
        elif key == curses.KEY_DOWN and current_row < len(visible):
            current_row += 1
        elif key == ord("\n"):
            if current_row < len(visible):
                idx_in_all = tasks.index(visible[current_row])
                tasks[idx_in_all]["done"] = not tasks[idx_in_all]["done"]
                save_tasks(tasks)
            else:
                curses.echo()
                stdscr.addstr(len(visible) + 5, 0, "Enter new task: ")
                new_task = stdscr.getstr().decode("utf-8")
                curses.noecho()
                if new_task.strip():
                    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    tasks.append({"title": new_task, "done": False, "created": timestamp})
                    save_tasks(tasks)
        elif key == ord("d") and current_row < len(visible):
            idx_in_all = tasks.index(visible[current_row])
            del tasks[idx_in_all]
            if current_row > 0:
                current_row -= 1
            save_tasks(tasks)
        elif key == ord("f"):
            show_completed_only = not show_completed_only
            current_row = 0
        elif key == 27:
            break

curses.wrapper(main)