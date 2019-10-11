import qtawesome as qta
from PyQt5 import QtCore, QtGui
from model.tree_item import TreeItem
from model.type_manager import TypeManager
import traceback


class TreeModel(QtCore.QAbstractItemModel):
    rowMoved = QtCore.pyqtSignal(object)

    def __init__(self):
        QtCore.QAbstractItemModel.__init__(self)
        self.root_item = TreeItem({"title": "root"})

    def load_data(self, data):
        for element in data:
            self.create_tree(element, self.root_item)

    def create_tree(self, data, parent_item):
        if len(data) == 0:
            return
        new_item = TreeItem(data, parent_item)
        parent_item.appendChild(new_item)
        if 'children' in data:
            for element in data["children"]:
                self.create_tree(element, new_item)

    def get_item(self, index):
        if index.isValid():
            item = index.internalPointer()
            if item:
                return item
        return self.root_item

    """
    The methods below are overridden methods of the base abstract class QAbstractItemModel
    """

    # inherited Method
    def index(self, row, column, parent=QtCore.QModelIndex()):
        if self.hasIndex(row, column, parent):
            parent_item = self.get_item(parent)
            child_item = parent_item.child(row)
            if child_item is not None:
                return self.createIndex(row, column, child_item)
        return QtCore.QModelIndex()

    # inherited Method
    def parent(self, index):
        if not index.isValid():
            return QtCore.QModelIndex()
        child_item = self.get_item(index)
        parent_item = child_item.parent()
        if parent_item == self.root_item:
            return QtCore.QModelIndex()
        parent_child_number = parent_item.childNumber()
        return self.createIndex(parent_child_number, 0, parent_item)

    # inherited Method
    def rowCount(self, parent):
        return self.get_item(parent).childCount()

    # inherited Method
    def columnCount(self, index):
        return 1

    # inherited Method
    def data(self, index, role=QtCore.Qt.DisplayRole):

        try:
            if not index.isValid():
                return None
            item = self.get_item(index)
            if role == QtCore.Qt.BackgroundRole:
                if not (item.newAdded or item.valueChanged):
                    return None
            elif role == QtCore.Qt.ForegroundRole:
                if item.newAdded:
                    return QtGui.QBrush(QtCore.Qt.darkGreen)
                elif item.valueChanged:
                    return QtGui.QBrush(QtCore.Qt.blue)
                else:
                    return None
            elif role == QtCore.Qt.DecorationRole:
                if item.newAdded:
                    return qta.icon(TypeManager.type_icon_dictionary[item.getDataType()], options=[{'color': 'green'}])
                elif item.valueChanged:
                    return qta.icon(TypeManager.type_icon_dictionary[item.getDataType()], options=[{'color': 'blue'}])
                else:
                    return qta.icon(TypeManager.type_icon_dictionary[item.getDataType()], options=[{'color': 'black'}])
            elif role == QtCore.Qt.DisplayRole:
                return item.data()
            else:
                return None
        except Exception as e:
            print("data failed: {}".format(e))
            print(traceback.format_exc())

    # inherited Method
    def setData(self, index, value, role=QtCore.Qt.EditRole):

        if role != QtCore.Qt.EditRole:
            return False
        if value == "":
            return False
        item = self.get_item(index)
        item.setData(value)
        self.dataChanged.emit(index, index)
        return True

    # inherited Method
    def insertRow(self, row, parent=QtCore.QModelIndex()):
        self.beginInsertRows(parent, row, row)
        self.endInsertRows()
        return True

    # inherited Method
    def removeRow(self, row, parent=QtCore.QModelIndex()):
        self.beginRemoveRows(parent, row, row)
        self.get_item(parent).removeChildren(row, 1)
        self.endRemoveRows()
        return True

    # inherited Method
    def supportedDropActions(self):
        return QtCore.Qt.CopyAction | QtCore.Qt.MoveAction

    # inherited Method
    def flags(self, index):
        if not index.isValid():
            return QtCore.Qt.ItemIsEnabled
        gen_flags = QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsDragEnabled | QtCore.Qt.ItemIsEditable
        if self.get_item(index).getDataType() in TypeManager.collections:
            return gen_flags | QtCore.Qt.ItemIsDropEnabled
        else:
            return gen_flags | QtCore.Qt.ItemNeverHasChildren

    # inherited Method
    def mimeTypes(self):
        return ['text/xml']

    # inherited Method
    def mimeData(self, indexes):
        self.drag_item_index = indexes[0]
        mimedata = QtCore.QMimeData()
        mimedata.setData('text/xml', bytes('mimeData', encoding='ascii'))
        return mimedata

    # inherited Method
    def dropMimeData(self, data, action, row, column, parent):
        try:
            if action != QtCore.Qt.MoveAction:
                return False
            target_parent_item = self.get_item(parent)
            source_item = self.get_item(self.drag_item_index)
            source_parent_idx = self.drag_item_index.parent()
            num = source_item.childNumber()
            new_item = source_item.create_duplicate(target_parent_item)
            self.removeRow(num, source_parent_idx)
            if row == -1:
                target_parent_item.appendChild(new_item)
                row = target_parent_item.childCount() - 1
            else:
                target_parent_item.insertChild(row, new_item)
            self.insertRow(row, parent)
            self.rowMoved.emit(self.index(row, 0, parent))
            return True
        except Exception as e:
            print("dropMineData failed: {}".format(e))
            print(traceback.format_exc())
