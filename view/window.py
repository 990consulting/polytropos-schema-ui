import logging

from PyQt5 import QtCore, QtWidgets

from view.left import LeftPane
from view.metadata import MetadataTableView
from view.source import SourceTableView

class MainWindow(QtWidgets.QWidget):

    data_type_changed = QtCore.pyqtSignal("QString")
    source_table_clicked = QtCore.pyqtSignal('QModelIndex')
    metadata_table_clicked = QtCore.pyqtSignal('QModelIndex')
    change_var_id = QtCore.pyqtSignal()

    def __init__(self):
        logging.info("Initializing MainWindow widget.")
        # noinspection PyArgumentList
        super().__init__()
        # UI Initialization
        logging.info("Constructing UI components.")
        self._create_source_table()
        self._create_metadata_table()
        # noinspection PyArgumentList
        self.left_pane = LeftPane()
        self.right_side_widget = QtWidgets.QGroupBox("Does this text ever appear?")
        self.var_id_textbox = QtWidgets.QLineEdit()
        self.path_value_textbox = QtWidgets.QLabel()
        self.type_combobox = QtWidgets.QComboBox()
        self._create_right_side_layout()
        splitter = QtWidgets.QSplitter()
        splitter.addWidget(self.left_pane)
        splitter.addWidget(self.right_side_widget)
        layout = QtWidgets.QHBoxLayout(self)
        # noinspection PyArgumentList
        layout.addWidget(splitter)
        # actions
        self.connect_signals()

    # noinspection PyUnresolvedReferences
    def connect_signals(self):
        self.type_combobox.currentTextChanged.connect(self.data_type_changed)
        self.source_table.clicked.connect(self.source_table_clicked)
        self.metadata_table.clicked.connect(self.metadata_table_clicked)
        self.var_id_textbox.editingFinished.connect(self.change_var_id)

    def _create_source_table(self):
        self.source_table = SourceTableView()

    def _create_metadata_table(self):
        self.metadata_table = MetadataTableView()

    # noinspection PyArgumentList
    def _create_right_side_layout(self):
        layout = QtWidgets.QGridLayout(self.right_side_widget)
        layout.addWidget(QtWidgets.QLabel("Variable ID:"), 0, 0)
        layout.addWidget(QtWidgets.QLabel("Absolute path:"), 1, 0)
        layout.addWidget(QtWidgets.QLabel("Data type:"), 2, 0)
        layout.addWidget(QtWidgets.QLabel("Sources"), 4, 0, QtCore.Qt.AlignTop)
        layout.addWidget(QtWidgets.QLabel("Metadata"), 6, 0, QtCore.Qt.AlignTop)
        layout.addWidget(self.var_id_textbox, 0, 1)
        layout.addWidget(self.path_value_textbox, 1, 1)
        layout.addWidget(self.type_combobox, 2, 1)
        layout.addItem(QtWidgets.QSpacerItem(100, 50), 3, 0, 1, 2)
        layout.addWidget(self.source_table, 4, 1)
        layout.addItem(QtWidgets.QSpacerItem(100, 50), 5, 0, 1, 2)
        layout.addWidget(self.metadata_table, 6, 1)
