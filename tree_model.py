"""
Simple custom tree model.

Resources:
https://doc.qt.io/qt-5/qtwidgets-itemviews-editabletreemodel-example.html
https://github.com/pyside/Examples/blob/master/examples/itemviews/editabletreemodel/editabletreemodel.py
https://stackoverflow.com/questions/4163740/qtreeview-with-drag-and-drop-support-in-pyqt
"""

import sys

import qtawesome as qta
from PyQt5 import QtWidgets, QtCore, QtGui

class TreeItem(object):
    def __init__(self, data, parent=None):
        self.parentItem = parent
        
        self.itemData = (data if data == None else data["title"])

        self.childItems = []
        self.varId = None
        self.dataType = None
        self.sources = None
        self.matadata = None

        self.valueChanged = False
        self.newAdded = False
        self.isHidden = True

        if data != None:
            self.varId = (data["varId"] if 'varId' in data else None)
            self.dataType = (data["dataType"] if 'dataType' in data else None)
            self.sources = (data["sources"] if 'sources' in data else [])
            self.matadata = (data["metadata"] if 'metadata' in data else {})
                
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

    def getVarId(self):
        return self.varId

    def setVarId(self, value):
        self.varId = value
        return True

    def getDataType(self):
        return self.dataType

    def setDataType(self, value):
        self.dataType = value
        return True

    def getSources(self):
        return self.sources   

    def setSources(self, sources):
        self.sources = sources
        return True

    def setValueChanged(self, flag):
        self.valueChanged = flag
        return True

    def setNewAdded(self, flag):
        self.newAdded = flag
        return True

    def getMetaData(self):
        return self.matadata   

    def setMetaData(self, metadata):
        self.matadata = metadata
        return True

    def getJsonData(self):
        jsData = {}
        jsData["title"] = self.itemData
        jsData["varId"] = self.varId
        jsData["dataType"] = self.dataType

        if len(self.sources):
            jsData["sources"] = self.sources

        if len(self.matadata) :
            jsData["metadata"] = self.matadata

        if self.childCount():
            jsData["children"] = []
            for child in self.childItems:
                jsData["children"].append(child.getJsonData())

        return jsData

    def clone(self, parent_item):
        new_item = TreeItem(self.getJsonData(), parent_item)
        if self.childCount():
            for child in self.childItems:
                new_item.appendChild(child.clone(new_item))

        return new_item

    def appendChild(self, item):
        self.childItems.append(item)

    def insertChild(self, position, item):
        if position > len(self.childItems):
            return False

        self.childItems.insert(position, item)
        return True

    def removeChildren(self, position, count):
        if position < 0 or position + count > len(self.childItems):
            return False

        while count > 0:
            self.childItems.pop(position)
            count -= 1

        return True

    def fullPath(self):
        path = [self.data()]
        parent = self.parent()
        while parent.parent() is not None:
            path.append(parent.data())
            parent = parent.parent()
        return '/'.join(reversed(path))

class TreeModel(QtCore.QAbstractItemModel):
    rowMoved = QtCore.pyqtSignal(object) 

    def __init__(self):
        QtCore.QAbstractItemModel.__init__(self)

        self._root_item = TreeItem({"title":"root"})
    
    def loadData(self, data):
        for element in data:
            self.cerate_tree(element, self._root_item)

    def cerate_tree(self, data, parent_item):
        if len(data) == 0:
            return

        new_item = TreeItem(data,parent_item)
        parent_item.appendChild(new_item)

        if('children' in data):
            for element in data["children"]:
                self.cerate_tree(element,new_item)

    def index(self, row, column, parent = QtCore.QModelIndex()):
        if self.hasIndex(row, column, parent):
            parent_item = self.get_item(parent)
            child_item = parent_item.child(row)
            if child_item is not None:
                return self.createIndex(row, column, child_item)
        
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

    def data(self, index, role=QtCore.Qt.DisplayRole):
        if not index.isValid():
            return None
            
        item = self.get_item(index)

        if role == QtCore.Qt.BackgroundRole:
            if item.newAdded:
                return QtGui.QBrush(QtCore.Qt.green)
            elif item.valueChanged:
                return  QtGui.QBrush(QtCore.Qt.blue)
            else:
                return None
            
        
        if role == QtCore.Qt.DecorationRole:
            dataType = item.getDataType()
            if(dataType == "Folder"):
                return qta.icon('fa5s.folder')
            elif(dataType == "List"):
                return qta.icon('fa5s.flag')
            elif(dataType == "KeyedList"):
                return qta.icon('fa5s.music')                
            else:
                return qta.icon('fa5s.file')

        elif role == QtCore.Qt.DisplayRole:
            return item.data()

        return None

    def setData(self, index, value, role=QtCore.Qt.EditRole):
        if role != QtCore.Qt.EditRole:
            return False

        if value == "":
            return False
        item = self.get_item(index)
        item.setData(value)

        self.dataChanged.emit(index, index)

        return True

    def insertRow(self, row, parent = QtCore.QModelIndex()):
        self.beginInsertRows(parent, row, row)

        self.endInsertRows()
        return True

    def removeRow(self, row, parent = QtCore.QModelIndex() ):
        self.beginRemoveRows(parent, row, row)
        self.get_item(parent).removeChildren(row, 1)   
        self.endRemoveRows()
        
        return True

    def supportedDropActions(self):
        return QtCore.Qt.CopyAction | QtCore.Qt.MoveAction

    def flags(self, index):
        if not index.isValid():
            return QtCore.Qt.ItemIsEnabled

        item = self.get_item(index)
        data_type = item.getDataType()
        if data_type == "Folder" or data_type =="List" or data_type == "KeyedList":
            return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsDragEnabled | QtCore.Qt.ItemIsDropEnabled
            
        return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsDragEnabled | QtCore.Qt.ItemNeverHasChildren | QtCore.Qt.ItemIsEditable

    def mimeTypes(self):
        return ['text/xml']

    def mimeData(self, indexes):
        self._dragItem_index = indexes[0]
        mimedata = QtCore.QMimeData()
        mimedata.setData('text/xml', bytes('mimeData', encoding='ascii'))
        return mimedata

    def dropMimeData(self, data, action, row, column, parent):
        if action != QtCore.Qt.MoveAction:
            return False

        target_parent_item = self.get_item(parent)

        source_item = self.get_item(self._dragItem_index)
        source_parent_idx = self._dragItem_index.parent()

        num = source_item.childNumber()

        newItem = source_item.clone(target_parent_item)

        self.removeRow(num, source_parent_idx)
        if row == -1:
            target_parent_item.appendChild(newItem)
            row = target_parent_item.childCount()-1
        else:
            target_parent_item.insertChild(row, newItem)
                
        self.insertRow(row, parent)

        self.rowMoved.emit(self.index(row, 0, parent))

        return True


class TreeView(QtWidgets.QTreeView, QtCore.QObject):
    curChanged = QtCore.pyqtSignal(object) 
    valueChanged = QtCore.pyqtSignal(object) 

    def __init__(self):
        QtWidgets.QTreeView.__init__(self)

        self._context_menu = self._create_context_menu()

        self.header().hide()
        self.setDragDropMode(QtWidgets.QAbstractItemView.InternalMove)
        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self._open_menu)

        self._tree_model = TreeModel()
        self._tree_model.dataChanged.connect(self._dataChanged)
        self._tree_model.rowMoved.connect(self._rowMoved)
        self.setModel(self._tree_model)
        self.setDragEnabled(True)

        self._curIndex = None
        self._search = ""

    def loadData(self, data):
        self._tree_model.loadData(data)

    def clearContent(self):
        root_index = self._tree_model.index(0,0).parent()
        i = self._tree_model.rowCount(root_index)
        while i:
            self._tree_model.removeRow(i-1, root_index)
            i -= 1

    def getRootItem(self):
        if self._tree_model.hasIndex(0,0):
            return self._tree_model.get_item(self._tree_model.index(0,0).parent())
        return None

    def _rowMoved(self, curIdx):
        self.setCurrentIndex(curIdx)
        self._curIndex = curIdx
        self._curItem = self._tree_model.get_item(self._curIndex)
        self.curChanged.emit(self._curItem)

    def _dataChanged(self, index):
        self.valueChanged.emit(index.data())

    def mousePressEvent(self, event):
        QtWidgets.QTreeView.mousePressEvent(self, event)
        self._curIndex = self.indexAt(event.pos())
        self.setCurrentIndex(self._curIndex)

        self._curItem = None if self._curIndex.data()==None else self._tree_model.get_item(self._curIndex)
        self.curChanged.emit(self._curItem)

    def getCurItem(self):
        return self._curItem

    def _create_menu_action(self, name, slot):
        action = QtWidgets.QAction(name)
        action.triggered.connect(slot)
        return action

    def _create_context_menu(self):
        menu = QtWidgets.QMenu()
        
        self._delete_action = self._create_menu_action('Delete', self._delete_slot)
        menu.addAction( self._delete_action )

        self._dup_action = self._create_menu_action('Dupiicated', self._clone_slot)
        menu.addAction( self._dup_action )

        self._rename_action = self._create_menu_action('Rename', self._rename_slot)
        menu.addAction( self._rename_action )

        self._add_action = self._create_menu_action('', self._add_folder_slot)
        menu.addAction( self._add_action )

        self._text_action = self._create_menu_action('', self._text_slot)
        menu.addAction( self._text_action )
        
        return menu

    def _create_node_menu(self):
        self._delete_action.setVisible(True)
        self._dup_action.setVisible(True)
        self._rename_action.setVisible(True)
        self._add_action.setVisible(False)
        self._text_action.setVisible(False)

    def _create_branch_menu(self):
        self._delete_action.setVisible(False)
        self._dup_action.setVisible(False)
        self._rename_action.setVisible(False)
        self._add_action.setVisible(True)
        self._add_action.setText("New Folder")
        self._text_action.setVisible(True)
        self._text_action.setText("New Primitive")


    def _create_root_menu(self):
        self._delete_action.setVisible(False)
        self._dup_action.setVisible(False)
        self._rename_action.setVisible(False)
        self._add_action.setVisible(True)
        self._add_action.setText("Add child container")
        self._text_action.setVisible(True)
        self._text_action.setText("Add child primitive")

    def _open_menu(self, position):
        if self._curItem == None:
            self._create_root_menu()
        else:
            datatype = self._curItem.dataType
            if datatype == "Folder" or datatype == "List" or datatype == "KeyedList":
                self._create_branch_menu()
            else:
                self._create_node_menu()

        self._context_menu.exec_(self.viewport().mapToGlobal(position))

    def _rename_slot(self):
        self.edit(self.currentIndex())

    def _delete_slot(self):
        parent = self._curIndex.parent()

        pos = self._curIndex.row()
        self._tree_model.removeRow(pos, parent)

        self._curItem = self._tree_model.get_item(self.currentIndex())
        self.curChanged.emit(self._curItem)

    def _clone_slot(self):
        parentItem = self._curItem.parent()

        dup_Item = self._curItem.clone(parentItem)
        dup_Item.setData("Copy of " + self._curItem.data())
        dup_Item.setVarId("copy_of_" + self._curItem.getVarId())
        dup_Item.setNewAdded(True)

        pos = self._curIndex.row()
        parentItem.insertChild(pos+1, dup_Item)

        self._tree_model.insertRow(pos, self._curIndex.parent())

        self._curItem = dup_Item
        self.curChanged.emit(self._curItem)

    def _add_folder_slot(self):
        flag = (self._curItem == None)
        if(flag):
            self._curIndex = self._tree_model.index(0,0).parent()

        parentItem = self._tree_model.get_item(self._curIndex)
        
        new_Item = TreeItem(None, parentItem)
        new_Item.setData("New Folder")
        new_Item.setDataType("Folder")
        new_Item.setVarId("i_folder_randon_id")
        new_Item.setMetaData({})
        new_Item.setSources([])
        new_Item.setNewAdded(True)

        if(flag):
            parentItem.appendChild( new_Item )
        else:
            parentItem.insertChild(0, new_Item)

        count = parentItem.childCount()-1 if flag else 0
        self._tree_model.insertRow(count, self._curIndex)

        self.setCurrentIndex(self._tree_model.index(count, 0, self._curIndex))
        self._curItem = new_Item
        
        self.curChanged.emit(self._curItem)

    def _text_slot(self):
        flag = (self._curItem == None)
        if(flag):
            self._curIndex = self._tree_model.index(0,0).parent()

        parentItem = self._tree_model.get_item(self._curIndex)
        
        new_Item = TreeItem(None, parentItem)
        new_Item.setData("New Primitive")
        new_Item.setDataType("Text")
        new_Item.setVarId("i_text_randon_id")
        new_Item.setNewAdded(True)
        new_Item.setMetaData({})
        new_Item.setSources([])

        if(flag):
            parentItem.appendChild( new_Item )
        else:
            parentItem.insertChild(0, new_Item)

        count = parentItem.childCount()-1 if flag else 0
        self._tree_model.insertRow(count, self._curIndex)

        self.setCurrentIndex(self._tree_model.index(count, 0, self._curIndex))
        self._curItem = new_Item
        
        self.curChanged.emit(self._curItem)

    def _start_search(self, text):
        if not self._tree_model.hasIndex(0,0):
            return

        root_idx = self._tree_model.index(0,0).parent()
        self._show_all(root_idx)

        if text == "":
            return
        self._search = text
        self._searching(root_idx)
        self.expandAll()

    def _show_all(self, index):
        item = self._tree_model.get_item(index)
        if item.childCount() == 0:
            return

        for i in range(item.childCount()):
            idx = self._tree_model.index(i, 0, index)
            _item = self._tree_model.get_item(idx)
            _item.isHidden = False
            self.setRowHidden(_item.childNumber(), idx.parent(),False)

            self._show_all(idx)     
    
    def _searching(self,index):
        for i in range(self._tree_model.rowCount(index)):
            idx = self._tree_model.index(i,0)
            self._search_func(idx)           
    
    def _search_func(self, index):
        item = self._tree_model.get_item(index)
        if self._search in item.data() :
            item.isHidden = False
            item.parent().isHidden = False
            self.setRowHidden(item.childNumber(), index.parent(),False)   
            return

        if item.childCount() == 0:
            item.isHidden = True
            item.parent().isHidden = True
            self.setRowHidden(item.childNumber(), index.parent(), True)
            return

        for i in range(item.childCount()):
            idx = self._tree_model.index(i, 0, index)
            self._search_func(idx)

        self.setRowHidden(item.childNumber(), index.parent(),item.isHidden)

        