using System.Collections.Generic;
using System.Linq;
using Interfaces.View;
using Model;
using iTunesLib;

namespace Controller
{
	/// <summary>
	/// Controls the program flow for creating a playlist based on similar artists
	/// </summary>
	public class SimilarArtistController
	{
		public static readonly string DEFAULT_PLAYLIST_NAME = "Similar";
		public static readonly int MAX_TRACKS_PER_ARTIST = 5;
		public static readonly int MAX_TRACKS = 100;
		public static readonly int STARTING_SIMILAR_ARTISTS = 10;
		public static readonly int ADDITIONAL_SIMILAR_ARTISTS = 10;

		private LastFMModel model;

		private readonly iTunesAppClass itunes;
		private IITLibraryPlaylist libraryPlaylist;

		private readonly SimilarArtistView view;

		private int maxTracks;
		private int maxTracksPerArtist;
		private int startingSimilarArtists;
		private int additionalSimilarArtists;

		private IITTrackCollection selectedTracks;
		private IITUserPlaylist playlist;

		private Queue<string> similarArtists;
		private Dictionary<string, int> artistTrackCount;
		private Dictionary<string, Queue<string>> artistTracks;
		private List<string> missingTracks;
		
		private int playlistSize;

		public SimilarArtistController(SimilarArtistView view)
		{
			model = new LastFMModel();
			itunes = new iTunesAppClass();
			libraryPlaylist = itunes.LibraryPlaylist;

			similarArtists = new Queue<string>();
			artistTrackCount = new Dictionary<string, int>();
			artistTracks = new Dictionary<string, Queue<string>>();
			missingTracks = new List<string>();

			playlistSize = 0;

			this.view = view;
		}

		public void GeneratePlaylist()
		{
			IntializeGenerator();
			AddSelectedTracks();

			while (similarArtists.Count > 0 && playlistSize < maxTracks)
			{
				var artist = similarArtists.Dequeue();

				var searched = libraryPlaylist.Search(artist, ITPlaylistSearchField.ITPlaylistSearchFieldArtists);

				//Check to see if the user actually has anything in their library for this artist
				//before moving on
				if (searched != null)
				{
					if (!artistTracks.ContainsKey(artist))
					{
						artistTracks.Add(artist, new Queue<string>());
						foreach (var track in model.GetTopTracksForArtist(artist))
						{
							artistTracks[artist].Enqueue(track);
						}

						artistTrackCount.Add(artist, 0);
					}

					var foundTrack = false;
					while (!foundTrack)
					{
						//Make sure both that we haven't used this artist too much, and also that
						//there are some tracks to pick from
						if (artistTrackCount[artist] < maxTracksPerArtist && artistTracks[artist].Count > 0)
						{
							var track = artistTracks[artist].Dequeue();
							searched = libraryPlaylist.Search(artist + " " + track, ITPlaylistSearchField.ITPlaylistSearchFieldVisible);
							if (searched != null)
							{
								for (var i = 1; i <= searched.Count; i++)
								{
									var t = searched[i];
									//Make extra extra sure that these are the files we're looking for
									//and we aren't matching something by "The - Rock" when we really want "The Rocks - Something Else"
									if (t.Artist.ToLower() == artist.ToLower() && t.Name.ToLower() == track.ToLower())
									{
										var x = (object) t;
										playlist.AddTrack(ref x);
										playlistSize++;
										//Throw in more artists when we get here
										if (additionalSimilarArtists != 0)
										{
											foreach (var n in model.GetSimilarArtists(artist, additionalSimilarArtists))
											{
												similarArtists.Enqueue(n);
											}
										}

										foundTrack = true;
										artistTrackCount[artist]++;

										view.UpdatePlaylistCount(playlistSize, maxTracks);
									}
								}
							}
							else
							{
								missingTracks.Add(artist + " - " + track);
							}
						}
						else
						{
							foundTrack = true;
						}
					}
				}
				else
				{
					missingTracks.Add(artist);
				}
			}
		}

		private void AddSelectedTracks()
		{
			for (var i = 1; i <= selectedTracks.Count; i++)
			{
				var track = (object)selectedTracks[i];
				playlist.AddTrack(ref track);

				playlistSize++;

				foreach (var a in model.GetSimilarArtists(selectedTracks[i].Artist, startingSimilarArtists))
				{
					similarArtists.Enqueue(a);
				}
			}
		}

		private void IntializeGenerator()
		{
			selectedTracks = itunes.SelectedTracks;
			var playlistName = view.PlaylistName;

			if (playlistName.Length == 0)
			{
				playlistName = DEFAULT_PLAYLIST_NAME;
			}

			playlist = (IITUserPlaylist)itunes.CreatePlaylist(playlistName);

			maxTracksPerArtist = view.MaxTracksPerArtist;
			if (maxTracksPerArtist == 0)
				maxTracksPerArtist = MAX_TRACKS_PER_ARTIST;

			maxTracks = view.MaxTracks;
			if (maxTracks == 0)
				maxTracks = MAX_TRACKS;

			startingSimilarArtists = view.InitialSimilarArtists;
			if (startingSimilarArtists == 0)
				startingSimilarArtists = STARTING_SIMILAR_ARTISTS;

			additionalSimilarArtists = view.AdditionalSimilarArtists;
			if (additionalSimilarArtists == 0)
				additionalSimilarArtists = ADDITIONAL_SIMILAR_ARTISTS;
		}
	}
}
