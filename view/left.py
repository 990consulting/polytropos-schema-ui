import logging
from PyQt5 import QtWidgets, QtCore

from view.tree_view import TreeView

class LeftPane(QtWidgets.QWidget):

    # signals
    revert_button_clicked = QtCore.pyqtSignal()
    save_clicked = QtCore.pyqtSignal()
    search_text_entered = QtCore.pyqtSignal("QString ")

    def __init__(self):
        # noinspection PyArgumentList
        super().__init__()
        logging.info("Initializing LeftPane widget.")
        self.save_button = QtWidgets.QPushButton("Save")
        self.revert_button = QtWidgets.QPushButton("Revert")
        self.validate_button = QtWidgets.QPushButton("Validate")
        self.search_field = QtWidgets.QLineEdit()
        self.tree_view = TreeView()
        self._create_layout()
        self.connect_signals()

    # noinspection PyUnresolvedReferences
    def connect_signals(self):
        self.save_button.clicked.connect(self.save_clicked)
        self.revert_button.clicked.connect(self.revert_button_clicked)
        self.search_field.textChanged.connect(self.search_text_entered)
        self.search_text_entered.connect(self.tree_view.start_search)

    # noinspection PyArgumentList
    def _create_left_pane_buttons(self):
        layout = QtWidgets.QHBoxLayout()
        layout.addWidget(self.save_button)
        layout.addStretch()
        layout.addWidget(self.revert_button)
        layout.addStretch()
        layout.addWidget(self.validate_button)
        return layout

    def _create_search_bar(self):
        layout = QtWidgets.QHBoxLayout()
        self.search_field.setPlaceholderText("Search...")
        # noinspection PyArgumentList
        layout.addWidget(self.search_field)
        return layout

    def _create_layout(self):
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(9, 0, 9, 0)
        layout.addLayout(self._create_left_pane_buttons())
        layout.addLayout(self._create_search_bar())
        # noinspection PyArgumentList
        layout.addWidget(self.tree_view)
