from PyQt6.QtWidgets import QApplication, QWidget, QLabel, QPushButton, QSlider, QVBoxLayout, QSpacerItem, QSizePolicy
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QPixmap, QTransform
import spotipy
import requests
import backend
import sys

def load_cover(label):
    playback = backend.sp.current_playback()

    if not playback or not playback.get("item"):
        return

    url = playback["item"]["album"]["images"][0]["url"]

    img_data = requests.get(url).content

    pixmap = QPixmap()
    pixmap.loadFromData(img_data)

    label.setPixmap(pixmap)

def skip_clicked():
    backend.sp.next_track()

def pause_clicked():
    playback = backend.sp.current_playback()

    if playback is None:
        print("Kein aktiver Playback")
        return

    if playback["is_playing"]:
        backend.sp.pause_playback()
    else:
        backend.sp.start_playback()

def change_value(value):
    if value % 5 == 0:
        backend.sp.volume(value)

def update_song():
    playback = backend.sp.current_playback()

    if not playback or not playback.get("item"):
        current_song.setText("No song playing")
        return

    song = playback["item"]["name"]
    artist = playback["item"]["artists"][0]["name"]

    current_song.setText(f"{song} - {artist}")

    url = playback["item"]["album"]["images"][0]["url"]

    if url != backend.last_cover:
        backend.last_cover = url
        load_cover(cover)


app = QApplication(sys.argv)

layout = QVBoxLayout()

window = QWidget()
window.setWindowTitle("SpotNode")
window.resize(500, 500)

skip = QPushButton("Skip", parent=window)
skip.resize(240, 100)
skip.move(10, 390)
skip.clicked.connect(skip_clicked)

pause = QPushButton("Pause", parent=window)
pause.resize(240, 100)
pause.move(250, 390)
pause.clicked.connect(pause_clicked)

vol = QSlider(Qt.Orientation.Horizontal)
vol.setMinimum(0)
vol.setMaximum(100)

if backend.playback:
    current = backend.playback["device"]["volume_percent"]
    vol.setValue(current)

vol.valueChanged.connect(change_value)

layout.addSpacing(250)
layout.addWidget(vol)

current_song = QLabel("Loading...", parent=window)
current_song.setAlignment(Qt.AlignmentFlag.AlignCenter)
current_song.setGeometry(0, 340, window.width(), 40)

cover = QLabel(parent=window)
cover.setGeometry(100, 25, 300, 300)
cover.setScaledContents(True)

window.setLayout(layout)

timer = QTimer()
timer.timeout.connect(update_song)
timer.start(2000)

window.show()
sys.exit(app.exec())