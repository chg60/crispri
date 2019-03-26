from tkinter import *

from ui.frames.RootLayoutFrame import RootLayoutFrame

class MainWindow:
    def __init__(self, controller):
        # reference to controller
        self.controller = controller

        # create main window instance
        self.root = Tk()
        self.root.wm_title("CRISPRi Primer Finder")

        # create menu bar
        self.menu_bar = Menu(master=self.root, tearoff=0)
        self.root.config(menu=self.menu_bar)

        # create and populate help menu
        self.help_menu = Menu(master=self.menu_bar, tearoff=0)
        self.help_menu.add_command(label="Documentation", command=None)
        self.help_menu.add_command(label="Report a Bug", command=None)
        self.help_menu.add_command(label="Version Information", command=None)
        self.menu_bar.add_cascade(menu=self.help_menu, label="Help")

        # setup layout
        self.layout = RootLayoutFrame(root=self.root, controller=self.controller)

    def launch(self):
        self.root.mainloop()

    def destroy(self):
        self.root.destroy()
