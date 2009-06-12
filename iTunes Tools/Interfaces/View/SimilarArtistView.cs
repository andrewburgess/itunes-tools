using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;

namespace Interfaces.View
{
	public interface SimilarArtistView
	{
		int MaxTracksPerArtist { get; }
		int MaxTracks { get; }
		int InitialSimilarArtists { get; }
		int AdditionalSimilarArtists { get; }

		string PlaylistName { get; }
		void UpdatePlaylistCount(int size, int maxTracks);
	}
}
