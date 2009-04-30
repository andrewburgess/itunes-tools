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
	
def getSimilarTracks(artist, track, limit = 50):
	logging.info("Finding Similar Tracks for " + artist + " - " + track)
	
	url = (lastFMUrl + "track.getSimilar&artist=" +
			urllib.quote(unicodedata.normalize("NFKD", artist).encode("ascii", "ignore")) + 
			"&track=" + urllib.quote(unicodedata.normalize("NFKD", track).encode("ascii", "ignore")) +
			"&limit=" + str(limit) + "&api_key=" + apiKey)
	data = urllib.urlopen(url).read()
	sa = BeautifulSoup(data)
	
	tracks = sa.findAll("track")
	items = []
	for x in tracks[:limit]:
		trackName = urllib.unquote(x.find("name").next)
		artistName = urllib.unquote(x.find("artist").find("name").next)
		
		total = artistName + " " + trackName
		
		logging.debug("Adding Artist: " + total)
		items.append(total)
		
	#print "Found " + str(len(artists)) + " similar artists"
	logging.debug("Found " + str(len(items)) + " similar tracks")
		
	return items

def main():
	logging.basicConfig(level=logging.DEBUG,format='%(asctime)s %(levelname)s %(message)s',
							filename='debug.log', filemode='w')
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
	# Number of tracks in the playlist
	MAX_TRACKS					= raw_input("Playlist size [100]: ")
	if MAX_TRACKS == "": MAX_TRACKS = 100
	else: MAX_TRACKS = int(MAX_TRACKS)
	# Starting similar artists
	STARTING_SIMILAR_ARTISTS	= raw_input("Initial number of similar tracks [10]: ")
	if STARTING_SIMILAR_ARTISTS == "": STARTING_SIMILAR_ARTISTS = 10
	else: STARTING_SIMILAR_ARTISTS = int(STARTING_SIMILAR_ARTISTS)
	# Additional similar artists to add to the list when a track is a hit
	ADDITIONAL_SIMILAR_ARTISTS	= raw_input("Additional similar tracks to add per track [10]: ")
	if ADDITIONAL_SIMILAR_ARTISTS == "": ADDITIONAL_SIMILAR_ARTISTS = 10
	else: ADDITIONAL_SIMILAR_ARTISTS = int(ADDITIONAL_SIMILAR_ARTISTS)
	
	raw_input("\nPlease ensure that at least one track is selected in iTunes...")
	
	tracks = itunes.SelectedTracks
	
	artists = []
	used = []
	
	for track in tracks:
		playlist.AddTrack(track)
		
		for a in getSimilarTracks(track.Artist, track.Name, STARTING_SIMILAR_ARTISTS):
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
		t = libraryPlaylist.Search(artist, 1)
		if not t == None:
			
			if not artist in used:
				playlist.AddTrack(t[0])
				
				used.append(artist)
				
				for x in getSimilarTracks(t[0].Artist, t[0].Name, ADDITIONAL_SIMILAR_ARTISTS):
					artists.append(x)
				
				playlistSize = playlistSize + 1
				
				print "Size: " + str(playlistSize) + " / " + str(MAX_TRACKS)
		else:
			missingTracks.append(artist)
			
		

	f = open("missing.txt", "a")
	for x in missingTracks:
		f.write(unicodedata.normalize("NFKD", x).encode("ascii", "ignore") + "\n")
	f.close()

if __name__ == "__main__":
	main()
	print "Completed"
