# -*- coding: utf-8 -*-

# Copyright (c) 2015 - 2020 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing a QWebEngineView to load the web inspector in.
"""


import json
import os

from PyQt5.QtCore import pyqtSignal, QSize, QUrl
from PyQt5.QtNetwork import QNetworkRequest
from PyQt5.QtWebEngineWidgets import (
    QWebEngineView, QWebEnginePage, QWebEngineSettings
)

from Globals import qVersionTuple

import Preferences

_VIEWS = []


class WebInspector(QWebEngineView):
    """
    Class implementing a QWebEngineView to load the web inspector in.
    
    @signal inspectorClosed emitted to indicate the closing of the inspector
        window
    """
    inspectorClosed = pyqtSignal()
    
    def __init__(self, parent=None):
        """
        Constructor
        
        @param parent reference to the parent widget
        @type QWidget
        """
        super(WebInspector, self).__init__(parent)
        
        self.__view = None
        self.__inspectElement = False
        
        self.__reloadGeometry()
        
        registerView(self)
        
        self.page().windowCloseRequested.connect(self.close)
        self.page().loadFinished.connect(self.__loadFinished)
    
    def closeEvent(self, evt):
        """
        Protected method to save the geometry when closed.
        
        @param evt event object
        @type QCloseEvent
        """
        Preferences.setGeometry("WebInspectorGeometry", self.saveGeometry())
        super(WebInspector, self).closeEvent(evt)
        
        if evt.isAccepted():
            self.inspectorClosed.emit()

    def __reloadGeometry(self):
        """
        Private method to restore the geometry.
        """
        geom = Preferences.getGeometry("WebInspectorGeometry")
        if geom.isEmpty():
            s = QSize(600, 600)
            self.resize(s)
        else:
            self.restoreGeometry(geom)
    
    def setView(self, view, inspectElement=False):
        """
        Public method to connect a view to this inspector.
        
        @param view reference to the view object
        @type WebBrowserView
        @param inspectElement flag indicating to start a web inspection
        @type bool
        """
        self.__view = view
        if not self.isEnabled():
            return
        
        self.__inspectElement = inspectElement
        
        try:
            self.page().setInspectedPage(self.__view.page())
        except AttributeError:
            # pre Qt 5.11
            port = Preferences.getWebBrowser("WebInspectorPort")
            inspectorUrl = QUrl("http://localhost:{0}".format(port))
            
            from WebBrowser.WebBrowserWindow import WebBrowserWindow
            self.__reply = WebBrowserWindow.networkManager().get(
                QNetworkRequest(inspectorUrl.resolved(QUrl("json/list"))))
            self.__reply.finished.connect(self.__inspectorReplyFinished)
    
    def __inspectorReplyFinished(self):
        """
        Private slot handling the reply.
        """
        # used for pre Qt 5.11
        result = str(self.__reply.readAll(), encoding="utf8")
        
        self.__reply.deleteLater()
        self.__reply = None
        
        pageUrl = QUrl()
        try:
            index = _VIEWS.index(self.__view)
        except ValueError:
            index = -1
        try:
            clients = json.loads(result)
            if len(clients) > index:
                port = Preferences.getWebBrowser("WebInspectorPort")
                inspectorUrl = QUrl("http://localhost:{0}".format(port))
                
                client = clients[index]
                pageUrl = inspectorUrl.resolved(
                    QUrl(client["devtoolsFrontendUrl"]))
            self.load(pageUrl)
            pushView(self)
            self.show()
        except json.JSONDecodeError:
            # ignore silently
            pass
    
    def inspectElement(self):
        """
        Public method to inspect an element.
        """
        self.__inspectElement = True
    
    @classmethod
    def isEnabled(cls):
        """
        Class method to check, if the web inspector is enabled.
        
        @return flag indicating the enabled state
        @rtype bool
        """
        if qVersionTuple() < (5, 11, 0):
            if not os.getenv("QTWEBENGINE_REMOTE_DEBUGGING"):
                return False
        
        from WebBrowser.WebBrowserWindow import WebBrowserWindow
        if not WebBrowserWindow.webSettings().testAttribute(
                QWebEngineSettings.JavascriptEnabled):
            return False
        
        if qVersionTuple() < (5, 11, 0):
            return Preferences.getWebBrowser("WebInspectorEnabled")
        else:
            return True
    
    def __loadFinished(self):
        """
        Private slot handling the finished signal.
        """
        if self.__inspectElement:
            self.__view.triggerPageAction(QWebEnginePage.InspectElement)
            self.__inspectElement = False


def registerView(view):
    """
    Function to register a view.
    
    @param view reference to the view
    @type WebBrowserView
    """
    if _VIEWS is None:
        return
    
    _VIEWS.insert(0, view)


def unregisterView(view):
    """
    Function to unregister a view.
    
    @param view reference to the view
    @type WebBrowserView
    """
    if _VIEWS is None:
        return
    
    if view in _VIEWS:
        _VIEWS.remove(view)


def pushView(view):
    """
    Function to push a view to the front of the list.
    
    @param view reference to the view
    @type WebBrowserView
    """
    if _VIEWS is None:
        return
    
    if view in _VIEWS:
        _VIEWS.remove(view)
    _VIEWS.insert(0, view)
