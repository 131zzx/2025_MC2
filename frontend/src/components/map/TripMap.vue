<template>
  <div ref="mapEl" style="width: 100%; height: 280px; border-radius: 8px; overflow: hidden" />
</template>

<script setup lang="ts">
import { ref, onMounted, watch, onUnmounted, withDefaults } from 'vue'
import L from 'leaflet'
import type { PlaceNode, TripRecord } from '../../types'
import { DATASET_COLORS } from '../../types'

const props = withDefaults(defineProps<{
  places?: PlaceNode[]
  trips?:  TripRecord[]
}>(), {
  places: () => [],
  trips: () => []
})

const mapEl = ref<HTMLElement>()
let map: L.Map | null = null
let markersLayer: L.LayerGroup | null = null

const ZONE_COLORS: Record<string, string> = {
  tourism:     '#16a34a',
  industrial:  '#0369a1',
  commercial:  '#9333ea',
  residential: '#64748b',
  government:  '#f59e0b',
}

function initMap() {
  if (!mapEl.value || map) return

  map = L.map(mapEl.value, {
    center: [0, 0],
    zoom: 13,
    zoomControl: true,
    attributionControl: false,
  })

  L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
    attribution: '&copy; OpenStreetMap &copy; CartoDB',
    subdomains: 'abcd',
    maxZoom: 19,
  }).addTo(map)

  markersLayer = L.layerGroup().addTo(map)
  renderMarkers()
}

function renderMarkers() {
  if (!markersLayer || !map) return
  markersLayer.clearLayers()

  // 增加防御性检查
  const places = props.places || []
  const trips = props.trips || []

  // 过滤出有经纬度的地点
  const validPlaces = places.filter(p => p.lat != null && p.lon != null)
  if (!validPlaces.length) return

  const bounds: [number, number][] = []

  validPlaces.forEach(place => {
    const color = ZONE_COLORS[place.zone] ?? '#6b7280'
    const marker = L.circleMarker([place.lat!, place.lon!], {
      radius: 5,
      fillColor: color,
      color: '#0f172a',
      weight: 1,
      opacity: 1,
      fillOpacity: 0.8,
    })
    marker.bindTooltip(`${place.name || place.id}<br/><small>zone: ${place.zone || '未知'}</small>`)
    markersLayer!.addLayer(marker)
    bounds.push([place.lat!, place.lon!])
  })

  if (bounds.length > 0) {
    map.fitBounds(bounds, { padding: [20, 20] })
  }
}

onMounted(initMap)

watch([() => props.places, () => props.trips], renderMarkers, { deep: true })

onUnmounted(() => {
  map?.remove()
  map = null
})
</script>
