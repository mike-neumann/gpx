<script setup lang="ts">
import { onMounted, ref } from "vue";
import "leaflet/dist/leaflet.css";
import Map from "components/Map.vue";
import { Driver, Track, Vehicle } from "src/types/types";
import { apiService } from "src/services/apiService";
import { mapService } from "src/services/mapService";
import { Notify } from "quasar";
import { i18n } from "boot/i18n";
import { apiStore } from "stores/apiStore";
import MessageBox from "components/MessageBox.vue";

const selectedFile = ref<File>();
const selectedDriver = ref<Driver | null>(null);
const selectedVehicle = ref<Vehicle | null>(null);

const loadedTracks = ref<Track[]>([]);
const selectedTracks = ref<Track[]>([]);

const selectionTab = ref("uploadTrack");

const mapTab = ref("map");
const map = ref<InstanceType<typeof Map>>();

onMounted(() => {
  apiService.loadData();
});

function uploadTrack() {
  if (!selectedFile.value) {
    return;
  }

  apiService.uploadTrack(selectedFile.value!).then(() => {
    // reload api data after successfully uploading new track
    apiService.loadData();
    Notify.create({
      message: i18n.global.t("uploadSuccessful")
    });
  }).catch(error => {
    Notify.create({
      message: i18n.global.t(JSON.parse(error.message).message)
    });
  });
}

function loadTracks() {
  apiService.getTracks(selectedDriver.value?.driver_id, selectedVehicle.value?.vehicle_id).then(tracks => {
    loadedTracks.value = tracks;

    // reset selected tracks
    selectedTracks.value = [];
  }).catch(error => {
    Notify.create({
      message: i18n.global.t(JSON.parse(error.message).message)
    });
  });
}

function displayTracks() {
  mapService.displayTracks(selectedTracks.value!).then(() => {
    if (map.value) {
      map.value!.update();
    }

    Notify.create({
      message: i18n.global.t("displayTracksSuccessful")
    });
  }).catch(error => {
    Notify.create({
      message: i18n.global.t(JSON.parse(error.message).message)
    });
  });
}
</script>

<template>
  <q-card flat
          square
  >
    <q-card-actions align="right">
      <q-btn-dropdown :label="$t('language')"
                      flat
      >
        <q-list>
          <q-item v-for="locale in $i18n.availableLocales"
                  tag="label"
          >
            <q-item-section avatar>
              <q-radio v-model="$i18n.locale"
                       :val="locale"
              />
            </q-item-section>
            <q-item-section>
              <q-item-label>{{ $t(`locale.${locale}`) }}</q-item-label>
            </q-item-section>
          </q-item>
        </q-list>
      </q-btn-dropdown>

      <q-toggle v-model="$q.dark.isActive"
                unchecked-icon="light_mode"
                checked-icon="dark_mode"
      />
    </q-card-actions>
  </q-card>

  <q-card flat
          square
          class="window-height"
  >
    <q-card-section horizontal
                    class="row"
    >
      <!-- selections -->
      <q-card class="col-6">
        <q-tabs v-model="selectionTab">
          <q-tab name="uploadTrack"
                 :label="$t('uploadTrack')"
          />
          <q-tab name="searchTracks"
                 :label="$t('searchTracks')"
          />
        </q-tabs>

        <q-separator />

        <q-tab-panels v-model="selectionTab"
                      animated
        >
          <q-tab-panel name="uploadTrack">
            <q-card flat>
              <q-card-section>
                <message-box icon="info"
                             :text="$t('uploadTrackDescription')"
                             color="blue"
                />

                <q-file v-model="selectedFile"
                        :label="$t('upload')"
                        accept=".gpx"
                        class="q-pa-lg"
                />
              </q-card-section>

              <q-card-actions align="right">
                <q-btn :label="$t('upload')"
                       :disable="selectedFile == undefined"
                       @click="uploadTrack()"
                />
              </q-card-actions>
            </q-card>
          </q-tab-panel>

          <q-tab-panel name="searchTracks">
            <q-card flat>
              <q-card-section>
                <message-box icon="info"
                             :text="$t('searchTracksDescription')"
                             color="blue"
                />

                <div class="row">
                  <q-select v-model="selectedDriver"
                            :label="$t('driver')"
                            :options="[null, ...apiStore.state.drivers]"
                            :option-label="(driver?: Driver) => driver != null ? driver.driver_name : $t('empty')"
                            class="col-6 q-pa-lg"
                  />

                  <q-select v-model="selectedVehicle"
                            :label="$t('vehicle')"
                            :options="[null, ...apiStore.state.vehicles]"
                            :option-label="(vehicle?: Vehicle) => vehicle != null ? vehicle.vehicle_license_plate : $t('empty')"
                            class="col-6 q-pa-lg"
                  />
                </div>
              </q-card-section>

              <q-card-actions align="right">
                <q-btn :label="$t('searchTracks')"
                       @click="loadTracks()"
                />
              </q-card-actions>

              <q-separator class="q-mt-lg" />

              <q-card-section class="q-mt-lg">
                <message-box v-if="loadedTracks.length == 0"
                             icon="info"
                             color="blue"
                             :text="$t('noTracksFound')"
                />
                <q-list padding>
                  <q-item v-for="track in loadedTracks"
                          tag="label"
                          v-ripple
                  >
                    <q-item-section avatar>
                      <q-checkbox v-model="selectedTracks"
                                  :val="track"
                      />
                    </q-item-section>

                    <q-item-section>
                      <q-item-label>{{ track.track_file_name }}</q-item-label>
                    </q-item-section>
                  </q-item>
                </q-list>
              </q-card-section>

              <q-card-actions align="right">
                <q-btn :label="$t('displayTracks')"
                       :disable="selectedTracks.length == 0"
                       @click="displayTracks()"
                />
              </q-card-actions>
            </q-card>

          </q-tab-panel>
        </q-tab-panels>
      </q-card>

      <q-separator vertical />

      <!-- map view -->
      <q-card class="col-6">
        <q-tabs v-model="mapTab">
          <q-tab name="map"
                 :label="$t('map')"
          />
          <q-tab name="statistics"
                 :label="$t('statistics')"
          />
        </q-tabs>

        <q-separator />

        <q-tab-panels v-model="mapTab"
                      animated
        >
          <q-tab-panel name="map">
            <q-card flat>
              <q-card-section class="flex justify-center">
                <Map ref="map" />
              </q-card-section>
            </q-card>
          </q-tab-panel>

          <q-tab-panel name="statistics">
            <q-card flat>
              <q-card-section>
                TODO: STATISTICS
              </q-card-section>
            </q-card>
          </q-tab-panel>
        </q-tab-panels>
      </q-card>
    </q-card-section>
  </q-card>
</template>
