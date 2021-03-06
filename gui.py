from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QHBoxLayout, QVBoxLayout, QLabel, \
    QSlider, QStyle, QSizePolicy
import sys
import cv2
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtMultimediaWidgets import QVideoWidget
from PyQt5.QtGui import QIcon, QPalette
from PyQt5.QtCore import Qt, QUrl
import time
from client import Client
from mycv import Cap
class Window(QWidget):
    def __init__(self, filename, client, option):
        super().__init__()
        self.setWindowTitle("PyQt5 Media Player")
        self.setGeometry(350, 100, 700, 500)
        self.setWindowIcon(QIcon('player.png'))
 
        p =self.palette()
        p.setColor(QPalette.Window, Qt.black)
        self.setPalette(p)
        self.has_load_file = False
        self.init_ui()
        self.client = client
        self.filename = filename
        self.show()
        self.option = option
 
    def init_ui(self):
 
        #create media player object
        self.mediaPlayer = QMediaPlayer(None, QMediaPlayer.VideoSurface)
 
 
        #create videowidget object
 
        videowidget = QVideoWidget()
 
 
        #create buttons
        self.openBtn = QPushButton('SETUP')
        teardownBtn = QPushButton('TEARDOWN')
        self.openBtn.clicked.connect(self.setup)
        teardownBtn.clicked.connect(self.teardown)
        
 
        #create button for playing
        self.playBtn = QPushButton()
        self.playBtn.setEnabled(False)
        self.playBtn.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
        self.playBtn.clicked.connect(self.play_video)
 

 
        #create slider
        self.slider = QSlider(Qt.Horizontal)
        self.slider.setRange(0,0)
        self.slider.sliderMoved.connect(self.set_position)
 
 
 
        #create label
        self.label = QLabel()
        self.label.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Maximum)
 
 
        #create hbox layout
        hboxLayout = QHBoxLayout()
        hboxLayout.setContentsMargins(0,0,0,0)
 
        #set widgets to the hbox layout
        hboxLayout.addWidget(self.openBtn)
        hboxLayout.addWidget(teardownBtn)
        hboxLayout.addWidget(self.playBtn)
        hboxLayout.addWidget(self.slider)
 
 
 
        #create vbox layout
        vboxLayout = QVBoxLayout()
        vboxLayout.addWidget(videowidget)
        vboxLayout.addLayout(hboxLayout)
        vboxLayout.addWidget(self.label)
 
 
        self.setLayout(vboxLayout)
 
        self.mediaPlayer.setVideoOutput(videowidget)
 
 
        #media player signals
 
        self.mediaPlayer.stateChanged.connect(self.mediastate_changed)
        self.mediaPlayer.positionChanged.connect(self.position_changed)
        self.mediaPlayer.durationChanged.connect(self.duration_changed)
    
    def teardown(self):
        self.client.send_teardown()
        if self.option: self.cap.start = False
        exit(0)
    def setup(self):
        #filename, _ = QFileDialog.getOpenFileName(self, "Open Video")
        self.client.rtsp_connect()
        self.client.send_setup()
        self.playBtn.setEnabled(True)
        self.openBtn.setEnabled(False)
    
    def handle_file(self):
        if self.client.tempfilepath != '':
            print(self.client.tempfilepath)
            self.mediaPlayer.setMedia(QMediaContent(QUrl.fromLocalFile(self.client.tempfilepath)))
            if self.option: self.cap = Cap(self.client.tempfilepath)
            

    def play_video(self):
        if self.mediaPlayer.state() == QMediaPlayer.PlayingState:
            self.mediaPlayer.pause()
            #TODO: send pause
            self.client.send_pause()
        else:
            self.client.send_play()
            if not self.has_load_file:
                time.sleep(0.5)
                self.handle_file()
                self.has_load_file = True
            self.mediaPlayer.play()
            if self.option: self.cap.start = True
            if self.option: self.cap.E_thread()
            print("playing")
            #TODO: send play
            
 
    def mediastate_changed(self, state):
        if self.mediaPlayer.state() == QMediaPlayer.PlayingState:
            self.playBtn.setIcon(
                self.style().standardIcon(QStyle.SP_MediaPause)
            )

        else:
            self.playBtn.setIcon(
                self.style().standardIcon(QStyle.SP_MediaPlay)
            )
 
    def position_changed(self, position):
        self.slider.setValue(position)
 
 
    def duration_changed(self, duration):
        self.slider.setRange(0, duration)
 
 
    def set_position(self, position):
        self.mediaPlayer.setPosition(position)
 
 
    def handle_errors(self):
        self.playBtn.setEnabled(False)
        self.label.setText("Error: " + self.mediaPlayer.errorString())
option = None
filename = sys.argv[1]
try:
    option = sys.argv[2]
except:
    pass
app = QApplication(sys.argv)
client = Client("127.0.0.1", 8888, 5541, filename)
if option == "gray":
    window = Window(filename, client, option)
else:window = Window(filename, client, None)

sys.exit(app.exec_())