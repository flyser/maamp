# -*- coding: utf-8 -*-
#!/usr/bin/env python
from PyQt4 import QtCore, QtGui
from gui import MainWin

if __name__ == "__main__":
	print "import sys"
	import sys
	app = QtGui.QApplication(sys.argv)
	app.setApplicationName("MaAmp")
	gui = MainWin()
	gui.show()
	sys.exit(app.exec_())
