# -*- coding: utf-8 -*-
"""
Created on Thu Jun 20 11:03:22 2019

@author: bmoulay1
"""
from PyQt5 import QtCore, QtGui, QtWidgets
import pgm
import sys

class VideoWidget(QtWidgets.QWidget):
    """
    Klassendefinition für die Augen-"Leinwand" ( canvas)
    """
    # Konstruktor
    def __init__(self, video, **kwargs):
        super(VideoWidget, self).__init__(**kwargs)
        # Objekt der videodatei merken
        self.video = video
        # Fenstergröße auf Höhe und Breite des Videos setzen
        self.setFixedSize(video.width, video.height)
        # Qt benötigt einen Painter
        self.painter = QtGui.QPainter()
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
    def __init__(self, video, **kwargs):
        super(VideoTab, self).__init__(**kwargs)        
        # Objekt der videodatei merken
        self.video = video
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
        
class MainWindow(QtWidgets.QMainWindow):
    """
    Klassendefinition für Hauptfenster
    """
    # Konstruktor
    def __init__(self, video, **kwargs):
        super(MainWindow, self).__init__(**kwargs)
        # Objekt der videodatei merken
        self.video = video
        self.init_ui()
        
    def init_ui(self):

        self.tabs =QtWidgets.QTabWidget() 
        self.setCentralWidget(self.tabs)
        
        self.videotab = VideoTab(self.video, parent=self)
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
        print('Open %s' % (file))
        
                    
        
if __name__ == '__main__':
    # videodatei offnen
    pgmfile = 'sakkade.pgm'
    video = pgm.PGMReader(pgmfile)
    
    # Qt initialisieren
    app =  QtCore.QCoreApplication.instance()
    if app is None:
        app = QtWidgets.QApplication(sys.argv)
    app.references = set()  

    # Object für Hauptfenster erzeugen
    win = MainWindow(video)
    # Fenster registrieren 
    app.references.add(win)    
    # Fenster anzeigen
    win.show()
    # Fenster im Vordergrund
    win.raise_()
    # GUI-Ereignissschleife
    app.exec_()