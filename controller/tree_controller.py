from typing import TYPE_CHECKING, List

from PyQt5 import QtWidgets

from model.json_file_manager import JsonFileManager

if TYPE_CHECKING:
    from controller.main_controller import MainController

class TreePaneController:

    def __init__(self, main_controller: "MainController"):
        self.main_controller: "MainController" = main_controller
        self.json_manager = JsonFileManager()
        self.create_tree()
        self.connect_callbacks()

    def connect_callbacks(self):
        self.main_controller.main_view.revert_button_clicked.connect(self.revert_clicked)
        self.main_controller.main_view.save_clicked.connect(self.save_clicked)

    def create_tree(self):
        json_data: List = self.json_manager.get_json_data()
        self.main_controller.main_view.tree_view.load_data(json_data)
        self.main_controller.disable_right_panel()

    def save_clicked(self):
        dialog_result = QtWidgets.QMessageBox.question(QtWidgets.QMessageBox(), "Save", "Would you save the changes?")
        if dialog_result == QtWidgets.QMessageBox.Yes:
            root_item = self.main_controller.main_view.tree_view.getRootItem()
            result_file = []
            for child in root_item.childItems:
                result_file.append(child.create_new_item())
            self.json_manager.save_json_file(result_file)
            self.json_manager.json_data = result_file

    def revert_clicked(self):
        dialog_result = QtWidgets.QMessageBox.question(QtWidgets.QMessageBox(), "Confirm", "Would you revert?")
        if dialog_result == QtWidgets.QMessageBox.Yes:
            self.main_controller.main_view.tree_view.clearContent()
            self.json_manager.get_json_data()
            self.create_tree()
            self.main_controller.selectedItem = None
