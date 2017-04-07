################################################################################
#      Copyright (C) 2015 Surfacingx                                           #
#                                                                              #
#  This Program is free software; you can redistribute it and/or modify        #
#  it under the terms of the GNU General Public License as published by        #
#  the Free Software Foundation; either version 2, or (at your option)         #
#  any later version.                                                          #
#                                                                              #
#  This Program is distributed in the hope that it will be useful,             #
#  but WITHOUT ANY WARRANTY; without even the implied warranty of              #
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the                #
#  GNU General Public License for more details.                                #
#                                                                              #
#  You should have received a copy of the GNU General Public License           #
#  along with XBMC; see the file COPYING.  If not, write to                    #
#  the Free Software Foundation, 675 Mass Ave, Cambridge, MA 02139, USA.       #
#  http://www.gnu.org/copyleft/gpl.html                                        #
################################################################################

import xbmc, xbmcaddon, xbmcgui, xbmcplugin, os, sys, xbmcvfs, HTMLParser, glob, zipfile, json
import shutil
import errno
import string
import random
import urllib2,urllib
import re
import uservar
import time

from datetime import date, datetime, timedelta
try:    from sqlite3 import dbapi2 as database
except: from pysqlite2 import dbapi2 as database
from string import digits

ADDON_ID       = uservar.ADDON_ID
ADDONTITLE     = uservar.ADDONTITLE
ADDON          = xbmcaddon.Addon(ADDON_ID)
VERSION        = ADDON.getAddonInfo('version')
USER_AGENT     = 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.153 Safari/537.36 SE 2.X MetaSr 1.0'
DIALOG         = xbmcgui.Dialog()
DP             = xbmcgui.DialogProgress()
HOME           = xbmc.translatePath('special://home/')
XBMC           = xbmc.translatePath('special://xbmc/')
LOG            = xbmc.translatePath('special://logpath/')
PROFILE        = xbmc.translatePath('special://profile/')
SOURCE         = xbmc.translatePath('source://')
ADDONS         = os.path.join(HOME,      'addons')
USERDATA       = os.path.join(HOME,      'userdata')
PLUGIN         = os.path.join(ADDONS,    ADDON_ID)
PACKAGES       = os.path.join(ADDONS,    'packages')
ADDOND         = os.path.join(USERDATA,  'addon_data')
ADDONDATA      = os.path.join(USERDATA,  'addon_data', ADDON_ID)
ADVANCED       = os.path.join(USERDATA,  'advancedsettings.xml')
SOURCES        = os.path.join(USERDATA,  'sources.xml')
GUISETTINGS    = os.path.join(USERDATA,  'guisettings.xml')
FAVOURITES     = os.path.join(USERDATA,  'favourites.xml')
PROFILES       = os.path.join(USERDATA,  'profiles.xml')
THUMBS         = os.path.join(USERDATA,  'Thumbnails')
DATABASE       = os.path.join(USERDATA,  'Database')
FANART         = os.path.join(PLUGIN,    'fanart.jpg')
ICON           = os.path.join(PLUGIN,    'icon.png')
ART            = os.path.join(PLUGIN,    'resources', 'art')
WIZLOG         = os.path.join(ADDONDATA, 'wizard.log')
WHITELIST      = os.path.join(ADDONDATA, 'whitelist.txt')
QRCODES        = os.path.join(ADDONDATA, 'QRCodes')
SKIN           = xbmc.getSkinDir()
TODAY          = date.today()
TOMORROW       = TODAY + timedelta(days=1)
TWODAYS        = TODAY + timedelta(days=2)
THREEDAYS      = TODAY + timedelta(days=3)
ONEWEEK        = TODAY + timedelta(days=7)
MONTH          = TODAY + timedelta(days=30)
KODIV          = float(xbmc.getInfoLabel("System.BuildVersion")[:4])
EXCLUDES       = uservar.EXCLUDES

COLOR1         = uservar.COLOR1
COLOR2         = uservar.COLOR2
INCLUDEVIDEO   = ADDON.getSetting('includevideo')
INCLUDEALL     = ADDON.getSetting('includeall')
INCLUDEBOB     = ADDON.getSetting('includebob')
INCLUDEBOBP     = ADDON.getSetting('includebobp')
INCLUDEPHOENIX = ADDON.getSetting('includephoenix')
INCLUDESPECTO  = ADDON.getSetting('includespecto')
INCLUDESPECTOS  = ADDON.getSetting('includespectos')
INCLUDEGENESIS = ADDON.getSetting('includegenesis')
INCLUDEEXODUS  = ADDON.getSetting('includeexodus')
INCLUDEEXODUSP  = ADDON.getSetting('includeexodusp')
INCLUDEONECHAN = ADDON.getSetting('includeonechan')
INCLUDESALTS   = ADDON.getSetting('includesalts')
INCLUDESALTSHD = ADDON.getSetting('includesaltslite')
INCLUDEZEN		= ADDON.getSetting('includezen')
WIZDEBUGGING   = ADDON.getSetting('addon_debug')
DEBUGLEVEL     = ADDON.getSetting('debuglevel')
ENABLEWIZLOG   = ADDON.getSetting('wizardlog')
CLEANWIZLOG    = ADDON.getSetting('autocleanwiz')
CLEANWIZLOGBY  = ADDON.getSetting('wizlogcleanby')
CLEANDAYS      = ADDON.getSetting('wizlogcleandays')
CLEANSIZE      = ADDON.getSetting('wizlogcleansize')
CLEANLINES     = ADDON.getSetting('wizlogcleanlines')
LOGFILES       = ['log', 'xbmc.old.log', 'kodi.log', 'kodi.old.log', 'spmc.log', 'spmc.old.log', 'tvmc.log', 'tvmc.old.log']
DEFAULTPLUGINS = ['metadata.album.universal', 'metadata.artists.universal', 'metadata.common.fanart.tv', 'metadata.common.imdb.com', 'metadata.common.musicbrainz.org', 'metadata.themoviedb.org', 'metadata.tvdb.com', 'service.xbmc.versioncheck']
MAXWIZSIZE     = [100, 200, 300, 400, 500, 1000]
MAXWIZLINES    = [100, 200, 300, 400, 500]
MAXWIZDATES    = [1, 2, 3, 7, 30]


###########################
###### Settings Items #####
###########################

def getS(name):
	try: return ADDON.getSetting(name)
	except: return False

def setS(name, value):
	try: ADDON.setSetting(name, value)
	except: return False

def openS(name=""):
	ADDON.openSettings()



###########################
###### Display Items ######
###########################

ACTION_PREVIOUS_MENU 			=  10	## ESC action
ACTION_NAV_BACK 				=  92	## Backspace action
ACTION_MOVE_LEFT				=   1	## Left arrow key
ACTION_MOVE_RIGHT 				=   2	## Right arrow key
ACTION_MOVE_UP 					=   3	## Up arrow key
ACTION_MOVE_DOWN 				=   4	## Down arrow key
ACTION_MOUSE_WHEEL_UP 			= 104	## Mouse wheel up
ACTION_MOUSE_WHEEL_DOWN			= 105	## Mouse wheel down
ACTION_MOVE_MOUSE 				= 107	## Down arrow key
ACTION_SELECT_ITEM				=   7	## Number Pad Enter
ACTION_BACKSPACE				= 110	## ?
ACTION_MOUSE_LEFT_CLICK 		= 100
ACTION_MOUSE_LONG_CLICK 		= 108
def TextBox(title, msg):
	class TextBoxes(xbmcgui.WindowXMLDialog):
		def onInit(self):
			self.title      = 101
			self.msg        = 102
			self.scrollbar  = 103
			self.okbutton   = 201
			self.showdialog()

		def showdialog(self):
			self.getControl(self.title).setLabel(title)
			self.getControl(self.msg).setText(msg)
			self.setFocusId(self.scrollbar)
			
		def onClick(self, controlId):
			if (controlId == self.okbutton):
				self.close()
		
		def onAction(self, action):
			if   action == ACTION_PREVIOUS_MENU: self.close()
			elif action == ACTION_NAV_BACK: self.close()
			
	tb = TextBoxes( "Textbox.xml" , ADDON.getAddonInfo('path'), 'DefaultSkin', title=title, msg=msg)
	tb.doModal()
	del tb

def highlightText(msg):
	msg = msg.replace('\n', '[NL]')
	matches = re.compile("-->Python callback/script returned the following error<--(.+?)-->End of Python script error report<--").findall(msg)
	for item in matches:
		string = '-->Python callback/script returned the following error<--%s-->End of Python script error report<--' % item
		msg    = msg.replace(string, '[COLOR red]%s[/COLOR]' % string)
	msg = msg.replace('WARNING', '[COLOR yellow]WARNING[/COLOR]').replace('ERROR', '[COLOR red]ERROR[/COLOR]').replace('[NL]', '\n').replace(': EXCEPTION Thrown (PythonToCppException) :', '[COLOR red]: EXCEPTION Thrown (PythonToCppException) :[/COLOR]')
	msg = msg.replace('\\\\', '\\').replace(HOME, '')
	return msg

def LogNotify(title, message, times=2000, icon=ICON,sound=False):
	DIALOG.notification(title, message, icon, int(times), sound)
	#ebi('XBMC.Notification(%s, %s, %s, %s)' % (title, message, times, icon))

def percentage(part, whole):
	return 100 * float(part)/float(whole)



###########################
###### URL Checks #########
###########################
 
def workingURL(url):
	if url in ['http://', 'https://', '']: return False
	check = 0; status = ''
	while check < 3:
		check += 1
		try:
			req = urllib2.Request(url)
			req.add_header('User-Agent', USER_AGENT)
			response = urllib2.urlopen(req)
			response.close()
			status = True
			break
		except Exception, e:
			status = str(e)
			log("Working Url Error: %s [%s]" % (e, url))
			xbmc.sleep(500)
	return status
 
def openURL(url):
	req = urllib2.Request(url)
	req.add_header('User-Agent', USER_AGENT)
	response = urllib2.urlopen(req)
	link=response.read()
	response.close()
	return link

###########################
###### Misc Functions #####
###########################

def getKeyboard( default="", heading="", hidden=False ):
	keyboard = xbmc.Keyboard( default, heading, hidden )
	keyboard.doModal()
	if keyboard.isConfirmed():
		return unicode( keyboard.getText(), "utf-8" )
	return default

def getSize(path, total=0):
	for dirpath, dirnames, filenames in os.walk(path):
		for f in filenames:
			fp = os.path.join(dirpath, f)
			total += os.path.getsize(fp)
	return total

def convertSize(num, suffix='B'):
	for unit in ['', 'K', 'M', 'G']:
		if abs(num) < 1024.0:
			return "%3.02f %s%s" % (num, unit, suffix)
		num /= 1024.0
	return "%.02f %s%s" % (num, 'G', suffix)

def getCacheSize():

	dbfiles   = [
		(os.path.join(ADDOND, 'plugin.video.phstreams', 'cache.db')),
		(os.path.join(ADDOND, 'plugin.video.bob', 'cache.db')),
		(os.path.join(ADDOND, 'plugin.video.bobp', 'providers.db')),
		(os.path.join(ADDOND, 'plugin.video.specto', 'cache.db')),
		(os.path.join(ADDOND, 'plugin.video.specto', 'sources.db')),
		(os.path.join(ADDOND, 'plugin.video.genesis', 'cache.db')),
		(os.path.join(ADDOND, 'plugin.video.exodus', 'cache.db')),
		(os.path.join(ADDOND, 'plugin.video.exodus', 'providers.13.db')),
		(os.path.join(ADDOND, 'plugin.video.zen', 'cache.db')),
		(os.path.join(DATABASE,  'onechannelcache.db')),
		(os.path.join(DATABASE,  'saltscache.db')),
		(os.path.join(DATABASE,  'saltshd.lite.db'))]
	
	cachelist = [
		(ADDOND),
		(os.path.join(HOME,'cache')),
		(os.path.join(HOME,'temp')),
####(os.path.join(ADDOND,'script.module.simple.downloader')),
		(os.path.join(ADDOND,'script.module.simple.downloader')),]
		
	totalsize = 0

	for item in cachelist:
		if os.path.exists(item) and not item in [ADDOND]:
###if os.path.exists(item) and not item in [ADDONDATA,ADDOND, PROFILEADDONDATA]:
			totalsize = getSize(item,+ totalsize)
			
			
			
		else:
			for root, dirs, files in os.walk(item):
				for d in dirs:
					if 'cache' in d.lower() and not d.lower() == 'meta_cache': totalsize = getSize(os.path.join(root, d), totalsize)
	
	if INCLUDEVIDEO == 'true':
		files = []
		if INCLUDEALL == 'true': files = dbfiles
		else:
			if INCLUDEBOB == 'true':     files.append(os.path.join(ADDOND, 'plugin.video.bob', 'cache.db'))
			if INCLUDEBOBP == 'true':     files.append(os.path.join(ADDOND, 'plugin.video.bob', 'cache.db'))
			if INCLUDEPHOENIX == 'true': files.append(os.path.join(ADDOND, 'plugin.video.phstreams', 'cache.db'))
			if INCLUDESPECTO == 'true':  files.append(os.path.join(ADDOND, 'plugin.video.specto', 'cache.db'))
			if INCLUDESPECTOS == 'true':  files.append(os.path.join(ADDOND, 'plugin.video.specto', 'sources.db'))
			if INCLUDEGENESIS == 'true': files.append(os.path.join(ADDOND, 'plugin.video.genesis', 'cache.db'))
			if INCLUDEEXODUS == 'true':  files.append(os.path.join(ADDOND, 'plugin.video.exodus', 'cache.db'))
			if INCLUDEEXODUSP == 'true':  files.append(os.path.join(ADDOND, 'plugin.video.exodus', 'providers.13.db'))
			if INCLUDEZEN == 	'true':  files.append(os.path.join(ADDOND, 'plugin.video.zen', 'cache.db'))
			if INCLUDEONECHAN == 'true': files.append(os.path.join(DATABASE,  'onechannelcache.db'))
			if INCLUDESALTS == 'true':   files.append(os.path.join(DATABASE,  'saltscache.db'))
			if INCLUDESALTSHD == 'true': files.append(os.path.join(DATABASE,  'saltshd.lite.db'))
		if len(files) > 0:
			for item in files: totalsize = getSize(item, totalsize)
		else: log("Clear Cache: Clear Video Cache Not Enabled", xbmc.LOGNOTICE)
	return totalsize

def getInfo(label):
	try: return xbmc.getInfoLabel(label)
	except: return False

def removeFolder(path):
	log("Deleting Folder: %s" % path, xbmc.LOGNOTICE)
	try: shutil.rmtree(path,ignore_errors=True, onerror=None)
	except: return False

def removeFile(path):
	log("Deleting File: %s" % path, xbmc.LOGNOTICE)
	try:    os.remove(path)
	except: return False

def currSkin():
	return xbmc.getSkinDir()

def cleanHouse(folder, ignore=False):
	log(folder)
	total_files = 0; total_folds = 0
	for root, dirs, files in os.walk(folder):
		if ignore == False: dirs[:] = [d for d in dirs if d not in EXCLUDES]
		file_count = 0
		file_count += len(files)
		if file_count >= 0:
			for f in files:
				try: 
					os.unlink(os.path.join(root, f))
					total_files += 1
				except: 
					try:
						shutil.rmtree(os.path.join(root, f))
					except:
						log("Error Deleting %s" % f, xbmc.LOGERROR)
			for d in dirs:
				total_folds += 1
				try: 
					shutil.rmtree(os.path.join(root, d))
					total_folds += 1
				except: 
					log("Error Deleting %s" % d, xbmc.LOGERROR)
	return total_files, total_folds

def emptyfolder(folder):
	total = 0
	for root, dirs, files in os.walk(folder, topdown=True):
		dirs[:] = [d for d in dirs if d not in EXCLUDES]
		file_count = 0
		file_count += len(files) + len(dirs)
		if file_count == 0:
			shutil.rmtree(os.path.join(root))
			total += 1
			log("Empty Folder: %s" % root, xbmc.LOGNOTICE)
	return total

def log(msg, level=xbmc.LOGDEBUG):
	if not os.path.exists(ADDONDATA): os.makedirs(ADDONDATA)
	if not os.path.exists(WIZLOG): f = open(WIZLOG, 'w'); f.close()
	if WIZDEBUGGING == 'false': return False
	if DEBUGLEVEL == '0': return False
	if DEBUGLEVEL == '1' and not level in [xbmc.LOGNOTICE, xbmc.LOGERROR, xbmc.LOGSEVERE, xbmc.LOGFATAL]: return False
	if DEBUGLEVEL == '2': level = xbmc.LOGNOTICE
	try:
		if isinstance(msg, unicode):
			msg = '%s' % (msg.encode('utf-8'))
		xbmc.log('%s: %s' % (ADDONTITLE, msg), level)
	except Exception as e:
		try: xbmc.log('Logging Failure: %s' % (e), level)
		except: pass
	if ENABLEWIZLOG == 'true':
		lastcheck = getS('nextcleandate') if not getS('nextcleandate') == '' else str(TODAY)
		if CLEANWIZLOG == 'true' and lastcheck <= str(TODAY): checkLog()
		with open(WIZLOG, 'a') as f:
			line = "[%s %s] %s" % (datetime.now().date(), str(datetime.now().time())[:8], msg)
			f.write(line.rstrip('\r\n')+'\n')

def checkLog():
	nextclean = getS('nextcleandate')
	next = TOMORROW
	if CLEANWIZLOGBY == '0':
		keep = TODAY - timedelta(days=MAXWIZDATES[int(float(CLEANDAYS))])
		x    = 0
		f    = open(WIZLOG); a = f.read(); f.close(); lines = a.split('\n')
		for line in lines:
			if str(line[1:11]) >= str(keep):
				break
			x += 1
		newfile = lines[x:]
		writing = '\n'.join(newfile)
		f = open(WIZLOG, 'w'); f.write(writing); f.close()
	elif CLEANWIZLOGBY == '1':
		maxsize = MAXWIZSIZE[int(float(CLEANSIZE))]*1024
		f    = open(WIZLOG); a = f.read(); f.close(); lines = a.split('\n')
		if os.path.getsize(WIZLOG) >= maxsize:
			start = len(lines)/2
			newfile = lines[start:]
			writing = '\n'.join(newfile)
			f = open(WIZLOG, 'w'); f.write(writing); f.close()
	elif CLEANWIZLOGBY == '2':
		f      = open(WIZLOG); a = f.read(); f.close(); lines = a.split('\n')
		maxlines = MAXWIZLINES[int(float(CLEANLINES))]
		if len(lines) > maxlines:
			start = len(lines) - int(maxlines/2)
			newfile = lines[start:]
			writing = '\n'.join(newfile)
			f = open(WIZLOG, 'w'); f.write(writing); f.close()
	setS('nextcleandate', str(next))

def latestDB(DB):
	if DB in ['Addons', 'ADSP', 'Epg', 'MyMusic', 'MyVideos', 'Textures', 'TV', 'ViewModes']:
		match = glob.glob(os.path.join(DATABASE,'%s*.db' % DB))
		comp = '%s(.+?).db' % DB[1:]
		highest = 0
		for file in match :
			try: check = int(re.compile(comp).findall(file)[0])
			except: check = 0
			if highest < check :
				highest = check
		return '%s%s.db' % (DB, highest)
	else: return False

def addonId(add):
	try: 
		return xbmcaddon.Addon(id=add)
	except:
		return False

def toggleDependency(name, DP=None):
	dep=os.path.join(ADDONS, name, 'addon.xml')
	if os.path.exists(dep):
		source = open(dep,mode='r'); link=source.read(); source.close(); 
		match  = parseDOM(link, 'import', ret='addon')
		for depends in match:
			if not 'xbmc.python' in depends:
				dependspath=os.path.join(ADDONS, depends)
				if not DP == None: 
					DP.update("","Checking Dependency [COLOR yellow]%s[/COLOR] for [COLOR yellow]%s[/COLOR]" % (depends, name),"")
				if os.path.exists(dependspath):
					toggleAddon(name, 'true')
			xbmc.sleep(100)

def createTemp(plugin):
	temp   = os.path.join(PLUGIN, 'resources', 'tempaddon.xml')
	f      = open(temp, 'r'); r = f.read(); f.close()
	plugdir = os.path.join(ADDONS, plugin)
	if not os.path.exists(plugdir): os.makedirs(plugdir)
	a = open(os.path.join(plugdir, 'addon.xml'), 'w')
	a.write(r.replace('testid', plugin).replace('testversion', '0.0.1'))
	a.close()
	log("%s: wrote addon.xml" % plugin)

def fixmetas():
	idlist = ['plugin.video.metalliq', 'plugin.video.meta', 'script.renegadesmeta']
	temp   = os.path.join(PLUGIN, 'resources', 'tempaddon.xml')
	f      = open(temp, 'r'); r = f.read(); f.close()
	for item in idlist:
		fold = os.path.join(ADDONS, item)
		if os.path.exists(fold):
			if not os.path.exists(os.path.join(fold, 'addon.xml')): continue
			a = open(os.path.join(fold, 'addon.xml'), 'w')
			a.write(r.replace('testid', item).replace('testversion', '0.0.1'))
			a.close()
			log("%s: re-wrote addon.xml" % item)

def toggleAddon(id, value, over=None):
	if KODIV >= 17:
		addonDatabase(id, value)
		return
	addonid  = id
	addonxml = os.path.join(ADDONS, id, 'addon.xml')
	if os.path.exists(addonxml):
		f        = open(addonxml)
		b        = f.read()
		tid      = parseDOM(b, 'addon', ret='id')
		tname    = parseDOM(b, 'addon', ret='name')
		tservice = parseDOM(b, 'extension', ret='library', attrs = {'point': 'xbmc.service'})
		try:
			if len(tid) > 0:
				addonid = tid[0]
			if len(tservice) > 0:
				log("We got a live one, stopping script: %s" % match[0], xbmc.LOGDEBUG)
				ebi('StopScript(%s)' % os.path.join(ADDONS, addonid))
				ebi('StopScript(%s)' % addonid)
				ebi('StopScript(%s)' % os.path.join(ADDONS, addonid, tservice[0]))
				xbmc.sleep(500)
		except:
			pass
	query = '{"jsonrpc":"2.0", "method":"Addons.SetAddonEnabled","params":{"addonid":"%s","enabled":%s}, "id":1}' % (addonid, value)
	response = xbmc.executeJSONRPC(query)
	if 'error' in response and over == None:
		v = 'Enabling' if value == 'true' else 'Disabling'
		DIALOG.ok(ADDONTITLE, "[COLOR %s]Error %s [COLOR %s]%s[/COLOR]" % (COLOR2, COLOR1, v, id), "Check to make sure the addon list is upto date and try again.[/COLOR]")
		forceUpdate()

def addonInfo(add, info):
	addon = addonId(add)
	if addon: return addon.getAddonInfo(info)
	else: return False

def whileWindow(window, active=False, count=0, counter=15):
	windowopen = getCond('Window.IsActive(%s)' % window)
	log("%s is %s" % (window, windowopen), xbmc.LOGDEBUG)
	while not windowopen and count < counter:
		log("%s is %s(%s)" % (window, windowopen, count))
		windowopen = getCond('Window.IsActive(%s)' % window)
		count += 1 
		xbmc.sleep(500)
		
	while windowopen:
		active = True
		log("%s is %s" % (window, windowopen), xbmc.LOGDEBUG)
		windowopen = getCond('Window.IsActive(%s)' % window)
		xbmc.sleep(250)
	return active



def getCond(type):
	return xbmc.getCondVisibility(type)

def ebi(proc):
	xbmc.executebuiltin(proc)

def refresh():
	ebi('Container.Refresh()')

def splitNotify(notify):
	link = openURL(notify).replace('\r','').replace('\t','').replace('\n', '[CR]')
	if link.find('|||') == -1: return False, False
	id, msg = link.split('|||')
	if msg.startswith('[CR]'): msg = msg[4:]
	return id.replace('[CR]', ''), msg

def forceUpdate(silent=False):
	ebi('UpdateAddonRepos()')
	ebi('UpdateLocalAddons()')
	if silent == False: LogNotify("[COLOR %s]%s[/COLOR]" % (COLOR1, ADDONTITLE), '[COLOR %s]Forcing Addon Updates[/COLOR]' % COLOR2)

def convertSpecial(url, over=False):
	total = fileCount(url); start = 0
	DP.create(ADDONTITLE, "[COLOR %s]Changing Physical Paths To Special" % COLOR2, "", "Please Wait[/COLOR]")
	for root, dirs, files in os.walk(url):
		for file in files:
			start += 1
			perc = int(percentage(start, total))
			if file.endswith(".xml") or file.endswith(".hash") or file.endswith("properies"):
				DP.update(perc, "[COLOR %s]Scanning: [COLOR %s]%s[/COLOR]" % (COLOR2, COLOR1, root.replace(HOME, '')), "[COLOR %s]%s[/COLOR]" % (COLOR1, file), "Please Wait[/COLOR]")
				a = open(os.path.join(root, file)).read()
				encodedpath  = urllib.quote(HOME)
				encodedpath2  = urllib.quote(HOME).replace('%3A','%3a').replace('%5C','%5c')
				b = a.replace(HOME, 'special://home/').replace(encodedpath, 'special://home/').replace(encodedpath2, 'special://home/')
				f = open((os.path.join(root, file)), mode='w')
				f.write(str(b))
				f.close()
	DP.close()
	log("[Convert Paths to Special] Complete", xbmc.LOGNOTICE)
	if over == False: LogNotify("[COLOR %s]%s[/COLOR]" % (COLOR1, ADDONTITLE), "[COLOR %s]Convert Paths to Special: Complete![/COLOR]" % COLOR2)

def clearCrash():  
	files = []
	for file in glob.glob(os.path.join(LOG, '*crashlog*.*')):
		files.append(file)
	if len(files) > 0:
		if DIALOG.yesno(ADDONTITLE, '[COLOR %s]Would you like to delete the Crash logs?' % COLOR2, '[COLOR %s]%s[/COLOR] Files Found[/COLOR]' % (COLOR1, len(files)), yeslabel="[B][COLOR green]Remove Logs[/COLOR][/B]", nolabel="[B][COLOR red]Keep Logs[/COLOR][/B]"):
			for f in files:
				os.remove(f)
			LogNotify('[COLOR %s]Clear Crash Logs[/COLOR]' % COLOR1, '[COLOR %s]%s Crash Logs Removed[/COLOR]' % (COLOR2, len(files)))
		else: LogNotify('[COLOR %s]%s[/COLOR]' % (COLOR1, ADDONTITLE), '[COLOR %s]Clear Crash Logs Cancelled[/COLOR]' % COLOR2)
	else: LogNotify('[COLOR %s]Clear Crash Logs[/COLOR]' % COLOR1, '[COLOR %s]No Crash Logs Found[/COLOR]' % COLOR2)

def hidePassword():
	if DIALOG.yesno(ADDONTITLE, "[COLOR %s]Would you like to [COLOR %s]hide[/COLOR] all passwords when typing in the add-on settings menus?[/COLOR]" % COLOR2, yeslabel="[B][COLOR green]Hide Passwords[/COLOR][/B]", nolabel="[B][COLOR red]No Cancel[/COLOR][/B]"):
		count = 0
		for folder in glob.glob(os.path.join(ADDONS, '*/')):
			sett = os.path.join(folder, 'resources', 'settings.xml')
			if os.path.exists(sett):
				f = open(sett).read()
				match = parseDOM(f, 'addon', ret='id')
				for line in match:
					if 'pass' in line:
						if not 'option="hidden"' in line:
							try:
								change = line.replace('/', 'option="hidden" /')
								f.replace(line, change)
								count += 1
								log("[Hide Passwords] found in %s on %s" % (sett.replace(HOME, ''), line), xbmc.LOGDEBUG)
							except:
								pass
				f2 = open(sett, mode='w'); f2.write(f); f2.close()
		LogNotify("[COLOR %s]Hide Passwords[/COLOR]" % COLOR1, "[COLOR %s]%s items changed[/COLOR]" % (COLOR2, count))
		log("[Hide Passwords] %s items changed" % count, xbmc.LOGNOTICE)
	else: log("[Hide Passwords] Cancelled", xbmc.LOGNOTICE)

def unhidePassword():
	if DIALOG.yesno(ADDONTITLE, "[COLOR %s]Would you like to [COLOR %s]unhide[/COLOR] all passwords when typing in the add-on settings menus?[/COLOR]" % (COLOR2, COLOR1), yeslabel="[B][COLOR green]Unhide Passwords[/COLOR][/B]", nolabel="[B][COLOR red]No Cancel[/COLOR][/B]"):
		count = 0
		for folder in glob.glob(os.path.join(ADDONS, '*/')):
			sett = os.path.join(folder, 'resources', 'settings.xml')
			if os.path.exists(sett):
				f = open(sett).read()
				match = parseDOM(f, 'addon', ret='id')
				for line in match:
					if 'pass' in line:
						if 'option="hidden"' in line:
							try:
								change = line.replace('option="hidden"', '')
								f.replace(line, change)
								count += 1
								log("[Unhide Passwords] found in %s on %s" % (sett.replace(HOME, ''), line), xbmc.LOGDEBUG)
							except:
								pass
				f2 = open(sett, mode='w'); f2.write(f); f2.close()
		LogNotify("[COLOR %s]Unhide Passwords[/COLOR]" % COLOR1, "[COLOR %s]%s items changed[/COLOR]" % (COLOR2, count))
		log("[Unhide Passwords] %s items changed" % count, xbmc.LOGNOTICE)
	else: log("[Unhide Passwords] Cancelled", xbmc.LOGNOTICE)



def convertText():
	TEXTFILES = os.path.join(ADDONDATA, 'TextFiles')
	if not os.path.exists(TEXTFILES): os.makedirs(TEXTFILES)
	
	DP.create(ADDONTITLE,'[COLOR %s][B]Converting Text:[/B][/COLOR]' % (COLOR2),'', 'Please Wait')
	
	if not BUILDFILE == 'http://':
		filename = os.path.join(TEXTFILES, 'builds.txt')
		writing = '';x = 0
		a = openURL(BUILDFILE).replace('\n','').replace('\r','').replace('\t','')
		DP.update(0,'[COLOR %s][B]Converting Text:[/B][/COLOR] [COLOR %s]Builds.txt[/COLOR]' % (COLOR2, COLOR1),'', 'Please Wait')
		if WIZARDFILE == BUILDFILE:
			try:
				addonid, version, url = checkWizard('all')
				writing  = 'id="%s"\n' % addonid
				writing += 'version="%s"\n' % version
				writing += 'zip="%s"\n' % url
			except:
				pass
		match = re.compile('name="(.+?)".+?ersion="(.+?)".+?rl="(.+?)".+?ui="(.+?)".+?odi="(.+?)".+?heme="(.+?)".+?con="(.+?)".+?anart="(.+?)"').findall(a)
		match2 = re.compile('name="(.+?)".+?ersion="(.+?)".+?rl="(.+?)".+?ui="(.+?)".+?odi="(.+?)".+?heme="(.+?)".+?con="(.+?)".+?anart="(.+?)".+?dult="(.+?)".+?escription="(.+?)"').findall(a)
		if len(match2) == 0:
			for name, version, url, gui, kodi, theme, icon, fanart in match:
				x += 1
				DP.update(int(percentage(x, len(match2))), '', "[COLOR %s]%s[/COLOR]" % (COLOR1, name))
				if not writing == '': writing += '\n'
				writing += 'name="%s"\n' % name
				writing += 'version="%s"\n' % version
				writing += 'url="%s"\n' % url
				writing += 'gui="%s"\n' % gui
				writing += 'kodi="%s"\n' % kodi
				writing += 'theme="%s"\n' % theme
				writing += 'icon="%s"\n' % icon
				writing += 'fanart="%s"\n' % fanart
				writing += 'preview="http://"\n'
				writing += 'adult="no"\n'
				writing += 'description="Download %s from %s"\n' % (name, ADDONTITLE)
				if not theme == 'http://':
					filename2 = os.path.join(TEXTFILES, '%s_theme.txt' % name)
					themewrite = ''; x2 = 0
					a = openURL(theme).replace('\n','').replace('\r','').replace('\t','')
					DP.update(0,'[COLOR %s][B]Converting Text:[/B][/COLOR] [COLOR %s]%s_theme.txt[/COLOR]' % (COLOR2, COLOR1, name),'', 'Please Wait')
					match3 = re.compile('name="(.+?)".+?rl="(.+?)".+?con="(.+?)".+?anart="(.+?)".+?escription="(.+?)"').findall(a)
					for name, url, icon, fanart, description in match3:
						x2 += 1
						DP.update(int(percentage(x2, len(match2))), '', "[COLOR %s]%s[/COLOR]" % (COLOR1, name))
						if not themewrite == '': themewrite += '\n'
						themewrite += 'name="%s"\n' % name
						themewrite += 'url="%s"\n' % url
						themewrite += 'icon="%s"\n' % icon
						themewrite += 'fanart="%s"\n' % fanart
						themewrite += 'adult="no"\n'
						themewrite += 'description="%s"\n' % description
					f = open(filename2, 'w'); f.write(themewrite); f.close()
		else:
			for name, version, url, gui, kodi, theme, icon, fanart, adult, description in match2:
				x += 1
				DP.update(int(percentage(x, len(match2))), '', "[COLOR %s]%s[/COLOR]" % (COLOR1, name))
				if not writing == '': writing += '\n'
				writing += 'name="%s"\n' % name
				writing += 'version="%s"\n' % version
				writing += 'url="%s"\n' % url
				writing += 'gui="%s"\n' % gui
				writing += 'kodi="%s"\n' % kodi
				writing += 'theme="%s"\n' % theme
				writing += 'icon="%s"\n' % icon
				writing += 'fanart="%s"\n' % fanart
				writing += 'preview="http://"\n'
				writing += 'adult="%s"\n' % adult
				writing += 'description="%s"\n' % description
				if not theme == 'http://':
					filename2 = os.path.join(TEXTFILES, '%s_theme.txt' % name)
					themewrite = ''; x2 = 0
					a = openURL(theme).replace('\n','').replace('\r','').replace('\t','')
					DP.update(0,'[COLOR %s][B]Converting Text:[/B][/COLOR] [COLOR %s]%s_theme.txt[/COLOR]' % (COLOR2, COLOR1, name),'', 'Please Wait')
					match3 = re.compile('name="(.+?)".+?rl="(.+?)".+?con="(.+?)".+?anart="(.+?)".+?escription="(.+?)"').findall(a)
					for name, url, icon, fanart, description in match3:
						x2 += 1
						DP.update(int(percentage(x2, len(match2))), '', "[COLOR %s]%s[/COLOR]" % (COLOR1, name))
						if not themewrite == '': themewrite += '\n'
						themewrite += 'name="%s"\n' % name
						themewrite += 'url="%s"\n' % url
						themewrite += 'icon="%s"\n' % icon
						themewrite += 'fanart="%s"\n' % fanart
						themewrite += 'adult="no"\n'
						themewrite += 'description="%s"\n' % description
					f = open(filename2, 'w'); f.write(themewrite); f.close()
		f = open(filename, 'w'); f.write(writing); f.close()
	
	if not APKFILE == 'http://':
		filename = os.path.join(TEXTFILES, 'apks.txt')
		writing = ''; x = 0
		a = openURL(APKFILE).replace('\n','').replace('\r','').replace('\t','')
		DP.update(0,'[COLOR %s][B]Converting Text:[/B][/COLOR] [COLOR %s]Apks.txt[/COLOR]' % (COLOR2, COLOR1), '', 'Please Wait')
		match = re.compile('name="(.+?)".+?rl="(.+?)".+?con="(.+?)".+?anart="(.+?)"').findall(a)
		match2 = re.compile('name="(.+?)".+?rl="(.+?)".+?con="(.+?)".+?anart="(.+?)".+?dult="(.+?)".+?escription="(.+?)"').findall(a)
		if len(match2) == 0:
			for name, url, icon, fanart in match:
				x += 1
				DP.update(int(percentage(x, len(match))), '', "[COLOR %s]%s[/COLOR]" % (COLOR1, name))
				if not writing == '': writing += '\n'
				writing += 'name="%s"\n' % name
				writing += 'section="no"'
				writing += 'url="%s"\n' % url
				writing += 'icon="%s"\n' % icon
				writing += 'fanart="%s"\n' % fanart
				writing += 'adult="no"\n'
				writing += 'description="Download %s from %s"\n' % (name, ADDONTITLE)
		else:
			for name, url, icon, fanart, adult, description in match2:
				x += 1
				DP.update(int(percentage(x, len(match2))), '', "[COLOR %s]%s[/COLOR]" % (COLOR1, name))
				if not writing == '': writing += '\n'
				writing += 'name="%s"\n' % name
				writing += 'section="no"'
				writing += 'url="%s"\n' % url
				writing += 'icon="%s"\n' % icon
				writing += 'fanart="%s"\n' % fanart
				writing += 'adult="%s"\n' % adult
				writing += 'description="%s"\n' % description
		f = open(filename, 'w'); f.write(writing); f.close()
	
	if not YOUTUBEFILE == 'http://':
		filename = os.path.join(TEXTFILES, 'youtube.txt')
		writing = ''; x = 0
		a = openURL(YOUTUBEFILE).replace('\n','').replace('\r','').replace('\t','')
		DP.update(0,'[COLOR %s][B]Converting Text:[/B][/COLOR] [COLOR %s]YouTube.txt[/COLOR]' % (COLOR2, COLOR1), '', 'Please Wait')
		match = re.compile('name="(.+?)".+?rl="(.+?)".+?con="(.+?)".+?anart="(.+?)".+?escription="(.+?)"').findall(a)
		for name, url, icon, fanart, description in match:
			x += 1
			DP.update(int(percentage(x, len(match))), '', "[COLOR %s]%s[/COLOR]" % (COLOR1, name))
			if not writing == '': writing += '\n'
			writing += 'name="%s"\n' % name
			writing += 'section="no"'
			writing += 'url="%s"\n' % url
			writing += 'icon="%s"\n' % icon
			writing += 'fanart="%s"\n' % fanart
			writing += 'description="%s"\n' % description
		f = open(filename, 'w'); f.write(writing); f.close()

	if not ADVANCEDFILE == 'http://':
		filename = os.path.join(TEXTFILES, 'advancedsettings.txt')
		writing = ''; x = 0
		a = openURL(ADVANCEDFILE).replace('\n','').replace('\r','').replace('\t','')
		DP.update(0,'[COLOR %s][B]Converting Text:[/B][/COLOR] [COLOR %s]AdvancedSettings.txt[/COLOR]' % (COLOR2, COLOR1), '', 'Please Wait')
		match = re.compile('name="(.+?)".+?rl="(.+?)".+?con="(.+?)".+?anart="(.+?)".+?escription="(.+?)"').findall(a)
		for name, url, icon, fanart, description in match:
			x += 1
			DP.update(int(percentage(x, len(match))), '', "[COLOR %s]%s[/COLOR]" % (COLOR1, name))
			if not writing == '': writing += '\n'
			writing += 'name="%s"\n' % name
			writing += 'section="no"'
			writing += 'url="%s"\n' % url
			writing += 'icon="%s"\n' % icon
			writing += 'fanart="%s"\n' % fanart
			writing += 'description="%s"\n' % description
		f = open(filename, 'w'); f.write(writing); f.close()
	
	DP.close()
	DIALOG.ok(ADDONTITLE, '[COLOR %s]Your text files have been converted to 0.1.7 and are location in the [COLOR %s]/addon_data/%s/[/COLOR] folder[/COLOR]' % (COLOR2, COLOR1, ADDON_ID))

def reloadProfile(profile=None):
	if profile == None: 
		#if os.path.exists(PROFILES):
		#	profile = getInfo('System.ProfileName')
		#	log("Profile: %s" % profile)
		#	ebi('LoadProfile(%s)' % profile)
		#else:
		#ebi('Mastermode')
		ebi('LoadProfile(Master user)')
	else: ebi('LoadProfile(%s)' % profile)

def chunks(s, n):
	for start in range(0, len(s), n):
		yield s[start:start+n]

def asciiCheck(use=None, over=False):
	if use == None:
		source = DIALOG.browse(3, '[COLOR %s]Select the folder you want to scan[/COLOR]' % COLOR2, 'files', '', False, False, HOME)
		if over == True:
			yes = 1
		else:
			yes = DIALOG.yesno(ADDONTITLE,'[COLOR %s]Do you want to [COLOR %s]delete[/COLOR] all filenames with special characters or would you rather just [COLOR %s]scan and view[/COLOR] the results in the log?[/COLOR]' % (COLOR2, COLOR1, COLOR1), yeslabel='[B][COLOR green]Delete[/COLOR][/B]', nolabel='[B][COLOR red]Scan[/COLOR][/B]')
	else: 
		source = use
		yes = 1

	if source == "":
		LogNotify("[COLOR %s]%s[/COLOR]" % (COLOR1, ADDONTITLE), "[COLOR %s]ASCII Check: Cancelled[/COLOR]" % COLOR2)
		return
	
	files_found  = os.path.join(ADDONDATA, 'asciifiles.txt')
	files_fails  = os.path.join(ADDONDATA, 'asciifails.txt')
	afiles       = open(files_found, mode='w+')
	afails       = open(files_fails, mode='w+')
	f1           = 0; f2           = 0
	items        = fileCount(source)
	msg          = ''
	prog         = []
	log("Source file: (%s)" % str(source), xbmc.LOGNOTICE)
	
	DP.create(ADDONTITLE, 'Please wait...')
	for base, dirs, files in os.walk(source):
		dirs[:] = [d for d in dirs]
		files[:] = [f for f in files]
		for file in files:
			prog.append(file) 
			prog2 = int(len(prog) / float(items) * 100)
			DP.update(prog2,"[COLOR %s]Checking for non ASCII files" % COLOR2,'[COLOR %s]%s[/COLOR]' % (COLOR1, d), 'Please Wait[/COLOR]')
			try:
				file.encode('ascii')
			except UnicodeDecodeError:
				badfile = os.path.join(base, file)
				if yes:
					try: 
						os.remove(badfile)
						for chunk in chunks(badfile, 75):
							afiles.write(chunk+'\n')
						afiles.write('\n')
						f1 += 1
						log("[ASCII Check] File Removed: %s " % badfile, xbmc.LOGERROR)
					except:
						for chunk in chunks(badfile, 75):
							afails.write(chunk+'\n')
						afails.write('\n')
						f2 += 1
						log("[ASCII Check] File Failed: %s " % badfile, xbmc.LOGERROR)
				else:
					for chunk in chunks(badfile, 75):
						afiles.write(chunk+'\n')
					afiles.write('\n')
					f1 += 1
					log("[ASCII Check] File Found: %s " % badfile, xbmc.LOGERROR)
				pass
	DP.close(); afiles.close(); afails.close()
	total = int(f1) + int(f2)
	if total > 0:
		if os.path.exists(files_found): afiles = open(files_found, mode='r'); msg = afiles.read(); afiles.close()
		if os.path.exists(files_fails): afails = open(files_fails, mode='r'); msg2 = afails.read(); afails.close()
		if yes:
			if use:
				LogNotify("[COLOR %s]%s[/COLOR]" % (COLOR1, ADDONTITLE), "[COLOR %s]ASCII Check: %s Removed / %s Failed.[/COLOR]" % (COLOR2, f1, f2))
			else:
				TextBox(ADDONTITLE, "[COLOR yellow][B]%s Files Removed:[/B][/COLOR]\n %s\n\n[COLOR yellow][B]%s Files Failed:[B][/COLOR]\n %s" % (f1, msg, f2, msg2))
		else: 
			TextBox(ADDONTITLE, "[COLOR yellow][B]%s Files Found:[/B][/COLOR]\n %s" % (f1, msg))
	else: LogNotify("[COLOR %s]%s[/COLOR]" % (COLOR1, ADDONTITLE), "[COLOR %s]ASCII Check: None Found.[/COLOR]" % COLOR2)

def fileCount(home, excludes=True):
	exclude_dirs  = [ADDON_ID, 'cache', 'system', 'packages', 'Thumbnails', 'peripheral_data', 'temp', 'My_Builds', 'library', 'keymaps']
	exclude_files = ['Textures13.db', '.DS_Store', 'advancedsettings.xml', 'Thumbs.db', '.gitignore']
	item = []
	for base, dirs, files in os.walk(home):
		if excludes:
			dirs[:] = [d for d in dirs if d not in exclude_dirs]
			files[:] = [f for f in files if f not in exclude_files]
		for file in files:
			item.append(file)
	return len(item)

def defaultSkin():
	log("[Default Skin Check]", xbmc.LOGNOTICE)
	tempgui = os.path.join(USERDATA, 'guitemp.xml')
	gui = tempgui if os.path.exists(tempgui) else GUISETTINGS
	if not os.path.exists(gui): return False
	log("Reading gui file: %s" % gui, xbmc.LOGNOTICE)
	guif = open(gui, 'r+')
	msg = guif.read().replace('\n','').replace('\r','').replace('\t','').replace('    ',''); guif.close()
	log("Opening gui settings", xbmc.LOGNOTICE)
	match = re.compile('<lookandfeel>.+?<ski.+?>(.+?)</skin>.+?</lookandfeel>').findall(msg)
	log("Matches: %s" % str(match), xbmc.LOGNOTICE)
	if len(match) > 0:
		skinid = match[0]
		addonxml = os.path.join(ADDONS, match[0], 'addon.xml')
		if os.path.exists(addonxml):
			addf = open(addonxml, 'r+')
			msg2 = addf.read(); addf.close()
			match2 = parseDOM(msg2, 'addon', ret='name')
			if len(match2) > 0: skinname = match2[0]
			else: skinname = 'no match'
		else: skinname = 'no file'
		log("[Default Skin Check] Skin name: %s" % skinname, xbmc.LOGNOTICE)
		log("[Default Skin Check] Skin id: %s" % skinid, xbmc.LOGNOTICE)
		setS('defaultskin', skinid)
		setS('defaultskinname', skinname)
		setS('defaultskinignore', 'false')
	if os.path.exists(tempgui):
		log("Deleting Temp Gui File.", xbmc.LOGNOTICE)
		os.remove(tempgui)
	log("[Default Skin Check] End", xbmc.LOGNOTICE)

def lookandFeelData(do='save'):
	scan = ['lookandfeel.enablerssfeeds', 'lookandfeel.font', 'lookandfeel.rssedit', 'lookandfeel.skincolors', 'lookandfeel.skintheme', 'lookandfeel.skinzoom', 'lookandfeel.soundskin', 'lookandfeel.startupwindow', 'lookandfeel.stereostrength']
	if do == 'save':
		for item in scan:
			query = '{"jsonrpc":"2.0", "method":"Settings.GetSettingValue","params":{"setting":"%s"}, "id":1}' % (item)
			response = xbmc.executeJSONRPC(query)
			if not 'error' in response:
				match = re.compile('{"value":(.+?)}').findall(str(response))
				setS(item.replace('lookandfeel', 'default'), match[0])
				log("%s saved to %s" % (item, match[0]), xbmc.LOGNOTICE)
	else:
		for item in scan:
			value = getS(item.replace('lookandfeel', 'default'))
			query = '{"jsonrpc":"2.0", "method":"Settings.SetSettingValue","params":{"setting":"%s","value":%s}, "id":1}' % (item, value)
			response = xbmc.executeJSONRPC(query)
			log("%s restored to %s" % (item, value), xbmc.LOGNOTICE)

def sep(middle=''):
	char = uservar.SPACER
	ret = char * 40
	if not middle == '': 
		middle = '[ %s ]' % middle
		fluff = int((40 - len(middle))/2)
		ret = "%s%s%s" % (ret[:fluff], middle, ret[:fluff+2])
	return ret[:40]

def convertAdvanced():
	if os.path.exists(ADVANCED):
		f = open(ADVANCED)
		a = f.read()
		if KODIV >= 17:
			return
		else:
			return
	else: LogNotify("[COLOR %s]%s[/COLOR]" % (COLOR1, ADDONTITLE), "[COLOR %s]AdvancedSettings.xml not found[/COLOR]")

##########################

##########################

##########################

##########################

def platform():
	if xbmc.getCondVisibility('system.platform.android'):             return 'android'
	elif xbmc.getCondVisibility('system.platform.linux'):             return 'linux'
	elif xbmc.getCondVisibility('system.platform.linux.Raspberrypi'): return 'linux'
	elif xbmc.getCondVisibility('system.platform.windows'):           return 'windows'
	elif xbmc.getCondVisibility('system.platform.osx'):               return 'osx'
	elif xbmc.getCondVisibility('system.platform.atv2'):              return 'atv2'
	elif xbmc.getCondVisibility('system.platform.ios'):               return 'ios'
	elif xbmc.getCondVisibility('system.platform.darwin'):            return 'ios'

def Grab_Log(file=False, old=False, wizard=False):
	if wizard == True:
		if not os.path.exists(WIZLOG): return False
		else:
			if file == True:
				return WIZLOG
			else:
				filename    = open(WIZLOG, 'r')
				logtext     = filename.read()
				filename.close()
				return logtext
	finalfile   = 0
	logfilepath = os.listdir(LOG)
	logsfound   = []

	for item in logfilepath:
		if old == True and item.endswith('.old.log'): logsfound.append(os.path.join(LOG, item))
		elif old == False and item.endswith('.log') and not item.endswith('.old.log'): logsfound.append(os.path.join(LOG, item))

	if len(logsfound) > 0:
		logsfound.sort(key=lambda f: os.path.getmtime(f))
		if file == True: return logsfound[-1]
		else:
			filename    = open(logsfound[-1], 'r')
			logtext     = filename.read()
			filename.close()
			return logtext
	else: 
		return False



def clearPackages(over=None):
	if os.path.exists(PACKAGES):
		try:
			for root, dirs, files in os.walk(PACKAGES):
				file_count = 0
				file_count += len(files)
				if file_count > 0:
					size = convertSize(getSize(PACKAGES))
					if over: yes=1
					else: yes=DIALOG.yesno("[COLOR %s]Delete Package Files" % COLOR2, "[COLOR %s]%s[/COLOR] files found / [COLOR %s]%s[/COLOR] in size." % (COLOR1, str(file_count), COLOR1, size), "Do you want to delete them?[/COLOR]", nolabel='[B][COLOR red]Don\'t Clear[/COLOR][/B]',yeslabel='[B][COLOR green]Clear Packages[/COLOR][/B]')
					if yes:
						for f in files: os.unlink(os.path.join(root, f))
						for d in dirs: shutil.rmtree(os.path.join(root, d))
						LogNotify("[COLOR %s]%s[/COLOR]" % (COLOR1, ADDONTITLE),'[COLOR %s]Clear Packages: Success![/COLOR]' % COLOR2)
				else: LogNotify("[COLOR %s]%s[/COLOR]" % (COLOR1, ADDONTITLE),'[COLOR %s]Clear Packages: None Found![/COLOR]' % COLOR2)
		except Exception, e:
			LogNotify("[COLOR %s]%s[/COLOR]" % (COLOR1, ADDONTITLE),'[COLOR %s]Clear Packages: Error![/COLOR]' % COLOR2)
			log("Clear Packages Error: %s" % str(e), xbmc.LOGERROR)
	else: LogNotify("[COLOR %s]%s[/COLOR]" % (COLOR1, ADDONTITLE),'[COLOR %s]Clear Packages: None Found![/COLOR]' % COLOR2)

def clearPackagesStartup():
	start = datetime.utcnow() - timedelta(minutes=3)
	file_count = 0; cleanupsize = 0
	if os.path.exists(PACKAGES):
		pack = os.listdir(PACKAGES)
		pack.sort(key=lambda f: os.path.getmtime(os.path.join(PACKAGES, f)))
		try:
			for item in pack:
				file = os.path.join(PACKAGES, item)
				lastedit = datetime.utcfromtimestamp(os.path.getmtime(file))
				if lastedit <= start:
					if os.path.isfile(file):
						file_count += 1
						cleanupsize += os.path.getsize(file)
						os.unlink(file)
					elif os.path.isdir(file): 
						cleanupsize += getSize(file)
						cleanfiles, cleanfold = cleanHouse(file)
						file_count += cleanfiles + cleanfold
						try:
							shutil.rmtree(file)
						except Exception, e:
							log("Failed to remove %s: %s" % (file, str(e), xbmc.LOGERROR))
			if file_count > 0: LogNotify("[COLOR %s]%s[/COLOR]" % (COLOR1, ADDONTITLE), '[COLOR %s]Clear Packages: Success: %s[/COLOR]' % (COLOR2, convertSize(cleanupsize)))
			else: LogNotify("[COLOR %s]%s[/COLOR]" % (COLOR1, ADDONTITLE), '[COLOR %s]Clear Packages: None Found![/COLOR]' % COLOR2)
		except Exception, e:
			LogNotify("[COLOR %s]%s[/COLOR]" % (COLOR1, ADDONTITLE), '[COLOR %s]Clear Packages: Error![/COLOR]' % COLOR2)
			log("Clear Packages Error: %s" % str(e), xbmc.LOGERROR)
	else: LogNotify("[COLOR %s]%s[/COLOR]" % (COLOR1, ADDONTITLE), '[COLOR %s]Clear Packages: None Found![/COLOR]' % COLOR2)

def clearCache(over=None):
	PROFILEADDONDATA = os.path.join(PROFILE,'addon_data')
	dbfiles   = [
		(os.path.join(ADDOND, 'plugin.video.phstreams', 'cache.db')),
		(os.path.join(ADDOND, 'plugin.video.bob', 'cache.db')),
		(os.path.join(ADDOND, 'plugin.video.bob', 'providers.db')),
		(os.path.join(ADDOND, 'plugin.video.specto', 'cache.db')),
		(os.path.join(ADDOND, 'plugin.video.specto', 'sources.db')),
		(os.path.join(ADDOND, 'plugin.video.genesis', 'cache.db')),
		(os.path.join(ADDOND, 'plugin.video.exodus', 'cache.db')),
		(os.path.join(ADDOND, 'plugin.video.exodus', 'providers.13.db')),
		(os.path.join(ADDOND, 'plugin.video.zen', 'cache.db')),
		(os.path.join(DATABASE,  'onechannelcache.db')),
		(os.path.join(DATABASE,  'saltscache.db')),
		(os.path.join(DATABASE,  'saltshd.lite.db'))]
		
	cachelist = [
		(PROFILEADDONDATA),
		(ADDONDATA),
		(os.path.join(HOME,'cache')),
		(os.path.join(HOME,'temp')),
		(os.path.join(ADDOND,'script.module.simple.downloader')),
		(os.path.join(PROFILEADDONDATA,'script.module.simple.downloader')),]
		
	delfiles = 0
	excludes = ['meta_cache', 'archive_cache']
	for item in cachelist:
		if os.path.exists(item) and not item in [ADDONDATA, ADDOND]:
			for root, dirs, files in os.walk(item):
				dirs[:] = [d for d in dirs if d not in excludes]
				file_count = 0
				file_count += len(files)
				if file_count > 0:
					for f in files:
						if not f in LOGFILES:
							try:
								os.unlink(os.path.join(root, f))
								log("[Wiped] %s" % os.path.join(root, f), xbmc.LOGNOTICE)
								delfiles += 1
							except:
								pass
						else: log('Ignore Log File: %s' % f, xbmc.LOGNOTICE)
					for d in dirs:
						try:
							shutil.rmtree(os.path.join(root, d))
							delfiles += 1
							log("[Success] cleared %s files from %s" % (str(file_count), os.path.join(item,d)), xbmc.LOGNOTICE)
						except:
							log("[Failed] to wipe cache in: %s" % os.path.join(item,d), xbmc.LOGNOTICE)
		else:
			for root, dirs, files in os.walk(item):
				dirs[:] = [d for d in dirs if d not in excludes]
				for d in dirs:
					if not str(d.lower()).find('cache') == -1:
						try:
							shutil.rmtree(os.path.join(root, d))
							delfiles += 1
							log("[Success] wiped %s " % os.path.join(root,d), xbmc.LOGNOTICE)
						except:
							log("[Failed] to wipe cache in: %s" % os.path.join(item,d), xbmc.LOGNOTICE)
	if INCLUDEVIDEO == 'true' and over == None:
		files = []
		if INCLUDEALL == 'true': files = dbfiles
		else:
			if INCLUDEBOB == 'true':     files.append(os.path.join(ADDOND, 'plugin.video.bob', 'cache.db'))
			if INCLUDEBOBP == 'true':     files.append(os.path.join(ADDOND, 'plugin.video.bob', 'providers.db'))
			if INCLUDEPHOENIX == 'true': files.append(os.path.join(ADDOND, 'plugin.video.phstreams', 'cache.db'))
			if INCLUDESPECTO == 'true':  files.append(os.path.join(ADDOND, 'plugin.video.specto', 'cache.db'))
			if INCLUDESPECTOS == 'true':  files.append(os.path.join(ADDOND, 'plugin.video.specto', 'sources.db'))
			if INCLUDEGENESIS == 'true': files.append(os.path.join(ADDOND, 'plugin.video.genesis', 'cache.db'))
			if INCLUDEEXODUS == 'true':  files.append(os.path.join(ADDOND, 'plugin.video.exodus', 'cache.db'))
			if INCLUDEEXODUSP == 'true':  files.append(os.path.join(ADDOND, 'plugin.video.exodus', 'providers.13.db'))
			if INCLUDEZEN == 'true':  files.append(os.path.join(ADDOND, 'plugin.video.zen', 'cache.db'))
			if INCLUDEONECHAN == 'true': files.append(os.path.join(DATABASE,  'onechannelcache.db'))
			if INCLUDESALTS == 'true':   files.append(os.path.join(DATABASE,  'saltscache.db'))
			if INCLUDESALTSHD == 'true': files.append(os.path.join(DATABASE,  'saltshd.lite.db'))
		if len(files) > 0:
			for item in files:
				if os.path.exists(item):
					delfiles += 1
					try:
						textdb = database.connect(item)
						textexe = textdb.cursor()
					except Exception, e:
						log("DB Connection error: %s" % str(e), xbmc.LOGERROR)
						continue
					if 'Database' in item:
						try:
							textexe.execute("DELETE FROM url_cache")
							textexe.execute("VACUUM")
							textdb.commit()
							textexe.close()
							log("[Success] wiped %s" % item, xbmc.LOGNOTICE)
						except Exception, e:
							log("[Failed] wiped %s: %s" % (item, str(e)), xbmc.LOGNOTICE)
					else:
						textexe.execute("SELECT name FROM sqlite_master WHERE type = 'table'")
						for table in textexe.fetchall():
							try:
								textexe.execute("DELETE FROM %s" % table[0])
								textexe.execute("VACUUM")
								textdb.commit()
								log("[Success] wiped %s in %s" % (table, item), xbmc.LOGNOTICE)
							except Exception, e:
								log("[Failed] wiped %s in %s: %s" % (table, item, str(e)), xbmc.LOGNOTICE)
						textexe.close()
		else: log("Clear Cache: Clear Video Cache Not Enabled", xbmc.LOGNOTICE)
	LogNotify("[COLOR %s]%s[/COLOR]" % (COLOR1, ADDONTITLE), '[COLOR %s]Clear Cache: Removed %s Files[/COLOR]' % (COLOR2, delfiles))

def checkSources():
	if not os.path.exists(SOURCES):
		LogNotify("[COLOR %s]%s[/COLOR]" % (COLOR1, ADDONTITLE), "[COLOR %s]No Sources.xml File Found![/COLOR]" % COLOR2)
		return False
	x      = 0
	bad    = []
	remove = []
	f      = open(SOURCES)
	a      = f.read()
	temp   = a.replace('\r','').replace('\n','').replace('\t','')
	match  = re.compile('<files>.+?</files>').findall(temp)
	f.close()
	if len(match) > 0:
		match2  = re.compile('<source>.+?<name>(.+?)</name>.+?<path pathversion="1">(.+?)</path>.+?<allowsharing>(.+?)</allowsharing>.+?</source>').findall(match[0])
		DP.create(ADDONTITLE, "[COLOR %s]Scanning Sources for Broken links[/COLOR]" % COLOR2)
		for name, path, sharing in match2:
			x     += 1
			perc   = int(percentage(x, len(match2)))
			DP.update(perc, '', "[COLOR %s]Checking [COLOR %s]%s[/COLOR]:[/COLOR]" % (COLOR2, COLOR1, name), "[COLOR %s]%s[/COLOR]" % (COLOR1, path))
			if 'http' in path:
				working = workingURL(path)
				if not working == True:
					bad.append([name, path, sharing, working])

		log("Bad Sources: %s" % len(bad), xbmc.LOGNOTICE)
		if len(bad) > 0:
			choice = DIALOG.yesno(ADDONTITLE, "[COLOR %s]%s[/COLOR][COLOR %s] Source(s) have been found Broken" % (COLOR1, len(bad), COLOR2),"Would you like to Remove all or choose one by one?[/COLOR]", yeslabel="[B][COLOR green]Remove All[/COLOR][/B]", nolabel="[B][COLOR red]Choose to Delete[/COLOR][/B]")
			if choice == 1:
				remove = bad
			else:
				for name, path, sharing, working in bad: 
					log("%s sources: %s, %s" % (name, path, working), xbmc.LOGNOTICE)
					if DIALOG.yesno(ADDONTITLE, "[COLOR %s]%s[/COLOR][COLOR %s] was reported as non working" % (COLOR1, name, COLOR2), "[COLOR %s]%s[/COLOR]" % (COLOR1, path), "[COLOR %s]%s[/COLOR]" % (COLOR1, working), yeslabel="[B][COLOR green]Remove Source[/COLOR][/B]", nolabel="[B][COLOR red]Keep Source[/COLOR][/B]"):
						remove.append([name, path, sharing, working])
						log("Removing Source %s" % name, xbmc.LOGNOTICE)
					else: log("Source %s was not removed" % name, xbmc.LOGNOTICE)
			if len(remove) > 0:
				for name, path, sharing, working in remove: 
					a = a.replace('\n        <source>\n            <name>%s</name>\n            <path pathversion="1">%s</path>\n            <allowsharing>%s</allowsharing>\n        </source>' % (name, path, sharing), '')
					log("Removing Source %s" % name, xbmc.LOGNOTICE)
				
				f = open(SOURCES, mode='w')
				f.write(str(a))
				f.close()
				alive = len(match) - len(bad)
				kept = len(bad) - len(remove)
				removed = len(remove)
				DIALOG.ok(ADDONTITLE, "[COLOR %s]Checking sources for broken paths has been completed" % COLOR2, "Working: [COLOR %s]%s[/COLOR] | Kept: [COLOR %s]%s[/COLOR] | Removed: [COLOR %s]%s[/COLOR][/COLOR]" % (COLOR2, COLOR1, alive, COLOR1, kept, COLOR1, removed))
			else: log("No Bad Sources to be removed.", xbmc.LOGNOTICE)
		else: LogNotify("[COLOR %s]%s[/COLOR]" % (COLOR1, ADDONTITLE), "[COLOR %s]All Sources Are Working[/COLOR]" % COLOR2)
	else: log("No Sources Found", xbmc.LOGNOTICE)

def checkRepos():
	DP.create(ADDONTITLE, '[COLOR %s]Checking Repositories...[/COLOR]' % COLOR2)
	badrepos = []
	ebi('UpdateAddonRepos')
	repolist = glob.glob(os.path.join(ADDONS,'repo*'))
	if len(repolist) == 0:
		DP.close()
		LogNotify("[COLOR %s]%s[/COLOR]" % (COLOR1, ADDONTITLE), "[COLOR %s]No Repositories Found![/COLOR]" % COLOR2)
		return
	sleeptime = len(repolist); start = 0;
	while start < sleeptime:
		start += 1
		if DP.iscanceled(): break
		perc = int(percentage(start, sleeptime))
		DP.update(perc, '', '[COLOR %s]Checking: [/COLOR][COLOR %s]%s[/COLOR]' % (COLOR2, COLOR1, repolist[start-1].replace(ADDONS, '')[1:]))
		xbmc.sleep(1000)
	if DP.iscanceled(): 
		DP.close()
		LogNotify("[COLOR %s]%s[/COLOR]" % (COLOR1, ADDONTITLE), "[COLOR %s]Enabling Addons Cancelled[/COLOR]" % COLOR2)
		sys.exit()
	DP.close()
	logfile = Grab_Log(False)
	fails = re.compile('CRepositoryUpdateJob(.+?)failed').findall(logfile)
	for item in fails:
		log("Bad Repository: %s " % item, xbmc.LOGNOTICE)
		brokenrepo = item.replace('[','').replace(']','').replace(' ','').replace('/','').replace('\\','')
		if not brokenrepo in badrepos:
			badrepos.append(brokenrepo)
	if len(badrepos) > 0:
		msg  = "[COLOR %s]Below is a list of Repositories that did not resolve.  This does not mean that they are Depreciated, sometimes hosts go down for a short period of time.  Please do serveral scans of your repository list before removing a repository just to make sure it is broken.[/COLOR][CR][CR][COLOR %s]" % (COLOR2, COLOR1)
		msg += '[CR]'.join(badrepos)
		msg += '[/COLOR]'
		TextBox("%s: Bad Repositories" % ADDONTITLE, msg)
	else: 
		LogNotify("[COLOR %s]%s[/COLOR]" % (COLOR1, ADDONTITLE), "[COLOR %s]All Repositories Working![/COLOR]" % COLOR2)

#############################
####KILL XBMC ###############
#####THANKS BRACKETS ########

def killxbmc(over=None):
	if over: choice = 1
	else: choice = DIALOG.yesno('Force Close Kodi', '[COLOR %s]You are about to close Kodi' % COLOR2, 'Would you like to continue?[/COLOR]', nolabel='[B][COLOR red] No Cancel[/COLOR][/B]',yeslabel='[B][COLOR green]Force Close Kodi[/COLOR][/B]')
	if choice == 1:
		log("Force Closing Kodi: Platform[%s]" % str(platform()), xbmc.LOGNOTICE)
		os._exit(1)

def redoThumbs():
	if not os.path.exists(THUMBS): os.makedirs(THUMBS)
	thumbfolders = '0123456789abcdef'
	videos = os.path.join(THUMBS, 'Video', 'Bookmarks')
	for item in thumbfolders:
		foldname = os.path.join(THUMBS, item)
		if not os.path.exists(foldname): os.makedirs(foldname)
	if not os.path.exists(videos): os.makedirs(videos)

def reloadFix(default=None):
	DIALOG.ok(ADDONTITLE, "[COLOR %s]WARNING: Sometimes Reloading the Profile causes Kodi to crash.  While Kodi is Reloading the Profile Please Do Not Press Any Buttons![/COLOR]" % COLOR2)
	if not os.path.exists(PACKAGES): os.makedirs(PACKAGES)
	if default == None:
		lookandFeelData('save')
	redoThumbs()
	ebi('ActivateWindow(Home)')
	reloadProfile()
	xbmc.sleep(10000)
	if KODIV >= 17: kodi17Fix()
	if default == None:
		log("Switching to: %s" % getS('defaultskin'))
		gotoskin = getS('defaultskin')
		skinSwitch.swapSkins(gotoskin)
		x = 0
		while not xbmc.getCondVisibility("Window.isVisible(yesnodialog)") and x < 150:
			x += 1
			xbmc.sleep(200)
		if xbmc.getCondVisibility("Window.isVisible(yesnodialog)"):
			ebi('SendClick(11)')
		lookandFeelData('restore')
	addonUpdates('reset')
	forceUpdate()
	ebi("ReloadSkin()")



def mediaCenter():
	if str(HOME).lower().find('kodi'):
		return 'Kodi'
	elif str(HOME).lower().find('spmc'):
		return 'SPMC'
	else: 
		return 'Unknown Fork'

def kodi17Fix():
	addonlist = glob.glob(os.path.join(ADDONS, '*/'))
	disabledAddons = []
	for folder in sorted(addonlist, key = lambda x: x):
		addonxml = os.path.join(folder, 'addon.xml')
		if os.path.exists(addonxml):
			fold   = folder.replace(ADDONS, '')[1:-1]
			f      = open(addonxml)
			a      = f.read()
			aid    = parseDOM(a, 'addon', ret='id')
			f.close()
			try:
				add    = xbmcaddon.Addon(id=aid[0])
			except:
				try:
					log("%s was disabled" % aid[0], xbmc.LOGDEBUG)
					disabledAddons.append(aid[0])
				except:
					try:
						log("%s was disabled" % fold, xbmc.LOGDEBUG)
						disabledAddons.append(fold)
					except:
						if len(aid) == 0: log("Unabled to enable: %s(Cannot Determine Addon ID)" % fold, xbmc.LOGERROR)
						else: log("Unabled to enable: %s" % folder, xbmc.LOGERROR)
	if len(disabledAddons) > 0:
		x = 0
		DP.create(ADDONTITLE,'[COLOR %s]Enabling disabled Addons' % COLOR2,'', 'Please Wait[/COLOR]')
		for item in disabledAddons:
			x += 1
			prog = int(percentage(x, len(disabledAddons)))
			DP.update(prog, "", "Enabling: [COLOR %s]%s[/COLOR]" % (COLOR1, item))
			addonDatabase(item, 1)
			if DP.iscanceled(): break
		if DP.iscanceled(): 
			DP.close()
			LogNotify("[COLOR %s]%s[/COLOR]" % (COLOR1, ADDONTITLE), "[COLOR %s]Enabling Addons Cancelled![/COLOR]" % COLOR2)
			sys.exit()
		DP.close()
	forceUpdate()
	ebi("ReloadSkin()")

def addonDatabase(addon=None, state=1):
	dbfile = latestDB('Addons')
	dbfile = os.path.join(DATABASE, dbfile)
	installedtime = str(datetime.now())[:-7]
	if os.path.exists(dbfile):
		try:
			textdb = database.connect(dbfile)
			textexe = textdb.cursor()
		except Exception, e:
			log("DB Connection Error: %s" % str(e), xbmc.LOGERROR)
			return False
	else: return False
	if state == 2:
		try:
			textexe.execute("DELETE FROM installed WHERE addonID = ?", (addon,))
			textdb.commit()
			textexe.close()
		except Exception, e:
			log("Error Removing %s from DB" % addon)
		return True
	try:
		textexe.execute("SELECT id, addonID, enabled FROM installed WHERE addonID = ?", (addon,))
		found = textexe.fetchone()
		if found == None:
			textexe.execute('INSERT INTO installed (addonID , enabled, installDate) VALUES (?,?,?)', (addon, state, installedtime,))
			log("Insert %s into db" % addon)
		else:
			tid, taddonid, tenabled = found
			textexe.execute('UPDATE installed SET enabled = ? WHERE id = ? ', (state, tid,))
			log("Updated %s in db" % addon)
		textdb.commit()
		textexe.close()
	except Exception, e:
		log("Erroring enabling addon: %s" % addon)

##########################
### PURGE DATABASE #######
##########################
def purgeDb(name):
	#dbfile = name.replace('.db','').translate(None, digits)
	#if dbfile not in ['Addons', 'ADSP', 'Epg', 'MyMusic', 'MyVideos', 'Textures', 'TV', 'ViewModes']: return False
	#textfile = os.path.join(DATABASE, name)
	log('Purging DB %s.' % name, xbmc.LOGNOTICE)
	if os.path.exists(name):
		try:
			textdb = database.connect(name)
			textexe = textdb.cursor()
		except Exception, e:
			log("DB Connection Error: %s" % str(e), xbmc.LOGERROR)
			return False
	else: log('%s not found.' % name, xbmc.LOGERROR); return False
	textexe.execute("SELECT name FROM sqlite_master WHERE type = 'table'")
	for table in textexe.fetchall():
		if table[0] == 'version': 
			log('Data from table `%s` skipped.' % table[0], xbmc.LOGDEBUG)
		else:
			try:
				textexe.execute("DELETE FROM %s" % table[0])
				textdb.commit()
				log('Data from table `%s` cleared.' % table[0], xbmc.LOGDEBUG)
			except Exception, e: log("DB Remove Table `%s` Error: %s" % (table[0], str(e)), xbmc.LOGERROR)
	textexe.close()
	log('%s DB Purging Complete.' % name, xbmc.LOGNOTICE)
	show = name.replace('\\', '/').split('/')
	LogNotify("[COLOR %s]Purge Database[/COLOR]" % COLOR1, "[COLOR %s]%s Complete[/COLOR]" % (COLOR2, show[len(show)-1]))

def oldThumbs():
	dbfile = os.path.join(DATABASE, latestDB('Textures'))
	use    = 10
	week   = TODAY - timedelta(days=7)
	ids    = []
	images = []
	size   = 0
	if os.path.exists(dbfile):
		try:
			textdb = database.connect(dbfile)
			textexe = textdb.cursor()
		except Exception, e:
			log("DB Connection Error: %s" % str(e), xbmc.LOGERROR)
			return False
	else: log('%s not found.' % dbfile, xbmc.LOGERROR); return False
	textexe.execute("SELECT idtexture FROM sizes WHERE usecount < ? AND lastusetime < ?", (use, str(week)))
	found = textexe.fetchall()
	for rows in found:
		idfound = rows[0]
		ids.append(idfound)
		textexe.execute("SELECT cachedurl FROM texture WHERE id = ?", (idfound, ))
		found2 = textexe.fetchall()
		for rows2 in found2:
			images.append(rows2[0])
	log("%s total thumbs cleaned up." % str(len(images)), xbmc.LOGNOTICE)
	for id in ids:       
		textexe.execute("DELETE FROM sizes   WHERE idtexture = ?", (id, ))
		textexe.execute("DELETE FROM texture WHERE id        = ?", (id, ))
	textexe.execute("VACUUM")
	textdb.commit()
	textexe.close()
	for image in images:
		path = os.path.join(THUMBS, image)
		try:
			imagesize = os.path.getsize(path)
			os.remove(path)
			size += imagesize
		except:
			pass
	removed = convertSize(size)
	if len(images) > 0: LogNotify("[COLOR %s]%s[/COLOR]" % (COLOR1, ADDONTITLE), '[COLOR %s]Clear Thumbs: %s Files / %s MB[/COLOR]!' % (COLOR2, str(len(images)), removed))
	else: LogNotify("[COLOR %s]%s[/COLOR]" % (COLOR1, ADDONTITLE), '[COLOR %s]Clear Thumbs: None Found![/COLOR]' % COLOR2)

def parseDOM(html, name=u"", attrs={}, ret=False):
    # Copyright (C) 2010-2011 Tobias Ussing And Henrik Mosgaard Jensen

    if isinstance(html, str):
        try:
            html = [html.decode("utf-8")]
        except:
            html = [html]
    elif isinstance(html, unicode):
        html = [html]
    elif not isinstance(html, list):
        return u""

    if not name.strip():
        return u""

    ret_lst = []
    for item in html:
        temp_item = re.compile('(<[^>]*?\n[^>]*?>)').findall(item)
        for match in temp_item:
            item = item.replace(match, match.replace("\n", " "))

        lst = []
        for key in attrs:
            lst2 = re.compile('(<' + name + '[^>]*?(?:' + key + '=[\'"]' + attrs[key] + '[\'"].*?>))', re.M | re.S).findall(item)
            if len(lst2) == 0 and attrs[key].find(" ") == -1:
                lst2 = re.compile('(<' + name + '[^>]*?(?:' + key + '=' + attrs[key] + '.*?>))', re.M | re.S).findall(item)

            if len(lst) == 0:
                lst = lst2
                lst2 = []
            else:
                test = range(len(lst))
                test.reverse()
                for i in test:
                    if not lst[i] in lst2:
                        del(lst[i])

        if len(lst) == 0 and attrs == {}:
            lst = re.compile('(<' + name + '>)', re.M | re.S).findall(item)
            if len(lst) == 0:
                lst = re.compile('(<' + name + ' .*?>)', re.M | re.S).findall(item)

        if isinstance(ret, str):
            lst2 = []
            for match in lst:
                attr_lst = re.compile('<' + name + '.*?' + ret + '=([\'"].[^>]*?[\'"])>', re.M | re.S).findall(match)
                if len(attr_lst) == 0:
                    attr_lst = re.compile('<' + name + '.*?' + ret + '=(.[^>]*?)>', re.M | re.S).findall(match)
                for tmp in attr_lst:
                    cont_char = tmp[0]
                    if cont_char in "'\"":
                        if tmp.find('=' + cont_char, tmp.find(cont_char, 1)) > -1:
                            tmp = tmp[:tmp.find('=' + cont_char, tmp.find(cont_char, 1))]

                        if tmp.rfind(cont_char, 1) > -1:
                            tmp = tmp[1:tmp.rfind(cont_char)]
                    else:
                        if tmp.find(" ") > 0:
                            tmp = tmp[:tmp.find(" ")]
                        elif tmp.find("/") > 0:
                            tmp = tmp[:tmp.find("/")]
                        elif tmp.find(">") > 0:
                            tmp = tmp[:tmp.find(">")]

                    lst2.append(tmp.strip())
            lst = lst2
        else:
            lst2 = []
            for match in lst:
                endstr = u"</" + name

                start = item.find(match)
                end = item.find(endstr, start)
                pos = item.find("<" + name, start + 1 )

                while pos < end and pos != -1:
                    tend = item.find(endstr, end + len(endstr))
                    if tend != -1:
                        end = tend
                    pos = item.find("<" + name, pos + 1)

                if start == -1 and end == -1:
                    temp = u""
                elif start > -1 and end > -1:
                    temp = item[start + len(match):end]
                elif end > -1:
                    temp = item[:end]
                elif start > -1:
                    temp = item[start + len(match):]

                if ret:
                    endstr = item[end:item.find(">", item.find(endstr)) + 1]
                    temp = match + temp + endstr

                item = item[item.find(temp, item.find(match)) + len(temp):]
                lst2.append(temp)
            lst = lst2
        ret_lst += lst

    return ret_lst


def replaceHTMLCodes(txt):
    txt = re.sub("(&#[0-9]+)([^;^0-9]+)", "\\1;\\2", txt)
    txt = HTMLParser.HTMLParser().unescape(txt)
    txt = txt.replace("&quot;", "\"")
    txt = txt.replace("&amp;", "&")
    return txt

import os
from shutil import *
def copytree(src, dst, symlinks=False, ignore=None):
	names = os.listdir(src)
	if ignore is not None:
		ignored_names = ignore(src, names)
	else:
		ignored_names = set()
	if not os.path.isdir(dst):
		os.makedirs(dst)
	errors = []
	for name in names:
		if name in ignored_names:
			continue
		srcname = os.path.join(src, name)
		dstname = os.path.join(dst, name)
		try:
			if symlinks and os.path.islink(srcname):
				linkto = os.readlink(srcname)
				os.symlink(linkto, dstname)
			elif os.path.isdir(srcname):
				copytree(srcname, dstname, symlinks, ignore)
			else:
				copy2(srcname, dstname)
		except Error, err:
			errors.extend(err.args[0])
		except EnvironmentError, why:
			errors.append((srcname, dstname, str(why)))
	try:
		copystat(src, dst)
	except OSError, why:
		errors.extend((src, dst, str(why)))
	if errors:
		raise Error, errors