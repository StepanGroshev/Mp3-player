from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtMultimedia import *
from PyQt5.QtMultimediaWidgets import *
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLineEdit, QDialogButtonBox, QFileDialog
import os
from MainWindow import Ui_MainWindow
from PlayListManagement import PlayListManagement, PlaylistDialog
def hhmmss(ms):
    h, r = divmod(ms, 3600000)  # milliseconds to hours
    m, r = divmod(r, 60000)  # milliseconds to minutes
    s, _ = divmod(r, 1000)  # milliseconds to seconds
    return f"{h}:{m:02d}:{s:02d}" if h else f"{m}:{s:02d}"

class ViewerWindow(QMainWindow):
    state = pyqtSignal(bool)

    def closeEvent(self, event):
        self.state.emit(False)
        super().closeEvent(event)

class PlaylistModel(QAbstractListModel):
    def __init__(self, playlist, *args, **kwargs):
        super(PlaylistModel, self).__init__(*args, **kwargs)
        self.playlist = playlist

    def data(self, index, role):
        if role == Qt.DisplayRole:
            media = self.playlist.media(index.row())
            return media.canonicalUrl().fileName()

    def rowCount(self, parent):
        return self.playlist.mediaCount()

class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)

        self.setupUi(self)

        self.player = QMediaPlayer()

        self.playlist_manager = PlayListManagement()  # Создание экземпляра PlayListManagement
        self.pushButton.clicked.connect(self.playlist_manager.open_create_playlist_dialog)

        self.player.play()

        self.playButton = self.findChild(QPushButton, "playButton")
        self.viewButton = self.findChild(QPushButton, "viewButton")

        self.playlist = QMediaPlaylist()
        self.player.setPlaylist(self.playlist)

        self.viewer = ViewerWindow(self)
        self.viewer.setWindowFlags(self.viewer.windowFlags() | Qt.WindowStaysOnTopHint)
        self.viewer.setMinimumSize(QSize(480, 360))

        videoWidget = QVideoWidget()
        self.viewer.setCentralWidget(videoWidget)
        self.player.setVideoOutput(videoWidget)

        self.playButton.pressed.connect(self.toggle_play)
        self.stopButton.pressed.connect(self.player.stop)
        self.volumeSlider.valueChanged.connect(self.player.setVolume)

        if self.viewButton:  # Проверка наличия viewButton
            self.viewButton.toggled.connect(self.toggle_viewer)
            self.viewer.state.connect(self.viewButton.setChecked)

        self.previousButton.pressed.connect(self.playlist.previous)
        self.nextButton.pressed.connect(self.playlist.next)

        self.model = PlaylistModel(self.playlist)
        self.playlistView.setModel(self.model)
        self.playlist.currentIndexChanged.connect(self.playlist_position_changed)
        selection_model = self.playlistView.selectionModel()
        selection_model.selectionChanged.connect(self.playlist_selection_changed)

        self.player.durationChanged.connect(self.update_duration)
        self.player.positionChanged.connect(self.update_position)
        self.timeSlider.sliderMoved.connect(self.player.setPosition)

        self.open_file_action.triggered.connect(self.open_file)

        self.setAcceptDrops(True)
        self.pushButton_6.clicked.connect(self.clear_playlist)
        self.show()

    def toggle_play(self):
        if self.player.state() == QMediaPlayer.PlayingState:
            self.player.pause()
        else:
            self.player.play()

    def clear_playlist(self):
        self.playlist.clear()
        self.model.layoutChanged.emit()
    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event):
        for url in event.mimeData().urls():
            self.playlist.addMedia(QMediaContent(url))

        self.model.layoutChanged.emit()

        if self.player.state() != QMediaPlayer.PlayingState:
            i = self.playlist.mediaCount() - len(event.mimeData().urls())
            self.playlist.setCurrentIndex(i)
            self.player.play()

    def open_file(self):
        paths, _ = QFileDialog.getOpenFileNames(self, "Open files", "",
                                                "mp3 Audio (*.mp3);mp4 Video (*.mp4)")
        for path in paths:
            media = QMediaContent(QUrl.fromLocalFile(path))
            duplicate = False
            for i in range(self.playlist.mediaCount()):
                if self.playlist.media(i) == media:
                    duplicate = True
                    break
            if not duplicate:
                self.playlist.addMedia(media)

        self.model.layoutChanged.emit()

        if self.player.state() != QMediaPlayer.PlayingState:
            i = self.playlist.mediaCount() - len(paths)
            self.playlist.setCurrentIndex(i)

    def update_duration(self, duration):
        self.timeSlider.setMaximum(duration)
        if duration >= 0:
            self.totalTimeLabel.setText(hhmmss(duration))

    def update_position(self, position):
        if position >= 0:
            self.currentTimeLabel.setText(hhmmss(position))

        self.timeSlider.blockSignals(True)
        self.timeSlider.setValue(position)
        self.timeSlider.blockSignals(False)

    def playlist_selection_changed(self, index):
        if index.indexes():
            i = index.indexes()[0].row()
            self.playlist.setCurrentIndex(i)

    def playlist_position_changed(self, position):
        if position > -1:
            self.playlistView.setCurrentIndex(self.model.index(position))

    def toggle_viewer(self, state):
        if state:
            self.viewer.show()
        else:
            self.viewer.hide()

    def erroralert(self, error):
        print("Error:", error)

if __name__ == '__main__':
    app = QApplication([])
    app.setApplicationName("Failamp")
    app.setStyle("Fusion")

    # Fusion dark palette from https://gist.github.com/QuantumCD/6245215.
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(53, 53, 53))
    palette.setColor(QPalette.WindowText, Qt.white)
    palette.setColor(QPalette.Base, QColor(25, 25, 25))
    palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
    palette.setColor(QPalette.ToolTipBase, Qt.white)
    palette.setColor(QPalette.ToolTipText, Qt.white)
    palette.setColor(QPalette.Text, Qt.white)
    palette.setColor(QPalette.Button, QColor(53, 53, 53))
    palette.setColor(QPalette.ButtonText, Qt.white)
    palette.setColor(QPalette.BrightText, Qt.red)
    palette.setColor(QPalette.Link, QColor(42, 130, 218))
    palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
    palette.setColor(QPalette.HighlightedText, Qt.black)
    app.setPalette(palette)
    app.setStyleSheet("QToolTip { color: #ffffff; background-color: #2a82da; border: 1px solid white; }")

    window = MainWindow()
    app.exec_()