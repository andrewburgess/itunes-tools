import win32com.client
import urllib2
from BeautifulSoup import BeautifulSoup
import unicodedata

lastFMUrl = "http://ws.audioscrobbler.com/2.0/?method="
apiKey = "21edbb30193dc36e6fb21cc57b1d8e18"
itunes = None

def getArtistTags(artist):
	url = lastFMUrl + "artist.getTopTags&artist=" + urllib2.quote(unicodedata.normalize("NFKD", artist).encode("ascii", "ignore")) + "&api_key=" + apiKey
	data = urllib2.urlopen(url).read()
	
	soup = BeautifulSoup(data)
	
	tagsxml = soup.findAll("tag")
	tags = []
	for x in tagsxml:
		name = urllib2.unquote(x.find("name").next)
		words = name.split(" ")
		name = ""
		for word in words:
			name = name + word.capitalize() + " "
		name = name[:-1]
		count = int(x.find("count").next)
		tags.append({"name" : name, "count" : count})
		
	return tags
	
def main():
	itunes = win32com.client.gencache.EnsureDispatch("iTunes.Application")
	raw_input("Please ensure that at least one track is selected in iTunes...")
	
	tracks = itunes.SelectedTracks
	count = 1
	
	artistTags = {}
	
	for track in tracks:
		print "Track: " + str(count) + " of " + str(len(tracks))
		
		try:
			if not artistTags.has_key(track.Artist):
				artistTags[track.Artist] = getArtistTags(track.Artist)
		except:
			print track.Artist
			
		tags = artistTags[track.Artist][:]
			
		count = count + 1
		if len(tags) == 0:
			continue
		track.Genre = tags[0]["name"]
		tags.pop(0)
		
		if len(tags) == 0:
			continue
		track.Comment = tags[0]["name"]
		tags.pop(0)
		
		for t in tags:
			if t["count"] >= 20:
				track.Comment = track.Comment + ", " + t["name"]
		
		
		
if __name__ == "__main__":
	main()
