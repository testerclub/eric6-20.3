# -*- coding: utf-8 -*-

# Copyright (c) 2012 - 2020 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing a data structure for login forms.
"""


from PyQt5.QtCore import QUrl


class LoginForm(object):
    """
    Class implementing a data structure for login forms.
    """
    def __init__(self):
        """
        Constructor
        """
        self.url = QUrl()
        self.name = ""
        self.postData = ""
    
    def isValid(self):
        """
        Public method to test for validity.
        
        @return flag indicating a valid form (boolean)
        """
        return (
            not self.url.isEmpty() and
            bool(self.postData)
        )
