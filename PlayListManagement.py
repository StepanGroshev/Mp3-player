from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLineEdit, QDialogButtonBox, QFileDialog
import os

class PlayListManagement(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(PlayListManagement, self).__init__(parent)

        self.listView = QtWidgets.QListView(self)
        self.listView.setGeometry(QtCore.QRect(0, 0, 411, 321))
        self.listView.setObjectName("listView")

        self.pushButton = QtWidgets.QPushButton(self)
        self.pushButton.setGeometry(QtCore.QRect(420, 10, 91, 31))
        self.pushButton.setObjectName("pushButton")
        self.pushButton.setText("Create Playlist")

        self.pushButton.clicked.connect(self.open_create_playlist_dialog)

        self.all_playlists_dir = "AllPlaylists"  # Директория для сохранения всех плейлистов
        if not os.path.exists(self.all_playlists_dir):
            os.mkdir(self.all_playlists_dir)

        # Отображение списка плейлистов в ListView
        self.model = QtGui.QStandardItemModel(self.listView)
        self.listView.setModel(self.model)
        self.update_playlist_view()

    def open_create_playlist_dialog(self):
        dialog = PlaylistDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            # Действия при нажатии кнопки "Далее"
            playlist_name = dialog.get_playlist_name()
            playlist_files = dialog.get_selected_files()

            playlist_dir = os.path.join(self.all_playlists_dir, playlist_name)
            if not os.path.exists(playlist_dir):
                os.mkdir(playlist_dir)

            for file_path in playlist_files:
                file_name = os.path.basename(file_path)
                destination_path = os.path.join(playlist_dir, file_name)
                os.rename(file_path, destination_path)

            self.update_playlist_view()

    def update_playlist_view(self):
        self.model.clear()
        playlists = os.listdir(self.all_playlists_dir)
        for playlist in playlists:
            item = QtGui.QStandardItem(playlist)
            self.model.appendRow(item)

class PlaylistDialog(QDialog):
    def __init__(self, parent=None):
        super(PlaylistDialog, self).__init__(parent)

        self.setWindowTitle('Create Playlist')
        self.layout = QVBoxLayout(self)

        self.playlist_name_input = QLineEdit()
        self.layout.addWidget(self.playlist_name_input)

        self.button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.layout.addWidget(self.button_box)

        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)

        self.selected_files = []

    def get_playlist_name(self):
        return self.playlist_name_input.text().strip()

    def get_selected_files(self):
        return self.selected_files

    def accept(self):
        self.selected_files = QFileDialog.getOpenFileNames(self, 'Select Files', '', 'All files (*.*)')[0]
        super(PlaylistDialog, self).accept()

        