from tkinter import *
import tkinter.filedialog


class PreferencesWindow:
    def __init__(self, controller, parent):
        self.preferences = controller.get_preferences()

        self.controller = controller
        self.master = parent

        self.top = Toplevel()
        self.top.wm_title("Preferences...")

        self.save_primers = IntVar().set(self.preferences['save'])
        self.show_primers = IntVar().set(self.preferences['show'])
        self.default_dir = StringVar().set(self.preferences['default_dir'])

        self.primer_save_frame = Frame(master=self.top, borderwidth=1, relief=GROOVE)
        self.primer_save_checkbutton = Checkbutton(master=self.primer_save_frame, text="Save discovered primers to a file", variable=self.save_primers, onvalue=1, offvalue=0)
        self.primer_save_checkbutton.pack(side=LEFT, fill=None, expand=True, anchor=W)
        self.primer_save_frame.pack(side=TOP, fill=X, expand=True, anchor=N)

        self.primer_show_frame = Frame(master=self.top, borderwidth=1, relief=GROOVE)
        self.primer_show_checkbutton = Checkbutton(master=self.primer_show_frame, text="Show discovered primers in new window", variable=self.show_primers, onvalue=1, offvalue=0)
        self.primer_show_checkbutton.pack(side=LEFT, fill=None, expand=True, anchor=W)
        self.primer_show_frame.pack(side=TOP, fill=X, expand=True, anchor=N)

        self.default_save_frame = Frame(master=self.top, borderwidth=1, relief=GROOVE)
        self.default_save_label = Label(master=self.default_save_frame, text="Default folder to save files to:")
        self.default_save_entry = Entry(master=self.default_save_frame, textvariable=self.default_dir)
        self.default_save_button = Button(master=self.default_save_frame, text="Choose folder", command=self.choose_folder)
        self.default_save_label.pack(side=LEFT, fill=None, expand=True, anchor=W)
        self.default_save_entry.pack(side=LEFT, fill=None, expand=True, anchor=W)
        self.default_save_button.pack(side=LEFT, fill=None, expand=True, anchor=W)
        self.default_save_frame.pack(side=TOP, fill=X, expand=True, anchor=N)

        self.button_frame = Frame(master=self.top, borderwidth=1, relief=GROOVE)
        self.cancel = Button(master=self.button_frame, text="Cancel", command=self.cancel)
        self.ok = Button(master=self.button_frame, text="Ok", command=self.ok)
        self.cancel.pack(side=LEFT, fill=None, expand=True, anchor=W)
        self.ok.pack(side=LEFT, fill=None, expand=True, anchor=W)
        self.button_frame.pack(side=TOP, fill=None, expand=True, anchor=N)

    def choose_folder(self):
        response = filedialog.askdirectory(initialdir=self.default_dir)
        self.default_dir = response

    def ok(self):
        # we need to either save primers or show them, otherwise CPU cycles are wasted.
        # if both save and show are set to 0, set show to 1
        if self.save_primers == 0:
            if self.show_primers == 0:
                self.show_primers = 1
        dictionary = {"save": self.save_primers, "show": self.show_primers, "default_dir": self.default_dir}
        with open("data/preferences.json", "w") as filehandle:
            json.dump(dictionary, filehandle, sort_keys=True, indent=4)
        self.controller.preferences = dictionary
        self.top.destroy()

    def cancel(self):
        self.top.destroy()
