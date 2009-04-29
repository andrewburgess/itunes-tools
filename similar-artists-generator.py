#
#	Similar Artists Playlist Generator
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
#	This script builds an iTunes playlist by having the user pick a seed song
#	and then traversing Last.FM's similar artists, and pulling the list of top
#	tracks from each similar artist, and adding them to the playlist if the user
#	has that song. It will build a playlist of MAX_TRACKS size
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

defaultPlaylistName = "Similar"
lastFMUrl = "http://ws.audioscrobbler.com/2.0/?method="

apiKey = "21edbb30193dc36e6fb21cc57b1d8e18"
itunes = None
libraryPlaylist = None

similarArtists = {}
artistTracks = {}
missingTracks = []
	
def getSimilarArtists(artist, limit = 50):
	logging.info("Finding Similar Artists for " + artist)
	
	url = lastFMUrl + "artist.getSimilar&artist=" + urllib.quote(unicodedata.normalize("NFKD", artist).encode("ascii", "ignore")) + "&limit=" + str(limit) + "&api_key=" + apiKey
	data = urllib.urlopen(url).read()
	sa = BeautifulSoup(data)
	
	artistsxml = sa.findAll("name")
	artists = []
	for x in artistsxml:
		logging.debug("Adding Artist: " + urllib.unquote(x.next))
		artists.append(urllib.unquote(x.next))
		
	#print "Found " + str(len(artists)) + " similar artists"
	logging.debug("Found " + str(len(artists)) + " similar artists")
		
	return artists

def main():
	logging.basicConfig(level=logging.DEBUG,format='%(asctime)s %(levelname)s %(message)s',
							filename='debug.log', filemode='w')
	try:
		playlistSize = 0
		
		itunes = win32com.client.gencache.EnsureDispatch("iTunes.Application")
		libraryPlaylist = itunes.LibraryPlaylist
		
		#We have the itunes object, get the playlist name
		playlistName = raw_input("Enter playlist name [Similar]: ")
		if (playlistName == "") : playlistName = defaultPlaylistName
		
		playlist = itunes.CreatePlaylist(playlistName)
		playlist = win32com.client.CastTo(playlist, "IITUserPlaylist")
		
		############################################################################
		#   CONFIG VALUES                                                          #
		############################################################################
		# Change this value to limit the number of tracks an artist can have in the playlist
		MAX_ARTIST_TRACKS			= raw_input("Max tracks per artist [5]: ")
		if MAX_ARTIST_TRACKS == "": MAX_ARTIST_TRACKS = 5
		else: MAX_ARTIST_TRACKS = int(MAX_ARTIST_TRACKS)
		# Number of tracks in the playlist
		MAX_TRACKS					= raw_input("Playlist size [100]: ")
		if MAX_TRACKS == "": MAX_TRACKS = 100
		else: MAX_TRACKS = int(MAX_TRACKS)
		# Starting similar artists
		STARTING_SIMILAR_ARTISTS	= raw_input("Initial number of similar artists [10]: ")
		if STARTING_SIMILAR_ARTISTS == "": STARTING_SIMILAR_ARTISTS = 10
		# Additional similar artists to add to the list when a track is a hit
		ADDITIONAL_SIMILAR_ARTISTS	= raw_input("Additional similar artists to add per track [10]: ")
		if ADDITIONAL_SIMILAR_ARTISTS == "": ADDITIONAL_SIMILAR_ARTISTS = 10
		
		raw_input("\nPlease ensure that at least one track is selected in iTunes...")
		
		tracks = itunes.SelectedTracks
		
		artists = []
		
		for track in tracks:
			playlist.AddTrack(track)
			
			for a in getSimilarArtists(track.Artist):
				artists.append(a)
			
			playlistSize = playlistSize + 1
			
		while len(artists) > 0 and playlistSize < MAX_TRACKS:
			unicodeArtist = artists.pop(0)
			artist = ""
			for x in unicodeArtist:
				if x in strangeCharacterMap:
					artist = artist + strangeCharacterMap[x]
				else:
					artist = artist + x
			
			#print "Queue: " + str(len(artists))
			#Check to see if the artist actually exists in the User's library
			logging.debug("Searching for " + artist)
			t = libraryPlaylist.Search(artist, 2)
			if not t == None:
				#The user has some songs by the artist
				#Check to see if we've already downloaded tracks for the artist
				
				logging.info("Found " + str(t.Count) + " tracks in the library for " + artist)
				#print "Found " + str(t.Count) + " tracks in the library for " + unicodedata.normalize("NFKD", artist).encode("ascii", "ignore")
				
				if not artist in similarArtists:
					#Download tracks for the Artist
					url = lastFMUrl + "artist.getTopTracks&artist=" + urllib.quote(unicodedata.normalize("NFKD", artist).encode("ascii", "ignore")) + "&api_key=" + apiKey
					tt = BeautifulSoup(urllib.urlopen(url).read())
					tts = tt.findAll("track")
					toptracks = []
					for t in tts:
						x = urllib.unquote(t.find("name").next)
						logging.debug("Adding Track: " + x)
						toptracks.append(x)
					artistTracks[artist] = toptracks
					similarArtists[artist] = 0
					logging.debug("Got " + str(len(toptracks)) + " tracks for " + artist)
					#print "Got " + str(len(toptracks)) + " tracks for " + unicodedata.normalize("NFKD", artist).encode("ascii", "ignore")
				
				#Basic Process:
				#	1. Make sure we haven't searched past the end of the list of top tracks
				#	2. Do a general search (search mode 1 guarantees artist and title search)
				#	3. If there are hits, loop through the hits, and check if the fields match the data
				#		- Avoids matching "Hello - Goodbye Song" to "HelloGoodbye - Song"
				#	4. If we have a match, add the track to the playlist
				#	5. Increment the similarArtists[artist] counter, which is the index to the TopTracks list
				foundTrack = False
				#print "Searching iTunes for tracks..."
				while not foundTrack:
					if similarArtists[artist] < MAX_ARTIST_TRACKS and len(artistTracks[artist]) != 0:
						#Make sure we're in range
						logging.debug("Searching for " + artist + " - " + artistTracks[artist][0])
						
						search = (libraryPlaylist.Search(artist + " " + artistTracks[artist][0], 1))
						
						if not search == None:
							logging.debug(str(search.Count) + " hits for " + artist + " - " + artistTracks[artist][0])
							#print str(search.Count) + " hits for " + artist + " - " + artistTracks[artist][0]
							if search.Count > 100:
								logging.debug("Found " + str(search.Count) + " hits, skipping")
								#print "Too many matches, skipping track"
							else:
								for t in search:
									logging.debug("Comparing: " + t.Artist.lower() + " to " + artist.lower())
									logging.debug("Comparing: " + t.Name.lower() + " to " + artistTracks[artist][0].lower())
									if (unicodedata.normalize("NFKD", t.Artist.lower()).encode("ascii", "ignore") == unicodedata.normalize("NFKD", artist.lower()).encode("ascii", "ignore") and 
										t.Name.lower() == artistTracks[artist][0].lower()):
										#Matched
										logging.info("Adding " + t.Artist + " - " + t.Name + " to the playlist")
										#print "Adding " + t.Artist + " - " + t.Name + " to the playlist"
										playlist.AddTrack(t)
										playlistSize = playlistSize + 1
										print "Playlist: " + str(playlistSize) + " / " + str(MAX_TRACKS)
										logging.info("Queue count: " + str(len(artists)))
										if ADDITIONAL_SIMILAR_ARTISTS != 0:
											for a in getSimilarArtists(t.Artist, ADDITIONAL_SIMILAR_ARTISTS):
												artists.append(a)
										foundTrack = True
										similarArtists[artist] = similarArtists[artist] + 1
						else:
							missingTracks.append(artist + " - " + artistTracks[artist][0])
							
						artistTracks[artist].pop(0)
						
					else:
						foundTrack = True
						
			else:
				missingTracks.append(artist)				

		f = open("missing.txt", "a")
		for x in missingTracks:
			f.write(unicodedata.normalize("NFKD", x).encode("ascii", "ignore") + "\n")
		f.close()
	except Exception, err:
		print "Fatal Exception, check debug.log"
		logging.error(err)



if __name__ == "__main__":
	main()
	print "Completed"
