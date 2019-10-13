"""
JSON I/O
"""

import json
from typing import List

from PyQt5 import QtWidgets


class JsonFileManager(QtWidgets.QWidget):
    def __init__(self):
        # noinspection PyArgumentList
        super().__init__()
        self.file_path = ""

    def get_json_data(self) -> List:
        if self.file_path == "":
            options = QtWidgets.QFileDialog.Options()
            options |= QtWidgets.QFileDialog.DontUseNativeDialog
            self.file_path, _ = QtWidgets.QFileDialog.getOpenFileName(QtWidgets.QFileDialog(), "Open", "",
                                                                      "Json Files (*.json);;All Files (*)",
                                                                      options=options)
        if self.file_path:
            with open(self.file_path) as f:
                return json.load(f)

    def save_json_file(self, result_file):
        with open(self.file_path, 'w') as file:
            json.dump(result_file, file, indent=2)
