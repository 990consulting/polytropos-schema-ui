from typing import TYPE_CHECKING, List

from PyQt5 import QtWidgets

from model.json_file_manager import JsonFileManager
from model.type_manager import TypeManager

if TYPE_CHECKING:
    from controller.main import MainController

class LeftPaneController:

    def __init__(self, main_controller: "MainController"):
        self.main_controller: "MainController" = main_controller
        self.left_pane = self.main_controller.left_pane
        self.json_manager = JsonFileManager()
        self.create_tree()
        self.connect_callbacks()

    def connect_callbacks(self):
        self.left_pane.revert_button_clicked.connect(self.revert_clicked)
        self.left_pane.save_clicked.connect(self.save_clicked)

    def create_tree(self):
        json_data: List = self.json_manager.get_json_data()
        self.left_pane.tree_view.load_data(json_data)
        self.main_controller.disable_right_panel()

    def save_clicked(self):
        # noinspection PyArgumentList
        dialog_result = QtWidgets.QMessageBox.question(QtWidgets.QMessageBox(), "Save", "Would you save the changes?")
        if dialog_result == QtWidgets.QMessageBox.Yes:
            root_item = self.left_pane.tree_view.getRootItem()
            result_file = []
            for child in root_item.childItems:
                result_file.append(child.create_new_item())
            self.json_manager.save_json_file(result_file)
            self.json_manager.json_data = result_file

    def revert_clicked(self):
        # noinspection PyArgumentList
        dialog_result = QtWidgets.QMessageBox.question(QtWidgets.QMessageBox(), "Confirm", "Would you revert?")
        if dialog_result == QtWidgets.QMessageBox.Yes:
            self.left_pane.tree_view.clearContent()
            self.json_manager.get_json_data()
            self.create_tree()
            self.main_controller.selectedItem = None

    def tree_value_changed(self, value):
        self.main_controller.main_view.right_side_widget.setTitle(value)
        self.main_controller.main_view.path_value_textbox.setText(self.main_controller.selectedItem.fullPath())

    def tree_selection_changed(self, selected):
        self.main_controller.select_dynamic_style(selected)
        self.main_controller.selectedItem = selected
        if selected is None:
            self.main_controller.disable_right_panel()
            return
        self.main_controller.main_view.right_side_widget.setEnabled(True)
        self.main_controller.main_view.var_id_textbox.setText(self.main_controller.selectedItem.getVarId())
        self.main_controller.main_view.right_side_widget.setTitle(self.main_controller.selectedItem.data())
        self.main_controller.main_view.path_value_textbox.setText(self.main_controller.selectedItem.fullPath())
        self.main_controller.is_selection_changed = True
        self.main_controller.main_view.type_combobox.clear()
        if len(selected.getSources()) > 0 and "Folder" in TypeManager.get_types_list(self.main_controller.selectedItem
                                                                                     .getDataType()):
            self.main_controller.main_view.type_combobox.addItems(TypeManager.get_types_list(self.main_controller
                                                                                             .selectedItem
                                                                                             .getDataType()))
            self.main_controller.main_view.type_combobox.model().item(0).setEnabled(False)
        else:
            self.main_controller.main_view.type_combobox.addItems(TypeManager.get_types_list(self.main_controller
                                                                                             .selectedItem
                                                                                             .getDataType()))
        self.main_controller.main_view.type_combobox.setCurrentText(self.main_controller.selectedItem.getDataType())
        self.main_controller.is_selection_changed = False
        self.main_controller.data_type_changed(self.main_controller.selectedItem.getDataType())
        self.main_controller.update_metadata_model()
