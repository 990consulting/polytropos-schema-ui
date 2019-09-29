import sys
import json

from PyQt5 import QtCore, QtGui, QtWidgets
import qtawesome as qta

from tree_model import TreeModel, TreeView
from tkinter import messagebox

class MainWindow(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        self._jsData = []
        self._openFileName = ""
     
        self._tree_view = None
        layout = QtWidgets.QHBoxLayout(self)
        layout.addWidget(self._add_splitter())
        
        self.openFileNameDialog()

        self._selectedItem = None
        self._treeSelChanged_flag = False

    def openFileNameDialog(self):
        options = QtWidgets.QFileDialog.Options()
        options |= QtWidgets.QFileDialog.DontUseNativeDialog
        fileName, _ = QtWidgets.QFileDialog.getOpenFileName(self,"Open", "","Json Files (*.json);;All Files (*)", options=options)
        if fileName:
            self._openFileName = fileName
            with open(self._openFileName) as f:
                try:
                    self._jsData = json.load(f)
                    self._treeLoad()
                except ValueError:
                    QtWidgets.QMessageBox.critical(self, "Json Error", "Json TypeError")
                    sys.exit()
            
    def _treeLoad(self):
        self._tree_view.loadData(self._jsData)
        self._disable_right_pane()        

    def _disable_right_pane(self):
        self._right_side_widget.setEnabled(False)
        self._right_side_widget.setTitle("Loreum ipsum dolor sit")

        self._variable_value.setText("")
        self._path_value.setText("")
        self._source_table.setModel(SourceTableModel())
        self._metadata_table.setModel(MetadataTableModel())

    def _add_splitter(self):
        splitter = QtWidgets.QSplitter()
        splitter.addWidget(self._create_left_pane())
        splitter.addWidget(self._create_right_pane())
        return splitter

    def _create_left_pane(self):
        left_side_widget = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(left_side_widget)
        layout.setContentsMargins(9, 0, 9, 0)
        layout.addLayout(self._create_left_pane_buttons())
        layout.addLayout(self._create_search_bar())

        self._tree_view = TreeView()
        self._tree_view.valueChanged.connect(self._tree_value_changed)
        self._tree_view.curChanged.connect(self._tree_selection_changed)

        layout.addWidget(self._tree_view)

        return left_side_widget

    def _tree_value_changed(self,value):
        self._right_side_widget.setTitle( value )
        self._path_value.setText(self._selectedItem.fullPath())

    def _create_right_pane(self):
        self._right_side_widget = QtWidgets.QGroupBox("Loreum ipsum dolor sit")
        layout = QtWidgets.QGridLayout()
        self._right_side_widget.setLayout(layout)

        variable_id = QtWidgets.QLabel("Variable ID:")
        layout.addWidget(variable_id, 0, 0)
        self._variable_value = QtWidgets.QLineEdit()
        self._variable_value.setReadOnly(True)
        layout.addWidget(self._variable_value, 0, 1)

        path = QtWidgets.QLabel("Absolute path:")
        layout.addWidget(path, 1, 0)
        self._path_value = QtWidgets.QLineEdit()
        self._path_value.setReadOnly(True)
        layout.addWidget(self._path_value, 1, 1)

        data_type = QtWidgets.QLabel("Data type:")
        layout.addWidget(data_type, 2, 0)
        self._data_type_value = QtWidgets.QComboBox()
        self._data_type_value.currentTextChanged.connect(self._data_type_changed)
        layout.addWidget(self._data_type_value, 2, 1)

        layout.addItem(QtWidgets.QSpacerItem(100, 50), 3, 0, 1, 2)

        sources = QtWidgets.QLabel("Sources")
        layout.addWidget(sources, 4, 0, QtCore.Qt.AlignTop)
        layout.addWidget(self._create_source_table(), 4, 1)

        layout.addItem(QtWidgets.QSpacerItem(100, 50), 5, 0, 1, 2)

        metadata = QtWidgets.QLabel("Metadata")
        layout.addWidget(metadata, 6, 0, QtCore.Qt.AlignTop)
        layout.addWidget(self._create_metadata_table(), 6, 1)

        return self._right_side_widget

    def _create_source_table(self):
        self._source_table = QtWidgets.QTableView()
        self._source_table.horizontalHeader().hide()
        self._source_table.verticalHeader().hide()

        self._source_table.setFixedHeight(62)

        model = SourceTableModel()
        self._source_table.setModel(model)
        self._source_table.clicked.connect(self._source_table_clicked)

        horizontal_header = self._source_table.horizontalHeader()
        horizontal_header.setSectionResizeMode(0, QtWidgets.QHeaderView.Stretch)
        horizontal_header.setSectionResizeMode(1, QtWidgets.QHeaderView.ResizeToContents)
        horizontal_header.setSectionResizeMode(2, QtWidgets.QHeaderView.ResizeToContents)

        return self._source_table

    def _source_table_clicked(self, index):
        row = index.row()
        column = index.column()
        model = self._source_table.model()
        
        if(model.index(row,0).data() == ""):
            return

        if(column == 1):
            model.insertRow(row)
        elif (column == 2):
            model.removeRow(row)
    
    def _source_changed(self, topLeft, bottomRight, role):
        self._selectedItem.setSources(self._source_table.model().getSources())
        self._selectedItem.setValueChanged(True)
        return

    def _create_metadata_table(self):
        self._metadata_table = QtWidgets.QTableView()
        self._metadata_table.verticalHeader().hide()

        model = MetadataTableModel()
        self._metadata_table.setModel(model)
        self._metadata_table.clicked.connect(self._metadata_table_clicked)

        horizontal_header = self._metadata_table.horizontalHeader()
        horizontal_header.setSectionResizeMode(0, QtWidgets.QHeaderView.Stretch)
        horizontal_header.setSectionResizeMode(1, QtWidgets.QHeaderView.Stretch)
        horizontal_header.setSectionResizeMode(2, QtWidgets.QHeaderView.ResizeToContents)
        horizontal_header.setSectionResizeMode(3, QtWidgets.QHeaderView.ResizeToContents)

        return self._metadata_table

    def _metadata_table_clicked(self, index):
        row = index.row()
        column = index.column()
        model = self._metadata_table.model()
        
        if(model.index(row,0).data() == ""):
            return

        if(column == 2):
            model.insertRow(row)
        elif (column == 3):
            model.removeRow(row)

    def metadata_changed(self, topLeft, bottomRight, role):
        self._selectedItem.setMetaData(self._metadata_table.model().getMetaData())
        self._selectedItem.setValueChanged(True)
        return

    def _save_clicked(self):
        conDiag = QtWidgets.QMessageBox.question(self, "Save", "Would you save the changes?")
        if conDiag == QtWidgets.QMessageBox.Yes:
            root_item = self._tree_view.getRootItem()
            saveJS = []
            for child in root_item.childItems:
                saveJS.append(child.getJsonData())

            with open(self._openFileName, 'w') as savefile:
                json.dump(saveJS, savefile)

    def _revert_clicked(self):
        conDiag = QtWidgets.QMessageBox.question(self, "Confirm", "Would you revert?")
        if conDiag == QtWidgets.QMessageBox.Yes:
            self._tree_view.clearContent()
            self._treeLoad()

    def _create_left_pane_buttons(self):
        layout = QtWidgets.QHBoxLayout()
        save_button = QtWidgets.QPushButton("Save")
        save_button.clicked.connect(self._save_clicked)

        revert_button = QtWidgets.QPushButton("Revert")
        revert_button.clicked.connect(self._revert_clicked)

        validate_button = QtWidgets.QPushButton("Validate")

        layout.addWidget(save_button)
        layout.addStretch()

        layout.addWidget(revert_button)
        layout.addStretch()

        layout.addWidget(validate_button)

        return layout

    def _create_search_bar(self):
        layout = QtWidgets.QHBoxLayout()
        search_field = QtWidgets.QLineEdit()
        search_field.setPlaceholderText("Search...")
        search_field.textChanged.connect(self._searchFilter)

        layout.addWidget(search_field)

        return layout

    def _searchFilter(self, text):
        self._tree_view._start_search(text)

    def _tree_selection_changed(self, selected):
        self._selectedItem = selected

        if(self._selectedItem == None):
            self._disable_right_pane()
            return

        self._right_side_widget.setEnabled(True)
        
        self._variable_value.setText(self._selectedItem.getVarId())
        self._right_side_widget.setTitle(self._selectedItem.data())
        self._path_value.setText(self._selectedItem.fullPath())
        #data_type
        self._treeSelChanged_flag = True
        self._data_type_value.clear()

        dataType = self._selectedItem.getDataType()
        if(dataType == "Folder" or dataType == "List" or dataType == "KeyedList"):
            self._data_type_value.addItems(["Folder", "List", "KeyedList"])
        else :
            self._data_type_value.addItems(["Text", "Integer", "Float", "Decimal", "Currency", "Date", "Unary", "Binary"])

        self._data_type_value.setCurrentText(self._selectedItem.getDataType())
        self._treeSelChanged_flag = False

        self._data_type_changed(self._selectedItem.getDataType())
        #data_type

        #metadata_table
        model = MetadataTableModel(self._selectedItem.getMetaData())
        self._metadata_table.setModel(model)        
        model.dataChanged.connect(self.metadata_changed)
        #metadata_table

    def _data_type_changed(self, selected):
        if self._treeSelChanged_flag == True:
            return
        
        model = SourceTableModel(self._selectedItem.getSources())
        self._source_table.setModel(model)
        model.dataChanged.connect(self._source_changed)

        if selected == "Folder":
            self._source_table.setDisabled(True)
        else:
            self._source_table.setDisabled(False)            

        if self._selectedItem.getDataType() == selected:
            return

        self._selectedItem.setDataType(selected)
        modelIndex = self._tree_view.selectedIndexes()[0]
        self._tree_view.dataChanged(modelIndex, modelIndex, [QtCore.Qt.DecorationRole])


class SourceTableModel(QtCore.QAbstractTableModel):

    def __init__(self, sources=None, parent=None):
        super().__init__(parent)

        if sources == None:
            self.sources = None
            return

        self.sources = []
        for e in sources:
            if e != "":
                self.sources.append(e)

    def flags(self, index):
        if index.column() == 0:
            return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsEditable
        return super().flags(index)

    def rowCount(self, parent=QtCore.QModelIndex()):
        if self.sources == None:
            return 0

        count = len(self.sources)
        if count == 0:
            return 1    
        return count

    def columnCount(self, parent=QtCore.QModelIndex()):
        return 3

    def data(self, index, role=QtCore.Qt.DisplayRole):

        if not index.isValid():
            return None

        column = index.column()
        if role == QtCore.Qt.DecorationRole and column == 1:
            icon = qta.icon('fa5s.plus-circle')
            return icon

        if role == QtCore.Qt.DecorationRole and column == 2:
            icon = qta.icon('fa5s.minus-circle')
            return icon

        if role == QtCore.Qt.DisplayRole and column == 0:
            if len(self.sources) == 0:
                return ""
            return self.sources[index.row()] 

    def setData(self, index, value, role=QtCore.Qt.EditRole):
        row = index.row()
        column = index.column()
        if column != 0 or role != QtCore.Qt.EditRole:
            return False

        if(len(self.sources)):
            self.sources[row] = value
        else:
            self.sources.insert(row, value)

        self.dataChanged.emit(index, index)

        return True

    def insertRow(self, row):
        self.beginInsertRows(QtCore.QModelIndex(), row, row)
        self.sources.insert(row + 1, "")
        self.endInsertRows()
        return True

    def removeRow(self, row):
        if(len(self.sources)==1):
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

    def getSources(self):
        return self.sources

class MetadataTableModel(QtCore.QAbstractTableModel):
    def __init__(self, metadata=None, parent=None):
        super().__init__(parent)

        if metadata == None:
            self.metadata = None
            return

        self.metadata = []
        for key,value in metadata.items():
            if key != "":
                self.metadata.append({"key":key,"value":value})

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
        row =  index.row()
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

        if role == QtCore.Qt.DecorationRole and column == 2:
            icon = qta.icon('fa5s.plus-circle')
            return icon

        if role == QtCore.Qt.DecorationRole and column == 3:
            icon = qta.icon('fa5s.minus-circle')
            return icon

    def setData(self, index, value, role=QtCore.Qt.EditRole):
        if(role != QtCore.Qt.EditRole):
            return False
        
        column = index.column()
        row =  index.row()
        
        if column == 0:
            if value == "":
                if self.metadata[row]["value"] == "":
                    QtWidgets.QMessageBox.critical(None,"Critical","this key cannot have empty value")
                    return False
                value = "#real_empty#"

            for e in self.metadata:
                if e["key"] ==  value:
                    QtWidgets.QMessageBox.critical(None,"Critical","this key already exists")
                    return False
    
            self.metadata[row]["key"] = value
        elif column == 1:
            if (value == "" and self.metadata[row]["key"] == "#real_empty#"):
                QtWidgets.QMessageBox.critical(None,"Critical","this key cannot have empty value")
                return False
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
        self.metadata.insert(row + 1, {"key":"", "value":""})
        self.endInsertRows()
        return True

    def removeRow(self, row):
        if(len(self.metadata)==1):
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
            if key != "":
                metadata[key] = e["value"]

        return metadata

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
