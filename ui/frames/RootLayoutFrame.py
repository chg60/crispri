from tkinter import *
from tkinter.ttk import *
import tkinter.messagebox
import tkinter.filedialog

class RootLayoutFrame(Frame):
    def __init__(self, root, controller):
        super(RootLayoutFrame, self).__init__(master=root)
        self.pack(expand=True, fill=BOTH)

        self.root = root
        self.controller = controller

        self.output_file = StringVar()

        self.name_frame = Frame(master=self)
        self.seq_name_label = Label(master=self.name_frame, text="Enter a name for your sequence:")
        self.seq_name_label.pack(side=LEFT, fill=None, expand=True)
        self.seq_name_entry = Entry(master=self.name_frame)
        self.seq_name_entry.pack(side=LEFT, fill=None, expand=True)
        self.name_frame.pack(side=TOP, fill=None, expand=True, anchor=NW)

        self.sequence_frame = Frame(master=self)
        self.sequence_label = Label(master=self.sequence_frame, text="Enter the knockdown gene's coding strand sequence:")
        self.sequence_label.pack(side=TOP, fill=None, expand=True, anchor=W)
        self.fiveprime_frame = Frame(master=self.sequence_frame, borderwidth=1, relief=GROOVE)
        self.fiveprime_label = Label(master=self.fiveprime_frame, text="5'-")
        self.fiveprime_label.pack(side=TOP, fill=X, expand=True, anchor=N)
        self.fiveprime_frame.pack(side=LEFT, fill=Y, expand=True)
        self.sequence_entry = Text(master=self.sequence_frame, borderwidth=1, relief=GROOVE, height=10)
        self.sequence_entry.pack(side=LEFT, fill=Y, expand=True)
        self.threeprime_frame = Frame(master=self.sequence_frame, borderwidth=1, relief=GROOVE)
        self.threeprime_label = Label(master=self.threeprime_frame, text="-3'")
        self.threeprime_label.pack(side=TOP, fill=X, expand=True, anchor=S)
        self.threeprime_frame.pack(side=LEFT, fill=Y, expand=True)
        self.sequence_frame.pack(side=TOP, fill=X, expand=True, anchor=NW)

        self.use_for_crispr_var = IntVar()
        self.use_for_crispr_frame = Frame(master=self, borderwidth=1, relief=GROOVE)
        self.use_for_crispr_checkbutton = Checkbutton(master=self.use_for_crispr_frame, text="CRISPR primers, check both strands for PAM sites", variable=self.use_for_crispr_var, onvalue=1, offvalue=0)
        self.use_for_crispr_checkbutton.pack(side=LEFT, fill=None, expand=True, anchor=W)
        self.use_for_crispr_frame.pack(side=TOP, fill=X, expand=True, anchor=NW)

        self.output_file_frame = Frame(master=self)
        self.output_file_label = Label(master=self.output_file_frame, text="Choose where to save the primers ->")
        self.output_file_label.pack(side=LEFT, fill=None, expand=True)
        self.output_file_button = Button(master=self.output_file_frame, text="Choose save file", command=self.choose_save_file)
        self.output_file_button.pack(side=LEFT, fill=None, expand=True)
        self.output_file_frame.pack(side=TOP, fill=None, expand=True, anchor=NW)

        self.button_frame = Frame(master=self)
        self.quit_button = Button(master=self.button_frame, text="Quit Program", command=self.quit)
        self.quit_button.pack(side=LEFT, fill=None, expand=True, anchor=SW)
        self.run_button = Button(master=self.button_frame, text="Run Program", command=self.run)
        self.run_button.pack(side=LEFT, fill=None, expand=True, anchor=SE)
        self.button_frame.pack(side=TOP, fill=X, expand=True, anchor=NW)

    def choose_save_file(self):
        self.output_file.set(tkinter.filedialog.asksaveasfilename(defaultextension=".txt", initialdir="/Users/"))
        return

    def quit(self):
        self.root.destroy()

    def run(self):
        if self.output_file.get() is None or self.output_file.get() == "":
            response = tkinter.messagebox.askyesnocancel(title="No Save File Chosen",
            message="No save file has been selected. Click 'Cancel' or 'No' to go back and choose one. Click 'Yes' to proceed anyway.")
            if response is None or response == False:
                self
                return
            else:
                self.controller.get_primers(name=self.seq_name_entry.get(), sequence=self.sequence_entry.get("1.0","end-1c"), save_file=None, mode="strong", crispr=self.use_for_crispr_var.get())
        else:
            self.controller.get_primers(name=self.seq_name_entry.get(), sequence=self.sequence_entry.get("1.0","end-1c"), save_file=self.output_file.get(), mode="strong", crispr=self.use_for_crispr_var.get())
