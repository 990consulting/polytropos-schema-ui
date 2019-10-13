import logging

from PyQt5 import QtCore, QtWidgets

from view.metadata_table_view import MetadataTableView
from view.source_table_view import SourceTableView
from view.tree_view import TreeView


class MainWindow(QtWidgets.QWidget):

    # signals
    revert_button_clicked = QtCore.pyqtSignal()
    data_type_changed = QtCore.pyqtSignal("QString")
    source_table_clicked = QtCore.pyqtSignal('QModelIndex')
    metadata_table_clicked = QtCore.pyqtSignal('QModelIndex')
    save_clicked = QtCore.pyqtSignal()
    search_text_entered = QtCore.pyqtSignal("QString ")
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
        self.left_side_widget = QtWidgets.QWidget()
        self.right_side_widget = QtWidgets.QGroupBox("Does this text ever appear?")
        self.var_id_textbox = QtWidgets.QLineEdit()
        self.path_value_textbox = QtWidgets.QLabel()
        self.type_combobox = QtWidgets.QComboBox()
        self.tree_view = TreeView()
        self._create_right_side_layout()
        self._create_left_side_layout()
        splitter = QtWidgets.QSplitter()
        splitter.addWidget(self.left_side_widget)
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
        self.save_button.clicked.connect(self.save_clicked)
        self.var_id_textbox.editingFinished.connect(self.change_var_id)
        self.revert_button.clicked.connect(self.revert_button_clicked)
        self.search_field.textChanged.connect(self.search_text_entered)
        self.search_text_entered.connect(self.tree_view.start_search)

    def _create_source_table(self):
        self.source_table = SourceTableView()

    def _create_metadata_table(self):
        self.metadata_table = MetadataTableView()

    # noinspection PyArgumentList
    def _create_left_pane_buttons(self):
        layout = QtWidgets.QHBoxLayout()
        self.save_button = QtWidgets.QPushButton("Save")
        self.revert_button = QtWidgets.QPushButton("Revert")
        self.validate_button = QtWidgets.QPushButton("Validate")
        layout.addWidget(self.save_button)
        layout.addStretch()
        layout.addWidget(self.revert_button)
        layout.addStretch()
        layout.addWidget(self.validate_button)
        return layout

    def _create_search_bar(self):
        layout = QtWidgets.QHBoxLayout()
        self.search_field = QtWidgets.QLineEdit()
        self.search_field.setPlaceholderText("Search...")
        # noinspection PyArgumentList
        layout.addWidget(self.search_field)
        return layout

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

    def _create_left_side_layout(self):
        layout = QtWidgets.QVBoxLayout(self.left_side_widget)
        layout.setContentsMargins(9, 0, 9, 0)
        layout.addLayout(self._create_left_pane_buttons())
        layout.addLayout(self._create_search_bar())
        # noinspection PyArgumentList
        layout.addWidget(self.tree_view)
