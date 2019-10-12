from PyQt5 import QtCore
import qtawesome as qta
import traceback


class SourceTableModel(QtCore.QAbstractTableModel):
    """Table for viewing and modifying the variable sources, appearing within the detail pane."""

    def __init__(self, sources=None, parent=None):
        super().__init__(parent)
        try:
            if sources is None:
                self.sources = None
                return
            self.sources = []
            for source in sources:
                if source != "":
                    self.sources.append(source)
        except Exception as e:
            print("Initialization failed: {}".format(e))
            print(traceback.format_exc())

    # override
    def flags(self, index):
        if index.column() == 0:
            return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsEditable
        return super().flags(index)

    # override
    def rowCount(self, parent=QtCore.QModelIndex()):
        if self.sources is None:
            return 0
        elif len(self.sources) == 0:
            return 1
        else:
            return len(self.sources)

    # override
    def columnCount(self, parent=QtCore.QModelIndex()):
        return 3

    # override
    def data(self, index, role=QtCore.Qt.DisplayRole):

        if not index.isValid():
            return None

        column = index.column()
        if role == QtCore.Qt.DecorationRole:
            if column == 1:
                return qta.icon('fa5s.plus-circle')
            if column == 2:
                return qta.icon('fa5s.minus-circle')

        if role == QtCore.Qt.DisplayRole and column == 0:
            if len(self.sources) == 0:
                return ""
            return self.sources[index.row()]

    # override
    def setData(self, index, value, role=QtCore.Qt.EditRole):
        try:
            row = index.row()
            column = index.column()
            if column != 0 or role != QtCore.Qt.EditRole or value == "":
                return False
            if len(self.sources):
                self.sources[row] = value
            else:
                self.sources.insert(row, value)
            self.dataChanged.emit(index, index)
            return True
        except Exception as e:
            print("setData failed: {}".format(e))
            print(traceback.format_exc())

    # override
    def insertRow(self, row):
        try:
            self.beginInsertRows(QtCore.QModelIndex(), row, row)
            self.sources.insert(row + 1, "")
            self.endInsertRows()
            return True
        except Exception as e:
            print("insertRow failed: {}".format(e))
            print(traceback.format_exc())

    # override
    def removeRow(self, row):
        try:
            if len(self.sources) == 1:
                self.sources = []
                self.beginRemoveRows(QtCore.QModelIndex(), 0, 0)
                self.endRemoveRows()
                self.beginInsertRows(QtCore.QModelIndex(), 0, 0)
                self.endInsertRows()
            else:
                self.beginRemoveRows(QtCore.QModelIndex(), row, row)
                new_sources = []
                for i in range(len(self.sources)):
                    if i != row:
                        new_sources.append(self.sources[i])
                self.sources = new_sources
                self.endRemoveRows()
            self.dataChanged.emit(QtCore.QModelIndex(), QtCore.QModelIndex())
            return True
        except Exception as e:
            print("removeRow failed: {}".format(e))
            print(traceback.format_exc())

    # override
    def getSources(self):
        return self.sources
