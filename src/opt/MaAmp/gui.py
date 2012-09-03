# -*- coding: utf-8 -*-
from PyQt4 import QtCore, QtGui,QtNetwork
### Can be used on KDE (Tested on openSUSE 11.3). Looks bad, but works... :)
try:
	from PyQt4.phonon import Phonon
except:
	from PyKDE4.phonon import Phonon
try:
	from PyQt4.QtMaemo5 import QMaemo5InformationBox
except:
	pass

from ui.mainwindow import Ui_MainWindow
from ui.listwindow import Ui_ListWindow
from ui.extended_gui import pushLabel
from ui.configure import Ui_Config
from ui.about import Ui_AboutDialog
from lib.ampache import ampache

import os
import dbus

ANIMSPEED = 350
ONLINE = False

class MainWin(QtGui.QMainWindow):
	def __init__(self, parent=None):
		QtGui.QWidget.__init__(self, parent)
		self.ui = Ui_MainWindow()
		self.ui.setupUi(self)
		self.ui.lcdcurrent.display("00:00")
		self.ui.lcdtotal.display("00:00")

		self.PORT = False
		self.SHOW = False
		self.songs = []
		self.chosen = 0

		###### WINDOW SETTINGS ######
		try:
			self.setAttribute(QtCore.Qt.WA_Maemo5StackedWindow, True)
			self.setAttribute(QtCore.Qt.WA_Maemo5AutoOrientation, True);
		except:
			pass
		self.setWindowTitle("MaAmp - Offline") # Should show artist name here

		self.connect(QtGui.QApplication.desktop(), QtCore.SIGNAL("resized(int)"), self.orientationChanged );

		### SETUP CUSTOM LABEL, PUSHLABEL ###
		self.ui.cover_art = pushLabel(self)
		self.ui.cover_art.setGeometry(QtCore.QRect(20, 35, 280, 280))
		self.ui.cover_art.setScaledContents(True)
		#self.ui.cover_art.setPixmap(QtGui.QPixmap(current[3]))
		self.ui.cover_art.setPixmap(QtGui.QPixmap(os.path.dirname(os.path.realpath( __file__ ) )+"/empty.png"))
		self.connect(self.ui.cover_art, QtCore.SIGNAL("clicked()"),self.animate)

		### INIT THINGS ###
		self.getconnected()
		self.disablebuttons()

		### ACTIONBUTTONS (MENU) ###
		self.connect(self.ui.actionConfigure, QtCore.SIGNAL("triggered()"),self.configure)
		self.connect(self.ui.actionAbout, QtCore.SIGNAL("triggered()"),self.about)
		self.connect(self.ui.actionFM_Radio, QtCore.SIGNAL('triggered()'), self.fmradio)
		self.connect(self.ui.actionClearRefresh, QtCore.SIGNAL('triggered()'), self.clearrefresh)

		### BUTTONS ###
		self.connect(self.ui.artistsButton, QtCore.SIGNAL("clicked()"),self.listartists)
		#self.connect(self.ui.albumsButton, QtCore.SIGNAL("clicked()"),self.listalbums)

		### PLAYER BUTTONS ###
		self.connect(self.ui.playButton, QtCore.SIGNAL("clicked()"),self.play)
		self.connect(self.ui.stopButton, QtCore.SIGNAL("clicked()"),self.stop)
		self.connect(self.ui.nextButton, QtCore.SIGNAL("clicked()"),self.next)
		self.connect(self.ui.previousButton, QtCore.SIGNAL("clicked()"),self.prev)
		self.connect(self.ui.listWidget, QtCore.SIGNAL("itemClicked(QListWidgetItem*)"), self.itemClicked)

		### INIT ALL ANIMATIONS ###
		self.f_animate = QtCore.QPropertyAnimation(self.ui.frame, "geometry")
		self.f_animate.setDuration(ANIMSPEED)
		self.f2_animate = QtCore.QPropertyAnimation(self.ui.frame_2, "geometry")
		self.f2_animate.setDuration(ANIMSPEED)
		self.l_animate = QtCore.QPropertyAnimation(self.ui.listWidget, "geometry")
		self.l_animate.setDuration(ANIMSPEED)

		### ANIMATION GEOMETRY ###
		### PORTRAIT ###
		self.fp_visible = QtCore.QRect(35, 655, 411, 91)
		self.fp_invisible = QtCore.QRect (35, 810, 411, 91)
		self.f2p_visible = QtCore.QRect (0, 330, 480, 311)
		self.f2p_invisible = QtCore.QRect (490, 330, 480, 311)
		self.lp_visible = QtCore.QRect (0, 330, 480, 430)
		self.lp_invisible = QtCore.QRect (490, 330, 480, 430)
		### LANDSCAPE ###
		self.fl_visible = QtCore.QRect (360, 330, 411, 91)
		self.fl_invisible = QtCore.QRect (360, 490, 411, 91)
		self.f2l_visible = QtCore.QRect (320, 5, 480, 311)
		self.f2l_invisible = QtCore.QRect (810, 5, 480, 311)
		self.ll_visible = QtCore.QRect (320, 0, 480, 430)
		self.ll_invisible = QtCore.QRect (810, 0, 480, 430)
		
		### SETUP & INIT PHONON SOUND ###
		self.mediaObject = Phonon.createPlayer(Phonon.MusicCategory)
		self.audioOutput = Phonon.AudioOutput(Phonon.MusicCategory)
		#print self.audioOutput.outputDevice().name()

		self.mediaObject.setTickInterval(1000)
		self.mediaObject.tick.connect(self.tick)
		self.mediaObject.stateChanged.connect(self.stateChanged)
		self.mediaObject.currentSourceChanged.connect(self.sourceChanged)
		self.mediaObject.aboutToFinish.connect(self.aboutToFinish)
		self.mediaObject.finished.connect(self.finished)

		### CREATE AND CONNCT SEEKSLIDER TO PHONON ###
		self.ui.seekSlider = Phonon.SeekSlider(self.mediaObject,self.ui.frame_2)
		self.ui.seekSlider.setGeometry(QtCore.QRect(10, 245, 268, 61))
		self.ui.seekSlider.setOrientation(QtCore.Qt.Horizontal)
		self.ui.seekSlider.setObjectName("seekSlider")
		
		### JUST TO UPDATE SCREEN... HMMM.... ###
		self.animate()
		
	### STILL PHONON ###
	def play(self):
		QtGui.QApplication.processEvents()
		playing = (self.mediaObject.state() == Phonon.PlayingState)
		if not playing:
			self.ui.lcdtotal.display(self.current_song[4])
			self.mediaObject.play()
		else:
			self.mediaObject.pause()
		try:
			self.setAttribute(QtCore.Qt.WA_Maemo5ShowProgressIndicator, False);
		except:
			pass
		
	def stop(self):
		self.ui.playButton.setText("Play")
		self.mediaObject.stop()

	def prev(self):
		QtGui.QApplication.processEvents()
		try:
			self.setAttribute(QtCore.Qt.WA_Maemo5ShowProgressIndicator, True);
		except:
			pass
		self.chosen = self.chosen - 1
		if self.chosen < 0:
			self.chosen = len(self.songs)-1
		self.ui.listWidget.setCurrentRow(self.chosen)
		self.url = self.amp.getSongurl(self.songs[self.chosen][6]) 
		self.current_song = self.songs[self.chosen] 
		self.ui.songLabel.setText(self.songs[self.chosen][1])
		self.ui.songsLabel.setText("Songs: "+str(self.current_song[0])+"/"+str(len(self.songs)))
		self.ui.artistLabel.setText(self.songs[self.chosen][2])
		self.ui.albumLabel.setText(self.songs[self.chosen][3])
		self.mediaObject.setCurrentSource(Phonon.MediaSource(self.url))
		self.ui.seekSlider.setMediaObject(self.mediaObject)
		self.play()

	def next(self):
		QtGui.QApplication.processEvents()
		try:
			self.setAttribute(QtCore.Qt.WA_Maemo5ShowProgressIndicator, True);
		except:
			pass
		self.chosen = self.chosen + 1
		if self.chosen > len(self.songs):
			self.chosen = 0
		self.ui.listWidget.setCurrentRow(self.chosen)
		self.url = self.amp.getSongurl(self.songs[self.chosen][6]) 
		self.current_song = self.songs[self.chosen] 
		self.ui.songLabel.setText(self.songs[self.chosen][1])
		self.ui.songsLabel.setText("Songs: "+str(self.current_song[0])+"/"+str(len(self.songs)))
		self.ui.artistLabel.setText(self.songs[self.chosen][2])
		self.ui.albumLabel.setText(self.songs[self.chosen][3])
		self.mediaObject.setCurrentSource(Phonon.MediaSource(self.url))
		self.ui.seekSlider.setMediaObject(self.mediaObject)
		self.play()

	def stateChanged(self, newState, oldState):
		if newState == Phonon.ErrorState:
			if self.mediaObject.errorType() == Phonon.FatalError:
				QtGui.QMessageBox.warning(self, "Fatal Error",
						self.mediaObject.errorString())
			else:
				QtGui.QMessageBox.warning(self, "Error",
						self.mediaObject.errorString())

		elif newState == Phonon.PlayingState:
			self.ui.playButton.setText("Pause")

		elif newState == Phonon.StoppedState:
			self.ui.lcdcurrent.display("00:00")

		elif newState == Phonon.PausedState:
			self.ui.playButton.setText("Play")

	def tick(self, time):
		displayTime = QtCore.QTime(0, (time / 60000) % 60, (time / 1000) % 60)
		self.ui.lcdcurrent.display(displayTime.toString('mm:ss'))

	def sourceChanged(self, source):
		pass

	def aboutToFinish(self):
		### SO WE DONT HAVE TO WAIT FOR AMPACHEE-AUTH WHEN PLAYING NEXT ###
		if not self.amp.is_authenticated():
			self.amp.authenticate()

	def finished(self):
		self.next()
	### PHONON FINISHED ###

	### ENABLE BUTTONS (IF ALBUM IS LOADED) ###
	def enablebuttons(self):
		self.ui.cover_art.setEnabled(True)
		self.ui.playButton.setEnabled(True)
		self.ui.stopButton.setEnabled(True)
		self.ui.nextButton.setEnabled(True)
		self.ui.previousButton.setEnabled(True)

	### DISABLE BUTTONS (IF NO ALBUM IS LOADED)
	def disablebuttons(self):
		self.ui.cover_art.setEnabled(False)
		self.ui.playButton.setEnabled(False)
		self.ui.stopButton.setEnabled(False)
		self.ui.nextButton.setEnabled(False)
		self.ui.previousButton.setEnabled(False)

	### TRY TO CONNECT TO AMPACHE ###
	def getconnected(self):
		### GET AMACHE CONFIGURATION AND STUFF ###
		self.amp = ampache()
		self.config = self.amp.getconfig()
		if not self.config[0] == "http://":
			if self.amp.authenticate():
				self.ui.actionConnect.setText(QtGui.QApplication.translate("MainWindow", "Connected", None, QtGui.QApplication.UnicodeUTF8))
				self.ui.actionClearRefresh.setEnabled(True)
				self.ui.actionFM_Radio.setEnabled(True)
				self.ui.actionConnect.setChecked(True)
				self.artists = self.amp.getArtists()
				self.setWindowTitle("MaAmp - Online")
				ONLINE = True
				self.ui.frame.setEnabled(True)
				try:
					QMaemo5InformationBox.information(None, "Connected ... :)", 5000)
				except:
					pass
			else:
				self.setWindowTitle("MaAmp - Offline") 
				self.ui.frame.setEnabled(False)
				self.ui.cover_art.setEnabled(False)
				self.ui.actionConnect.setText(QtGui.QApplication.translate("MainWindow", "Connect", None, QtGui.QApplication.UnicodeUTF8))
				self.ui.actionClearRefresh.setEnabled(False)
				self.ui.actionFM_Radio.setEnabled(False)
				self.ui.actionConnect.setChecked(False)
				ONLINE = False
		else:
			self.setWindowTitle("MaAmp - Offline") 
			self.ui.frame.setEnabled(False)
			self.ui.cover_art.setEnabled(False)
			self.ui.actionConnect.setText(QtGui.QApplication.translate("MainWindow", "Connect", None, QtGui.QApplication.UnicodeUTF8))
			self.ui.actionClearRefresh.setEnabled(False)
			self.ui.actionFM_Radio.setEnabled(False)
			self.ui.actionConnect.setChecked(False)
			ONLINE = False
			#try:
			QMaemo5InformationBox.information(None, "You need to configure MaAmp!", 5000)
			#except:
			#	pass
			

	def about(self):
		ad = AboutDialog(self)
		if self.PORT:
			ad.resize(480, 650)
		else:
			ad.resize(800, 400)
		ad.show()

	def configure(self):
		cd = ConfigDialog(self)
		### SETUP UI ###
		if self.PORT:
			cd.resize(480, 267)
		else:
			cd.resize(800, 267)
		self.cdui = Ui_Config()
		self.cdui.setupUi(cd)
		self.cdui.serverEdit.setText(self.config[0])
		self.cdui.userEdit.setText(self.config[1])
		self.cdui.passwordEdit.setText(self.config[2])
		self.cdui.autoLoginCheck.setChecked(self.config[3])
		cd.show()
		if cd.exec_() == 1:
			self.config = [self.cdui.serverEdit.text(),self.cdui.userEdit.text(),self.cdui.passwordEdit.text(),self.cdui.autoLoginCheck.isChecked()]
			cd.destroy()
			self.amp.setconfig(self.config)
			if self.config[3] == True:
				self.getconnected()

	def itemClicked(self,item):
		QtGui.QApplication.processEvents()
		try:
			self.setAttribute(QtCore.Qt.WA_Maemo5ShowProgressIndicator, True);
		except:
			pass
		self.animate()
		if self.ui.listWidget.row(item) < 0:
			self.chosen = 1
		else:
			self.chosen = self.ui.listWidget.row(item)
		self.url = self.amp.getSongurl(self.songs[self.chosen][6]) 
		self.current_song = self.songs[self.chosen] 
		self.ui.songLabel.setText(self.songs[self.chosen][1])
		self.ui.songsLabel.setText("Songs: "+str(self.current_song[0])+"/"+str(len(self.songs)))
		self.ui.artistLabel.setText(self.songs[self.chosen][2])
		self.ui.albumLabel.setText(self.songs[self.chosen][3])
		self.ui.lcdtotal.display(self.current_song[4])
		self.mediaObject.setCurrentSource(Phonon.MediaSource(self.url))
		self.ui.seekSlider.setMediaObject(self.mediaObject)
		self.ui.seekSlider.setEnabled(True)
		self.play()
		self.ui.playButton.setText("Pause")

	def clearrefresh(self):
		result = self.amp.clearCache()
		self.artists = result

	def orientationChanged ( self ): #called when N900 is rotated
		screenGeometry=QtGui.QApplication.desktop().screenGeometry();
		if screenGeometry.width() > screenGeometry.height(): #landscape
			if self.SHOW: # SHOW FRAMES, HIDE LISTWIDGET
				self.ui.frame.setGeometry(self.fl_visible)
				self.ui.frame_2.setGeometry(self.f2l_visible)
				self.ui.listWidget.setGeometry(self.ll_invisible)
			else: # SHOW LISTWIDGET, HIDE FRAMES
				self.ui.frame.setGeometry(self.fl_invisible)
				self.ui.frame_2.setGeometry(self.f2l_invisible)
				self.ui.listWidget.setGeometry(self.ll_visible)
			self.ui.artistsButton.setGeometry(QtCore.QRect(10, 340, 141, 71))
			self.ui.playlistButton.setGeometry(QtCore.QRect(160, 340, 141, 71))
			self.PORT = False
		else: #portrait
			if self.SHOW: # SHOW FRAMES, HIDE LISTWIDGET
				self.ui.frame.setGeometry(self.fp_visible)
				self.ui.frame_2.setGeometry(self.f2p_visible)
				self.ui.listWidget.setGeometry(self.lp_invisible)
			else: # SHOW LISTWIDGET, HIDE FRAMES
				self.ui.frame.setGeometry(self.fp_invisible)
				self.ui.frame_2.setGeometry(self.f2p_invisible)
				self.ui.listWidget.setGeometry(self.lp_visible)
			self.ui.artistsButton.setGeometry(QtCore.QRect(330, 140, 141, 71))
			self.ui.playlistButton.setGeometry(QtCore.QRect(330, 220, 141, 71))
			self.PORT = True
	
	def animate(self):
		if self.PORT: 
			if self.SHOW: # SHOW LISTWIDGET, HIDE FRAMES
				self.f_animate.setStartValue(self.fp_visible)
				self.f_animate.setEndValue(self.fp_invisible)
				self.f2_animate.setStartValue(self.f2p_visible)
				self.f2_animate.setEndValue(self.f2p_invisible)
				self.l_animate.setStartValue(self.lp_invisible)
				self.l_animate.setEndValue(self.lp_visible)
				self.SHOW = False
			else: # SHOW FRAMES HIDE LISTWIDGET
				self.f_animate.setStartValue(self.fp_invisible)
				self.f_animate.setEndValue(self.fp_visible)
				self.f2_animate.setStartValue(self.f2p_invisible)
				self.f2_animate.setEndValue(self.f2p_visible)
				self.l_animate.setStartValue(self.lp_visible)
				self.l_animate.setEndValue(self.lp_invisible)
				self.SHOW = True
		else:
			if self.SHOW: # SHOW LISTWIDGET HIDE FRAMES
				self.f_animate.setStartValue(self.fl_visible)
				self.f_animate.setEndValue(self.fl_invisible)
				self.f2_animate.setStartValue(self.f2l_visible)
				self.f2_animate.setEndValue(self.f2l_invisible)
				self.l_animate.setStartValue(self.ll_invisible)
				self.l_animate.setEndValue(self.ll_visible)
				self.SHOW = False
			else: # SHOW FRAMES, HIDE LISTWIDGET
				self.f_animate.setStartValue(self.fl_invisible)
				self.f_animate.setEndValue(self.fl_visible)
				self.f2_animate.setStartValue(self.f2l_invisible)
				self.f2_animate.setEndValue(self.f2l_visible)
				self.l_animate.setStartValue(self.ll_visible)
				self.l_animate.setEndValue(self.ll_invisible)
				self.SHOW = True
		self.f_animate.start()
		self.f2_animate.start()
		self.l_animate.start()
			
	def connected(self):
		if self.ONLINE:
			self.ui.actionConnect.setText(QtGui.QApplication.translate("MainWindow", "Connected", None, QtGui.QApplication.UnicodeUTF8))
			self.getconnected()
			self.ONLINE = True
		else:
			self.ui.actionConnect.setText(QtGui.QApplication.translate("MainWindow", "Connect", None, QtGui.QApplication.UnicodeUTF8))
			self.disablebuttons()
			self.ONLINE = False
			
	# BORROWED FROM PYRADIO! #
	def fmradio(self, initial=False): #Turn on FM transmitter
		try : #test for FM transmitter.
			sysbus = dbus.SystemBus()
			fmtx = sysbus.get_object('com.nokia.FMTx', '/com/nokia/fmtx/default', False)
			fmtx_iface = dbus.Interface(fmtx, dbus_interface='org.freedesktop.DBus.Properties')

			state = fmtx_iface.Get("com.nokia.FMTx.Device", "state")
			if state == 'disabled':
				if not initial: 
					self.ui.actionFM_Radio.setText(QtGui.QApplication.translate("MainWindow", "Disable FM", None, QtGui.QApplication.UnicodeUTF8))
					fmtx_iface.Set("com.nokia.FMTx.Device", "state", dbus.String(u'%s' % 'enabled', variant_level=1))
				else:
					self.ui.actionFM_Radio.setText(QtGui.QApplication.translate("MainWindow", "Enable FM", None, QtGui.QApplication.UnicodeUTF8))
			else:
				if not initial: 
					self.ui.actionFM_Radio.setText(QtGui.QApplication.translate("MainWindow", "Enable FM", None, QtGui.QApplication.UnicodeUTF8))
					fmtx_iface.Set("com.nokia.FMTx.Device", "state", dbus.String(u'%s' % 'disabled', variant_level=1))
				else:
					self.ui.actionEnable_FM_Radio.setText(QtGui.QApplication.translate("MainWindow", "Disable FM", None, QtGui.QApplication.UnicodeUTF8))
		except: print "No FM Transmitter."
	###########################
	
	def listartists(self):
		if not self.amp.is_authenticated():
			self.getconnected()
		self.ArtistWin = ArtistWin(self)
		try:
			self.ArtistWin.setAttribute(QtCore.Qt.WA_Maemo5ShowProgressIndicator, True);
		except:
			pass
		self.ArtistWin.setWindowTitle("All Artists ("+str(len(self.artists))+")")
		self.ArtistWin.show()
		self.ArtistWin.artists(self.artists)

	def selectedAristAlbum(self,artist_id):
		album = self.amp.getAlbums(artist_id)
		self.selectedAlbum(album,0)

	def selectedAlbum(self,album,nr):
		QtGui.QApplication.processEvents()
		self.songs = self.amp.getSongs(album[nr][0])
		self.ui.cover_art.setPixmap(QtGui.QPixmap(album[nr][3]))
		self.ui.songLabel.setText(self.songs[0][1])
		self.ui.artistLabel.setText(self.songs[0][2])
		self.ui.albumLabel.setText(self.songs[0][3])
		self.ui.yearLabel.setText("Year: "+album[nr][6])
		self.ui.songsLabel.setText("Songs: 1/"+str(album[nr][2]))
		self.ui.tagsLabel.setText(album[nr][7])
		self.ui.listWidget.clear()
		for row in self.songs:
			self.ui.listWidget.addItem(row[1])
		self.url = self.amp.getSongurl(self.songs[0][6]) 
		self.current_song = self.songs[0] 
		self.ui.lcdtotal.display(self.current_song[4])
		wasPlaying = (self.mediaObject.state() == Phonon.PlayingState)
		if wasPlaying:
			self.stop()
		self.mediaObject.setCurrentSource(Phonon.MediaSource(self.url))
		self.ui.seekSlider.setMediaObject(self.mediaObject)
		self.enablebuttons()
		self.SHOW = True
		self.animate()
		try:
			self.setAttribute(QtCore.Qt.WA_Maemo5ShowProgressIndicator, False);
		except:
			pass

### LIST ALL ALBUMS WINDOW ###
class ArtistWin(QtGui.QMainWindow):
	def __init__(self, parent=None):
		QtGui.QWidget.__init__(self, parent)
		### SETUP UI ###
		self.ui = Ui_ListWindow()
		self.ui.setupUi(self)
		### MAEMO ###
		try:
			self.setAttribute(QtCore.Qt.WA_Maemo5StackedWindow, True)
			self.setAttribute(QtCore.Qt.WA_Maemo5AutoOrientation, True);

			#self.setAttribute(QtCore.Qt.WA_Maemo5AutoOrientation, True)
		except:
			pass
		### ACTION FOR CLICKING LISTWIDGETITEM ###
		self.connect(self.ui.listWidget, QtCore.SIGNAL("itemClicked(QListWidgetItem*)"), self.awclicked)
		self.parent = parent

	### POPULATE LISTWIDGET WITH ARTISTS ###
	def artists(self,artists):
		QtGui.QApplication.processEvents()
		self.artists = artists
		for row in artists:
			self.ui.listWidget.addItem(row[1]+" ("+row[2]+")")
		try:
			self.setAttribute(QtCore.Qt.WA_Maemo5ShowProgressIndicator, False);
		except:
			pass

	### RETURN CHOSEN ARTIST ID ###
	def awclicked(self,item):
		#self.setAttribute(QtCore.Qt.WA_Maemo5ShowProgressIndicator, True);
		if self.artists[self.ui.listWidget.row(item)][2] == "1":
			try:
				self.parent.setAttribute(QtCore.Qt.WA_Maemo5ShowProgressIndicator, True);
			except:
				pass
			self.close()
			self.parent.selectedAristAlbum(self.artists[self.ui.listWidget.row(item)][0])
		else:
			aaw = ArtistAlbumWin(self)
			aaw.setWindowTitle(self.artists[self.ui.listWidget.row(item)][1])
			aaw.show()
			try:
				aaw.setAttribute(QtCore.Qt.WA_Maemo5ShowProgressIndicator, True);
			except:
				pass
			aaw.albums(self.artists[self.ui.listWidget.row(item)][0],self.parent)
		
### LIST ALL ALBUMS OF CHOOSEN ARTIST WINDOW ###
class ArtistAlbumWin(QtGui.QMainWindow):
	def __init__(self, parent=None):
		QtGui.QWidget.__init__(self, parent)
		### SETUP UI ###
		self.ui = Ui_ListWindow()
		self.ui.setupUi(self)
		self.ui.listWidget.setViewMode(QtGui.QListView.IconMode)
		self.ui.listWidget.setIconSize(QtCore.QSize(200,200))
		self.ui.listWidget.setGridSize(QtCore.QSize(210,210))
		self.ui.listWidget.setSpacing(5)
		self.ui.listWidget.setSelectionMode(QtGui.QAbstractItemView.NoSelection)
		self.parent = parent
		### MAEMO ###
		try:
			self.setAttribute(QtCore.Qt.WA_Maemo5StackedWindow, True)
			self.setAttribute(QtCore.Qt.WA_Maemo5AutoOrientation, True);
		except:
			pass
		self.connect(self.ui.listWidget, QtCore.SIGNAL("itemClicked(QListWidgetItem*)"), self.clicked)

	### POPULATE LISTWIDGET WITH ARTIST'S ALBUMS ###
	def albums(self,artist,mw):
		QtGui.QApplication.processEvents()
		self.mw = mw
		self.albums = self.mw.amp.getAlbums(artist)
		for row in self.albums:
			self.pixmap = QtGui.QPixmap(row[3])
			self.pixmap = self.pixmap.scaled(150,150, QtCore.Qt.IgnoreAspectRatio, QtCore.Qt.SmoothTransformation)
			self.icon = QtGui.QIcon()
			self.icon.addPixmap(self.pixmap, QtGui.QIcon.Normal, QtGui.QIcon.On)
			self.item = QtGui.QListWidgetItem(self.ui.listWidget)
			self.item.setIcon(self.icon)
			self.item.setText(row[1])
			
		try:
			self.setAttribute(QtCore.Qt.WA_Maemo5ShowProgressIndicator, False);
		except:
			pass
		
	### RETURN CHOSEN ALBUM ###
	def clicked(self,item):
		self.close()
		self.parent.close()
		try:
			self.mw.setAttribute(QtCore.Qt.WA_Maemo5ShowProgressIndicator, True);
		except:
			pass
		self.mw.selectedAlbum(self.albums,self.ui.listWidget.row(item))

class ConfigDialog(QtGui.QDialog):
	def __init__(self, parent=None):
		QtGui.QDialog.__init__(self, parent)
	### MANAGE CHOICES ###		
	def rejected(self):
		self.close()
	def accepted(self):
		self.close()

class AboutDialog(QtGui.QDialog):
	def __init__(self, parent=None):
		QtGui.QDialog.__init__(self, parent)
		self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
		self.ui = Ui_AboutDialog()
		self.ui.setupUi(self)
