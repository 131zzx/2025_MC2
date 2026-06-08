<template>
  <div ref="mapEl" style="width: 100%; height: 280px; border-radius: 8px; overflow: hidden" />
</template>

<script setup lang="ts">
import { ref, onMounted, watch, onUnmounted } from 'vue'
import L from 'leaflet'
import type { PlaceNode, TripRecord, DatasetKey } from '../../types'
import { DATASET_COLORS } from '../../types'

const props = defineProps<{
  member: string
  trips:  TripRecord[]
  places: PlaceNode[]
}>()

const mapEl = ref<HTMLElement>()
let map: L.Map | null = null
let layer: L.LayerGroup | null = null

const placeMap = new Map<string, PlaceNode>()

function buildPlaceMap() {
  placeMap.clear()
  props.places.forEach(p => placeMap.set(p.id, p))
}

function initMap() {
  if (!mapEl.value || map) return
  map = L.map(mapEl.value, { center: [0, 0], zoom: 13, attributionControl: false })
  L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
    subdomains: 'abcd', maxZoom: 19,
  }).addTo(map)
  layer = L.layerGroup().addTo(map)
  buildPlaceMap()
  render()
}

function render() {
  if (!layer || !map) return
  layer.clearLayers()

  const memberTrips = props.trips.filter(t => t.person === props.member)
  const bounds: [number, number][] = []

  const datasets: DatasetKey[] = ['filah', 'trout', 'journalist']
  datasets.forEach(ds => {
    const dsTrips = memberTrips.filter(t => t.dataset === ds)
    const color = DATASET_COLORS[ds]

    dsTrips.forEach(trip => {
      const pts: [number, number][] = []
      trip.places.forEach(pl => {
        const place = placeMap.get(pl.id)
        if (place?.lat != null && place?.lon != null) {
          const latlng: [number, number] = [place.lat, place.lon]
          pts.push(latlng)
          bounds.push(latlng)
          L.circleMarker(latlng, {
            radius: 4, fillColor: color, color: '#0f172a',
            weight: 1, fillOpacity: 0.9,
          })
          .bindTooltip(`[${ds.toUpperCase()}] ${place.name || pl.id}<br/>${trip.date}`)
          .addTo(layer!)
        }
      })
      if (pts.length > 1) {
        L.polyline(pts, { color, weight: 1.5, opacity: 0.6, dashArray: '4 4' }).addTo(layer!)
      }
    })
  })

  if (bounds.length > 0) map.fitBounds(bounds, { padding: [20, 20] })
}

onMounted(initMap)
watch([() => props.member, () => props.trips], () => { buildPlaceMap(); render() }, { deep: true })
onUnmounted(() => { map?.remove(); map = null })
</script>
