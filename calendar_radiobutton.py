"""
This source code was copied directly from https://github.com/Ripley6811/TixCalendar
"""

import tkinter as TKx
import calendar

class Calendar(TKx.Frame):
    datetime = calendar.datetime.date
    timedelta = calendar.datetime.timedelta
    today = datetime.today()

    # Use 3 or 4 different light colors for best results.
    MONTH_COLORS = ['grey92', 'thistle2', 'white', 'lightblue']

    def __init__(self, master=None, **kw):
        """Setup.

        Display defaults to system current month and year.

        Kwargs:
            year (int): Year integer for displaying year.
            month (int): Month integer for displaying month.
            day (int): Day integer used for preselecting date.
            settoday (bool): Set selection to today.
            selectbackground (str): Color string for selection background.
            textvariable (StringVar): Tk.StringVar for storing selection date.
            preweeks (int): Number of weeks to include before month.
            postweeks (int): Number of weeks to include after month.
            selectrange (bool): True to return dates as a range pair.
            monthsoncalendar (bool): True (default) shows month name on 1st.
        """

        # remove custom options from kw before initializating ttk.Frame
        today = self.datetime.today()
        self.year = kw.pop('year', today.year)
        self.month = kw.pop('month', today.month)
        self.day = kw.pop('day', None)
        self.settoday = kw.pop('settoday', False)
        self.sel_bg = kw.pop('selectbackground', 'gold')
        self.preweeks = kw.pop('preweeks', 0)
        self.postweeks = kw.pop('postweeks', 0)
        self.userange = kw.pop('selectrange', False)
        self.months_on_calendar = kw.pop('monthsoncalendar', True)

        self.range = []

        # StringVar parameter for returning a date selection.
        self.strvar = kw.pop('textvariable', TKx.StringVar())

        TKx.Frame.__init__(self, master, **kw)

        self._cal = calendar.Calendar(calendar.SUNDAY)


        # Insert dates in the currently empty calendar
        self._build_calendar()

        if self.settoday:
            self.date_set(today)
        elif self.day:
            self.date_set(self.year, self.month, self.day)

        self._build_dategrid()


    def _build_calendar(self):
        # Create frame and widgets.
        # Add header.
        hframe = TKx.Frame(self)
        hframe.pack(fill='x', expand=1)
        self.month_str = TKx.StringVar()
        lbtn = TKx.Button(hframe, text=u'\u25b2', command=self._prev_month)
        rbtn = TKx.Button(hframe, text=u'\u25bc', command=self._next_month)
        lbtn.pack(side='left')
        rbtn.pack(side='right')
        tl = TKx.Label(hframe, textvariable=self.month_str)
        tl.pack(side='top')
        self.top_label = tl
        self._set_month_str()
        self.days_frame = TKx.Frame(self)
        self.days_frame.pack(fill='x', expand=1)

    def _set_month_str(self):
        if self.date_obj:
            if self.userange:
                self.month_str.set(u' \u25c0\u25b6 '.join([unicode(d) for d in self.date_obj]))
            else:
                text = u'{}-{}-{}'.format(self.date_obj.year, calendar.month_name[self.date_obj.month], self.date_obj.day)
                self.month_str.set(text)
        else:
            #TODO: Fix month name encoding error on Chinese system.
            text = u'{}-{}'.format(self.year, calendar.month_name[self.month])
            self.month_str.set(text)

        if self.userange:
            try:
                self._color_date_range()
            except AttributeError:
                pass


    def _edit_range(self, event, date):
        #8 normal, 12 held ctrl, 1032 held B3
        if len(self.range) < 2:
            self.range = date, date
            return
        if event.state in (9, 12, 1032):
            self.range = self.range[1], date
        else:
            self.range = date, date

        self._color_buttons()
        self._set_month_str()
#        self._color_date_range()

    def _build_dategrid(self):
        # Prepare data.
        datematrix = self._cal.monthdatescalendar(self.year, self.month)
        for i in range(self.postweeks + 6 - len(datematrix)):
            # Get first day in list.
            d = datematrix[-1][-1]
            # Add a list of seven days prior to first in datematrix.
            datematrix.append([d + self.timedelta(x) for x in range(1,8)])
        for i in range(self.preweeks):
            # Get first day in list.
            d = datematrix[0][0]
            # Add a list of seven days prior to first in datematrix.
            datematrix.insert(0, [d - self.timedelta(x) for x in range(7,0,-1)])

        # Clear out date frame.
        for child in self.days_frame.winfo_children():
            child.destroy()

        # Add day headers and day radiobuttons.
        for col, text in enumerate(calendar.day_abbr):
            tl = TKx.Label(self.days_frame, text=text[:2])
            tl.grid(row=0, column=(col+1)%7, sticky='nsew')
        for row, week in enumerate(datematrix):
            for col, day in enumerate(week):
                text = str(day.day)
                if text == '1' and self.months_on_calendar:
                    text = calendar.month_name[day.month][:3]# + u'\n1'
                if self.userange:
                    trb = TKx.Checkbutton(self.days_frame,
                                      text=text,
                                      padx=4,
                                      indicator=False,
                                      onvalue=day,
                                      )
                else:
                    trb = TKx.Radiobutton(self.days_frame,
                                      text=text,
                                      padx=4,
                                      indicator=False,
                                      variable=self.strvar,
                                      value=day,
                                      )
                trb['command'] = self._set_month_str
                trb.grid(row=row + 1, column=col, sticky='nsew')
                self.days_frame.columnconfigure(col, weight=1)
                if self.sel_bg:
                    trb.config(selectcolor=self.sel_bg)
                if self.userange:
                    trb.bind('<1>', lambda e,x=day: self._edit_range(e,x))

        self._set_month_str()
        self._color_buttons()
        self._color_date_range()


    def _color_buttons(self):
        """
        Fill the background colors to distinguish months.
        """
        value = 'onvalue' if self.userange else 'value'
        for child in self.days_frame.winfo_children()[7:]:
            month = int(child[value].split('-')[1])
            child.config(bg=self.MONTH_COLORS[month%len(self.MONTH_COLORS)])

    def _color_date_range(self):
        """
        Color the selected date range if using range mode.
        """
        if self.userange:
            try:
                start, end = [str(d) for d in sorted(self.range)]
            except:
                start, end = 0,0

            for child in self.days_frame.winfo_children()[7:]:
                if start <= child['onvalue'] <= end:
                    child.select()
                else:
                    child.deselect()


    def _prev_month(self):
        """
        Shift month focus to the previous month and redraw radiobuttons.
        """
        tmp = self.datetime(self.year, self.month, 1)
        prev_month = tmp - self.timedelta(1)
        self.year = prev_month.year
        self.month = prev_month.month
        self._build_dategrid()

    def _next_month(self):
        """
        Shift month focus to the following month and redraw radiobuttons.
        """
        tmp = self.datetime(self.year, self.month, 25)
        next_month = tmp + self.timedelta(10)
        self.year = next_month.year
        self.month = next_month.month
        self._build_dategrid()

    def date_set(self, *args):
        """Set the current selected date.

        Args should either be a single datetime.date object or a
        list of three integers, [year, month, day].
        No args sets current date to None.

        Args:
            datetime.date: A date to set as selected.
            [int, int, int]: Three integers for year, month and day.

        """
        if len(args) == 0:
            """
            No arguments sets date to None.
            """
            self.strvar.set(None)
            return
        elif isinstance(args[0], self.datetime):
            """
            Date entered as datetime.date object.
            """
            self.range = args[0], args[0]
            self.strvar.set(args[0])
            if args[0].month != self.month or args[0].year != self.year:
                self.year = args[0].year
                self.month = args[0].month
                self._build_dategrid()
            return
        elif isinstance(args[0], int) and len(args) == 3:
            """
            Date entered as three integers; [year, month, day].
            """
            try:
                tmpdate = self.datetime(args[0], args[1], args[2])
                self.range = tmpdate, tmpdate
                self.strvar.set(tmpdate)
                if args[1] != self.month or args[0] != self.year:
                    self.year = args[0]
                    self.month = args[1]
                    self._build_dategrid()
            except TypeError:
                pass
            return

    @property
    def date_str(self):
        """Get string representation of selected date.

        Format is YYYY-MM-DD or an empty string if nothing is selected.
        """
        if self.userange:
            return [str(d) for d in sorted(self.range)]
        return self.strvar.get()

    @property
    def date_obj(self):
        """Get a datetime.date object of selected date.

        Returns a datetime.date object or None if nothing is selected.
        """
        if self.userange:
            return sorted(self.range)
        try:
            return self.datetime(*[int(x) for x in self.date_str.split(u'-')])
        except ValueError:
            return None
