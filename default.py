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

import xbmc, xbmcaddon, xbmcgui, xbmcplugin, os, sys, xbmcvfs, glob
import shutil
import urllib2,urllib
import re
import zipfile
import uservar
import fnmatch
try:    from sqlite3 import dbapi2 as database
except: from pysqlite2 import dbapi2 as database
from datetime import date, datetime, timedelta
from urlparse import urljoin
from resources.libs import downloader, wizard as wiz

ADDON_ID         = uservar.ADDON_ID
ADDONTITLE       = uservar.ADDONTITLE
ADDON            = wiz.addonId(ADDON_ID)
VERSION          = wiz.addonInfo(ADDON_ID,'version')
ADDONPATH        = wiz.addonInfo(ADDON_ID,'path')
DIALOG           = xbmcgui.Dialog()
DP               = xbmcgui.DialogProgress()
HOME             = xbmc.translatePath('special://home/')
LOG              = xbmc.translatePath('special://logpath/')
PROFILE          = xbmc.translatePath('special://profile/')
ADDONS           = os.path.join(HOME,      'addons')
USERDATA         = os.path.join(HOME,      'userdata')
PLUGIN           = os.path.join(ADDONS,    ADDON_ID)
PACKAGES         = os.path.join(ADDONS,    'packages')
ADDOND           = os.path.join(USERDATA,  'addon_data')
ADDONDATA        = os.path.join(USERDATA,  'addon_data', ADDON_ID)
ADVANCED         = os.path.join(USERDATA,  'advancedsettings.xml')
SOURCES          = os.path.join(USERDATA,  'sources.xml')
FAVOURITES       = os.path.join(USERDATA,  'favourites.xml')
PROFILES         = os.path.join(USERDATA,  'profiles.xml')
GUISETTINGS      = os.path.join(USERDATA,  'guisettings.xml')
THUMBS           = os.path.join(USERDATA,  'Thumbnails')
DATABASE         = os.path.join(USERDATA,  'Database')
FANART           = os.path.join(ADDONPATH, 'fanart.jpg')
ICON             = os.path.join(ADDONPATH, 'icon.png')
ART              = os.path.join(ADDONPATH, 'resources', 'art')
WIZLOG           = os.path.join(ADDONDATA, 'wizard.log')
SKIN             = xbmc.getSkinDir()

SHOWMAINT        = wiz.getS('showmaint')
AUTOCLEANUP      = wiz.getS('autoclean')
AUTOCACHE        = wiz.getS('clearcache')
AUTOPACKAGES     = wiz.getS('clearpackages')
AUTOTHUMBS       = wiz.getS('clearthumbs')
AUTOFEQ          = wiz.getS('autocleanfeq')
AUTONEXTRUN      = wiz.getS('nextautocleanup')
INCLUDEVIDEO     = wiz.getS('includevideo')
INCLUDEALL       = wiz.getS('includeall')
INCLUDEBOB       = wiz.getS('includebob')
INCLUDEBOBP       = wiz.getS('includebobp')
INCLUDEPHOENIX   = wiz.getS('includephoenix')
INCLUDESPECTO    = wiz.getS('includespecto')
INCLUDESPECTOS    = wiz.getS('includespectos')
INCLUDEGENESIS   = wiz.getS('includegenesis')
INCLUDEEXODUS    = wiz.getS('includeexodus')
INCLUDEEXODUSP    = wiz.getS('includeexodusp')
INCLUDEONECHAN   = wiz.getS('includeonechan')
INCLUDESALTS     = wiz.getS('includesalts')
INCLUDESALTSHD   = wiz.getS('includesaltslite')
SEPERATE         = wiz.getS('seperate')
NOTIFY           = wiz.getS('notify')
NOTEID           = wiz.getS('noteid')
NOTEDISMISS      = wiz.getS('notedismiss')
AUTOFEQ          = int(float(AUTOFEQ)) if AUTOFEQ.isdigit() else 0
TODAY            = date.today()
TOMORROW         = TODAY + timedelta(days=1)
THREEDAYS        = TODAY + timedelta(days=3)
WEEK       		 = TODAY + timedelta(days=7)
MONTH       	 = TODAY + timedelta(days=30)
KODIV            = float(xbmc.getInfoLabel("System.BuildVersion")[:4])
MCNAME           = wiz.mediaCenter()
EXCLUDES         = uservar.EXCLUDES
HEADERMESSAGE    = uservar.HEADERMESSAGE

HIDESPACERS      = uservar.HIDESPACERS
COLOR1           = uservar.COLOR1
COLOR2           = uservar.COLOR2
THEME1           = uservar.THEME1
THEME2           = uservar.THEME2
THEME3           = uservar.THEME3
THEME4           = uservar.THEME4
THEME5           = uservar.THEME5
ICONBUILDS       = uservar.ICONBUILDS if not uservar.ICONBUILDS == 'http://' else ICON
ICONMAINT        = uservar.ICONMAINT if not uservar.ICONMAINT == 'http://' else ICON
ICONAPK          = uservar.ICONAPK if not uservar.ICONAPK == 'http://' else ICON
ICONADDONS       = uservar.ICONADDONS if not uservar.ICONADDONS == 'http://' else ICON
ICONYOUTUBE      = uservar.ICONYOUTUBE if not uservar.ICONYOUTUBE == 'http://' else ICON
ICONSAVE         = uservar.ICONSAVE if not uservar.ICONSAVE == 'http://' else ICON
ICONTRAKT        = uservar.ICONTRAKT if not uservar.ICONTRAKT == 'http://' else ICON
ICONREAL         = uservar.ICONREAL if not uservar.ICONREAL == 'http://' else ICON
ICONLOGIN        = uservar.ICONLOGIN if not uservar.ICONLOGIN == 'http://' else ICON
ICONCONTACT      = uservar.ICONCONTACT if not uservar.ICONCONTACT == 'http://' else ICON
ICONSETTINGS     = uservar.ICONSETTINGS if not uservar.ICONSETTINGS == 'http://' else ICON
LOGFILES         = wiz.LOGFILES


###########################
###### Menu Items   #######
###########################
#addDir (display,mode,name=None,url=None,menu=None,overwrite=True,fanart=FANART,icon=ICON, themeit=None)
#addFile(display,mode,name=None,url=None,menu=None,overwrite=True,fanart=FANART,icon=ICON, themeit=None)

def index():
	
	on = '[B][COLOR green]ON[/COLOR][/B]'; off = '[B][COLOR red]OFF[/COLOR][/B]'
	autoclean   = 'true' if AUTOCLEANUP    == 'true' else 'false'
	cache       = 'true' if AUTOCACHE      == 'true' else 'false'
	packages    = 'true' if AUTOPACKAGES   == 'true' else 'false'
	thumbs      = 'true' if AUTOTHUMBS     == 'true' else 'false'
	maint       = 'true' if SHOWMAINT      == 'true' else 'false'
	includevid  = 'true' if INCLUDEVIDEO   == 'true' else 'false'
	includeall  = 'true' if INCLUDEALL     == 'true' else 'false'
	if wiz.Grab_Log(True) == False: kodilog = 0
	else: kodilog = errorChecking(wiz.Grab_Log(True), True, True)
	if wiz.Grab_Log(True, True) == False: kodioldlog = 0
	else: kodioldlog = errorChecking(wiz.Grab_Log(True,True), True, True)
	errorsinlog = int(kodilog) + int(kodioldlog)
	errorsfound = str(errorsinlog) + ' Error(s) Found' if errorsinlog > 0 else 'None Found'
	wizlogsize = ': [COLOR red]Not Found[/COLOR]' if not os.path.exists(WIZLOG) else ": [COLOR green]%s[/COLOR]" % wiz.convertSize(os.path.getsize(WIZLOG))
	if includeall == 'true':
		includebob = 'true'
		includebobp = 'true'
		includepho = 'true'
		includespe = 'true'
		includespes = 'true'
		includegen = 'true'
		includeexo = 'true'
		includeexop = 'true'
		includeone = 'true'
		includesal = 'true'
		includeshd = 'true'
	else:
		includebob = 'true' if INCLUDEBOB     == 'true' else 'false'
		includebobp = 'true' if INCLUDEBOBP     == 'true' else 'false'
		includepho = 'true' if INCLUDEPHOENIX == 'true' else 'false'
		includespe = 'true' if INCLUDESPECTO  == 'true' else 'false'
		includespes = 'true' if INCLUDESPECTOS  == 'true' else 'false'
		includegen = 'true' if INCLUDEGENESIS == 'true' else 'false'
		includeexo = 'true' if INCLUDEEXODUS  == 'true' else 'false'
		includeexop = 'true' if INCLUDEEXODUSP  == 'true' else 'false'
		includeone = 'true' if INCLUDEONECHAN == 'true' else 'false'
		includesal = 'true' if INCLUDESALTS   == 'true' else 'false'
		includeshd = 'true' if INCLUDESALTSHD == 'true' else 'false'
	sizepack   = wiz.getSize(PACKAGES)
	sizethumb  = wiz.getSize(THUMBS)
	sizecache  = wiz.getCacheSize()
	totalsize  = sizepack+sizethumb+sizecache
	feq        = ['Always', 'Daily', '3 Days', 'Weekly', 'Monthly']
	addDir ('[B]Cleaning Tools[/B]'       ,'', '',  icon=ICONMAINT, themeit=THEME1)

	addFile('Total Clean Up: [COLOR green][B]%s[/B][/COLOR]' % wiz.convertSize(totalsize)  ,'fullclean',       icon=ICONMAINT, themeit=THEME3)
	addFile('Clear Cache: [COLOR green][B]%s[/B][/COLOR]' % wiz.convertSize(sizecache)     ,'clearcache',      icon=ICONMAINT, themeit=THEME3)
	addFile('Clear Packages: [COLOR green][B]%s[/B][/COLOR]' % wiz.convertSize(sizepack)   ,'clearpackages',   icon=ICONMAINT, themeit=THEME3)
	addFile('Clear Thumbnails: [COLOR green][B]%s[/B][/COLOR]' % wiz.convertSize(sizethumb),'clearthumb',      icon=ICONMAINT, themeit=THEME3)
	addFile('Clear Old Thumbnails', 'oldThumbs',      icon=ICONMAINT, themeit=THEME3)
	addFile('Clear Crash Logs',               'clearcrash',      icon=ICONMAINT, themeit=THEME3)
	addFile('Purge Databases',                'purgedb',         icon=ICONMAINT, themeit=THEME3)
	addFile('Fresh Start,[COLOR red][B] WARNING This will wipe your Kodi data[/COLOR][/B]','freshstart', icon=ICONMAINT, themeit=THEME3)
	
	if HIDESPACERS == 'No': addFile(wiz.sep(), '', themeit=THEME3)
	addDir ('[B]Maintenance Tools[/B]'   ,'',    icon=ICONMAINT,    themeit=THEME1)
	addFile('Test only 1',  'test1',   icon=ICONMAINT, themeit=THEME3)
	addFile('Test 2run',  'test2',   icon=ICONMAINT, themeit=THEME3)
	addFile('Scan Sources for broken links',  'checksources',    icon=ICONMAINT, themeit=THEME3)
	addFile('Scan For Broken Repositories',   'checkrepos',      icon=ICONMAINT, themeit=THEME3)
	addFile('Remove Non-Ascii filenames',     'asciicheck',      icon=ICONMAINT, themeit=THEME3)
	addFile('Convert Paths to special',       'convertpath',     icon=ICONMAINT, themeit=THEME3)
	addFile('Show my IP address',  				'getip',   		 icon=ICONMAINT, themeit=THEME3)
	addFile('View Kodi Log',  			'viewlogfile',    	 icon=ICONMAINT, themeit=THEME3)
	addDir ('System Information',             'systeminfo',      icon=ICONMAINT, themeit=THEME3)

	if HIDESPACERS == 'No': addFile(wiz.sep(), '', themeit=THEME3)	
	addFile('Settings'      ,'settings', icon=ICONSETTINGS, themeit=THEME1)
	
	setView('files', 'viewType')
###############TEST AREA###################
###########################################
def testOne():
    print '############################################################       DELETING STANDARD CACHE             ###############################################################'
    xbmc_cache_path = os.path.join(xbmc.translatePath('special://home'), 'cache')
    if os.path.exists(xbmc_cache_path)==True:    
        for root, dirs, files in os.walk(xbmc_cache_path):
            file_count = 0
            file_count += len(files)
        
        # Count files and give option to delete
            if file_count > 0:
    
                dialog = xbmcgui.Dialog()
                if dialog.yesno("Delete Kodi Cache Files", str(file_count) + " files found", "Do you want to delete them?"):
                
                    for f in files:
                        try:
                            os.unlink(os.path.join(root, f))
                        except:
                            pass
                    for d in dirs:
                        try:
                            shutil.rmtree(os.path.join(root, d))
                        except:
                            pass
                        
            else:
                pass
    xbmc_cache_path = os.path.join(xbmc.translatePath('special://home'), 'temp')
    if os.path.exists(xbmc_cache_path)==True:    
        for root, dirs, files in os.walk(xbmc_cache_path):
            file_count = 0
            file_count += len(files)
        
        # Count files and give option to delete
            if file_count > 0:
    
                dialog = xbmcgui.Dialog()
                if dialog.yesno("Delete Kodi Temp Files", str(file_count) + " files found", "Do you want to delete them?"):
                
                    for f in files:
                        try:
                            os.unlink(os.path.join(root, f))
                        except:
                            pass
                    for d in dirs:
                        try:
                            shutil.rmtree(os.path.join(root, d))
                        except:
                            pass
                        
            else:
                pass            

                
                # Set path to BBC iPlayer cache files
    iplayer_cache_path= os.path.join(xbmc.translatePath('special://profile/addon_data/plugin.video.iplayer/iplayer_http_cache'), '')
    if os.path.exists(iplayer_cache_path)==True:    
        for root, dirs, files in os.walk(iplayer_cache_path):
            file_count = 0
            file_count += len(files)
        
        # Count files and give option to delete
            if file_count > 0:
    
                dialog = xbmcgui.Dialog()
                if dialog.yesno("Delete BBC iPlayer Cache Files", str(file_count) + " files found", "Do you want to delete them?"):
                
                    for f in files:
                        os.unlink(os.path.join(root, f))
                    for d in dirs:
                        shutil.rmtree(os.path.join(root, d))
                        
            else:
                pass

    dialog = xbmcgui.Dialog()
    dialog.ok("GeeTee Cleaner", "     Done", "          [COLOR green]Bye...[/COLOR]")
	
	
####################22222222222222222222222################
def testRun():
	#xbmc.executebuiltin('XBMC.RunScript(special://home/addons/plugin.program.geeteecleaner/resources/speed/default.py')
#runs a plugin:
	xbmc.executebuiltin('XBMC.RunScript(special://home/addons/script.kodispeedtest/default.py)')
# files.append(os.path.join(ADDOND, 'plugin.video.bob', 'cache.db'))
# xbmc.executebuiltin('XBMC.RunScript(/resources/libs/speed/default.py)')

#xbmc.executebuiltin('XBMC.RunPlugin(plugin://plugin.program.jdownloader/?action=addlink&url=http://www.abc.com/test.rar)')


##	__addon__ = xbmcaddon.Addon()
##	__addonname__ = __addon__.getAddonInfo('name')
##__icon__ = __addon__.getAddonInfo('icon')
 ##
#	line1 = "This is a simple example of notifications"
#	time = 5000 #in miliseconds
# 
#	xbmc.executebuiltin('Notification(%s, %s, %d, %s)'%(__addonname__,line1, time, __icon__))
#
#
#	__addon__ = xbmcaddon.Addon()
#	__addonname__ = __addon__.getAddonInfo('name')
#
#	line1 = "This is a simple example of OK dialog"
#	line2 = "Showing this message using"
#	line3 = "XBMC python modules"
#
#	xbmcgui.Dialog().ok(__addonname__, line1, line2, line3)
#	
	


    
###############TEST AREA END###################
###########################################

def getIP():
	site  = 'http://whatismyipaddress.com/'
	if not wiz.workingURL(site): return 'Unknown', 'Unknown', 'Unknown'
	page  = wiz.openURL(site).replace('\n','').replace('\r','')
	if not 'Access Denied' in page:
		ipmatch   = re.compile('whatismyipaddress.com/ip/(.+?)"').findall(page)
		ipfinal   = ipmatch[0] if (len(ipmatch) > 0) else 'Unknown'
		details   = re.compile('"font-size:14px;">(.+?)</td>').findall(page)
		provider  = details[0] if (len(details) > 0) else 'Unknown'
		location  = details[1]+', '+details[2]+', '+details[3] if (len(details) > 2) else 'Unknown'
		return ipfinal, provider, location
	else: return 'Unknown', 'Unknown', 'Unknown'

def systemInfo():
	infoLabel = ['System.FriendlyName', 
				 'System.BuildVersion', 
				 'System.CpuUsage',
				 'System.ScreenMode',
				 'Network.IPAddress',
				 'Network.MacAddress',
				 'System.Uptime',
				 'System.TotalUptime',
				 'System.FreeSpace',
				 'System.UsedSpace',
				 'System.TotalSpace',
				 'System.Memory(free)',
				 'System.Memory(used)',
				 'System.Memory(total)']
	data      = []; x = 0
	for info in infoLabel:
		temp = wiz.getInfo(info)
		y = 0
		while temp == "Busy" and y < 10:
			temp = wiz.getInfo(info); y += 1; wiz.log("%s sleep %s" % (info, str(y))); xbmc.sleep(200)
		data.append(temp)
		x += 1
	storage_free  = data[8] if 'Una' in data[8] else wiz.convertSize(int(float(data[8][:-8]))*1024*1024)
	storage_used  = data[9] if 'Una' in data[9] else wiz.convertSize(int(float(data[9][:-8]))*1024*1024)
	storage_total = data[10] if 'Una' in data[10] else wiz.convertSize(int(float(data[10][:-8]))*1024*1024)
	ram_free      = wiz.convertSize(int(float(data[11][:-2]))*1024*1024)
	ram_used      = wiz.convertSize(int(float(data[12][:-2]))*1024*1024)
	ram_total     = wiz.convertSize(int(float(data[13][:-2]))*1024*1024)
	exter_ip, provider, location = getIP()
	
	picture = []; music = []; video = []; programs = []; repos = []; scripts = []; skins = []
	
	fold = glob.glob(os.path.join(ADDONS, '*/'))
	for folder in sorted(fold, key = lambda x: x):
		foldername = os.path.split(folder[:-1])[1]
		if foldername == 'packages': continue
		xml = os.path.join(folder, 'addon.xml')
		if os.path.exists(xml):
			f      = open(xml)
			a      = f.read()
			prov   = re.compile("<provides>(.+?)</provides>").findall(a)
			if len(prov) == 0:
				if foldername.startswith('skin'): skins.append(foldername)
				if foldername.startswith('repo'): repos.append(foldername)
				else: scripts.append(foldername)
			elif not (prov[0]).find('executable') == -1: programs.append(foldername)
			elif not (prov[0]).find('video') == -1: video.append(foldername)
			elif not (prov[0]).find('audio') == -1: music.append(foldername)
			elif not (prov[0]).find('image') == -1: picture.append(foldername)

	addFile('[B]System Info:[/B]', '', icon=ICONMAINT, themeit=THEME2)
	addFile('[COLOR %s]Name:[/COLOR] [COLOR %s]%s[/COLOR]' % (COLOR1, COLOR2, data[0]), '', icon=ICONMAINT, themeit=THEME3)
	addFile('[COLOR %s]Version:[/COLOR] [COLOR %s]%s[/COLOR]' % (COLOR1, COLOR2, data[1]), '', icon=ICONMAINT, themeit=THEME3)
	addFile('[COLOR %s]Platform:[/COLOR] [COLOR %s]%s[/COLOR]' % (COLOR1, COLOR2, wiz.platform().title()), '', icon=ICONMAINT, themeit=THEME3)
	addFile('[COLOR %s]CPU Usage:[/COLOR] [COLOR %s]%s[/COLOR]' % (COLOR1, COLOR2, data[2]), '', icon=ICONMAINT, themeit=THEME3)
	addFile('[COLOR %s]Screen Mode:[/COLOR] [COLOR %s]%s[/COLOR]' % (COLOR1, COLOR2, data[3]), '', icon=ICONMAINT, themeit=THEME3)
	
	addFile('[B]Uptime:[/B]', '', icon=ICONMAINT, themeit=THEME2)
	addFile('[COLOR %s]Current Uptime:[/COLOR] [COLOR %s]%s[/COLOR]' % (COLOR1, COLOR2, data[6]), '', icon=ICONMAINT, themeit=THEME2)
	addFile('[COLOR %s]Total Uptime:[/COLOR] [COLOR %s]%s[/COLOR]' % (COLOR1, COLOR2, data[7]), '', icon=ICONMAINT, themeit=THEME2)
	
	addFile('[B]Local Storage:[/B]', '', icon=ICONMAINT, themeit=THEME2)
	addFile('[COLOR %s]Used Storage:[/COLOR] [COLOR %s]%s[/COLOR]' % (COLOR1, COLOR2, storage_free), '', icon=ICONMAINT, themeit=THEME2)
	addFile('[COLOR %s]Free Storage:[/COLOR] [COLOR %s]%s[/COLOR]' % (COLOR1, COLOR2, storage_used), '', icon=ICONMAINT, themeit=THEME2)
	addFile('[COLOR %s]Total Storage:[/COLOR] [COLOR %s]%s[/COLOR]' % (COLOR1, COLOR2, storage_total), '', icon=ICONMAINT, themeit=THEME2)
	
	addFile('[B]Ram Usage:[/B]', '', icon=ICONMAINT, themeit=THEME2)
	addFile('[COLOR %s]Used Memory:[/COLOR] [COLOR %s]%s[/COLOR]' % (COLOR1, COLOR2, ram_free), '', icon=ICONMAINT, themeit=THEME2)
	addFile('[COLOR %s]Free Memory:[/COLOR] [COLOR %s]%s[/COLOR]' % (COLOR1, COLOR2, ram_used), '', icon=ICONMAINT, themeit=THEME2)
	addFile('[COLOR %s]Total Memory:[/COLOR] [COLOR %s]%s[/COLOR]' % (COLOR1, COLOR2, ram_total), '', icon=ICONMAINT, themeit=THEME2)
	
	addFile('[B]Network:[/B]', '', icon=ICONMAINT, themeit=THEME2)
	addFile('[COLOR %s]Local IP:[/COLOR] [COLOR %s]%s[/COLOR]' % (COLOR1, COLOR2, data[4]), '', icon=ICONMAINT, themeit=THEME2)
	addFile('[COLOR %s]External IP:[/COLOR] [COLOR %s]%s[/COLOR]' % (COLOR1, COLOR2, exter_ip), '', icon=ICONMAINT, themeit=THEME2)
	addFile('[COLOR %s]Provider:[/COLOR] [COLOR %s]%s[/COLOR]' % (COLOR1, COLOR2, provider), '', icon=ICONMAINT, themeit=THEME2)
	addFile('[COLOR %s]Location:[/COLOR] [COLOR %s]%s[/COLOR]' % (COLOR1, COLOR2, location), '', icon=ICONMAINT, themeit=THEME2)
	addFile('[COLOR %s]MacAddress:[/COLOR] [COLOR %s]%s[/COLOR]' % (COLOR1, COLOR2, data[5]), '', icon=ICONMAINT, themeit=THEME2)
	
	totalcount = len(picture) + len(music) + len(video) + len(programs) + len(scripts) + len(skins) + len(repos) 
	addFile('[B]Addons([COLOR %s]%s[/COLOR]):[/B]' % (COLOR1, totalcount), '', icon=ICONMAINT, themeit=THEME2)
	addFile('[COLOR %s]Video Addons:[/COLOR] [COLOR %s]%s[/COLOR]' % (COLOR1, COLOR2, str(len(video))), '', icon=ICONMAINT, themeit=THEME2)
	addFile('[COLOR %s]Program Addons:[/COLOR] [COLOR %s]%s[/COLOR]' % (COLOR1, COLOR2, str(len(programs))), '', icon=ICONMAINT, themeit=THEME2)
	addFile('[COLOR %s]Music Addons:[/COLOR] [COLOR %s]%s[/COLOR]' % (COLOR1, COLOR2, str(len(music))), '', icon=ICONMAINT, themeit=THEME2)
	addFile('[COLOR %s]Picture Addons:[/COLOR] [COLOR %s]%s[/COLOR]' % (COLOR1, COLOR2, str(len(picture))), '', icon=ICONMAINT, themeit=THEME2)
	addFile('[COLOR %s]Repositories:[/COLOR] [COLOR %s]%s[/COLOR]' % (COLOR1, COLOR2, str(len(repos))), '', icon=ICONMAINT, themeit=THEME2)
	addFile('[COLOR %s]Skins:[/COLOR] [COLOR %s]%s[/COLOR]' % (COLOR1, COLOR2, str(len(skins))), '', icon=ICONMAINT, themeit=THEME2)
	addFile('[COLOR %s]Scripts/Modules:[/COLOR] [COLOR %s]%s[/COLOR]' % (COLOR1, COLOR2, str(len(scripts))), '', icon=ICONMAINT, themeit=THEME2)

def changeFeq():
	feq        = ['Every Startup', 'Every Day', 'Every Three Days', 'Every Weekly', 'Monthly']
	change     = DIALOG.select("[COLOR %s]How often would you list to Auto Clean on Startup?[/COLOR]" % COLOR2, feq)
	if not change == -1: 
		wiz.setS('autocleanfeq', str(change))
		wiz.LogNotify('[COLOR %s]Auto Clean Up[/COLOR]' % COLOR1, '[COLOR %s]Fequency Now %s[/COLOR]' % (COLOR2, feq[change]))
###########################
###### Misc Functions######
###########################

def toggleCache(state):
	cachelist = ['includevideo', 'includeall', 'includebob', 'includebobp', 'includephoenix', 'includespecto', 'includespectos', 'includegenesis', 'includeexodus', 'includeexodusp', 'includeonechan', 'includesalts', 'includesaltslite']
	titlelist = ['Include Video Addons', 'Include All Addons', 'Include BobP', 'Include Bob', 'Include Phoenix', 'Include Specto', 'Include SpectoS','Include Genesis', 'Include Exodus', 'Include ExodusP', 'Include One Channel', 'Include Salts', 'Include Salts Lite HD']
	if state in ['true', 'false']:
		for item in cachelist:
			wiz.setS(item, state)
	else:
		if not state in ['includevideo', 'includeall'] and wiz.getS('includeall') == 'true':
			try:
				item = titlelist[cachelist.index(state)]
				DIALOG.ok(ADDONTITLE, "[COLOR %s]You will need to turn off [COLOR %s]Include All Addons[/COLOR] to disable[/COLOR] [COLOR %s]%s[/COLOR]" % (COLOR2, COLOR1, COLOR1, item))
			except:
				wiz.LogNotify("[COLOR %s]Toggle Cache[/COLOR]" % COLOR1, "[COLOR %s]Invalid id: %s[/COLOR]" % (COLOR2, state))
		else:
			new = 'true' if wiz.getS(state) == 'false' else 'false'
			wiz.setS(state, new)


def viewLogFile():
	mainlog = wiz.Grab_Log(True)
	oldlog  = wiz.Grab_Log(True, True)
	which = 0; logtype = mainlog
	if not oldlog == False and not mainlog == False:
		which = DIALOG.select(ADDONTITLE, ["View %s" % mainlog.replace(LOG, ""), "View %s" % oldlog.replace(LOG, "")])
		if which == -1: wiz.LogNotify('[COLOR %s]View Log[/COLOR]' % COLOR1, '[COLOR %s]View Log Cancelled![/COLOR]' % COLOR2); return
	elif mainlog == False and oldlog == False:
		wiz.LogNotify('[COLOR %s]View Log[/COLOR]' % COLOR1, '[COLOR %s]No Log File Found![/COLOR]' % COLOR2)
		return
	elif not mainlog == False: which = 0
	elif not oldlog == False: which = 1
	
	logtype = mainlog if which == 0 else oldlog
	msg     = wiz.Grab_Log(False) if which == 0 else wiz.Grab_Log(False, True)
	
	wiz.TextBox("%s - %s" % (ADDONTITLE, logtype), msg)

def errorChecking(log=None, count=None, all=None):
	if log == None:
		mainlog = wiz.Grab_Log(True)
		oldlog  = wiz.Grab_Log(True, True)
		if not oldlog == False and not mainlog == False:
			which = DIALOG.select(ADDONTITLE, ["View %s: %s error(s)" % (mainlog.replace(LOG, ""), errorChecking(mainlog, True, True)), "View %s: %s error(s)" % (oldlog.replace(LOG, ""), errorChecking(oldlog, True, True))])
			if which == -1: wiz.LogNotify('[COLOR %s]View Log[/COLOR]' % COLOR1, '[COLOR %s]View Log Cancelled![/COLOR]' % COLOR2); return
		elif mainlog == False and oldlog == False:
			wiz.LogNotify('[COLOR %s]View Log[/COLOR]' % COLOR1, '[COLOR %s]No Log File Found![/COLOR]' % COLOR2)
			return
		elif not mainlog == False: which = 0
		elif not oldlog == False: which = 1
		log = mainlog if which == 0 else oldlog
	if log == False:
		if count == None:
			wiz.LogNotify("[COLOR %s]%s[/COLOR]" % (COLOR1, ADDONTITLE), "[COLOR %s]Log File not Found[/COLOR]" % COLOR2)
			return False
		else: 
			return 0
	else:
		if os.path.exists(log):
			f = open(log,mode='r'); a = f.read().replace('\n', '').replace('\r', ''); f.close()
			match = re.compile("-->Python callback/script returned the following error<--(.+?)-->End of Python script error report<--").findall(a)
			if not count == None:
				if all == None: 
					x = 0
					for item in match:
						if ADDON_ID in item: x += 1
					return x
				else: return len(match)
			if len(match) > 0:
				x = 0; msg = ""
				for item in match:
					if all == None and not ADDON_ID in item: continue
					else: 
						x += 1
						msg += "[COLOR red]Error Number %s[/COLOR]\n(PythonToCppException) : -->Python callback/script returned the following error<--%s-->End of Python script error report<--\n\n" % (x, item.replace('                                          ', '\n').replace('\\\\','\\').replace(HOME, ''))
				if x > 0:
					wiz.TextBox(ADDONTITLE, msg)
				else: wiz.LogNotify(ADDONTITLE, "No Errors Found in Log")
			else: wiz.LogNotify(ADDONTITLE, "No Errors Found in Log")
		else: wiz.LogNotify(ADDONTITLE, "Log File not Found")

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

def LogViewer(default=None):
	class LogViewer(xbmcgui.WindowXMLDialog):
		def __init__(self,*args,**kwargs):
			self.default = kwargs['default']

		def onInit(self):
			self.title      = 101
			self.msg        = 102
			self.scrollbar  = 103
			self.upload     = 201
			self.kodi       = 202
			self.kodiold    = 203
			self.wizard     = 204 
			self.okbutton   = 205 
			f = open(self.default, 'r')
			self.logmsg = f.read()
			f.close()
			self.titlemsg = "%s: %s" % (ADDONTITLE, self.default.replace(LOG, '').replace(ADDONDATA, ''))
			self.showdialog()

		def showdialog(self):
			self.getControl(self.title).setLabel(self.titlemsg)
			self.getControl(self.msg).setText(wiz.highlightText(self.logmsg))
			self.setFocusId(self.scrollbar)
			
		def onClick(self, controlId):
			if   controlId == self.okbutton: self.close()
			elif controlId == self.upload: self.close(); uploadLog.Main()
			elif controlId == self.kodi:
				newmsg = wiz.Grab_Log(False)
				filename = wiz.Grab_Log(True)
				if newmsg == False:
					self.titlemsg = "%s: View Log Error" % ADDONTITLE
					self.getControl(self.msg).setText("Log File Does Not Exists!")
				else:
					self.titlemsg = "%s: %s" % (ADDONTITLE, filename.replace(LOG, ''))
					self.getControl(self.title).setLabel(self.titlemsg)
					self.getControl(self.msg).setText(wiz.highlightText(newmsg))
					self.setFocusId(self.scrollbar)
			elif controlId == self.kodiold:  
				newmsg = wiz.Grab_Log(False, True)
				filename = wiz.Grab_Log(True, True)
				if newmsg == False:
					self.titlemsg = "%s: View Log Error" % ADDONTITLE
					self.getControl(self.msg).setText("Log File Does Not Exists!")
				else:
					self.titlemsg = "%s: %s" % (ADDONTITLE, filename.replace(LOG, ''))
					self.getControl(self.title).setLabel(self.titlemsg)
					self.getControl(self.msg).setText(wiz.highlightText(newmsg))
					self.setFocusId(self.scrollbar)
			elif controlId == self.wizard:
				newmsg = wiz.Grab_Log(False, False, True)
				filename = wiz.Grab_Log(True, False, True)
				if newmsg == False:
					self.titlemsg = "%s: View Log Error" % ADDONTITLE
					self.getControl(self.msg).setText("Log File Does Not Exists!")
				else:
					self.titlemsg = "%s: %s" % (ADDONTITLE, filename.replace(ADDONDATA, ''))
					self.getControl(self.title).setLabel(self.titlemsg)
					self.getControl(self.msg).setText(wiz.highlightText(newmsg))
					self.setFocusId(self.scrollbar)
		
		def onAction(self, action):
			if   action == ACTION_PREVIOUS_MENU: self.close()
			elif action == ACTION_NAV_BACK: self.close()
	if default == None: default = wiz.Grab_Log(True)
	lv = LogViewer( "LogViewer.xml" , ADDON.getAddonInfo('path'), 'DefaultSkin', default=default)
	lv.doModal()
	del lv


def dependsList(plugin):
	addonxml = os.path.join(ADDONS, plugin, 'addon.xml')
	if os.path.exists(addonxml):
		source = open(addonxml,mode='r'); link = source.read(); source.close(); 
		match  = wiz.parseDOM(link, 'import', ret='addon')
		items  = []
		for depends in match:
			if not 'xbmc.python' in depends:
				items.append(depends)
		return items
	return []


#############################
###DELETE CACHE##############
####THANKS GUYS @ NaN #######
def clearCache():
	if DIALOG.yesno(ADDONTITLE, '[COLOR %s]Would you like to clear cache?[/COLOR]' % COLOR2, nolabel='[B][COLOR red]No, Cancel[/COLOR][/B]', yeslabel='[B][COLOR green]Clear Cache[/COLOR][/B]'):
		wiz.clearCache()
		#clearThumb()

def totalClean():
	if DIALOG.yesno(ADDONTITLE, '[COLOR %s]Would you like to clear cache, packages and thumbnails?[/COLOR]' % COLOR2, nolabel='[B][COLOR red]Cancel Process[/COLOR][/B]',yeslabel='[B][COLOR green]Clean All[/COLOR][/B]'):
		wiz.clearCache()
		wiz.clearPackages('total')
		clearThumb('total')

def clearThumb(type=None):
	latest = wiz.latestDB('Textures')
	if not type == None: choice = 1
	else: choice = DIALOG.yesno(ADDONTITLE, '[COLOR %s]Would you like to delete the %s and Thumbnails folder?' % (COLOR2, latest), "They will repopulate on the next startup[/COLOR]", nolabel='[B][COLOR red]Don\'t Delete[/COLOR][/B]', yeslabel='[B][COLOR green]Delete Thumbs[/COLOR][/B]')
	if choice == 1:
		try: wiz.removeFile(os.join(DATABASE, latest))
		except: wiz.log('Failed to delete, Purging DB.'); wiz.purgeDb(latest)
		wiz.removeFolder(THUMBS)
		#if not type == 'total': wiz.killxbmc()
	else: wiz.log('Clear thumbnames cancelled')
	wiz.redoThumbs()

def purgeDb():
	DB = []; display = []
	for dirpath, dirnames, files in os.walk(HOME):
		for f in fnmatch.filter(files, '*.db'):
			if f != 'Thumbs.db':
				found = os.path.join(dirpath, f)
				DB.append(found)
				dir = found.replace('\\', '/').split('/')
				display.append('(%s) %s' % (dir[len(dir)-2], dir[len(dir)-1]))
	if KODIV >= 16: 
		choice = DIALOG.multiselect("[COLOR %s]Select DB File to Purge[/COLOR]" % COLOR2, display)
		if choice == None: wiz.LogNotify("[COLOR %s]Purge Database[/COLOR]" % COLOR1, "[COLOR %s]Cancelled[/COLOR]" % COLOR2)
		elif len(choice) == 0: wiz.LogNotify("[COLOR %s]Purge Database[/COLOR]" % COLOR1, "[COLOR %s]Cancelled[/COLOR]" % COLOR2)
		else: 
			for purge in choice: wiz.purgeDb(DB[purge])
	else:
		choice = DIALOG.select("[COLOR %s]Select DB File to Purge[/COLOR]" % COLOR2, display)
		if choice == -1: wiz.LogNotify("[COLOR %s]Purge Database[/COLOR]" % COLOR1, "[COLOR %s]Cancelled[/COLOR]" % COLOR2)
		else: wiz.purgeDb(DB[purge])



###########################
## Making the Directory####
###########################

def addDir(display, mode=None, name=None, url=None, menu=None, description=ADDONTITLE, overwrite=True, fanart=FANART, icon=ICON, themeit=None):
	u = sys.argv[0]
	if not mode == None: u += "?mode=%s" % urllib.quote_plus(mode)
	if not name == None: u += "&name="+urllib.quote_plus(name)
	if not url == None: u += "&url="+urllib.quote_plus(url)
	ok=True
	if themeit: display = themeit % display
	liz=xbmcgui.ListItem(display, iconImage="DefaultFolder.png", thumbnailImage=icon)
	liz.setInfo( type="Video", infoLabels={ "Title": display, "Plot": description} )
	liz.setProperty( "Fanart_Image", fanart )
	if not menu == None: liz.addContextMenuItems(menu, replaceItems=overwrite)
	ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=True)
	return ok

def addFile(display, mode=None, name=None, url=None, menu=None, description=ADDONTITLE, overwrite=True, fanart=FANART, icon=ICON, themeit=None):
	u = sys.argv[0]
	if not mode == None: u += "?mode=%s" % urllib.quote_plus(mode)
	if not name == None: u += "&name="+urllib.quote_plus(name)
	if not url == None: u += "&url="+urllib.quote_plus(url)
	ok=True
	if themeit: display = themeit % display
	liz=xbmcgui.ListItem(display, iconImage="DefaultFolder.png", thumbnailImage=icon)
	liz.setInfo( type="Video", infoLabels={ "Title": display, "Plot": description} )
	liz.setProperty( "Fanart_Image", fanart )
	if not menu == None: liz.addContextMenuItems(menu, replaceItems=overwrite)
	ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=False)
	return ok

def get_params():
	param=[]
	paramstring=sys.argv[2]
	if len(paramstring)>=2:
		params=sys.argv[2]
		cleanedparams=params.replace('?','')
		if (params[len(params)-1]=='/'):
			params=params[0:len(params)-2]
		pairsofparams=cleanedparams.split('&')
		param={}
		for i in range(len(pairsofparams)):
			splitparams={}
			splitparams=pairsofparams[i].split('=')
			if (len(splitparams))==2:
				param[splitparams[0]]=splitparams[1]

		return param

params=get_params()
url=None
name=None
mode=None

try:     mode=urllib.unquote_plus(params["mode"])
except:  pass
try:     name=urllib.unquote_plus(params["name"])
except:  pass
try:     url=urllib.unquote_plus(params["url"])
except:  pass

wiz.log('[ Version : \'%s\' ] [ Mode : \'%s\' ] [ Name : \'%s\' ] [ Url : \'%s\' ]' % (VERSION, mode if not mode == '' else None, name, url))

def setView(content, viewType):
	if wiz.getS('auto-view')=='true':
		views = wiz.getS(viewType)
		if views == '50' and KODIV >= 17 and SKIN == 'skin.estuary': views = '55'
		if views == '500' and KODIV >= 17 and SKIN == 'skin.estuary': views = '50'
		wiz.ebi("Container.SetViewMode(%s)" %  views)

if   mode==None             : index()

elif mode=='maint'          : maintMenu(name)
elif mode=='asciicheck'     : wiz.asciiCheck()
elif mode=='convertpath'    : wiz.convertSpecial(HOME)
elif mode=='currentsettings': viewAdvanced()
elif mode=='fullclean'      : totalClean(); wiz.refresh()
elif mode=='clearcache'     : clearCache(); wiz.refresh()
elif mode=='clearpackages'  : wiz.clearPackages(); wiz.refresh()
elif mode=='clearcrash'     : wiz.clearCrash(); wiz.refresh()
elif mode=='clearthumb'     : clearThumb(); wiz.refresh()
elif mode=='checksources'   : wiz.checkSources(); wiz.refresh()
elif mode=='checkrepos'     : wiz.checkRepos(); wiz.refresh()
elif mode=='freshstart'     : freshStart()
elif mode=='forceclose'     : wiz.killxbmc()

elif mode=='enableaddons'   : enableAddons()
elif mode=='toggleaddon'    : wiz.toggleAddon(name, url); wiz.refresh()
elif mode=='togglecache'    : toggleCache(name); wiz.refresh()
elif mode=='changefeq'      : changeFeq(); wiz.refresh()
elif mode=='uploadlog'      : uploadLog.Main()
elif mode=='viewlog'        : LogViewer()
elif mode=='purgedb'        : purgeDb()

elif mode=='test1'   		: testOne()
elif mode=='test2'   		: testRun()
elif mode=='systeminfo'     : systemInfo()
elif mode=='viewlogfile'    : viewLogFile()
elif mode=='getip'   		: getIP()
elif mode=='settings'       : wiz.openS(name); wiz.refresh()
elif mode=='opensettings'   : id = eval(url.upper()+'ID')[name]['plugin']; addonid = wiz.addonId(id); addonid.openSettings(); wiz.refresh()


xbmcplugin.endOfDirectory(int(sys.argv[1]))