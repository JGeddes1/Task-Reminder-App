import tkinter as tk
from tkinter import ttk, messagebox
import datetime
import json

class TaskManager:
    def __init__(self, root):
        self.root = root
        self.root.title("Task Manager")
        
        self.file_path = "tasks.json"  # Define the file path

        self.load_tasks()

                # Create and place widgets
        self.label_task = ttk.Label(root, text="Task:")
        self.label_task.grid(row=0, column=0, padx=10, pady=5, sticky=tk.W)

        self.task_entry = ttk.Entry(root, width=30)
        self.task_entry.grid(row=0, column=1, padx=10, pady=5, sticky=tk.W)

        self.label_deadline = ttk.Label(root, text="Deadline (HH:MM):")
        self.label_deadline.grid(row=1, column=0, padx=10, pady=5, sticky=tk.W)

        self.deadline_entry = ttk.Entry(root, width=30)
        self.deadline_entry.grid(row=1, column=1, padx=10, pady=5, sticky=tk.W)

        self.add_button = ttk.Button(root, text="Add Task", command=self.add_task)
        self.add_button.grid(row=2, column=0, columnspan=2, pady=10)

        self.task_tree = ttk.Treeview(root, columns=("Task", "Deadline", "Reminder Sent"), show="headings", selectmode=tk.BROWSE)
        self.task_tree.heading("Task", text="Task")
        self.task_tree.heading("Deadline", text="Deadline")
        self.task_tree.heading("Reminder Sent", text="Reminder Sent")
        self.task_tree.grid(row=3, column=0, columnspan=3, padx=10, pady=5, sticky=tk.W+tk.E+tk.N+tk.S)

        self.delete_button = ttk.Button(root, text="Delete Task", command=self.delete_task)
        self.delete_button.grid(row=4, column=0, columnspan=2, pady=10)

        self.remind_button = ttk.Button(root, text="Remind me at 5 PM", command=self.remind_tasks)
        self.remind_button.grid(row=5, column=0, columnspan=2, pady=10)

        # Schedule a call to check_tasks_reminders every 1000 milliseconds (1 second)
        self.root.after(1000, self.check_tasks_reminders)


    def add_task(self):
        task_text = self.task_entry.get()
        deadline_str = self.deadline_entry.get()

        if task_text and deadline_str:
            try:
                # Parse deadline as datetime
                deadline = datetime.datetime.strptime(deadline_str, "%H:%M").time()
            except ValueError:
                messagebox.showwarning("Invalid Deadline", "Please enter a valid deadline in HH:MM format.")
                return

            # Store deadline as ISO formatted string
            deadline_iso = deadline.strftime("%Y-%m-%dT%H:%M:%S")

            self.tasks[task_text] = {"deadline": deadline_iso, "reminder_sent": False}
            self.task_tree.insert("", "end", values=(task_text, deadline_str))
            self.save_tasks()
            messagebox.showinfo("Task Added", f'Task "{task_text}" added successfully!')
            self.task_entry.delete(0, tk.END)
            self.deadline_entry.delete(0, tk.END)
        else:
            messagebox.showwarning("Incomplete Task", "Please enter both a task and a deadline.")

    def delete_task(self):
        selected_item = self.task_tree.selection()
        if selected_item:
            selected_task = self.task_tree.item(selected_item, "values")[0]
            del self.tasks[selected_task]
            self.save_tasks()
            self.task_tree.delete(selected_item)
            messagebox.showinfo("Task Deleted", f'Task "{selected_task}" deleted successfully!')
        else:
            messagebox.showwarning("No Task Selected", "Please select a task to delete.")

    def remind_tasks(self):
        current_time = datetime.datetime.now().time()
        target_time = datetime.time(17, 0)  # 5 PM

        if current_time >= target_time:
            messagebox.showinfo("Reminders", "It's already past 5 PM. Check your tasks!")
        elif not self.tasks:
            messagebox.showinfo("Reminders", "No tasks to remind you about.")
        else:
            tasks_str = "\n".join(f"{task} ({details['deadline']})" for task, details in self.tasks.items())
            reminder_message = f"Tasks for today:\n\n{tasks_str}"
            messagebox.showinfo("Reminders", reminder_message)

    def check_tasks_reminders(self):
        current_time = datetime.datetime.now().time()

        for task, details in self.tasks.items():
            deadline_iso = details["deadline"]
            reminder_sent = details["reminder_sent"]

            # Convert deadline_iso to time for comparison
            deadline = datetime.datetime.strptime(deadline_iso, "%Y-%m-%dT%H:%M:%S").time()

            if not reminder_sent and current_time >= deadline:
                self.send_task_reminder(task)
                details["reminder_sent"] = True
                self.save_tasks()

        # Refresh the task_tree to display all tasks
        self.refresh_task_tree()

        # Schedule the next call to check_tasks_reminders after 1000 milliseconds (1 second)
        self.root.after(1000, self.check_tasks_reminders)


    def send_task_reminder(self, task):
        reminder_message = f"Reminder: Task '{task}' is due now!"
        messagebox.showwarning("Task Reminder", reminder_message)

    def load_tasks(self):
        try:
            with open(self.file_path, "r") as file:
                data = file.read()
                if data:
                    self.tasks = json.loads(data)
                else:
                    self.tasks = {}
        except FileNotFoundError:
            self.tasks = {}

    def save_tasks(self):
        with open(self.file_path, "w") as file:
            json.dump(self.tasks, file)

    def schedule_reminder_check(self):
        # Schedule a call to check_tasks_reminders every 1000 milliseconds (1 second)
        self.root.after(1000, self.check_tasks_reminders)#
    
    def refresh_task_tree(self):
        # Clear the existing items in the tree
        for item in self.task_tree.get_children():
            self.task_tree.delete(item)

        # Populate the tree with all tasks
        for task, details in self.tasks.items():
            deadline_iso = details["deadline"]
            deadline_str = datetime.datetime.strptime(deadline_iso, "%Y-%m-%dT%H:%M:%S").strftime("%H:%M")
            reminder_sent = details["reminder_sent"]

            # Display a checkmark or cross in the "Reminder Sent" column
            reminder_sent_str = "✔" if reminder_sent else "✘"

            self.task_tree.insert("", "end", values=(task, deadline_str, reminder_sent_str))

if __name__ == "__main__":
    root = tk.Tk()
    app = TaskManager(root)
    root.mainloop()
