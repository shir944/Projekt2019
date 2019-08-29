# -*- coding: utf-8 -*-
"""
Created on Thu Aug 29 10:58:42 2019

@author: shir-
"""

from PyQt5 import QtCore, QtGui, QtWidgets 
import sys
import traceback

from gui6_arch_video import VideoTab
from gui6_arch_analysis import AnalysisTab

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, **kwargs):
        super(MainWindow, self).__init__(**kwargs)
        self.init_ui()
    
    def init_ui(self):
        self.tabs = QtWidgets.QTabWidget() 
        self.setCentralWidget(self.tabs)
    
        self.videotab = VideoTab(parent=self)
        self.analytab = AnalysisTab(parent=self)
        
        self.tabs.addTab(self.videotab, self.tr('Video'))
        self.tabs.addTab(self.analytab, self.tr('Analysis'))
        self.tabs.setTabEnabled(self.tabs.indexOf(self.videotab), True)
        self.tabs.setTabEnabled(self.tabs.indexOf(self.analytab), True)
        self.tabs.currentChanged.connect(self.tab_changed)
        
        menu_file = self.menuBar().addMenu(self.tr('File'))
        menu_file.addAction(self.tr('Open') + ' ...', self.open_file)
        menu_file.addSeparator()
        menu_file.addAction(self.tr('Exit'), self.close)
        
    def open_file(self):
        # print("open")
        # Inhalte der Methode open_file wurden ausgelagert
        file = self.videotab.open_file()
        # Video-Tab in den Vordergrund
        if file:
            self.tabs.setTabEnabled(self.tabs.indexOf(self.videotab), True)
            self.tabs.setCurrentWidget(self.videotab) 
    
    def tab_changed(self, index):
        try:
            tab = self.tabs.widget(index)
        except:
            traceback.print_exc()
    
if __name__ == '__main__':
    app = QtCore.QCoreApplication.instance() 
    if app is None:
        app = QtWidgets.QApplication(sys.argv)
    app.references = set()
    app.setStyle('Fusion')
    
    win = MainWindow()
    app.references.add(win)
    win.show()
    win.raise_()
    app.exec_()