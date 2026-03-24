import sys
import tkinter as tk
from tkinter import messagebox
from datetime import date, datetime

import json
import os


pantry = []

def resource_path(filename):
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(os.getcwd(), filename)
    return os.path.join(os.path.dirname(__file__), filename)


SAVE_FILE = resource_path("pantry.json")

def load_pantry():
    global pantry
    if os.path.exists(SAVE_FILE):
        with open(SAVE_FILE, "r") as f:
            pantry = json.load(f)


def save_pantry():
    with open(SAVE_FILE, "w") as f:
        json.dump(pantry, f)


def ordinal_suffix(day):
    match day:
        case 11 | 12 | 13:
            return "th"
        case _:
            match day % 10:
                case 1:
                    return "st"
                case 2:
                    return "nd"
                case 3:
                    return "rd"
                case _:
                    return "th"


def str_to_date(date_str):
    return datetime.strptime(date_str, "%d%m%y").date()



def validate_date(date_str):
    current_year = date.today().year % 100

    if len(date_str) != 6 or not date_str.isdigit():
        return None, "Invalid format."

    day = int(date_str[:2])
    month = int(date_str[2:4])
    year = int(date_str[4:])

    if month < 1 or month > 12:
        return None, "Invalid month."

    if year < current_year:
        return None, "Invalid year."

    try:
        parsed_date = datetime.strptime(date_str, "%d%m%y").date()
    except ValueError:
        return None, "Invalid date."

    return parsed_date, None



def add_item():
    name = name_entry.get().strip()
    date_str = date_entry.get().strip()

    if not name:
        messagebox.showerror("Error", "Item name required.")
        return

    parsed_date, error = validate_date(date_str)
    if error:
        messagebox.showerror("Error", error)
        return

    day = parsed_date.day
    month = parsed_date.strftime("%B")
    year = parsed_date.strftime("%y")
    suffix = ordinal_suffix(day)

    formatted_date = f"{day}{suffix} {month} 20{year}"

    if not messagebox.askyesno("Confirm", f"You entered {formatted_date}\nIs this correct?"):
        return

    pantry.append((name, date_str))
    save_pantry()
    messagebox.showinfo("Success", "Item added.")
    refresh_list()


def remove_item():
    selection = pantry_list.curselection()
    if not selection:
        messagebox.showerror("Error", "Select an item to remove.")
        return

    index = selection[0]
    name, _ = pantry[index]

    if messagebox.askyesno("Confirm", f"Remove '{name}'?"):
        pantry.pop(index)
        save_pantry()
        messagebox.showinfo("Success", "Item removed.")
        refresh_list()


def refresh_list():
    pantry_list.delete(0, tk.END)

    if  not pantry:
        pantry_list.insert(
            tk.END,
            "Nothing to lose."
        )
        return

    today = date.today()
    sorted_pantry = sorted(pantry, key=lambda item: str_to_date(item[1]))

    for name, date_str in sorted_pantry:
        expiry_date = str_to_date(date_str)
        days_left = (expiry_date - today).days

        day = expiry_date.day
        month = expiry_date.strftime("%B")
        year = expiry_date.strftime("%y")
        suffix = ordinal_suffix(day)

        formatted_date = f"{day}{suffix} {month} 20{year}"
        output = f"{name} - {formatted_date}"

        if days_left < 0:
            output += " ❌ EXPIRED"
        elif days_left <= 21 and days_left >1:
            output += f" ⚠️ {days_left} days left"
        elif days_left == 1:
            output += " ⚠️ EXPIRES TOMORROW"

        pantry_list.insert(tk.END, output)
        
def focus_date(event):
    date_entry.focus_set()


def submit_item(event):
    add_item()



root = tk.Tk()
root.title("Pantry Tracker")
root.resizable(False, False)

tk.Label(root, text="Item Name").grid(row=0, column=0, padx=5, pady=5, sticky="w")
name_entry = tk.Entry(root, width=25)
name_entry.bind("<Return>", focus_date)
name_entry.grid(row=0, column=1, padx=5, pady=5)

tk.Label(root, text="Expiry Date (DDMMYY)").grid(row=1, column=0, padx=5, pady=5, sticky="w")
date_entry = tk.Entry(root, width=25)
date_entry.bind("<Return>", submit_item)
date_entry.grid(row=1, column=1, padx=5, pady=5)

tk.Button(root, text="Add Item", width=15, command=add_item).grid(row=2, column=0, pady=5)
tk.Button(root, text="Remove Item", width=15, command=remove_item).grid(row=2, column=1, pady=5)

pantry_list = tk.Listbox(root, width=50, height=10)
pantry_list.grid(row=4, column=0, columnspan=2, padx=5, pady=5)

load_pantry()

refresh_list()

root.mainloop()
