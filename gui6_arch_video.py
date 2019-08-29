# -*- coding: utf-8 -*-
"""
Created on Thu Aug 29 10:33:05 2019

@author: shir-
"""

from PyQt5 import QtCore, QtGui, QtWidgets
import pgm
import sys
import traceback
import numpy as np

class VideoFile():
    def __init__(self, pgmfile=None, **kwargs): 
        super(VideoFile, self).__init__(**kwargs) 
        self.video = None 
        self.width = 50
        self.height = 50
        self.length = 10
        self.img_buffer = None 
        self.frame_no = 0
        try:
            if pgmfile:
                self.video = pgm.PGMReader(pgmfile)
                self.width = self.video.width
                self.height = self.video.height
                self.length = self.video.length
                self.img_buffer = self.video.img_buffer
            else:
                self.img_buffer = \
                np.uint8(np.random.rand(self.height,self.width)*255)
        except:
            traceback.print_exc()
    
    def isend(self):
        return self.frame_no>=self.length 
    
    def nextframe(self): 
        self.frame_no += 1
        return self.frame_no
    
    def seek_frame(self, n):
        if self.video:
            self.video.seek_frame(n) 
            self.frame_no = n
            # print("Bild %d" % (n))
        else:
            # print("no file %d" %(n))
            return
        
class VideoWidget(QtWidgets.QWidget):
    
    def __init__(self, video, **kwargs):
        super(VideoWidget, self).__init__(**kwargs)
        self.painter = QtGui.QPainter()
        self.init_ui(video)
    
    def init_ui(self, video):
        self.video = video
        self.setFixedSize(video.width, video.height) 
        self.image = QtGui.QImage(video.img_buffer, 
                                  video.width,
                                  video.height,
                                  QtGui.QImage.Format_Grayscale8)
        
    def paintEvent(self, event):
        self.painter.begin(self)
        self.painter.drawImage(0, 0, self.image)
        self.painter.end()
        
class VideoTab(QtWidgets.QWidget):
    
    def __init__(self, **kwargs):
        super(VideoTab, self).__init__(**kwargs) 
        self.video = VideoFile()
        self.init_ui()
        
    def init_ui(self):
        self.display = VideoWidget(self.video, parent=self)
        
        self.slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.slider.setTickInterval(1)
        self.slider.setValue(0)
        self.slider.setRange(0, self.video.length - 1)
        self.slider.valueChanged.connect(self.display_frame)
        
        self.btn_play = QtWidgets.QPushButton(self.tr('Play'))
        self.btn_play.setCheckable(True)
        self.btn_play.clicked.connect(self.play_clicked)
        
        self.playback_timer = QtCore.QTimer(self) 
        self.playback_timer.setTimerType(QtCore.Qt.PreciseTimer)
        self.playback_timer.timeout.connect(self.timerfun)
        self.play_stop()
        
        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(self.display)
        layout.addWidget(self.slider)
        layout.addWidget(self.btn_play)
        
    def display_frame(self, n):
        try: 
            self.video.seek_frame(n)
            self.display.update()
        except:
            traceback.print_exc()
        
    # Funktion open_file zum Öffnen des Dateidialogs hierher verschieben 
    def open_file(self):
        file, _ = QtWidgets.QFileDialog\
        .getOpenFileName(caption=self.tr('Choose file'),
                         filter=self.tr('pgm Video File') + ' *.pgm')
        if file:
            try:
                self.open_video(file)
            except:
                traceback.print_exc()
        # None oder Dateinamen zurückgeben
        return file
    
    def open_video(self, pgmfile): 
        self.video = VideoFile(pgmfile) 
        self.slider.setValue(0) 
        self.slider.setRange(0, self.video.length - 1) 
        self.slider.valueChanged.disconnect()
        self.slider.valueChanged.connect(self.display_frame)
        self.play_stop()
        self.display.init_ui(self.video)
        self.display.update()
        
    def play_clicked(self):
        try:
            # print(’click’)
            if self.playback:
                self.play_stop()
            else:
                self.play_start()
        except:
            traceback.print_exc()
    
    def play_start(self):
        self.playback = True 
        self.playback_timer.start(0)
        self.slider.valueChanged.disconnect()
    def play_stop(self):
        self.playback = False
        self.playback_timer.stop()
        self.slider.valueChanged.connect(self.display_frame) 
        
    def timerfun(self):
        try:
            if self.video.isend(): 
                self.play_stop()
            else:
                self.video.seek_frame(self.video.frame_no) 
                self.slider.setValue(self.video.frame_no)
                self.display.update()
                self.video.nextframe()
        except EOFError:
            self.play_stop() 
        except:
            traceback.print_exc()
            self.play_stop()

if __name__ == '__main__':
    
    class MainWindow(QtWidgets.QMainWindow): 
        """ 
        Klasse für Hauptfenster verschlanken und in main-Bereich verschieben 
        Wird nur dann aufgerufen, wenn dieses Skript direkt aufgerufen wird, 
        aber nicht wenn Skript als Modul importiert wird. 
        Dieses Verfahren eignet sich gut zum isolierten Testen von Modulen. 
        Dieses Modul enthält nur die Klassen für die Videodarstellung. 
        """
        def __init__(self, **kwargs): 
            super(MainWindow, self).__init__(**kwargs) 
            self.init_ui()
        
        def init_ui(self):
            # Keine Tabs; VideoTab-Klasse wird direkt eingebunden
            self.videotab = VideoTab(parent=self)
            self.setCentralWidget(self.videotab)
            
            menu_file = self.menuBar().addMenu(self.tr('File'))
            menu_file.addAction(self.tr('Open') + ' ...', self.open_file)
            menu_file.addSeparator()
            menu_file.addAction(self.tr('Exit'), self.close)
            # Beim Testen immer gleich eine Test-Videodatei öffnen
            # Das erspart Mausklicks
            self.videotab.open_video('sakkade.pgm')
            
        def open_file(self):
            self.videotab.open_file() 
    
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