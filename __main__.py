#!/usr/local/bin/python3

import os

from controller.MainWindowController import MainWindowController

if __name__ == "__main__":
    os.environ["PATH"] += "/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin"
    MainWindowController()
