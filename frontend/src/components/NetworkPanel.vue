<script setup>
import { computed } from 'vue'
import { useDashboardStore } from '../stores/dashboard.js'
import { storeToRefs } from 'pinia'
import EventFeed from './EventFeed.vue'
import PricesFeed from './PricesFeed.vue'

const store = useDashboardStore()
const { networkEvents, prices } = storeToRefs(store)

const networks = [
  { key: 'ethereum', label: 'ETHEREUM',  ticker: 'ETH',   id: 'ethereum' },
  { key: 'polygon',  label: 'POLYGON',   ticker: 'MATIC',  id: 'matic-network' },
  { key: 'arbitrum', label: 'ARBITRUM',  ticker: 'ARB',    id: 'arbitrum' },
]

function eventCount(net) {
  return (networkEvents.value[net] || []).length
}

function getPrice(id) {
  const p = prices.value[id]
  if (!p) return null
  return p
}
</script>

<template>
  <div class="net-panel">
    <div class="section-title">Network Status</div>

    <!-- Network cards -->
    <div class="net-cards">
      <div
        v-for="net in networks"
        :key="net.key"
        class="net-card"
      >
        <div class="net-header">
          <span class="dot-live"></span>
          <span class="net-label">{{ net.label }}</span>
          <span class="badge badge-neon">LIVE</span>
        </div>
        <div class="net-stats">
          <div class="stat">
            <span class="label">Events (24h)</span>
            <span class="stat-val text-neon">{{ eventCount(net.key) }}</span>
          </div>
          <div class="stat" v-if="getPrice(net.id)">
            <span class="label">Price</span>
            <span class="stat-val" :class="getPrice(net.id).change_24h >= 0 ? 'price-up' : 'price-down'">
              ${{ getPrice(net.id).price >= 1 ? getPrice(net.id).price.toFixed(2) : getPrice(net.id).price.toFixed(4) }}
              <span style="font-size:9px">
                {{ getPrice(net.id).change_24h >= 0 ? '+' : '' }}{{ getPrice(net.id).change_24h?.toFixed(2) }}%
              </span>
            </span>
          </div>
        </div>
      </div>
    </div>

    <hr class="divider" />

    <!-- Prices -->
    <div class="section-title" style="margin-top:8px">Protocol Prices</div>
    <PricesFeed />

    <hr class="divider" />

    <!-- Event feed -->
    <div class="section-title">Live Events</div>
    <EventFeed />
  </div>
</template>

<style scoped>
.net-panel { display: flex; flex-direction: column; height: 100%; overflow-y: auto; }
.net-cards { display: flex; flex-direction: column; gap: 8px; }
.net-card { background: #0a0a0a; border: 1px solid #1a1a1a; border-radius: 4px; padding: 10px 12px; transition: border-color 0.2s; }
.net-card:hover { border-color: #00FF41; box-shadow: 0 0 10px rgba(0,255,65,0.1); }
.net-header { display: flex; align-items: center; gap: 7px; margin-bottom: 8px; }
.net-label { font-size: 12px; font-weight: 700; letter-spacing: 0.1em; color: #E5E7EB; flex: 1; }
.net-stats { display: flex; gap: 20px; }
.stat { display: flex; flex-direction: column; gap: 2px; }
.stat-val { font-size: 14px; font-weight: 700; }
</style>
