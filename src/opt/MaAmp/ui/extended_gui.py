# -*- coding: utf-8 -*-
from PyQt4 import QtCore, QtGui

class pushLabel(QtGui.QLabel):  
	def __init(self, parent=None):  
		QtGui.QLabel.__init__(self, parent)  
	
	def mouseReleaseEvent(self, ev):  
		self.emit(QtCore.SIGNAL('clicked()'))  
