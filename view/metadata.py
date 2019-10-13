from PyQt5 import QtWidgets

class MetadataTableView(QtWidgets.QTableView):
    def __init__(self):
        super().__init__()
        self.verticalHeader().hide()
        self.resizeRowsToContents()
        self.verticalHeader().setSectionResizeMode(QtWidgets.QHeaderView.ResizeToContents)

    def setup_horizontal_header(self):
        horizontal_header = self.horizontalHeader()
        horizontal_header.setSectionResizeMode(0, QtWidgets.QHeaderView.Stretch)
        horizontal_header.setSectionResizeMode(1, QtWidgets.QHeaderView.Stretch)
        horizontal_header.setSectionResizeMode(2, QtWidgets.QHeaderView.ResizeToContents)
        horizontal_header.setSectionResizeMode(3, QtWidgets.QHeaderView.ResizeToContents)
