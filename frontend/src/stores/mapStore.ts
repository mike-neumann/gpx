import Store from "stores/Store";
import { MapStore } from "src/types/types";

export const mapStore = new Store<MapStore>({
  displayedTracks: []
});
