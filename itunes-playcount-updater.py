#
#	iTunes Playcount Updater
#
#	This program is free software: you can redistribute it and/or modify
#	it under the terms of the GNU General Public License as published by
#	the Free Software Foundation, either version 3 of the License, or
#	(at your option) any later version.
#
#	This program is distributed in the hope that it will be useful,
#	but WITHOUT ANY WARRANTY; without even the implied warranty of
#	MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#	GNU General Public License for more details.
#
#	You should have received a copy of the GNU General Public License
#	along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#
#	INSTRUCTIONS:
#	----------------------------------------------------------------------------
#	This script downloads your Last.FM play history and updates the playcount
#	for all tracks it can find in your library. Anything missing will be put
#	into a separate text file so that you can reobtain the track if you wish
#
#	Requirements:
#		pywin32
#		BeautifulSoup

#Strange or International characters will be either replaced or removed. Map them here
strangeCharacterMap = ({ 
	u"\u042f" : "r" #Korn's crazy R
})

import sys
import win32com.client
import urllib
from BeautifulSoup import BeautifulSoup
import logging
import unicodedata
import sets

defaultPlaylistName = "Similar"
lastFMUrl = "http://ws.audioscrobbler.com/2.0/?method="

apiKey = "21edbb30193dc36e6fb21cc57b1d8e18"
itunes = None
libraryPlaylist = None

username = ""

def getTracks(page):
	logging.info("Getting page " + str(page))
	
	url = lastFMUrl + "library.gettracks&api_key=" + apiKey + "&user=" + username + "&page=" + str(page)
	data = urllib.urlopen(url).read()
	soup = BeautifulSoup(data)
	
	totalpages = int(soup.find("tracks")["totalpages"])
	
	tracks_soup = soup.findAll("track")
	
	tracks = {}
	
	for t in tracks_soup:
		name = t.find("name").next.replace("&amp;", "&").replace("&quot;", "\"")
		artist = t.find("artist").find("name").next.replace("&amp;", "&").replace("&quot;", "\"")
		plays = int(t.find("playcount").next)
		
		tracks[artist + " " + name] = [artist, name, plays]
		
	return (tracks, totalpages)

def main():
	global username
	
	missing = []
	
	logging.basicConfig(level=logging.DEBUG,format='%(asctime)s %(levelname)s %(message)s',
							filename='debug.log', filemode='w')
							
	username = raw_input("Last.FM Username: ")
							
	itunes = win32com.client.gencache.EnsureDispatch("iTunes.Application")
	libraryPlaylist = itunes.LibraryPlaylist
	
	page = 0
	
	tracks, pages = getTracks(1)
	
	logging.info("Pages: " + str(pages))
	
	
	
	while page < pages:
		page = page + 1
		tracks, x = getTracks(page)
		
		print "Page: " + str(page) + " / " + str(pages)
		
		for track in tracks:
			search = libraryPlaylist.Search(track, 1)
			if search == None:
				missing.append(tracks[track][0] + " - " + tracks[track][1])
			else:
				for x in search:
					if x.Artist.lower() == tracks[track][0].lower() and x.Name.lower() == tracks[track][1].lower():
						logging.debug("Updating " + tracks[track][0] + " - " + tracks[track][1] + " with playcount: " + str(tracks[track][2]))
						x.PlayedCount = tracks[track][2]
						
		

	
	f = open("missing.txt", "a")
	missing = sets.Set(missing)
	for x in missing:
		f.write(unicodedata.normalize("NFKD", x).encode("ascii", "ignore") + "\n")
	f.close()
	
if __name__ == "__main__":
	main()
	print "Completed"
