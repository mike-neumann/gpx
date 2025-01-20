import { mapStore } from "stores/mapStore";
import { apiService } from "src/services/apiService";
import { DisplayedTrack, Track } from "src/types/types";

class MapService {
  isTrackLoaded() {
    return mapStore.state.displayedTracks.length > 0;
  }

  async displayTracks(tracks: Track[]) {
    mapStore.state.displayedTracks = []

    for (const track of tracks) {
      // fetch all point for each track
      const points = await apiService.getPoints(track.track_id);

      // now that we have all points, we can load them into our map store
      const displayedTrack: DisplayedTrack = {
        track: track,
        points: points
      };

      mapStore.state.displayedTracks.push(displayedTrack);
    }
  }
}

export const mapService = new MapService();
