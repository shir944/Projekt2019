# -*- coding: utf-8 -*-
"""
Created on Thu Jun 20 11:03:22 2019

@author: bmoulay1
"""
from PyQt5 import QtCore, QtGui, QtWidgets
import pgm
import sys
import numpy as np
import traceback

class VideoFile():
    """
    Wrapper-Klasse für PGMReader
    """
    # Konstruktor
    def __init__(self, pgmfile, **kwargs):
        super(VideoFile, self).__init__(**kwargs)
        # Objektattribute mit Dummywerten belegen
        self.video = None
        self.width = 50
        self.height = 50
        self.length = 10
        self.img_buffer = False
        
        try:
            if pgmfile:
                self.video = pgm.PGMReader(pgmfile)
                self.width = self.video.width
                self.height = self.video.height
                self.lennght = self.video.length
                self.img_buffer = self.video.img_buffer
            else:
                self.img_buffer = \
                np.uint8(np.random.rand(self.height,self.width)*255)
        except:
            traceback.print_exc()
    
    #Methode zum Einlesen der Videobilder einpacken ("wrappen")            
    def seek_frame(self, n):
        if self.video:
            self.video.seek_frame(n)
        else:
            print('No File %d' %(n))                    
                
        
class VideoWidget(QtWidgets.QWidget):
    """
    Klassendefinition für die Augen-"Leinwand" ( canvas)
    """
    # Konstruktor
    def __init__(self, video, **kwargs):
        super(VideoWidget, self).__init__(**kwargs)
        # Qt benötigt einen Painter
        self.painter = QtGui.QPainter()
        self.init_ui(video)
        
      
    def init_ui(self, video):
       # Objekt der videodatei merken
       self.video = video
       # Fenstergröße auf Höhe und Breite des Videos setzen
       self.setFixedSize(video.width, video.height)
       # Erzeugen eines QImage-Objekt; Bild ist in video.img_buffer
       self.image = QtGui.QImage(video.img_buffer, 
                                  video.width, video.height,
                                  QtGui.QImage.Format_Grayscale8)
       
    # Definition der paintEvent-(Callback)-Funktion,
    # die von Qt Neuzeichnen aufgerufen wird     
    def paintEvent(self, event):
        self.painter.begin(self)
        # Malen des biulder 
        self.painter.drawImage(0,0, self.image)
        self.painter.end()
        
class ResultsTab(QtWidgets.QWidget):
    """
    Klassendefinition für Ergebnis-Tab
    """
    # Konstruktor
    def __init__(self, **kwargs):
        super(ResultsTab, self).__init__(**kwargs)
        
class VideoTab(QtWidgets.QWidget):
    """
    Klassendefinition für Video-Tabulator
    """
    # Konstruktor
    def __init__(self, **kwargs):
        super(VideoTab, self).__init__(**kwargs)        
        # Objekt der videodatei merken
        self.video = VideoFile(None)
        self.init_ui()
        
    def init_ui(self):

        self.display = VideoWidget(self.video, parent=self)
        # Schiberregler-Objekt mit horizontaler Ausrichtung
        self.slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.slider.setTickInterval(1)
        self.slider.setValue(0)
        self.slider.setRange(0, self.video.length-1)
        # Callback-Funktion registrieren 
        # Diese Funktion wird aufgerufen, wenn sich Schiberregler ändern
        self.slider.valueChanged.connect(self.display_frame)
        
        # Schieberregler in ein vertikales Layout einfügen
        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(self.display)
        layout.addWidget(self.slider)
        
    # Definition der Callback Funktion für Schiberregler    
    def display_frame(self, n):
        # Print anzahl von frame bei sliden
        #print("Slider: %d" % (n))
        self.video.seek_frame(n)
        self.display.update()
        
    def open_video(self, pgmfile):
        self.video = VideoFile(pgmfile)
        self.display.init_ui(self.video)
        self.display.update()
        
class MainWindow(QtWidgets.QMainWindow):
    """
    Klassendefinition für Hauptfenster
    """
    # Konstruktor
    def __init__(self, **kwargs):
        super(MainWindow, self).__init__(**kwargs)
        self.init_ui()
        
    def init_ui(self):

        self.tabs =QtWidgets.QTabWidget() 
        self.setCentralWidget(self.tabs)
        
        self.videotab = VideoTab(parent=self)
        self.resultstab = ResultsTab(parent=self)
        self.tabs.addTab(self.videotab, "Video")
        self.tabs.addTab(self.resultstab, "Results")
        
        #Menü erzeugen
        menu_file = self.menuBar().addMenu(self.tr('File'))
        menu_file.addAction(self.tr('Open') + ' ...', self.open_file)
        menu_file.addSeparator()
        menu_file.addAction(self.tr('Exit'), self.close)
        
    def open_file(self):
        file, _ = QtWidgets.QFileDialog\
        .getOpenFileName(caption=self.tr('Choose file'),
                         filter=self.tr('pgm Video File') + ' *.pgm') 
        if file:
            self.videotab.open_video(file)
            
        print('Open %s' % (file))
        
                    
        
if __name__ == '__main__':
    # Qt initialisieren
    app =  QtCore.QCoreApplication.instance()
    if app is None:
        app = QtWidgets.QApplication(sys.argv)
    app.references = set()  

    # Object für Hauptfenster erzeugen
    win = MainWindow()
    # Fenster registrieren 
    app.references.add(win)    
    # Fenster anzeigen
    win.show()
    # Fenster im Vordergrund
    win.raise_()
    # GUI-Ereignissschleife
    app.exec_()