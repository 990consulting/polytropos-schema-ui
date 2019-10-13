from typing import List

from PyQt5 import QtWidgets, QtCore
from model.tree import TreeModel
from model.node import TreeItem
from model.datatypes import DataTypes
import random
import string
import traceback


class TreeView(QtWidgets.QTreeView, QtCore.QObject):
    tree_selection_changed = QtCore.pyqtSignal(object)
    tree_value_changed = QtCore.pyqtSignal(object)

    def __init__(self):
        try:
            QtWidgets.QTreeView.__init__(self)
            self.set_actions()
            self.initUI()
            self.set_model()
            self.setDragEnabled(True)
            self.index_selected = None
            self.text_to_search = ""
            self.setFocusPolicy(QtCore.Qt.NoFocus)
        except Exception as e:
            print("View initialization failed: {}".format(e))
            print(traceback.format_exc())

    def set_actions(self):
        try:
            self._delete_action = self._create_menu_action('Delete', self._delete_slot)
            self._dup_action = self._create_menu_action('Duplicate', self._clone_slot)
            self._rename_action = self._create_menu_action('Rename', self._rename_slot)
            self._add_child_folder_action = self._create_menu_action('New Folder', self.add_child_folder)
            self._add_child_primitive_action = self._create_menu_action('New Primitive', self.create_child_primitive)
            self._add_root_folder_action = self._create_menu_action('Add child container', self.add_root_folder)
            self._add_root_primitive_action = self._create_menu_action('Add child primitive', self.create_root_primitive)
        except Exception as e:
            print("set_actions failed: {}".format(e))
            print(traceback.format_exc())

    def set_model(self):
        self.tree_model = TreeModel()
        self.tree_model.dataChanged.connect(self._dataChanged)
        self.tree_model.rowMoved.connect(self._rowMoved)
        self.setModel(self.tree_model)

    """
        actions
    """

    def load_data(self, data: List):
        self.tree_model.load_data(data)

    def clearContent(self):
        root_index = self.tree_model.index(0, 0).parent()
        i = self.tree_model.rowCount(root_index)
        while i:
            self.tree_model.removeRow(i - 1, root_index)
            i -= 1

    def getRootItem(self):
        if self.tree_model.hasIndex(0, 0):
            return self.tree_model.get_item(self.tree_model.index(0, 0).parent())
        return None

    def _rowMoved(self, curIdx):
        self.setCurrentIndex(curIdx)
        self.index_selected = curIdx
        self._curItem = self.tree_model.get_item(self.index_selected)
        self.tree_selection_changed.emit(self._curItem)

    def _dataChanged(self, index):
        self._curItem.setValueChanged(True)
        self.tree_value_changed.emit(index.data())

    def mousePressEvent(self, event):
        QtWidgets.QTreeView.mousePressEvent(self, event)
        self.index_selected = self.indexAt(event.pos())
        self.setCurrentIndex(self.index_selected)
        self._curItem = None if self.index_selected.data() is None else self.tree_model.get_item(self.index_selected)
        self.tree_selection_changed.emit(self._curItem)


    def getCurItem(self):
        return self._curItem

    def _create_menu_action(self, name, slot):
        action = QtWidgets.QAction(name)
        action.triggered.connect(slot)
        return action


    def randomString(self, stringLength=20):
        letters = string.ascii_letters + string.digits
        return ''.join(random.choice(letters) for i in range(stringLength))

    def _set_menu_items_visible(self, visible):
        self._delete_action.setVisible(visible[0])
        self._dup_action.setVisible(visible[1])
        self._rename_action.setVisible(visible[2])
        self._add_child_folder_action.setVisible(visible[3])
        self._add_child_primitive_action.setVisible(visible[4])
        self._add_root_folder_action.setVisible(visible[5])
        self._add_root_primitive_action.setVisible(visible[6])

    def _open_menu(self, position):
        if self._curItem is None:
            self._set_menu_items_visible([False, False, False, False, False, True, True])
        else:
            if self._curItem.dataType in DataTypes.collections:
                self._set_menu_items_visible([True, True, True, True, True, False, False])
            else:
                self._set_menu_items_visible([True, True, True, False, False, False, False])
        self._context_menu.exec_(self.viewport().mapToGlobal(position))

    def _rename_slot(self):
        try:
            self.edit(self.currentIndex())
            self._curItem.setValueChanged(True)
        except Exception as e:
            print(str(e))

    def _delete_slot(self):
        parent = self.index_selected.parent()
        pos = self.index_selected.row()
        self.tree_model.removeRow(pos, parent)
        self._curItem = self.tree_model.get_item(self.currentIndex())
        self.tree_selection_changed.emit(self._curItem)

    def set_copy_of(self, item):
        item.setVarId("copy_of_" + item.getVarId())
        item.setNewAdded(True)
        for child in item.childItems:
            self.set_copy_of(child)

    def _clone_slot(self):
        parentItem = self._curItem.parent()
        dup_Item = self.create_slot(parentItem)
        for item in dup_Item.childItems:
            self.set_copy_of(item)
        pos = self.index_selected.row()
        parentItem.insertChild(pos + 1, dup_Item)
        self.tree_model.insertRow(pos, self.index_selected.parent())
        self._curItem = dup_Item
        self.tree_selection_changed.emit(self._curItem)

    def create_slot(self, parentItem):
        dup_Item = self._curItem.create_duplicate(parentItem)
        dup_Item.setData("Copy of " + self._curItem.data())
        dup_Item.setVarId("copy_of_" + self._curItem.getVarId())
        dup_Item.setNewAdded(True)
        return dup_Item

    def add_child_folder(self):
        parentItem = self.tree_model.get_item(self.index_selected)
        new_Item = self.create_new_folder(parentItem)
        parentItem.insertChild(0, new_Item)
        count = 0
        self.insert_row_to_tree(count, new_Item)

    def add_root_folder(self):
        self.index_selected = self.tree_model.index(0, 0).parent()
        parentItem = self.tree_model.get_item(self.index_selected)
        new_Item = self.create_new_folder(parentItem)
        parentItem.appendChild(new_Item)
        count = parentItem.childCount() - 1
        self.insert_row_to_tree(count, new_Item)

    def create_root_primitive(self):
        self.index_selected = self.tree_model.index(0, 0).parent()
        parentItem = self.tree_model.get_item(self.index_selected)
        new_Item = self.create_new_item(parentItem)
        parentItem.appendChild(new_Item)
        count = parentItem.childCount() - 1
        self.insert_row_to_tree(count, new_Item)

    def create_child_primitive(self):
        parentItem = self.tree_model.get_item(self.index_selected)
        new_Item = self.create_new_item(parentItem)
        parentItem.insertChild(0, new_Item)
        count = 0
        self.insert_row_to_tree(count, new_Item)

    def insert_row_to_tree(self, count, new_Item):
        self.tree_model.insertRow(count, self.index_selected)
        self.setCurrentIndex(self.tree_model.index(count, 0, self.index_selected))
        self._curItem = new_Item
        self.tree_selection_changed.emit(self._curItem)

    def create_new_item(self, parentItem):
        new_Item = TreeItem(None, parentItem)
        new_Item.setData("New Primitive")
        new_Item.setDataType("Text")
        new_Item.setVarId(self.randomString())
        new_Item.setNewAdded(True)
        new_Item.setMetaData({})
        new_Item.setSources([])
        return new_Item

    def create_new_folder(self, parentItem):
        new_Item = TreeItem(None, parentItem)
        new_Item.setData("New Folder")
        new_Item.setDataType("Folder")
        new_Item.setVarId(self.randomString())
        new_Item.setMetaData({})
        new_Item.setSources([])
        new_Item.setNewAdded(True)
        return new_Item

    def start_search(self, text):
        if not self.tree_model.hasIndex(0, 0) or text.replace(' ', '') == "":
            self._show_all(self.tree_model.index(0, 0).parent())
            self.collapseAll()
            return
        root_idx = self.tree_model.index(0, 0).parent()
        self._show_all(root_idx)
        self.text_to_search = text
        self._searching(root_idx)
        self.expandAll()

    def _show_all(self, index):
        item = self.tree_model.get_item(index)
        if item.childCount() == 0:
            return
        for i in range(item.childCount()):
            idx = self.tree_model.index(i, 0, index)
            _item = self.tree_model.get_item(idx)
            _item.isHidden = False
            self.setRowHidden(_item.childNumber(), idx.parent(), False)

            self._show_all(idx)


    def _searching(self, index):
        for i in range(self.tree_model.rowCount(index)):
            idx = self.tree_model.index(i, 0)
            self._search_func(idx)

    def _search_func(self, index):
        try:
            item = self.tree_model.get_item(index)
            if self.text_to_search.lower() in item.data().lower():
                item.isHidden = False
                item.parent().isHidden = False
                self.setRowHidden(item.childNumber(), index.parent(), False)
                return

            if item.childCount() == 0:
                item.isHidden = True
                item.parent().isHidden = True
                self.setRowHidden(item.childNumber(), index.parent(), True)
                return

            for i in range(item.childCount()):
                idx = self.tree_model.index(i, 0, index)
                self._search_func(idx)

            self.setRowHidden(item.childNumber(), index.parent(), item.isHidden)
        except Exception as e:
            print("search failed: {}".format(e))
            print(traceback.format_exc())



    """
    Initialize UI
    """
    def initUI(self):
        self._context_menu = QtWidgets.QMenu()
        self._context_menu.addAction(self._delete_action)
        self._context_menu.addAction(self._dup_action)
        self._context_menu.addAction(self._rename_action)
        self._context_menu.addAction(self._add_child_folder_action)
        self._context_menu.addAction(self._add_child_primitive_action)
        self._context_menu.addAction(self._add_root_folder_action)
        self._context_menu.addAction(self._add_root_primitive_action)
        self.header().hide()
        self.setDragDropMode(QtWidgets.QAbstractItemView.InternalMove)
        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self._open_menu)


