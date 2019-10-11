"""
JSON I/O

"""

import sys
import json

from PyQt5 import  QtWidgets


class JsonFileManager(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.file_path = ""
        self.json_data = []

    def get_json_data(self):
        print(self.file_path)
        try:
            if self.file_path == "":
                options = QtWidgets.QFileDialog.Options()
                options |= QtWidgets.QFileDialog.DontUseNativeDialog
                self.file_path, _ = QtWidgets.QFileDialog.getOpenFileName(QtWidgets.QFileDialog(), "Open", "", "Json Files (*.json);;All Files (*)",
                                                                    options=options)
            if self.file_path:
                with open(self.file_path) as f:
                    try:
                        self.json_data = json.load(f)
                    except ValueError:
                        QtWidgets.QMessageBox.critical(QtWidgets.QMessageBox(), "Json Error", "Json TypeError")
                        sys.exit()
        except Exception as e:
            print(str(e))
            QtWidgets.QMessageBox.critical(QtWidgets.QMessageBox(), "Json Error", "Json TypeError")
            sys.exit()

    def save_json_file(self, result_file):
        with open(self.file_path, 'w') as file:
            json.dump(result_file, file)
