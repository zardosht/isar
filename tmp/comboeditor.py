import sys
from PyQt5.QtCore import Qt, QVariant, QModelIndex, QAbstractTableModel
from PyQt5.QtWidgets import QApplication, QTableView, QComboBox, QItemDelegate


class ComboDelegate(QItemDelegate):
    comboItems=['Combo_Zero', 'Combo_One','Combo_Two']

    def createEditor(self, parent, option, index):
        if index.row() == 1:
            combo = QComboBox(parent)
            combo.addItems(self.comboItems)
            # combo.setEditable(True)
            combo.currentIndexChanged.connect(self.current_index_changed)
            return combo
        else:
            return super().createEditor(parent, option, index)

    def setModelData(self, editor, model, index):
        if index.row() == 1:
            combo_index = editor.currentIndex()
            text = self.comboItems[combo_index]
            model.setData(index, text)
            print('\t\t\t ...setModelData() 1', text)
        else:
            super().setModelData(editor, model, index)

    def current_index_changed(self):
        self.commitData.emit(self.sender())


class MyModel(QAbstractTableModel):
    def __init__(self, parent=None, *args):
        QAbstractTableModel.__init__(self, parent, *args)
        self.items=['Data_Item01','Data_Item02','Data_Item03']

    def rowCount(self, parent=QModelIndex()):
        return len(self.items)

    def columnCount(self, parent=QModelIndex()):
        return 1

    def data(self, index, role):
        if not index.isValid(): return QVariant()

        row=index.row()
        item=self.items[row]

        if row>len(self.items): return QVariant()

        if role == Qt.DisplayRole:
            print(' << >> MyModel.data() returning ...', item)
            return QVariant(item)

    def flags(self, index):
        return Qt.ItemIsEditable | Qt.ItemIsEnabled

    def setData(self, index, text, kaka=True):
        self.items[index.row()] = text
        return True


if __name__ == '__main__':
    app = QApplication(sys.argv)

    model = MyModel()
    tableView = QTableView()
    tableView.setModel(model)

    delegate = ComboDelegate()

    tableView.setItemDelegate(delegate)
    tableView.resizeRowsToContents()

    tableView.show()
    sys.exit(app.exec_())