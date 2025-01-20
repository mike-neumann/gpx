<script setup lang="ts">
import leaflet, { LatLng } from "leaflet";
import { onMounted, ref } from "vue";
import "leaflet/dist/leaflet.css";
import { mapService } from "src/services/mapService";
import { mapStore } from "stores/mapStore";

onMounted(() => {
  update();
});

defineExpose({
  update
});

const map = ref<leaflet.Map>();

function update() {
  if (map.value) {
    map.value.remove();
  }

  map.value = leaflet
    .map("map")
    .setView([0, 0], 3);

  leaflet.tileLayer("https://tile.openstreetmap.org/{z}/{x}/{y}.png", {
    attribution: "&copy; <a href=\"https://www.openstreetmap.org/copyright\">OpenStreetMap</a> contributors"
  }).addTo(map.value);

  if (mapService.isTrackLoaded()) {
    for (const track of mapStore.state.displayedTracks) {
      const point = track.points[0];

      map.value.setView([point.point_lat as number, point.point_lon as number], 17);

      // Load points from store
      leaflet.polyline(
        track.points.map(point => {
          return {
            lat: point.point_lat,
            lng: point.point_lon
          } as LatLng;
        }),
        {
          color: "red"
        }
      ).addTo(map.value);
    }
  }
}
</script>

<template>
  <div id="map"></div>
</template>

<style scoped>
#map {
  width: 75vh;
  height: 75vh;
}
</style>
