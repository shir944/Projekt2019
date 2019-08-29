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
        # Aktuelle Bildnummer merken
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
            
    # Überprüfen ob Ende erreicht
    def isend(self):
        return self.frame_no>=self.length
    
    # Zähler für nächstes Bild berechnen (Inkrementieren)
    def nextframe(self):
        self.frame_no += 1
        return self.frame_no
    
    def seek_frame(self, n):
        if self.video:
            self.video.seek_frame(n)
            # Aktuelle Bildnummer merken
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

        # Pushbutton erzeugen und definieren
        self.btn_play = QtWidgets.QPushButton(self.tr('Play'))
        self.btn_play.setCheckable(True)
        # Slot-Funktion play_clicked übergeben
        # Diese Funktion wird aus der GUI-Eventschleife
        # beim Anklicken des Pushbuttons aufgerufen
        self.btn_play.clicked.connect(self.play_clicked)

        # Timer erzeugen und definieren
        self.playback_timer = QtCore.QTimer(self)
        self.playback_timer.setTimerType(QtCore.Qt.PreciseTimer)
        # Slot-Funktion timerfun übergeben
        # Diese Funktion wird aus der GUI-Eventschleife
        # immer dann aufgerufen, wenn nichts anderes passiert
        self.playback_timer.timeout.connect(self.timerfun)
        # Timer am Anfang stoppen
        self.play_stop()

        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(self.display)
        layout.addWidget(self.slider)
        # Pushbutton zum Layout hinzufügen
        layout.addWidget(self.btn_play)

    def display_frame(self, n):
        try:
            self.video.seek_frame(n)
            self.display.update()
        except:
            traceback.print_exc()

    def open_video(self, pgmfile):
        self.video = VideoFile(pgmfile)
        self.slider.setValue(0)
        self.slider.setRange(0, self.video.length - 1)
        self.slider.valueChanged.disconnect()
        self.slider.valueChanged.connect(self.display_frame)
        # Timer stoppen, da Abarbeiten der alten Datei sinnlos
        self.play_stop()
        self.display.init_ui(self.video)
        self.display.update()
            
    # Callback-Funktion für Pushbutton
    def play_clicked(self):
        try:
            # print('click')
            if self.playback:
                self.play_stop()
            else:
                self.play_start()
        except:
            traceback.print_exc()

    # Methoden zum Starten und Stoppen des Timers
    def play_start(self):
        # Zustand merken
        self.playback = True
        # Timer mit 0 ms Intervall starten
        self.playback_timer.start(0)
        # Schieberegler-Callback ausschalten
        self.slider.valueChanged.disconnect()
    def play_stop(self):
        self.playback = False
        # Timer stoppen
        self.playback_timer.stop()
        # Schieberegler-Callback wieder einschalten
        self.slider.valueChanged.connect(self.display_frame)
        # print("stop")
        
    # Callback-Funktion für Timer
    def timerfun(self):
        try:
            # Stoppen bei Erreichen des Endes der Videodatei
            if self.video.isend():
                self.play_stop()
            else:
                # Bild laden
                self.video.seek_frame(self.video.frame_no)
                # Schieberegler setzen
                self.slider.setValue(self.video.frame_no)
                # Bild anzeigen
                self.display.update()
                # Nächstes Bild
                self.video.nextframe()
        except EOFError:
            # Stoppen bei Dateifehler
            self.play_stop()
        except:
            traceback.print_exc()
            self.play_stop()

    
class AnalysisTab(QtWidgets.QWidget):
    def __init__(self, **kwargs):
        super(AnalysisTab, self).__init__(**kwargs)
        

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
        menu_file.addAction(self.tr('Open') + '...', self.open_file)
        menu_file.addSeparator()
        menu_file.addAction(self.tr('Exit'), self.close)

    def open_file(self):
        # print("open")
        file, _ = QtWidgets.QFileDialog\
        .getOpenFileName(caption=self.tr('Choose file'),
                         filter=self.tr('pgm Video File') + ' *.pgm')
        if file:
            self.tabs.setTabEnabled(self.tabs.indexOf(self.videotab), True)
            self.tabs.setCurrentWidget(self.videotab)
            try:
                self.videotab.open_video(file)
            except:
                traceback.print_exc()

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
    # GUI-Eventschleife unverändert, bearbeitet jetzt auch Timer-Events
    app.exec_()
