#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright (c) 2016 - 2020 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Eric6 Hex Editor.

This is the main Python script that performs the necessary initialization
of the hex editor and starts the Qt event loop. This is a standalone version
of the integrated hex editor.
"""


import sys
import os

sys.path.insert(1, os.path.dirname(__file__))

for arg in sys.argv[:]:
    if arg.startswith("--config="):
        import Globals
        configDir = arg.replace("--config=", "")
        Globals.setConfigDir(configDir)
        sys.argv.remove(arg)
    elif arg.startswith("--settings="):
        from PyQt5.QtCore import QSettings
        settingsDir = os.path.expanduser(arg.replace("--settings=", ""))
        if not os.path.isdir(settingsDir):
            os.makedirs(settingsDir)
        QSettings.setPath(QSettings.IniFormat, QSettings.UserScope,
                          settingsDir)
        sys.argv.remove(arg)

from Globals import AppInfo

from Toolbox import Startup


def createMainWidget(argv):
    """
    Function to create the main widget.
    
    @param argv list of commandline parameters (list of strings)
    @return reference to the main widget (QWidget)
    """
    from HexEdit.HexEditMainWindow import HexEditMainWindow
    
    try:
        fileName = argv[1]
    except IndexError:
        fileName = ""
    
    editor = HexEditMainWindow(fileName, None)
    return editor


def main():
    """
    Main entry point into the application.
    """
    from PyQt5.QtGui import QGuiApplication
    QGuiApplication.setDesktopFileName("eric6_hexeditor.desktop")
    
    options = [
        ("--config=configDir",
         "use the given directory as the one containing the config files"),
        ("--settings=settingsDir",
         "use the given directory to store the settings files"),
        ("", "name of file to edit")
    ]
    appinfo = AppInfo.makeAppInfo(sys.argv,
                                  "Eric6 Hex Editor",
                                  "",
                                  "Little tool to edit binary files.",
                                  options)
    res = Startup.simpleAppStartup(sys.argv,
                                   appinfo,
                                   createMainWidget)
    sys.exit(res)

if __name__ == '__main__':
    main()
