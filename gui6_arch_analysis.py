# -*- coding: utf-8 -*-
"""
Created on Thu Aug 29 11:05:26 2019

@author: shir-
"""

from PyQt5 import QtCore, QtGui, QtWidgets
import pgm
import sys
import traceback
import numpy as np

from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as QtCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
import pandas as pd
import abc

class MPLFigure(QtCore.QObject, Figure):
    
    def __init__(self):
        super(MPLFigure, self).__init__()
        
    @abc.abstractmethod
    def init_plots(self):
        pass
    
    @abc.abstractmethod 
    def plot_data(self, data): 
        pass
    
class Figure1(MPLFigure):
    def __init__(self):
        super(Figure1, self).__init__()
        self.canvas = QtCanvas(self)
        self.ax1 = self.add_subplot(311)
        self.ax2 = self.add_subplot(312, sharex=self.ax1)
        self.ax3 = self.add_subplot(313, sharex=self.ax1)
        self.init_plots()
        
    def init_plots(self):
        self.ax1.cla()
        self.ax1.grid()
        self.ax1.set_title(self.tr('Analysis Report'))
        self.ax1.set_ylabel(self.tr('Pupil Position') + ' [px]')
        self.ax1.set_xticklabels([''])
        
        self.ax2.cla()
        self.ax2.grid()
        self.ax2.set_ylabel(self.tr('Pupil Velocity') + ' [px/s]')
        #self.ax2.set_xticklabels([''])
        
        self.ax3.cla()
        self.ax3.grid()
        self.ax3.set_ylabel(self.tr('Absolute Velocity') + ' [px/s]')
        self.ax3.set_xlabel(self.tr('Time') + ' [s]')
        
    def plot_data(self, data):
        self.init_plots() 
        # self.ax1.plot(data.loc[:, 'Time'], data.loc[:, ('Hor','Ver')])
        self.ax1.legend(['Hor', 'Ver'], loc='upper right')
        self.ax1.autoscale(enable=True, axis='x', tight=True)
        
        self.ax2.legend(['Hor', 'Ver'], loc='upper right')
        self.ax2.autoscale(enable=True, axis='both', tight=True)

#           self.ax3.plot(data['Time'], data['vAbs']
#         , data['Time'], data['vConv']
#         , data['Time'], data['vFilt']
#         , data['Time'], data['vFFT']
#         )
        self.ax3.legend(['vAbs', 'vConv', 'vFilt', 'vFFT'], loc='upper right')
        self.ax3.autoscale(enable=True, axis='both', tight=True)
        np.interp
        
        self.canvas.draw()

class AnalysisTab(QtWidgets.QWidget):
    output_ready = QtCore.pyqtSignal(str)
    
    def __init__(self, *args, **kwargs): 
        super(AnalysisTab, self).__init__(*args, **kwargs) 
        self.init_ui() 
    
    def init_ui(self):
        self.fig1 = Figure1()
        
        self.toolbar = NavigationToolbar(self.fig1.canvas, self) 
        
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.toolbar)
        layout.addWidget(self.fig1.canvas)
        
    def plot_data(self, data):
        self.fig1.plot_data(data) 
        
if __name__ == '__main__':
    
    class MainWindow(QtWidgets.QMainWindow): 
        """
        Klasse für Hauptfenster verschlanken und in main-Bereich verschieben 
        Wird nur dann aufgerufen, wenn dieses Skript direkt aufgerufen wird, 
        aber nicht wenn Skript als Modul importiert wird. 
        Dieses Verfahren eignet sich gut zum isolierten Testen von Modulen. 
        Dieses Modul enthält nur die Klassen für die Datendiagramme.
        """
        def __init__(self, **kwargs):
            super(MainWindow, self).__init__(**kwargs) 
            self.init_ui() 
        
        def init_ui(self):
            # Keine Tabs; AnalysisTab-Klasse wird direkt eingebunden 
            self.analytab = AnalysisTab(parent=self)
            self.setCentralWidget(self.analytab) 
            
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