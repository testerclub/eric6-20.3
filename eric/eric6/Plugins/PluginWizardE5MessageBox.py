# -*- coding: utf-8 -*-

# Copyright (c) 2010 - 2020 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing the E5MessageBox wizard plugin.
"""


from PyQt5.QtCore import QObject
from PyQt5.QtWidgets import QDialog

from E5Gui.E5Application import e5App
from E5Gui.E5Action import E5Action
from E5Gui import E5MessageBox

import UI.Info

# Start-Of-Header
name = "E5MessageBox Wizard Plugin"
author = "Detlev Offenbach <detlev@die-offenbachs.de>"
autoactivate = True
deactivateable = True
version = UI.Info.VersionOnly
className = "E5MessageBoxWizard"
packageName = "__core__"
shortDescription = "Show the E5MessageBox wizard."
longDescription = """This plugin shows the E5MessageBox wizard."""
pyqtApi = 2
# End-Of-Header

error = ""


class E5MessageBoxWizard(QObject):
    """
    Class implementing the E5MessageBox wizard plugin.
    """
    def __init__(self, ui):
        """
        Constructor
        
        @param ui reference to the user interface object (UI.UserInterface)
        """
        super(E5MessageBoxWizard, self).__init__(ui)
        self.__ui = ui

    def activate(self):
        """
        Public method to activate this plugin.
        
        @return tuple of None and activation status (boolean)
        """
        self.__initAction()
        self.__initMenu()
        
        return None, True

    def deactivate(self):
        """
        Public method to deactivate this plugin.
        """
        menu = self.__ui.getMenu("wizards")
        if menu:
            menu.removeAction(self.action)
        self.__ui.removeE5Actions([self.action], 'wizards')
    
    def __initAction(self):
        """
        Private method to initialize the action.
        """
        self.action = E5Action(
            self.tr('E5MessageBox Wizard'),
            self.tr('&E5MessageBox Wizard...'), 0, 0, self,
            'wizards_e5messagebox')
        self.action.setStatusTip(self.tr('E5MessageBox Wizard'))
        self.action.setWhatsThis(self.tr(
            """<b>E5MessageBox Wizard</b>"""
            """<p>This wizard opens a dialog for entering all the parameters"""
            """ needed to create an E5MessageBox. The generated code is"""
            """ inserted at the current cursor position.</p>"""
        ))
        self.action.triggered.connect(self.__handle)
        
        self.__ui.addE5Actions([self.action], 'wizards')

    def __initMenu(self):
        """
        Private method to add the actions to the right menu.
        """
        menu = self.__ui.getMenu("wizards")
        if menu:
            menu.addAction(self.action)
    
    def __callForm(self, editor):
        """
        Private method to display a dialog and get the code.
        
        @param editor reference to the current editor
        @return the generated code (string)
        """
        from WizardPlugins.E5MessageBoxWizard.E5MessageBoxWizardDialog import (
            E5MessageBoxWizardDialog
        )
        dlg = E5MessageBoxWizardDialog(None)
        if dlg.exec_() == QDialog.Accepted:
            line, index = editor.getCursorPosition()
            indLevel = editor.indentation(line) // editor.indentationWidth()
            if editor.indentationsUseTabs():
                indString = '\t'
            else:
                indString = editor.indentationWidth() * ' '
            return (dlg.getCode(indLevel, indString), True)
        else:
            return (None, False)
        
    def __handle(self):
        """
        Private method to handle the wizards action.
        """
        editor = e5App().getObject("ViewManager").activeWindow()
        
        if editor is None:
            E5MessageBox.critical(
                self.__ui,
                self.tr('No current editor'),
                self.tr('Please open or create a file first.'))
        else:
            code, ok = self.__callForm(editor)
            if ok:
                line, index = editor.getCursorPosition()
                # It should be done on this way to allow undo
                editor.beginUndoAction()
                editor.insertAt(code, line, index)
                editor.endUndoAction()
