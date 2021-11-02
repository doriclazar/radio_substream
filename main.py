import sys
import json
import os
import requests
from PyQt5.QtCore import QUrl, Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import (QApplication, QWidget, QPushButton, QVBoxLayout, QHBoxLayout,
                             QSlider, QListWidget, QListWidgetItem, QTextEdit, QGroupBox)
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent

with open('data/radio_stations.json', 'r', encoding='utf-8') as radio_stations_file:
    radio_stations = json.loads(radio_stations_file.read())['radio_stations']


class LSquareButton(QPushButton):
    def __init__(self, parent=None, signal=None, icon_path=None):
        super(LSquareButton, self).__init__(parent)
        self.setMaximumHeight(60)
        self.setMinimumWidth(self.height())
        self.setMaximumWidth(self.height())
        self.setIcon(QIcon(icon_path))
        self.clicked.connect(signal)


class MainWindow(QWidget):
    """ Main widget with resizable borders."""

    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)

        self.resize(800, 600)
        self.setWindowTitle("Radio Substream")

        self.main_layout = QVBoxLayout()
        self.setLayout(self.main_layout)

        self.stations_list = QListWidget()
        self.create_info_panel()

        self.media_player = QMediaPlayer()
        self.media_player.setMedia(QMediaContent(QUrl(radio_stations[0]['url'])))
        self.media_player.stateChanged.connect(self.update_play_stop_button)

        self.play_stop_button = LSquareButton('', self.play_stop, 'fixtures/img/play.png')
        self.create_control_panel()

    def create_info_panel(self):
        """ Creates a panel with widgets for info display at the top of the main window."""

        info_group = QGroupBox()
        info_layout = QHBoxLayout()

        radio_widgets = {}
        if not os.path.exists('data/icons'):
            os.makedirs('data/icons')
        for radio_station in radio_stations:
            icon_name = radio_station['name'].replace(' ', '-')
            icon_path = f'data/icons/{icon_name}.ico'
            if not os.path.exists(icon_path):
                icon_response = requests.get(radio_station['icon'])
                with open(icon_path, 'wb') as icon_file:
                    icon_file.write(icon_response.content)

            radio_widgets[radio_station['name']] = QListWidgetItem(radio_station['name'])
            radio_widgets[radio_station['name']].setData(3, radio_station['url'])
            radio_widgets[radio_station['name']].setIcon(QIcon(icon_path))
            self.stations_list.addItem(radio_widgets[radio_station['name']])

        self.stations_list.item(0).setSelected(True)
        self.stations_list.itemDoubleClicked.connect(self.switch_the_station)
        self.stations_list.currentItemChanged.connect(self.get_recent_tracks)
        info_layout.addWidget(self.stations_list)

        history_box = QTextEdit()
        info_layout.addWidget(history_box)

        lyrics_box = QTextEdit()
        info_layout.addWidget(lyrics_box)

        info_group.setLayout(info_layout)
        self.main_layout.addWidget(info_group)

    def create_control_panel(self):
        """ Creates a panel with widgets for control over radio stations at the bottom of the main window."""

        control_group = QGroupBox()
        control_group.setMaximumHeight(80)
        control_layout = QHBoxLayout()
        control_group.setLayout(control_layout)

        volume_slider = QSlider(Qt.Vertical)
        volume_slider.setMaximum(100)
        volume_slider.valueChanged.connect(self.media_player.setVolume)
        volume_slider.setValue(15)
        control_layout.addWidget(volume_slider)
        control_layout.addStretch(1)

        previous_preview_button = LSquareButton('', self.previous_preview, 'fixtures/img/previous.png')
        control_layout.addWidget(previous_preview_button)

        previous_play_button = LSquareButton('', self.previous_play, 'fixtures/img/step-backward.png')
        control_layout.addWidget(previous_play_button)

        control_layout.addWidget(self.play_stop_button)

        next_preview_button = LSquareButton('', self.next_preview, 'fixtures/img/next.png')
        control_layout.addWidget(next_preview_button)

        next_play_button = LSquareButton('', self.next_play, 'fixtures/img/step-forward.png')
        control_layout.addWidget(next_play_button)

        control_layout.addStretch(1)
        self.main_layout.addWidget(control_group)

    def previous_preview(self):
        """ Selects previous radio station."""
        current_row = self.stations_list.currentRow()
        if not current_row == 0:
            self.stations_list.setCurrentRow(current_row-1)

    def previous_play(self):
        """ Selects previous radio station, and runs it's stream."""
        self.previous_preview()
        self.switch_the_station(self.stations_list.selectedItems()[0])

    def next_preview(self):
        """ Selects next radio station."""
        current_row = self.stations_list.currentRow()
        if not current_row == self.stations_list.count() - 1:
            self.stations_list.setCurrentRow(current_row + 1)

    def next_play(self):
        """ Selects next radio station, and runs it's stream."""
        self.next_preview()
        self.switch_the_station(self.stations_list.selectedItems()[0])

    def get_recent_tracks(self, sender_item):
        """ Displays song history for a selected radio station."""
        print(sender_item.data(3))

    def switch_the_station(self, sender_item):
        """ Plays selected radio station."""
        self.media_player.setMedia(QMediaContent(QUrl(sender_item.data(3))))
        self.media_player.play()

    def update_play_stop_button(self, is_playing):
        """ Switches "Stop" and "Play" signs for play_stop_button."""
        if is_playing:
            self.play_stop_button.setIcon(QIcon('fixtures/img/stop.png'))
        else:
            self.play_stop_button.setIcon(QIcon('fixtures/img/play.png'))

    def play_stop(self):
        """ Switches "Stop" and "Play" signs for play_stop_button."""
        if self.media_player.state():
            self.media_player.stop()
        else:
            self.switch_the_station(self.stations_list.selectedItems()[0])

    def keyPressEvent(self, key_event):
        """ Checks all keyboard inputs, executes "MainWindow.switch_the_station()" if return key is pressed.
        :param key_event: Keyboard key press event.
        :type key_event: QKeyEvent
        """
        if key_event.key() == Qt.Key_Return:
            self.switch_the_station(self.stations_list.selectedItems()[0])
        else:
            super().keyPressEvent(key_event)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())
