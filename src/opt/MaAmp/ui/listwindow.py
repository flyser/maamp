# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui/listwindow.ui'
#
# Created by: PyQt4 UI code generator 4.8
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_ListWindow(object):
    def setupUi(self, ListWindow):
        ListWindow.setObjectName(_fromUtf8("ListWindow"))
        ListWindow.setWindowModality(QtCore.Qt.NonModal)
        ListWindow.resize(800, 480)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(ListWindow.sizePolicy().hasHeightForWidth())
        ListWindow.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setPointSize(22)
        ListWindow.setFont(font)
        self.centralwidget = QtGui.QWidget(ListWindow)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.centralwidget.sizePolicy().hasHeightForWidth())
        self.centralwidget.setSizePolicy(sizePolicy)
        self.centralwidget.setObjectName(_fromUtf8("centralwidget"))
        self.gridLayout = QtGui.QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.listWidget = QtGui.QListWidget(self.centralwidget)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.MinimumExpanding, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.listWidget.sizePolicy().hasHeightForWidth())
        self.listWidget.setSizePolicy(sizePolicy)
        self.listWidget.setFrameShape(QtGui.QFrame.NoFrame)
        self.listWidget.setFrameShadow(QtGui.QFrame.Plain)
        self.listWidget.setLineWidth(0)
        self.listWidget.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.listWidget.setProperty(_fromUtf8("showDropIndicator"), False)
        self.listWidget.setResizeMode(QtGui.QListView.Adjust)
        self.listWidget.setSelectionRectVisible(True)
        self.listWidget.setObjectName(_fromUtf8("listWidget"))
        self.gridLayout.addWidget(self.listWidget, 0, 0, 1, 1)
        ListWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtGui.QMenuBar(ListWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 800, 40))
        self.menubar.setObjectName(_fromUtf8("menubar"))
        ListWindow.setMenuBar(self.menubar)

        self.retranslateUi(ListWindow)
        QtCore.QMetaObject.connectSlotsByName(ListWindow)

    def retranslateUi(self, ListWindow):
        ListWindow.setWindowTitle(QtGui.QApplication.translate("ListWindow", "LIstWindow", None, QtGui.QApplication.UnicodeUTF8))


if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    ListWindow = QtGui.QMainWindow()
    ui = Ui_ListWindow()
    ui.setupUi(ListWindow)
    ListWindow.show()
    sys.exit(app.exec_())

