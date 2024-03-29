"""
Script Name:        webMapView.py
Script Author:      Kevin Foley

Description:        This customw widget displays a leaflet map containing
                    geojson markers and polygons depicting the default 
                    hydroclimatic stations. 
"""

from PyQt5 import QtWebEngineWidgets, QtCore, QtGui, QtWebChannel
import os

class webMapView(QtWebEngineWidgets.QWebEngineView):
    """
    """
    def __init__(self, parent=None):
        """
        """
        QtWebEngineWidgets.QWebEngineView.__init__(self)
        self.settings().setAttribute(QtWebEngineWidgets.QWebEngineSettings.LocalContentCanAccessRemoteUrls, True)
        self.page = webMapPage()
        url = QtCore.QUrl.fromLocalFile(os.path.abspath('resources/GUI/WebMap/WebMap.html'))
        self.setPage(self.page)
        self.load(url)
        

class webMapPage(QtWebEngineWidgets.QWebEnginePage):
    """
    """
    java_msg_signal = QtCore.pyqtSignal(str)
    def __init__(self, parent=None):
        """
        """
        QtWebEngineWidgets.QWebEnginePage.__init__(self)

    def acceptNavigationRequest(self, url,  _type, isMainFrame):
        """
        """
        if _type == QtWebEngineWidgets.QWebEnginePage.NavigationTypeLinkClicked:
            QtGui.QDesktopServices.openUrl(url)    
            return False
        else: 
            return True
    
    def javaScriptConsoleMessage(self, lvl, msg, line, source):
        """
        """
        #if lvl != 0:
        #    return
        print("Message logged from webmap console: ", msg)
        self.java_msg_signal.emit(msg)

# Test implementation
if __name__ == '__main__':
    from PyQt5 import QtWidgets
    import sys
    app = QtWidgets.QApplication(sys.argv)
    window = QtWidgets.QMainWindow()
    webmap = webMapView()
    window.setCentralWidget(webmap)
    window.show()
    sys.exit(app.exec_())