"""
Simple custom tree model.

Resources:
https://doc.qt.io/qt-5/qtwidgets-itemviews-editabletreemodel-example.html
https://github.com/pyside/Examples/blob/master/examples/itemviews/editabletreemodel/editabletreemodel.py
https://stackoverflow.com/questions/4163740/qtreeview-with-drag-and-drop-support-in-pyqt
"""

import sys

import qtawesome as qta
from PyQt5 import QtWidgets, QtGui, QtCore

class TreeItem():
    def __init__(self, data, parent=None):
        self.parentItem = parent
        self.itemData = data
        self.childItems = []

    def parent(self):
        return self.parentItem

    def child(self, row):
        return self.childItems[row]

    def childCount(self):
        return len(self.childItems)

    def childNumber(self):
        if self.parentItem != None:
            return self.parentItem.childItems.index(self)
        return 0

    def data(self):
        return self.itemData

    def setData(self, value):
        self.itemData = value
        return True

    def insertChildren(self, position, count):
        if position < 0 or position > len(self.childItems):
            return False

        for row in range(count):
            data = None
            item = TreeItem(data, self)
            self.childItems.insert(position, item)

        return True

    def removeChildren(self, position, count):
        if position < 0 or position + count > len(self.childItems):
            return False

        for row in range(count):
            self.childItems.pop(position)

        return True

    def fullPath(self):
        path = [self.data()]
        parent = self.parent()
        while parent.parent() is not None:
            path.append(parent.data())
            parent = parent.parent()
        return '/'.join(reversed(path))


class TreeModel(QtCore.QAbstractItemModel):
    def __init__(self):
        QtCore.QAbstractItemModel.__init__(self)

        self._root_item = TreeItem(None)

        self._root_item.insertChildren(0, 2)
        self._root_item.child(0).setData('parent_0')

        self._root_item.child(0).insertChildren(0, 2)
        self._root_item.child(0).child(0).setData('child_0')
        self._root_item.child(0).child(1).setData('child_1')

        self._root_item.child(1).setData('parent_1')

        self._root_item.child(1).insertChildren(0, 1)
        self._root_item.child(1).child(0).setData('child_2')

    def index(self, row, column, parent):
        # if parent.isValid():
        #     return QtCore.QModelIndex()

        parent_item = self.get_item(parent)
        child_item = parent_item.child(row)
        if child_item is not None:
            return self.createIndex(row, column, child_item)
        else:
            return QtCore.QModelIndex()

    def parent(self, index):
        if not index.isValid():
            return QtCore.QModelIndex()

        child_item = self.get_item(index)
        parent_item = child_item.parent()

        if parent_item == self._root_item:
            return QtCore.QModelIndex()

        parent_child_number = parent_item.childNumber()
        return self.createIndex(parent_child_number, 0, parent_item)

    def get_item(self, index):
        if index.isValid():
            item = index.internalPointer()
            if item:
                return item

        return self._root_item

    def rowCount(self, parent):
        parent_item = self.get_item(parent)
        row_count = parent_item.childCount()
        return row_count

    def columnCount(self, index):
        return 1

    def data(self, index, role):
        if not index.isValid():
            return None

        if (
                role != QtCore.Qt.DisplayRole and
                role != QtCore.Qt.DecorationRole
        ):
            return None

        item = self.get_item(index)

        if role == QtCore.Qt.DecorationRole and item.childCount():
            icon = qta.icon('fa5s.folder')
            return icon
        elif role == QtCore.Qt.DecorationRole and not item.childCount():
            icon = qta.icon('fa5s.file')
            return icon
        elif role == QtCore.Qt.DisplayRole:
            return item.data()

    def supportedDropActions(self):
        return QtCore.Qt.CopyAction | QtCore.Qt.MoveAction

    def flags(self, index):
        if not index.isValid():
            return QtCore.Qt.ItemIsEnabled

        item = self.get_item(index)
        if item.childCount() == 0:
            return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable | \
                   QtCore.Qt.ItemIsDragEnabled

        return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable | \
               QtCore.Qt.ItemIsDragEnabled | QtCore.Qt.ItemIsDropEnabled

    def mimeTypes(self):
        return ['text/xml']

    def mimeData(self, indexes):
        item = self.get_item(indexes[0])
        mimedata = QtCore.QMimeData()
        mimedata.setData('text/xml', bytes(item.fullPath(), encoding='ascii'))
        return mimedata

    def dropMimeData(self, data, action, row, column, parent):
        print('dropMimeData %s %s %s %s %s' % (data.data('text/xml'), action, row, column, parent))
        # When row and column are -1 it means that the dropped data should be considered as
        # dropped directly on parent. Usually this will mean appending the data as child items
        # of parent. If row and column are greater than or equal zero, it means that the drop
        # occurred just before the specified row and column in the specified parent.

        target_parent_item = self.get_item(parent)

        item_path = data.data('text/xml').split('/')
        current_item = self._root_item
        current_level_of_nesting = 0
        while current_item.data() != item_path[-1]:
            for child_index in range(current_item.childCount()):
                child_item = current_item.child(child_index)
                if child_item.data() == item_path[current_level_of_nesting]:
                    current_item = child_item
                    current_level_of_nesting += 1
                    break

        if row == -1 and column == -1:

            if current_item.parent() != target_parent_item:
                self.beginInsertRows(
                    parent,
                    target_parent_item.childCount() - 1,
                    target_parent_item.childCount() - 1
                )
                current_item_parent = current_item.parent()
                current_item_parent.childItems.remove(current_item)
                current_item.parentItem = target_parent_item
                target_parent_item.childItems.append(current_item)
                self.endInsertRows()

        else:

            if current_item.parent() != target_parent_item:
                self.beginInsertRows(
                    parent,
                    row,
                    row
                )
                current_item_parent = current_item.parent()
                current_item_parent.childItems.remove(current_item)
                current_item.parentItem = target_parent_item
                target_parent_item.childItems.insert(row, current_item)
                self.endInsertRows()

            else:
                current_item_parent = current_item.parent()
                current_item_parent.childItems.remove(current_item)
                target_parent_item.childItems.insert(row, current_item)

        return True


class MainForm(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super(MainForm, self).__init__(parent)

        self.treeModel = TreeModel()

        self.view = QtWidgets.QTreeView()
        self.view.setModel(self.treeModel)
        self.view.setDragDropMode(QtWidgets.QAbstractItemView.InternalMove)

        self.setCentralWidget(self.view)


def main():
    app = QtWidgets.QApplication(sys.argv)
    form = MainForm()
    form.show()
    app.exec_()

if __name__ == '__main__':
    main()