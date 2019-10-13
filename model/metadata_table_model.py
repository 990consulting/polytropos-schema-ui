from PyQt5 import QtCore, QtWidgets
import qtawesome as qta
import traceback


class MetadataTableModel(QtCore.QAbstractTableModel):
    def __init__(self, metadata=None, parent=None):
        super().__init__(parent)
        if metadata is None:
            self.metadata = None
            return
        else:
            self.initialize_table(metadata)

    def initialize_table(self, metadata):
        self.metadata = []
        for key, value in metadata.items():
            if key != "":
                self.metadata.append({"key": key, "value": value})

    """
       The methods below are overridden methods of the base abstract class QAbstractItemModel
    """

    def rowCount(self, parent=QtCore.QModelIndex()):
        if self.metadata == None:
            return 0
        elif len(self.metadata) == 0:
            return 1
        else:
            return len(self.metadata)

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
        row = index.row()
        if role == QtCore.Qt.DisplayRole:
            if len(self.metadata) == 0:
                return None
            metadata = self.metadata[row]
            if column == 0:
                if(metadata["key"] == "#real_empty#"):
                    return ""
                return metadata["key"]
            elif column == 1:
                return metadata["value"]
            else:
                return None

        if role == QtCore.Qt.DecorationRole:
            if column == 2:
                return qta.icon('fa5s.plus-circle')
            if  column == 3:
                return qta.icon('fa5s.minus-circle')


    def setData(self, index, value, role=QtCore.Qt.EditRole):
        if role != QtCore.Qt.EditRole:
            return False
        column = index.column()
        row = index.row()
        if column == 0:
            for e in self.metadata:
                if e["key"] == value or value == '' and row > 0:
                    print(value)
                    QtWidgets.QMessageBox.critical(None,"Critical","this key already exists")
                    return False
            if not self.metadata:
                self.metadata.append({'key': '#real_empty#', 'value': ''})
            self.metadata[row]["key"] = value

        elif column == 1:
            if not self.metadata:
                self.metadata.append({'key': '#real_empty#', 'value': ''})
            if value == "" and self.metadata[row]["key"] == "#real_empty#":
                QtWidgets.QMessageBox.critical(None,"Critical","cannot have empty value")
                return False
            if self.metadata[row]["key"] == '':
                self.metadata[row]["key"] = '#real_empty#'
            self.metadata[row]["value"] = value

        else:
            return False
        self.dataChanged.emit(index, index)
        return True

    def headerData(self, section, orientation, role=QtCore.Qt.DisplayRole):
        if role == QtCore.Qt.DisplayRole and orientation == QtCore.Qt.Horizontal:
            if section == 0:
                return "Key"
            elif section == 1:
                return "Value"
            else:
                return ""

    def insertRow(self, row):
        self.beginInsertRows(QtCore.QModelIndex(), row, row)
        self.metadata.insert(row + 1, {"key":"#real_empty#", "value":""})
        self.endInsertRows()
        return True

    def removeRow(self, row):
        if len(self.metadata) == 1:
            self.metadata = []
            self.beginRemoveRows(QtCore.QModelIndex(), 0, 0)
            self.endRemoveRows()
            self.beginInsertRows(QtCore.QModelIndex(), 0, 0)
            self.endInsertRows()
        else:
            self.beginRemoveRows(QtCore.QModelIndex(), row, row)
            new_metas = []
            for i in range(len(self.metadata)):
                if i != row:
                    new_metas.append(self.metadata[i])
            self.metadata = new_metas
            self.endRemoveRows()

        self.dataChanged.emit(QtCore.QModelIndex(), QtCore.QModelIndex())
        return True

    def getMetaData(self):
        metadata = {}
        for e in self.metadata:
            key = e["key"]
            metadata[key] = e["value"]
        return metadata
