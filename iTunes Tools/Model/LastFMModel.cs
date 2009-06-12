using System.Collections.Generic;
using System.Linq;
using System.Net;
using System.Xml.Linq;

namespace Model
{
	public class LastFMModel
	{
		private const string API_KEY = "21edbb30193dc36e6fb21cc57b1d8e18";
		private const string LASTFM_URL = "http://ws.audioscrobbler.com/2.0/?method=";

		public List<string> GetSimilarArtists(string artist, int limit)
		{

			var url = LASTFM_URL + "artist.getSimilar&artist=" + artist + "&limit=" + limit + "&api_key=" + API_KEY;
			var client = new WebClient();
			var data = client.DownloadString(url);

			var doc = XDocument.Parse(data);
			var artists = from a in doc.Descendants("artist")
			              select a.Element("name");

			var list = new List<string>();
			foreach (var x in artists)
			{
				list.Add(x.Value);
			}

			return list;
		}

		public List<string> GetTopTracksForArtist(string artist)
		{
			var url = LASTFM_URL + "artist.getTopTracks&artist=" + artist + "&api_key=" + API_KEY;
			var client = new WebClient();
			var data = client.DownloadString(url);

			var doc = XDocument.Parse(data);
			var tracks = from t in doc.Descendants("track")
			             select t.Element("name");

			var list = new List<string>();
			foreach (var x in tracks)
			{
				list.Add(x.Value);
			}

			return list;
		}
	}
}
