<script setup lang="ts">
import { QIcon } from "quasar";

defineProps<{
  icon: String
  text: String
  color: String
}>();
</script>

<template>
  <q-item class="shadow-1 q-pa-lg">
    <q-item-section avatar>
      <q-icon :name="icon"
              :color="color"
      />
    </q-item-section>

    <q-item-section>
      {{ text }}
    </q-item-section>
  </q-item>
</template>

<style scoped>

</style>
