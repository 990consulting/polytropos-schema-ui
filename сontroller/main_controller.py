import sys
from PyQt5 import QtCore, QtWidgets
from model.type_manager import TypeManager
from model.json_file_manager import JsonFileManager
from model.source_table_model import SourceTableModel
from model.metadata_table_model import MetadataTableModel
from view.main_view import MainWindow
import traceback


class MainController:

    def __init__(self):
        self._app = QtWidgets.QApplication(sys.argv)
        self._source_model = SourceTableModel()
        self.main_view = MainWindow()
        self.selectedItem = None
        self.is_selection_changed = False
        self.is_selection_changed = False
        self.init()

    def init(self):
        try:
            self.get_json_data()
            self.create_tree()
            self.set_metadata_table_model()
            self.set_source_table_model()
            self.main_view.revert_button_clicked.connect(self.revert_clicked)
            self.main_view.data_type_changed.connect(self.data_type_changed)
            self.main_view.source_table_clicked.connect(self.source_table_clicked)
            self.main_view.tree_view.tree_selection_changed.connect(self.tree_selection_changed)
            self.main_view.tree_view.tree_value_changed.connect(self.tree_value_changed)
            self.main_view.metadata_table_clicked.connect(self.metadata_table_clicked)
            self.main_view.save_clicked.connect(self.save_clicked)
            self.main_view.search_text_entered.connect(self.do_search)
            self.main_view.change_var_id.connect(self.change_var_id)
        except Exception as e:
            print("Controller initialization failed: {}".format(e))
            print(traceback.format_exc())

    def disable_right_panel(self):
        try:
            self.main_view.right_side_widget.setEnabled(False)
            self.main_view.right_side_widget.setTitle("")
            self.main_view.var_id_textbox.setText("")
            self.main_view.path_value_textbox.setText("")
            self.main_view.source_table.setModel(SourceTableModel())
            self.main_view.metadata_table.setModel(MetadataTableModel())
        except Exception as e:
            print("disable_right_panel failed: {}".format(e))
            print(traceback.format_exc())

    def metadata_changed(self):
        try:
            self.selectedItem.setMetaData(self.main_view.metadata_table.model().getMetaData())
            self.selectedItem.setValueChanged(True)
            self.set_decoration_role()
            return
        except Exception as e:
            print("metadata_changed failed: {}".format(e))
            print(traceback.format_exc())

    def do_search(self, text):
        try:
            self.main_view.tree_view._start_search(text)
        except Exception as e:
            print("do_search failed: {}".format(e))
            print(traceback.format_exc())

    def change_var_id(self):
        try:
            if self.selectedItem is not None and self.main_view.var_id_textbox.text() != self.selectedItem.getVarId():
                dialog_result = QtWidgets.QMessageBox.question(QtWidgets.QMessageBox(), "Confirm",
                                                               "Are you sure you want to change VarId?")
                if dialog_result == QtWidgets.QMessageBox.Yes:
                    self.selectedItem.setVarId(self.main_view.var_id_textbox.text())
                    self.selectedItem.setValueChanged(True)
                    self.set_decoration_role()
        except Exception as e:
            print("change_var_id failed: {}".format(e))
            print(traceback.format_exc())

    def source_changed(self):
        try:
            self.selectedItem.setSources(self.main_view.source_table.model().getSources())
            self.selectedItem.setValueChanged(True)
            self.set_decoration_role()
            return
        except Exception as e:
            print("source_changed failed: {}".format(e))
            print(traceback.format_exc())

    def set_decoration_role(self):
        index = self.main_view.tree_view.selectedIndexes()[0]
        self.main_view.tree_view.dataChanged(index,
                                             index,
                                             [QtCore.Qt.DecorationRole])
        self.main_view.tree_view.dataChanged(index,
                                             index,
                                             [QtCore.Qt.ForegroundRole])
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
        try:
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
        except Exception as e:
            print("data_type_changed failed: {}".format(e))
            print(traceback.format_exc())

    def tree_value_changed(self, value):
        try:
            self.main_view.right_side_widget.setTitle(value)
            self.main_view.path_value_textbox.setText(self.selectedItem.fullPath())

        except Exception as e:
            print("tree_value_changed failed: {}".format(e))
            print(traceback.format_exc())

    def tree_selection_changed(self, selected):
        try:
            self.select_dynamic_style(selected)
            #self.change_var_id()
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
        except Exception as e:
            print("tree_selection_changed failed: {}".format(e))
            print(traceback.format_exc())



    def select_dynamic_style(self, selected):
        if selected.valueChanged:
            style = 'blue'
        elif selected.newAdded:
            style = 'green'
        else:
            style = 'black'
        self.set_style_to_tree(style)


    def update_metadata_model(self):
        try:
            model = MetadataTableModel(self.selectedItem.getMetaData())
            self.main_view.metadata_table.setModel(model)
            model.dataChanged.connect(self.metadata_changed)
        except Exception as e:
            print("update_metadata_model failed: {}".format(e))
            print(traceback.format_exc())

    def source_table_clicked(self, index):
        try:
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


        except Exception as e:
            print("source_table_clicked failed: {}".format(e))
            print(traceback.format_exc())

    def metadata_table_clicked(self, index):
        try:
            row = index.row()
            column = index.column()
            model = self.main_view.metadata_table.model()
            if column == 2:
                model.insertRow(row)
            elif column == 3:
                model.removeRow(row)
        except Exception as e:
            print("metadata_table_clicked failed: {}".format(e))
            print(traceback.format_exc())

    def save_clicked(self):
        try:
            dialog_result = QtWidgets.QMessageBox.question(QtWidgets.QMessageBox(), "Save", "Would you save the changes?")
            if dialog_result == QtWidgets.QMessageBox.Yes:
                root_item = self.main_view.tree_view.getRootItem()
                result_file = []
                for child in root_item.childItems:
                    result_file.append(child.create_new_item())
                self.JsonManager.save_json_file(result_file)
                self.JsonManager.json_data = result_file
        except Exception as e:
            print("save_clicked failed: {}".format(e))
            print(traceback.format_exc())

    def get_json_data(self):
        try:
            self.JsonManager = JsonFileManager()
            self.JsonManager.get_json_data()
        except Exception as e:
            print("get_json_data failed: {}".format(e))
            print(traceback.format_exc())

    def create_tree(self):
        try:
            self.main_view.tree_view.load_data(self.JsonManager.json_data)
            self.disable_right_panel()
        except Exception as e:
            print("create_tree failed: {}".format(e))
            print(traceback.format_exc())

    def revert_clicked(self):
        try:
            dialog_result = QtWidgets.QMessageBox.question(QtWidgets.QMessageBox(), "Confirm", "Would you revert?")
            if dialog_result == QtWidgets.QMessageBox.Yes:
                self.main_view.tree_view.clearContent()
                self.JsonManager.get_json_data()
                self.create_tree()
                self.selectedItem = None
        except Exception as e:
            print("revert_clicked failed: {}".format(e))
            print(traceback.format_exc())

    def set_metadata_table_model(self):
        try:
            self.main_view.metadata_table.setModel(MetadataTableModel())
            horizontal_header = self.main_view.metadata_table.horizontalHeader()
            horizontal_header.setSectionResizeMode(0, QtWidgets.QHeaderView.Stretch)
            horizontal_header.setSectionResizeMode(1, QtWidgets.QHeaderView.Stretch)
            horizontal_header.setSectionResizeMode(2, QtWidgets.QHeaderView.ResizeToContents)
            horizontal_header.setSectionResizeMode(3, QtWidgets.QHeaderView.ResizeToContents)
        except Exception as e:
            print("set_metadata_table_model failed: {}".format(e))
            print(traceback.format_exc())

    def set_source_table_model(self):
        try:
            self.main_view.source_table.setModel(SourceTableModel())
            horizontal_header = self.main_view.source_table.horizontalHeader()
            horizontal_header.setSectionResizeMode(0, QtWidgets.QHeaderView.Stretch)
            horizontal_header.setSectionResizeMode(1, QtWidgets.QHeaderView.ResizeToContents)
            horizontal_header.setSectionResizeMode(2, QtWidgets.QHeaderView.ResizeToContents)
        except Exception as e:
            print("set_source_table_model failed: {}".format(e))
            print(traceback.format_exc())

    def run(self):
        self.main_view.show()
        return self._app.exec_()
