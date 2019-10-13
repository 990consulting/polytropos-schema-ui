import logging
from PyQt5 import QtWidgets

class LeftPane(QtWidgets.QWidget):
    def __init__(self):
        # noinspection PyArgumentList
        super().__init__()
        logging.info("Initializing LeftPane widget.")