import tkinter as tk
from tkinter import ttk
from datetime import datetime

import database
from calendar_radiobutton import Calendar

class App(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)

        database.initialize_db()

        self.container = ttk.Frame(self)
        self.container.pack(side="top", fill="both", expand = True)
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

        self.show_window(Login)

    def show_window(self, window, current=None, *args):
        if current:
            current.destroy()
        frame = window(self.container, self, *args)
        frame.grid(row=0, column=0, sticky="nsew")
        frame.tkraise()

    def exit_app(self):
        self.destroy()

class Login(ttk.Frame):
    def __init__(self, parent, controller):
        ttk.Frame.__init__(self,parent)
        self.controller = controller

        ttk.Label(self, text='Username').grid(row=0, column=0)
        ttk.Label(self, text='Password').grid(row=1, column=0)

        self.username = tk.StringVar()
        self.password = tk.StringVar()

        ttk.Entry(self, textvariable=self.username).grid(row=0, column=1)
        ttk.Entry(self, textvariable=self.password).grid(row=1, column=1)

        ttk.Button(self, text="Exit", command=self.controller.exit_app).grid(row=2, column=0)
        ttk.Button(self, text="Login", command=self.sign_in).grid(row=2, column=1)

    def sign_in(self):
        self.controller.show_window(MainMenu, self)

class MainMenu(ttk.Frame):
    def __init__(self, parent, controller):
        ttk.Frame.__init__(self,parent)

        ttk.Button(self, text="Ticket List", command=lambda: controller.show_window(Toc, self)).grid(row=0)
        ttk.Button(self, text="Exit", command=controller.exit_app).grid(row=1)

class Toc(ttk.Frame):
    def __init__(self, parent, controller):
        ttk.Frame.__init__(self, parent)
        self.controller = controller

        self.field_names = ('No', 'Date', 'Time', 'Informed by', 'Description')

        self.record_tree = self.create_table()
        ttk.Button(self, text="Add", command=lambda: controller.show_window(AddTicket, self)).grid(row=1, column=0)
        ttk.Button(self, text="Main Menu", command=lambda: controller.show_window(MainMenu, self)).grid(row=1, column=1)

        self.update_table()

        self.record_tree.bind('<Double-1>', self.open_update_ticket)

    def create_table(self):
        record_tree = ttk.Treeview(self, columns=self.field_names, show="headings")
        record_tree.grid(row=0)
        for column in self.field_names:
            record_tree.heading(column, text=column)
        return record_tree

    def open_update_ticket(self, event):
        self.controller.show_window(
            UpdateTicket,
            self,
            self.record_tree.item(self.record_tree.identify_row(event.y))['values']
        )

    def update_table(self):
        self.record_tree.delete(*self.record_tree.get_children())
        for ticket in database.get_all_records():
            self.record_tree.insert('', 'end', values=ticket)

class BaseTicket(ttk.Frame):
    def __init__(self, parent, controller):
        ttk.Frame.__init__(self, parent)
        self.controller = controller

    def build_form(self):
        record = []
        for row, field in enumerate(self.field_names):
            ttk.Label(self, text=field[0]).grid(row=row, column=0)
            record.append(field[1](self) if len(field) == 2 else field[1](self, **field[2]))
            record[-1].grid(row=row, column=1)
        return record

    def get_record(self):
        return [self.record[0].date_str] + [field.get() for field in self.record[1:]]


class AddTicket(BaseTicket):
    def __init__(self, parent, controller):
        BaseTicket.__init__(self, parent, controller)

        self.field_names = (
            ('Date', Calendar, {'settoday': True, 'monthsoncalendar': False}),
            ('Time', ttk.Entry),
            ('Informed by', ttk.Entry),
            ('Description', ttk.Entry),
        )

        self.record = self.build_form()

        ttk.Button(self, text="Add", command=self.add_record).grid(row=4, column=0)
        ttk.Button(self, text="Ticket List", command=lambda: controller.show_window(Toc, self)).grid(row=4, column=1)

    def add_record(self):
        database.add_record(self.get_record())
        self.controller.show_window(Toc, self)

class UpdateTicket(BaseTicket):
    def __init__(self, parent, controller, data):
        BaseTicket.__init__(self, parent, controller)

        date = datetime.strptime(data[1], '%Y-%m-%d')

        self.field_names = (
            ('Date', Calendar, {'day': date.day, 'year': date.year, 'month': date.month, 'monthsoncalendar': False}),
            ('Time', ttk.Entry),
            ('Informed by', ttk.Entry),
            ('Description', ttk.Entry),
        )

        self.record = self.build_form()

        for x in range(1, len(self.field_names)):
            self.record[x].insert('end', data[x+1])

        ttk.Button(self, text="Update", command=lambda: self.update_record(data[0])).grid(row=4, column=0)
        ttk.Button(self, text="Ticket List", command=lambda: controller.show_window(Toc, self)).grid(row=4, column=1)

    def update_record(self, number):
        database.update_record(number, self.get_record())
        self.controller.show_window(Toc, self)

if __name__ == "__main__":
    app = App()
    app.mainloop()
