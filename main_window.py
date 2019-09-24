import sys

from PyQt5 import QtCore, QtGui, QtWidgets
import qtawesome as qta

from tree_model import TreeModel


class MainWindow(QtWidgets.QWidget):

    def __init__(self):
        super().__init__()
        self._tree_view = None
        layout = QtWidgets.QHBoxLayout(self)
        layout.addWidget(self._add_splitter())
        self._add_child_action = self._create_menu_action('Add child...', self._add_child_slot)
        self._delete_action = self._create_menu_action('Delete', self._delete_slot)
        self._clone_action = self._create_menu_action('Clone', self._clone_slot)
        self._context_menu = self._create_context_menu()

    def _add_splitter(self):
        splitter = QtWidgets.QSplitter()
        splitter.addWidget(self._create_left_pane())
        splitter.addWidget(self._create_right_pane())
        return splitter

    def _create_left_pane(self):
        left_side_widget = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(left_side_widget)
        layout.setContentsMargins(9, 0, 9, 0)
        layout.addLayout(self._create_left_pane_buttons())
        layout.addLayout(self._create_search_bar())
        layout.addWidget(self._create_tree_view())
        return left_side_widget

    def _create_right_pane(self):
        right_side_widget = QtWidgets.QGroupBox("Loreum ipsum dolor sit")
        layout = QtWidgets.QGridLayout()
        right_side_widget.setLayout(layout)

        variable_id = QtWidgets.QLabel("Variable ID:")
        layout.addWidget(variable_id, 0, 0)
        variable_value = QtWidgets.QLineEdit()
        variable_value.setReadOnly(True)
        layout.addWidget(variable_value, 0, 1)

        path = QtWidgets.QLabel("Absolute path:")
        layout.addWidget(path, 1, 0)
        path_value = QtWidgets.QLineEdit()
        path_value.setReadOnly(True)
        layout.addWidget(path_value, 1, 1)

        data_type = QtWidgets.QLabel("Data type:")
        layout.addWidget(data_type, 2, 0)
        data_type_value = QtWidgets.QComboBox()
        data_type_value.addItems(["Text", "Integer", "Date"])
        layout.addWidget(data_type_value, 2, 1)

        layout.addItem(QtWidgets.QSpacerItem(100, 50), 3, 0, 1, 2)

        sources = QtWidgets.QLabel("Sources")
        layout.addWidget(sources, 4, 0, QtCore.Qt.AlignTop)
        layout.addWidget(self._create_source_table(), 4, 1)

        layout.addItem(QtWidgets.QSpacerItem(100, 50), 5, 0, 1, 2)

        metadata = QtWidgets.QLabel("Metadata")
        layout.addWidget(metadata, 6, 0, QtCore.Qt.AlignTop)
        layout.addWidget(self._create_metadata_table(), 6, 1)

        return right_side_widget

    def _create_source_table(self):
        table = QtWidgets.QTableView()
        table.horizontalHeader().hide()
        table.verticalHeader().hide()

        table.setFixedHeight(62)

        model = SourceTableModel()
        table.setModel(model)

        horizontal_header = table.horizontalHeader()
        horizontal_header.setSectionResizeMode(0, QtWidgets.QHeaderView.Stretch)
        horizontal_header.setSectionResizeMode(1, QtWidgets.QHeaderView.ResizeToContents)
        horizontal_header.setSectionResizeMode(2, QtWidgets.QHeaderView.ResizeToContents)

        return table

    def _create_metadata_table(self):
        table = QtWidgets.QTableView()
        table.verticalHeader().hide()

        model = MetadataTableModel()
        table.setModel(model)

        horizontal_header = table.horizontalHeader()
        horizontal_header.setSectionResizeMode(0, QtWidgets.QHeaderView.Stretch)
        horizontal_header.setSectionResizeMode(1, QtWidgets.QHeaderView.Stretch)
        horizontal_header.setSectionResizeMode(2, QtWidgets.QHeaderView.ResizeToContents)
        horizontal_header.setSectionResizeMode(3, QtWidgets.QHeaderView.ResizeToContents)

        return table

    def _create_left_pane_buttons(self):
        layout = QtWidgets.QHBoxLayout()
        save_button = QtWidgets.QPushButton("Save")

        revert_button = QtWidgets.QPushButton("Revert")
        validate_button = QtWidgets.QPushButton("Validate")

        layout.addWidget(save_button)
        layout.addStretch()

        layout.addWidget(revert_button)
        layout.addStretch()

        layout.addWidget(validate_button)

        return layout

    def _create_search_bar(self):
        layout = QtWidgets.QHBoxLayout()
        search_field = QtWidgets.QLineEdit()
        search_field.setPlaceholderText("Search...")
        search_button = QtWidgets.QPushButton("Search")

        layout.addWidget(search_field)
        layout.addWidget(search_button)

        return layout

    def _create_tree_view(self):
        self._tree_view = QtWidgets.QTreeView()
        self._tree_view.header().hide()
        self._tree_view.setDragDropMode(QtWidgets.QAbstractItemView.InternalMove)
        self._tree_view.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self._tree_view.customContextMenuRequested.connect(self._open_menu)

        tree_model = TreeModel()
        self._tree_view.setModel(tree_model)
        self._tree_view.setDragEnabled(True)
        return self._tree_view

    def _create_menu_action(self, name, slot):
        action = QtWidgets.QAction(name)
        action.triggered.connect(slot)
        return action

    def _create_context_menu(self):
        menu = QtWidgets.QMenu()
        for action in [self._add_child_action, self._delete_action, self._clone_action]:
            menu.addAction(action)
        return menu

    def _open_menu(self, position):
        indexes = self._tree_view.selectedIndexes()
        if len(indexes) == 0:
            return

        self._context_menu.exec_(self._tree_view.viewport().mapToGlobal(position))

    def _add_child_slot(self):
        print('Add child menu command executed')

    def _delete_slot(self):
        print('Delete menu command executed')

    def _clone_slot(self):
        print('Clone menu command executed')


class SourceTableModel(QtCore.QAbstractTableModel):

    def __init__(self, parent=None):
        super().__init__(parent)

    def flags(self, index):
        if index.column() == 0:
            return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsEditable
        return super().flags(index)

    def rowCount(self, parent=QtCore.QModelIndex()):
        return 2

    def columnCount(self, parent=QtCore.QModelIndex()):
        return 3

    def data(self, index, role=QtCore.Qt.DisplayRole):

        if not index.isValid():
            return None

        column = index.column()
        if role == QtCore.Qt.DecorationRole and column == 1:
            icon = qta.icon('fa5s.plus-circle')
            return icon

        if role == QtCore.Qt.DecorationRole and column == 2:
            icon = qta.icon('fa5s.minus-circle')
            return icon


class MetadataTableModel(QtCore.QAbstractTableModel):
    def __init__(self, parenrt=None):
        super().__init__(parenrt)

    def __init__(self, parent=None):
        super().__init__(parent)

    def rowCount(self, parent=QtCore.QModelIndex()):
        return 6

    def columnCount(self, parent=QtCore.QModelIndex()):
        return 4

    def flags(self, index):
        if index.column() in [0, 1]:
            return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsEditable
        return super().flags(index)

    def data(self, index, role=QtCore.Qt.DisplayRole):

        if not index.isValid():
            return None

        column = index.column()
        if role == QtCore.Qt.DecorationRole and column == 2:
            icon = qta.icon('fa5s.plus-circle')
            return icon

        if role == QtCore.Qt.DecorationRole and column == 3:
            icon = qta.icon('fa5s.minus-circle')
            return icon

    def headerData(self, section, orientation, role=QtCore.Qt.DisplayRole):
        if role == QtCore.Qt.DisplayRole and orientation == QtCore.Qt.Horizontal:
            if section == 0:
                return "Key"
            elif section == 1:
                return "Value"
            else:
                return ""



if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
