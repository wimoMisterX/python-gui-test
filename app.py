import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
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
        controller.title('Login')
        self.controller = controller

        ttk.Label(self, text='Username').grid(row=0, column=0)
        ttk.Label(self, text='Password').grid(row=1, column=0)

        self.username = ttk.Entry(self)
        self.password = ttk.Entry(self)
        self.username.grid(row=0, column=1)
        self.password.grid(row=1, column=1)

        ttk.Button(self, text="Exit", command=self.controller.exit_app).grid(row=2, column=0)
        ttk.Button(self, text="Login", command=self.sign_in).grid(row=2, column=1)

    def sign_in(self):
        if self.username.get() == 'admin' and self.password.get() == 'admin':
            self.controller.show_window(MainMenu, self)
        else:
            messagebox.showerror("Error", "Invalid username or password")

class MainMenu(ttk.Frame):
    def __init__(self, parent, controller):
        ttk.Frame.__init__(self,parent)
        controller.title('Main Menu')

        ttk.Button(self, text="Ticket List", command=lambda: controller.show_window(TicketList, self)).grid(row=0)
        ttk.Button(self, text="Exit", command=controller.exit_app).grid(row=1)

class TicketList(ttk.Frame):
    def __init__(self, parent, controller):
        ttk.Frame.__init__(self, parent)
        controller.title('Open tickets list')
        self.controller = controller

        self.field_names = ('No', 'Date', 'Time', 'Informed by', 'Description', '2G', '3G', 'LTE', 'Wifi', 'Fault responsible', 'Fault details', 'Fault cause')

        self.record_tree = self.create_table()
        ttk.Button(self, text="New Ticket", command=lambda: controller.show_window(AddTicket, self)).grid(row=1, column=0)
        ttk.Button(self, text="Main Menu", command=lambda: controller.show_window(MainMenu, self)).grid(row=1, column=1)

        self.update_table()

        self.record_tree.bind('<Double-1>', self.open_update_ticket)

    def create_table(self):
        record_tree = ttk.Treeview(self, columns=self.field_names, show="headings")
        record_tree.grid(row=0, columnspan=2)
        for column in self.field_names:
            record_tree.heading(column, text=column)
        return record_tree

    def open_update_ticket(self, event):
        record = self.record_tree.item(self.record_tree.identify_row(event.y))['values']
        if record:
            self.controller.show_window(
                UpdateTicket,
                self,
                record
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
            if len(field) == 3 and type(field[2]) == tuple:
                if field[2][0] == True:
                    field[1](self, **field[2][1]).grid(row=row, column=1)
                else:
                    field[1](self, *field[2]).grid(row=row, column=1)
                record.append(field[2][1]['variable'] if field[2][0] == True else field[2][0])
            else:
                record.append(field[1](self) if len(field) == 2 else field[1](self, **field[2]))
                record[-1].grid(row=row, column=1)
        return record

    def clean_record(self, record):
        return ['' if record[x] in ['Select a option'] else record[x] for x in range(len(record))]

    def get_record(self):
        return [self.record[0].date_str] + [field.get() for field in self.record[1:]]


class AddTicket(BaseTicket):
    def __init__(self, parent, controller):
        BaseTicket.__init__(self, parent, controller)
        controller.title('Add Ticket')

        self.field_names = (
            ('Date', Calendar, {'settoday': True, 'monthsoncalendar': False}),
            ('Time', ttk.Entry, {'state': 'disabled'}),
            ('Informed by', ttk.OptionMenu, (tk.StringVar(controller), 'Select a option', 'INOC', 'Regional OP', 'Dialog', 'SLT')),
            ('Description', ttk.Entry),
            ('2G', ttk.Entry),
            ('3G', ttk.Entry),
            ('LTE', ttk.Entry),
            ('Wifi', ttk.Entry),
        )

        self.record = self.build_form()

        ttk.Button(self, text="Add", command=self.add_record).grid(row=8, column=0)
        ttk.Button(self, text="Ticket List", command=lambda: controller.show_window(TicketList, self)).grid(row=8, column=1)

        self.show_current_time()

    def show_current_time(self):
        self.record[1].configure(state='normal')
        self.record[1].delete(0, 'end')
        self.record[1].insert(0, datetime.now().strftime('%H:%M'))
        self.record[1].configure(state='disabled')
        self.time_update = self.record[1].after(60000, self.show_current_time)

    def add_record(self):
        self.record[1].after_cancel(self.time_update)
        self.time_update = None
        database.add_record(self.clean_record(self.get_record()))
        self.controller.show_window(TicketList, self)

class UpdateTicket(BaseTicket):
    def __init__(self, parent, controller, data):
        BaseTicket.__init__(self, parent, controller)
        controller.title('Update Ticket')

        date = datetime.strptime(data[1], '%Y-%m-%d')
        ticket_status = tk.StringVar(controller)
        ticket_status.set('Open')

        self.field_names = (
            ('Date', Calendar, {'day': date.day, 'year': date.year, 'month': date.month, 'monthsoncalendar': False}),
            ('Time', ttk.Entry),
            ('Informed by', ttk.OptionMenu, (tk.StringVar(controller), data[3] or 'Select a option', 'INOC', 'Regional OP', 'Dialog', 'SLT')),
            ('Description', ttk.Entry),
            ('2G', ttk.Entry),
            ('3G', ttk.Entry),
            ('LTE', ttk.Entry),
            ('Wifi', ttk.Entry),
            ('Fault responsible', ttk.OptionMenu, (tk.StringVar(controller), data[9] or 'Select a option', 'TxOP', 'Regional Op', 'SLT', 'Dialog')),
            ('Fault details', ttk.Entry),
            ('Fault cause', ttk.OptionMenu, (tk.StringVar(controller), data[11] or 'Select a option', 'Annexure')),
            ('Close ticket', ttk.Checkbutton, (True, {'text': '', 'variable': ticket_status, 'onvalue': 'Closed', 'offvalue': 'Open'}))
        )

        self.record = self.build_form()

        for x in [n for n in range(2, len(self.field_names)) if n not in [3, 9, 11, 12]]:
            self.record[x-1].insert('end', data[x])

        ttk.Button(self, text="Update", command=lambda: self.update_record(data[0])).grid(row=12, column=0)
        ttk.Button(self, text="Ticket List", command=lambda: controller.show_window(TicketList, self)).grid(row=12, column=1)

    def update_record(self, number):
        database.update_record(number, self.clean_record(self.get_record()))
        self.controller.show_window(TicketList, self)

if __name__ == "__main__":
    app = App()
    app.mainloop()
