#!/usr/bin/env python
#
#       library-comparer.py
#       
#       Copyright 2009 Andrew Burgess <andrew@deceptacle.com>
#       
#       This program is free software; you can redistribute it and/or modify
#       it under the terms of the GNU General Public License as published by
#       the Free Software Foundation; either version 2 of the License, or
#       (at your option) any later version.
#       
#       This program is distributed in the hope that it will be useful,
#       but WITHOUT ANY WARRANTY; without even the implied warranty of
#       MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#       GNU General Public License for more details.
#       
#       You should have received a copy of the GNU General Public License
#       along with this program; if not, write to the Free Software
#       Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#       MA 02110-1301, USA.

from BeautifulSoup import BeautifulSoup
import win32com.client
from sets import Set

def main():
	
	libraryFile = raw_input("Path to the Library.xml file: ")
	file = open(libraryFile, "r")
	soup = BeautifulSoup(file.read())
	file.close()
	
	artistKeys = soup.findAll("key", text="Artist")
	print len(artistKeys)
	artists = []
	for artistKey in artistKeys:
		artists.append(artistKey.findParent().findNextSibling("string").next)
		
	file = open("artists.txt", "w")
	itunes = win32com.client.gencache.EnsureDispatch("iTunes.Application")
	pl = itunes.LibraryPlaylist
	artists = Set(artists)
	for artist in artists:
		t = pl.Search(artist, 2)
		if t == None:
			file.write(artist + "\n")
		else:
			for x in t:
				if not x.Artist.lower() == artist.lower():
					file.write(artist + "\n")
					break
	
	file.close()
	
	return 0

if __name__ == '__main__': main()
