import traceback


class TreeItem(object):

    def __init__(self, data, parent=None):
        self.parentItem = parent
        self.childItems = []
        self.varId = None
        self.dataType = None
        self.sources = None
        self.metadata = None
        self.itemData = None
        self.valueChanged = False
        self.newAdded = False
        self.isHidden = True

        if data is not None:
            self.itemData = data["title"]
            self.varId = (data["varId"] if 'varId' in data else None)
            self.dataType = (data["dataType"] if 'dataType' in data else None)
            self.sources = (data["sources"] if 'sources' in data else [])
            self.metadata = (data["metadata"] if 'metadata' in data else {})

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
        return self.metadata

    def setMetaData(self, metadata):
        self.metadata = metadata
        return True

    def create_new_item(self):
        try:
            new_item = {}
            new_item["title"] = self.itemData
            new_item["varId"] = self.varId
            new_item["dataType"] = self.dataType
            if len(self.sources):
                new_item["sources"] = self.sources
            if len(self.metadata):
                new_item["metadata"] = self.metadata
            if self.childCount():
                new_item["children"] = []
                for child in self.childItems:
                    new_item["children"].append(child.create_new_item())
            return new_item
        except Exception as e:
            print("create_new_item failed: {}".format(e))
            print(traceback.format_exc())

    def create_duplicate(self, parent_item):
        try:
            new_item = TreeItem(self.create_new_item(), parent_item)
            if self.childCount():
                for child in self.childItems:
                    new_item.appendChild(child.create_duplicate(new_item))

            return new_item
        except Exception as e:
            print("create_duplicate failed: {}".format(e))
            print(traceback.format_exc())

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
        try:
            path = [self.data()]
            parent = self.parent()
            while parent.parent() is not None:
                path.append(parent.data())
                parent = parent.parent()
            return '/' + '/'.join(reversed(path))
        except Exception as e:
            print("fullPath failed: {}".format(e))
            print(traceback.format_exc())
