# -*- coding: utf-8 -*-
import sys
import hashlib
import time
import urllib
import urllib2
import xml.dom.minidom
import pickle
import os
import datetime
import time
try:
	from PyQt4.QtMaemo5 import QMaemo5InformationBox
except:
	pass

MAX = 3 ### RETRYING NO. TIMES ###

class ampache():
	def __init__(self):
		self.auth_current_retry = 0
		self.last_update = 0

	def __human_readable_filesize(self, bytes):
		"""Converts bytes to humand_readable form."""
		if bytes >= 1073741824:
			return str(round(bytes / 1024 / 1024 / 1024, 1)) + ' GB'
		elif bytes >= 1048576:
			return str(round(bytes / 1024 / 1024, 1)) + ' MB'
		elif bytes >= 1024:
			return str(round(bytes / 1024, 1)) + ' KB'
		elif bytes < 1024:
			return str(bytes) + ' bytes'

	def setconfig(self,config):
		if not os.path.exists("~/MyDocs/.MaAMP"):
			os.system('mkdir -p ~/MyDocs/.MaAMP')
		fh = open(os.path.expanduser('~/MyDocs/.MaAMP/save'), 'w')
		pickle.dump(config,fh)
		fh.close()
		self.configuration=config

	def getconfig(self):
		try:
			fh = open(os.path.expanduser('~/MyDocs/.MaAMP/save'), 'r')
			self.configuration = pickle.load(fh)
			fh.close()
		except:
			self.configuration = ["http://","","",True]
			#print "Error: get config"
		return self.configuration

	def authenticate(self):
		self.xml_rpc = str(self.configuration[0])+"/server/xml.server.php"
		timestamp = int(time.time())
		password = hashlib.sha256(str(self.configuration[2])).hexdigest()
		authkey = hashlib.sha256(str(timestamp) + password).hexdigest()
		values = {'action'    : 'handshake',
				'auth'      : authkey,
				'timestamp' : timestamp,
				'user'      : str(self.configuration[1]),
				'version'   : '350001',
		}
		data = urllib.urlencode(values)
		try:
			response = urllib2.urlopen(self.xml_rpc + "?" + data)
			dom = xml.dom.minidom.parseString(response.read())
			self.auth = dom.getElementsByTagName("auth")[0].childNodes[0].data
			self.artists_num = int(dom.getElementsByTagName("artists")[0].childNodes[0].data)
		except: # couldn't auth, try up to AUTH_MAX_RETRY times
			self.auth = None
			self.auth_current_retry += 1
			### ERROR AUTH... RETRYING MAX TIMES ###
			if ( self.auth_current_retry < MAX ):
				time.sleep(1)
				self.authenticate()
			else:
				self.auth_current_retry = 0
				try:
					QMaemo5InformationBox.information(None, "Unable to authenticate!?!", 0)
				except:
					pass
				### FAILED MAX TIMES, REPORT ERROR (SIGNAL?!)
			return False
		self.new_last_update_time = 0
		try: 
			# check to see if ampache has been updated or cleaned since the last time this ran
			update = dom.getElementsByTagName("update")[0].childNodes[0].data
			add    = dom.getElementsByTagName("add")[0].childNodes[0].data
			clean  = dom.getElementsByTagName("clean")[0].childNodes[0].data
			# convert ISO 8601 to epoch
			update = int(time.mktime(time.strptime( update[:-6], "%Y-%m-%dT%H:%M:%S" )))
			add    = int(time.mktime(time.strptime( add[:-6], "%Y-%m-%dT%H:%M:%S" )))
			clean  = int(time.mktime(time.strptime( clean[:-6], "%Y-%m-%dT%H:%M:%S" )))
			new_time  = max([update, add, clean])
			self.new_last_update_time = new_time
		except:
			try:
				QMaemo5InformationBox.information(None, "Something is wrong with update time!?!", 0)
			except:
				pass
			#print "Couldn't get time catalog was updated -- assuming catalog is dirty"
		self.auth_current_retry = 0
		return True

	def is_authenticated(self):
		try:
			if self.auth != None:
				return True
			else:
				return False
		except:
			return False

	### GET LIST OF ARTISTS FROM SERVER ###
	def fetchArtists(self):
		values = {'action' : 'artists',
			'auth'   : self.auth,
		}
		data = urllib.urlencode(values)
		try: 
			response = urllib2.urlopen(self.xml_rpc + "?" + data)
			dom = xml.dom.minidom.parseString(response.read())
		except: # The data pulled from Ampache was invalid
			try:
				QMaemo5InformationBox.information(None, "Unable to get artist-data --- Check Ampache!", 0)
			except:
				pass
			return False
		try: # try to get the list of artists
			root  = dom.getElementsByTagName('root')[0]
			nodes = root.getElementsByTagName('artist')
		except:
			if self.authenticate():
				self.fetchArtists()
			else: # couldn't authenticate
				return False
			nodes = ""
		return nodes

	### MANAGE & CACHE ARTIST (GET FROM SERVER IS NECCESARY) ###
	def getArtists(self):
		artists = []
		try:
			fh = open(os.path.expanduser('~/MyDocs/.MaAMP/artists'), 'r')
			artists = pickle.load(fh)
			fh.close()
		except:
			artists = []
			temp = self.fetchArtists()
			for child in temp:
				artist_id    = int(child.getAttribute('id'))
				artist_name  = child.getElementsByTagName('name')[0].childNodes[0].data
				albums = child.getElementsByTagName('albums')[0].childNodes[0].data
				l = [artist_id,artist_name,albums]
				artists.append(l)
			fh = open(os.path.expanduser('~/MyDocs/.MaAMP/artists'), 'w')
			pickle.dump(artists,fh)
			fh.close()
		return artists

	### GET LIST OF ALBUMS AND EVENTUALLY DL COVER FROM ARTIST ID ### ERROR IN THIS FUNCTION ::: :(
	def getAlbums(self,artist_id):
		if not os.path.exists("~/MyDocs/.MaAMP/albums"):
			os.system("mkdir -p ~/MyDocs/.MaAMP/albums")

		try:
			fh = open(os.path.expanduser("~/MyDocs/.MaAMP/albums/"+str(artist_id)+".dat"), 'r')
			lalbums = pickle.load(fh)
			fh.close()
			return lalbums
		except:
			values = {'action' : 'artist_albums',
				'filter' : artist_id,
				'auth'   : self.auth,
			}
			data = urllib.urlencode(values)
			try:
				response = urllib2.urlopen(self.xml_rpc + "?" + data)
				dom = xml.dom.minidom.parseString(response.read())
			except: # The data pulled from Ampache was invalid
				try:
					QMaemo5InformationBox.information(None, "Unable to get album-data --- Check Ampache!", 0)
				except:
					pass
				return False
			try: # try to get the list of artists
				root  = dom.getElementsByTagName('root')[0]
				nodes = root.getElementsByTagName('album')
				lalbums = []
				for child in nodes:
					album_id    = int(child.getAttribute('id'))
					album_name  = child.getElementsByTagName('name')[0].childNodes[0].data
					album_tracks = int(child.getElementsByTagName('tracks')[0].childNodes[0].data)
					album_cover = child.getElementsByTagName('art')[0].childNodes[0].data
					album_artist = child.getElementsByTagName('artist')[0].childNodes[0].data
					artist_id = artist_id
					album_year     = child.getElementsByTagName('year')[0].childNodes[0].data
					try:
						album_tags     = child.getElementsByTagName('tag')[0].childNodes[0].data
					except:
						album_tags = "No tag"
					if len(album_cover) > 3 and not os.path.exists("~/MyDocs/.MaAMP/albums/"+str(album_id)):
						art_file = os.path.expanduser('~/MyDocs/.MaAMP/albums/' + str(album_id))
						data = urllib2.urlopen(album_cover)
						f = open(art_file, 'w')
						f.write(data.read())
						f.close()
					album_cover = os.path.expanduser('~/MyDocs/.MaAMP/albums/'+str(album_id))

					l = [album_id,album_name,album_tracks,album_cover,album_artist,artist_id,album_year,album_tags]
					lalbums.append(l)
					fh = open(os.path.expanduser("~/MyDocs/.MaAMP/albums/"+str(artist_id)+".dat"), 'w')
					pickle.dump(lalbums,fh)
					fh.close()
				return lalbums
			except:
				if self.authenticate():
					self.getAlbums(artist_id)
				else: # couldn't authenticate
					return False

	def getSongs(self, album_id):
		values = {'action' : 'album_songs',
			'filter' : album_id,
			'auth'   : self.auth,
		}
		data = urllib.urlencode(values)
		try:
			response = urllib2.urlopen(self.xml_rpc + "?" + data)
			dom = xml.dom.minidom.parseString(response.read())
		except: # The data pulled from Ampache was invalid
			try:
				QMaemo5InformationBox.information(None, "Unable to get song-data --- Check Ampache!", 0)
			except:
				pass
			return False
		try:
			root  = dom.getElementsByTagName('root')[0]
			nodes = root.getElementsByTagName('song')
			songs = []
			count = 0
			for child in nodes:
				song_id     = int(child.getAttribute('id'))
				song_title  = child.getElementsByTagName('title')[0].childNodes[0].data
				song_track  = int(child.getElementsByTagName('track')[0].childNodes[0].data)
				song_time   = int(child.getElementsByTagName('time')[0].childNodes[0].data)
				song_size   = int(child.getElementsByTagName('size')[0].childNodes[0].data)
				artist_name = child.getElementsByTagName('artist')[0].childNodes[0].data
				album_name  = child.getElementsByTagName('album')[0].childNodes[0].data
				song_time = time.strftime('%H:%M:%S', time.gmtime(song_time))
				if song_time[:2] == "00": # strip out hours if below 60 minutes
					song_time = song_time[3:]
				song_size = self.__human_readable_filesize(float(song_size))
				songs.append([song_track, song_title, artist_name, album_name, song_time, song_size, song_id])
			return songs
		except: # something failed, try to reauth and do it again
			if self.authenticate():
				self.getSongs(album_id)
			else: # couldn't authenticate
				return False

	def getSongurl(self, song_id):
		values = {'action' : 'song',
			'filter' : song_id,
			'auth'   : self.auth,
		}
		data = urllib.urlencode(values)
		try:
			response = urllib2.urlopen(self.xml_rpc + "?" + data)
			dom = xml.dom.minidom.parseString(response.read())
		except: # The data pulled from Ampache was invalid
			try:
				QMaemo5InformationBox.information(None, "Unable to get song-url --- Check Ampache!", 0)
			except:
				pass
			return False
		try:
			root     = dom.getElementsByTagName('root')[0]
			song     = root.getElementsByTagName('song')[0]
			song_url = song.getElementsByTagName('url')[0].childNodes[0].data
		except: # something failed, try to reauth and do it again
			if self.authenticate():
				self.getSongurl(song_id)
			else: # couldn't authenticate
				return False
		return song_url

	def clearCache(self):

		os.system("rm ~/MyDocs/.MaAMP/artists")
		os.system("rm -rf ~/MyDocs/.MaAMP/albums")
		artists = self.getArtists()
		current = ["","","",os.path.dirname( os.path.realpath( __file__ ) )+"/empty.png",""]
		return artists
		try:
			QMaemo5InformationBox.information(None, "Cache cleared!", 0)
		except:
			pass
