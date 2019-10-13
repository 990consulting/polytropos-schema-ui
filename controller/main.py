import sys

from PyQt5 import QtCore, QtWidgets

from controller.left import LeftPaneController
from model.source_table_model import SourceTableModel
from model.metadata_table_model import MetadataTableModel
from view.window import MainWindow
import logging

class MainController:

    def __init__(self):
        logging.info("Initializing MainController.")
        # Initialize Qt state -- this must happen before constructing other Qt "widgets"
        self.app = QtWidgets.QApplication(sys.argv)
        self.main_view = MainWindow()
        self.left_pane = self.main_view.left_pane
        self.selectedItem = None
        self.is_selection_changed = False
        self.left_pane_controller = LeftPaneController(self)
        self.set_models()
        self.connect_callbacks()

    def set_models(self):
        self.initialize_metadata_table()
        self.initialize_source_table()

    def connect_callbacks(self):
        logging.info("Connecting main controller events to main view changes.")
        self.main_view.data_type_changed.connect(self.data_type_changed)
        self.main_view.source_table_clicked.connect(self.source_table_clicked)
        self.main_view.metadata_table_clicked.connect(self.metadata_table_clicked)
        self.main_view.change_var_id.connect(self.change_var_id)

    def disable_right_panel(self):
        logging.info("Disabling the right panel.")
        self.main_view.right_side_widget.setEnabled(False)
        self.main_view.right_side_widget.setTitle("")
        self.main_view.var_id_textbox.setText("")
        self.main_view.path_value_textbox.setText("")
        self.main_view.source_table.setModel(SourceTableModel())
        self.main_view.metadata_table.setModel(MetadataTableModel())

    def metadata_changed(self):
        logging.info("Detected metadata change; updating data model and UI.")
        self.selectedItem.setMetaData(self.main_view.metadata_table.model().getMetaData())
        self.selectedItem.setValueChanged(True)
        self.set_decoration_role()

    def change_var_id(self):
        if self.selectedItem is not None and self.main_view.var_id_textbox.text() != self.selectedItem.getVarId():
            # noinspection PyArgumentList
            dialog_result = QtWidgets.QMessageBox.question(QtWidgets.QMessageBox(), "Confirm",
                                                           "Are you sure you want to change VarId?")
            if dialog_result == QtWidgets.QMessageBox.Yes:
                self.selectedItem.setVarId(self.main_view.var_id_textbox.text())
                self.selectedItem.setValueChanged(True)
                self.set_decoration_role()

    def source_changed(self):
        self.selectedItem.setSources(self.main_view.source_table.model().getSources())
        self.selectedItem.setValueChanged(True)
        self.set_decoration_role()

    def set_decoration_role(self):
        index = self.left_pane.tree_view.selectedIndexes()[0]
        self.left_pane.tree_view.dataChanged(index, index, [QtCore.Qt.DecorationRole])
        self.left_pane.tree_view.dataChanged(index, index, [QtCore.Qt.ForegroundRole])
        self.set_style_to_tree('blue')

    def set_style_to_tree(self, style):
        self.left_pane.tree_view.setStyleSheet(
            '''
                QTreeView::item::selected {
                  selection-color: ''' + style + ''';
                }
            '''
        )

    def data_type_changed(self, selected):
        if self.is_selection_changed:
            return
        model = SourceTableModel(self.selectedItem.getSources())
        self.main_view.source_table.setModel(model)
        model.dataChanged.connect(self.source_changed)
        self.main_view.source_table.setDisabled(selected == "Folder")
        if self.selectedItem.getDataType() == selected:
            return
        self.selectedItem.setDataType(selected)
        current_index = self.left_pane.tree_view.selectedIndexes()[0]
        self.left_pane.tree_view.dataChanged(current_index, current_index, [QtCore.Qt.DecorationRole])
        self.selectedItem.setValueChanged(True)
        self.set_decoration_role()

    def select_dynamic_style(self, selected):
        if selected is None:
            return
        if selected.valueChanged:
            style = 'blue'
        elif selected.newAdded:
            style = 'green'
        else:
            style = 'black'
        self.set_style_to_tree(style)

    def update_metadata_model(self):
        model = MetadataTableModel(self.selectedItem.getMetaData())
        self.main_view.metadata_table.setModel(model)
        model.dataChanged.connect(self.metadata_changed)

    def source_table_clicked(self, index):
        row = index.row()
        column = index.column()
        model = self.main_view.source_table.model()
        if model.index(row, 0).data() == "":
            self.main_view.type_combobox.model().item(0).setEnabled(False)
            return
        else:
            self.main_view.type_combobox.model().item(0).setEnabled(True)
        if column == 1:
            model.insertRow(row)
        elif column == 2:
            model.removeRow(row)

    def metadata_table_clicked(self, index):
        row = index.row()
        column = index.column()
        model = self.main_view.metadata_table.model()
        if column == 2:
            model.insertRow(row)
        elif column == 3:
            model.removeRow(row)

    def initialize_metadata_table(self):
        self.main_view.metadata_table.setModel(MetadataTableModel())
        self.main_view.metadata_table.setup_horizontal_header()

    def initialize_source_table(self):
        self.main_view.source_table.setModel(SourceTableModel())
        self.main_view.source_table.setup_horizontal_header()

    def run(self):
        self.main_view.show()
        return self.app.exec_()
