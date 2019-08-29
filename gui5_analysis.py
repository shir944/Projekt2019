from PyQt5 import QtCore, QtGui, QtWidgets
import pgm
import sys
import traceback
import numpy as np

"""
Import der Matplotlib-Funktionalität sowie sowie zusätzlicher Klassen
für die Integration von Matplotlib in ein Qt-GUI
""" 
import matplotlib
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as QtCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
import matplotlib.ticker as ticker
# Pandas importieren; Excel-ähnliche Tabellen uund Funktionen für Datenanalyse
# siehe Buch Python4DataAnalysis
import pandas as pd

# Import von Dekoratoren
import abc

class MPLFigure(QtCore.QObject, Figure):

    """Basisklasse für wiederverwendbare matplotlib Figure.
    Die zusätzliche Vererbung von der QObject-Klasse ermöglicht die
    Verwendung der Qt-Mechanismen signals/slots und translation
    """

    def __init__(self):
        super(MPLFigure, self).__init__()

    # Decorator zur Definition einer abstrakten Methode, die unbedingt
    # überschrieben werden muss, ansonsten Exception bei Objektinitialisierung
    @abc.abstractmethod
    def init_plots(self):
        # Löschen und Initialisieren von Plot-Elementen vor dem Neuzeichnen
        pass

    @abc.abstractmethod
    def plot_data(self, data):
        """Zeichnen der Daten

        :param data: Übergabe der zu zeichnenden Daten
        """
        pass


class Figure1(MPLFigure):

    """Sample figure class
    
    """

    def __init__(self):
        super(Figure1, self).__init__()

        # Zuordnung einer Leinwand "Canvas" zur Figure ermöglicht
        # das Speichern der Figure und ihre Ingegrations in ein Qt-Layout
        self.canvas = QtCanvas(self)

        # Erzeugen von drei Unterdiagrammen (subplot)
        self.ax1 = self.add_subplot(311)
        self.ax2 = self.add_subplot(312, sharex=self.ax1)
        self.ax3 = self.add_subplot(313, sharex=self.ax1)
        # GUI initialisieren
        self.init_plots()

    # Überschreiben der abstrakten Methode aus der geerbten Klasse MPLFigure
    def init_plots(self):
        # Löschen der Inhalte in den Unterdiagremmen (subplot)
        self.ax1.cla()
        # Zeichnen von Gitterlinien
        self.ax1.grid()
        # Titel setzen
        self.ax1.set_title(self.tr('Analysis Report'))
        # Beschriftung der Y-Achse
        self.ax1.set_ylabel(self.tr('Pupil Position') + ' [px]')
        self.ax1.set_xticklabels([''])

        # Wie zuvor bei ax1
        self.ax2.cla()
        self.ax2.grid()
        self.ax2.set_ylabel(self.tr('Pupil Velocity') + ' [px/s]')
        #self.ax2.set_xticklabels([''])

        # Wie zuvor bei ax1
        self.ax3.cla()
        self.ax3.grid()
        self.ax3.set_ylabel(self.tr('Absolute Velocity') + ' [px/s]')
        # Zusätzlich Beschriftung der X-Achse
        self.ax3.set_xlabel(self.tr('Time') + ' [s]')
        
    # Überschreiben der abstrakten Methode aus der geerbten Klasse MPLFigure
    def plot_data(self, data):
        # GUI erneut initialisieren
        self.init_plots()
        # Datenreihen 'Hor' und 'Ver' mit Augenpositionen über
        # Datenreihe 'Time' aus dem Pandas-Dataframe data zeichnen
        # self.ax1.plot(data.loc[:, 'Time'], data.loc[:, ('Hor','Ver')])
        # Legende Zeichnen
        self.ax1.legend(['Hor', 'Ver'], loc='upper right')
        # Datenskalierung an Diagramm anpassen, ohne Lücken am Rand
        self.ax1.autoscale(enable=True, axis='x', tight=True)

        # Wie zuvor bei ax1, jetzt aber mit Geschwindigkeitsdatan
        # self.ax2.plot(data.loc[:, 'Time'], data.loc[:, ('vHor','vVer')])
        self.ax2.legend(['Hor', 'Ver'], loc='upper right')
        self.ax2.autoscale(enable=True, axis='both', tight=True)

        # Wie zuvor bei ax1, jetzt aber mit gefilterten Daten
#        self.ax3.plot(data['Time'], data['vAbs']
#        , data['Time'], data['vConv']
#        , data['Time'], data['vFilt']
#        , data['Time'], data['vFFT']
#        )
        self.ax3.legend(['vAbs', 'vConv', 'vFilt', 'vFFT'], loc='upper right')
        self.ax3.autoscale(enable=True, axis='both', tight=True)
        np.interp

        # Leinwand neu bemalen
        self.canvas.draw()


class AnalysisTab(QtWidgets.QWidget):
    """Anzeige der Datenanalyse-Ergebnisse
    """
    output_ready = QtCore.pyqtSignal(str)

    def __init__(self, *args, **kwargs):
        # Konstruktor 
        super(AnalysisTab, self).__init__(*args, **kwargs)
        # GUI initialisieren
        self.init_ui()

    def init_ui(self):
        self.fig1 = Figure1()

        # Create Navigation controls to inspect figure
        self.toolbar = NavigationToolbar(self.fig1.canvas, self)

        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.toolbar)
        layout.addWidget(self.fig1.canvas)

    def plot_data(self, data):
        self.fig1.plot_data(data)
        

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
            # print('click')
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
    app.exec_()
