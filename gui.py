from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QHBoxLayout, QVBoxLayout, QLabel, \
    QSlider, QStyle, QSizePolicy
from PyQt5.QtWidgets import QMainWindow
import sys
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtMultimediaWidgets import QVideoWidget
from PyQt5.QtGui import QIcon, QPalette, QPixmap
from PyQt5.QtCore import Qt, QUrl, pyqtSignal, QTimer
import time
from client import Client
from PIL.ImageQt import ImageQt

class ClientWindow(QMainWindow):
    _update_image_signal = pyqtSignal()

    def __init__(
            self,
            client,
            parent=None):
        super(ClientWindow, self).__init__(parent)
        self.video_player = QLabel()
        self.setup_button = QPushButton()
        self.play_button = QPushButton()
        self.pause_button = QPushButton()
        self.tear_button = QPushButton()
        self.error_label = QLabel()

        self._media_client = client
        self._update_image_signal.connect(self.update_image)
        self._update_image_timer = QTimer()
        self._update_image_timer.timeout.connect(self._update_image_signal.emit)

        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Client")

        self.setup_button.setEnabled(True)
        self.setup_button.setText('Setup')
        self.setup_button.clicked.connect(self.handle_setup)

        self.play_button.setEnabled(False)
        self.play_button.setText('Play')
        self.play_button.clicked.connect(self.handle_play)

        self.pause_button.setEnabled(False)
        self.pause_button.setText('Pause')
        self.pause_button.clicked.connect(self.handle_pause)

        self.tear_button.setEnabled(False)
        self.tear_button.setText('Teardown')
        self.tear_button.clicked.connect(self.handle_teardown)

        self.error_label.setSizePolicy(
            QSizePolicy.Preferred,
            QSizePolicy.Maximum)

        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)

        control_layout = QHBoxLayout()
        control_layout.setContentsMargins(0, 0, 0, 0)
        control_layout.addWidget(self.setup_button)
        control_layout.addWidget(self.play_button)
        control_layout.addWidget(self.pause_button)
        control_layout.addWidget(self.tear_button)

        layout = QVBoxLayout()
        layout.addWidget(self.video_player)
        layout.addLayout(control_layout)
        layout.addWidget(self.error_label)

        central_widget.setLayout(layout)

    def update_image(self):
        if not self._media_client.is_play:
            return
        frame = self._media_client.get_next_frame()
        if frame is not None:
            try:
                pix = QPixmap.fromImage(ImageQt(frame[0]).copy())
                self.video_player.setPixmap(pix)
            except:pass

    def handle_setup(self):
        self._media_client.rtsp_connect()
        self._media_client.send_setup()
        self.setup_button.setEnabled(False)
        self.play_button.setEnabled(True)
        self.tear_button.setEnabled(True)
        self._update_image_timer.start(1000//30)

    def handle_play(self):
        self._media_client.send_play()
        self.play_button.setEnabled(False)
        self.pause_button.setEnabled(True)

    def handle_pause(self):
        self._media_client.send_pause()
        self.pause_button.setEnabled(False)
        self.play_button.setEnabled(True)

    def handle_teardown(self):
        self._media_client.send_teardown()
        self.setup_button.setEnabled(True)
        self.play_button.setEnabled(False)
        self.pause_button.setEnabled(False)
        exit(0)


class Window(QWidget):
    def __init__(self, filename, client):
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

filename = sys.argv[1]
app = QApplication(sys.argv)
client = Client("127.0.0.1", 8888, 5541, filename)

if filename == "stream": 
    window = ClientWindow(client)
    window.resize(400, 300)
    window.show()
else: window = Window(filename, client)

sys.exit(app.exec_())