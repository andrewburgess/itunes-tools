using System;
using Controller;
using Interfaces.View;

namespace SimilarArtistsGenerator
{
	class Program : SimilarArtistView
	{
		static void Main(string[] args)
		{
			var program = new Program();
			program.Run();
			Console.ReadLine();
		}

		public void Run()
		{
			var controller = new SimilarArtistController(this);
			controller.GeneratePlaylist();
		}

		public int MaxTracksPerArtist
		{
			get
			{
				Console.Write("Maximum tracks per artist [" + SimilarArtistController.MAX_TRACKS_PER_ARTIST + "]: ");
				var input = Console.ReadLine();
				return string.IsNullOrEmpty(input) == false ? int.Parse(input) : 0;
			}
		}

		public int MaxTracks
		{
			get
			{
				Console.Write("Size of playlist [" + SimilarArtistController.MAX_TRACKS + "]: ");
				var input = Console.ReadLine();
				return string.IsNullOrEmpty(input) == false ? int.Parse(input) : 0;
			}
		}

		public int InitialSimilarArtists
		{
			get
			{
				Console.Write("Initial number of similar artists [" + SimilarArtistController.STARTING_SIMILAR_ARTISTS + "]: ");
				var input = Console.ReadLine();
				return string.IsNullOrEmpty(input) == false ? int.Parse(input) : 0;
			}
		}

		public int AdditionalSimilarArtists
		{
			get
			{
				Console.Write("Additional similar artists to add [" + SimilarArtistController.ADDITIONAL_SIMILAR_ARTISTS + "]: ");
				var input = Console.ReadLine();
				return string.IsNullOrEmpty(input) == false ? int.Parse(input) : 0;
			}
		}

		public string PlaylistName
		{
			get
			{
				Console.Write("Name of the playlist [" + SimilarArtistController.DEFAULT_PLAYLIST_NAME + "]: ");
				var input = Console.ReadLine();
				return input;
			}
		}

		public void UpdatePlaylistCount(int size, int maxTracks)
		{
			Console.WriteLine(size + " / " + maxTracks);
		}
	}
}
