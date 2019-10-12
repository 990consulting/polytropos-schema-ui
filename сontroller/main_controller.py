import sys
from typing import List

from PyQt5 import QtCore, QtWidgets
from model.type_manager import TypeManager
from model.json_file_manager import JsonFileManager
from model.source_table_model import SourceTableModel
from model.metadata_table_model import MetadataTableModel
from view.main_view import MainWindow
import logging

class MainController:

    def __init__(self):
        logging.info("Initializing MainController.")
        # Initialize Qt state -- this must happen before constructing other Qt "widgets"
        self.app = QtWidgets.QApplication(sys.argv)
        self.main_view = MainWindow()
        self.selectedItem = None
        self.is_selection_changed = False
        self.json_manager = JsonFileManager()

        self.create_tree()

        self.set_models()
        self.connect_callbacks()

    def set_models(self):
        self.set_metadata_table_model()
        self.set_source_table_model()

    def connect_callbacks(self):
        logging.info("Connecting events to view changes.")
        self.main_view.revert_button_clicked.connect(self.revert_clicked)
        self.main_view.data_type_changed.connect(self.data_type_changed)
        self.main_view.source_table_clicked.connect(self.source_table_clicked)
        self.main_view.tree_view.tree_selection_changed.connect(self.tree_selection_changed)
        self.main_view.tree_view.tree_value_changed.connect(self.tree_value_changed)
        self.main_view.metadata_table_clicked.connect(self.metadata_table_clicked)
        self.main_view.save_clicked.connect(self.save_clicked)
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
        index = self.main_view.tree_view.selectedIndexes()[0]
        self.main_view.tree_view.dataChanged(index, index, [QtCore.Qt.DecorationRole])
        self.main_view.tree_view.dataChanged(index, index, [QtCore.Qt.ForegroundRole])
        self.set_style_to_tree('blue')

    def set_style_to_tree(self, style):
        self.main_view.tree_view.setStyleSheet(
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
        current_index = self.main_view.tree_view.selectedIndexes()[0]
        self.main_view.tree_view.dataChanged(current_index, current_index, [QtCore.Qt.DecorationRole])
        self.selectedItem.setValueChanged(True)
        self.set_decoration_role()

    def tree_value_changed(self, value):
        self.main_view.right_side_widget.setTitle(value)
        self.main_view.path_value_textbox.setText(self.selectedItem.fullPath())

    def tree_selection_changed(self, selected):
        self.select_dynamic_style(selected)
        self.selectedItem = selected
        if selected is None:
            self.disable_right_panel()
            return
        self.main_view.right_side_widget.setEnabled(True)
        self.main_view.var_id_textbox.setText(self.selectedItem.getVarId())
        self.main_view.right_side_widget.setTitle(self.selectedItem.data())
        self.main_view.path_value_textbox.setText(self.selectedItem.fullPath())
        self.is_selection_changed = True
        self.main_view.type_combobox.clear()
        if len(selected.getSources()) > 0 and "Folder" in TypeManager.get_types_list(self.selectedItem.getDataType()):
            self.main_view.type_combobox.addItems(TypeManager.get_types_list(self.selectedItem.getDataType()))
            self.main_view.type_combobox.model().item(0).setEnabled(False)
        else:
            self.main_view.type_combobox.addItems(TypeManager.get_types_list(self.selectedItem.getDataType()))
        self.main_view.type_combobox.setCurrentText(self.selectedItem.getDataType())
        self.is_selection_changed = False
        self.data_type_changed(self.selectedItem.getDataType())
        self.update_metadata_model()

    def select_dynamic_style(self, selected):
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

    def save_clicked(self):
        dialog_result = QtWidgets.QMessageBox.question(QtWidgets.QMessageBox(), "Save", "Would you save the changes?")
        if dialog_result == QtWidgets.QMessageBox.Yes:
            root_item = self.main_view.tree_view.getRootItem()
            result_file = []
            for child in root_item.childItems:
                result_file.append(child.create_new_item())
            self.json_manager.save_json_file(result_file)
            self.json_manager.json_data = result_file

    def create_tree(self):
        json_data: List = self.json_manager.get_json_data()
        self.main_view.tree_view.load_data(json_data)
        self.disable_right_panel()

    def revert_clicked(self):
        dialog_result = QtWidgets.QMessageBox.question(QtWidgets.QMessageBox(), "Confirm", "Would you revert?")
        if dialog_result == QtWidgets.QMessageBox.Yes:
            self.main_view.tree_view.clearContent()
            self.json_manager.get_json_data()
            self.create_tree()
            self.selectedItem = None

    def set_metadata_table_model(self):
        logging.info("Connecting metadata view to underlying data model.")
        self.main_view.metadata_table.setModel(MetadataTableModel())
        # TODO The following is not data-related and should be handled inside the view
        horizontal_header = self.main_view.metadata_table.horizontalHeader()
        horizontal_header.setSectionResizeMode(0, QtWidgets.QHeaderView.Stretch)
        horizontal_header.setSectionResizeMode(1, QtWidgets.QHeaderView.Stretch)
        horizontal_header.setSectionResizeMode(2, QtWidgets.QHeaderView.ResizeToContents)
        horizontal_header.setSectionResizeMode(3, QtWidgets.QHeaderView.ResizeToContents)

    def set_source_table_model(self):
        logging.info("Connecting source view to underlying data model.")
        self.main_view.source_table.setModel(SourceTableModel())
        # TODO The following is not data-related and should be handled inside the view
        horizontal_header = self.main_view.source_table.horizontalHeader()
        horizontal_header.setSectionResizeMode(0, QtWidgets.QHeaderView.Stretch)
        horizontal_header.setSectionResizeMode(1, QtWidgets.QHeaderView.ResizeToContents)
        horizontal_header.setSectionResizeMode(2, QtWidgets.QHeaderView.ResizeToContents)

    def run(self):
        self.main_view.show()
        return self.app.exec_()
