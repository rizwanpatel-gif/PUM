<script setup>
import { useDashboardStore } from '../stores/dashboard.js'
import { storeToRefs } from 'pinia'
import EventFeed from './EventFeed.vue'
import PricesFeed from './PricesFeed.vue'

const store = useDashboardStore()
const { networkEvents, prices } = storeToRefs(store)

const networks = [
  { key: 'ethereum', label: 'Ethereum',  ticker: 'ETH',  id: 'ethereum',    color: '#627EEA' },
  { key: 'polygon',  label: 'Polygon',   ticker: 'MATIC', id: 'matic-network', color: '#8247E5' },
  { key: 'arbitrum', label: 'Arbitrum',  ticker: 'ARB',  id: 'arbitrum',    color: '#28A0F0' },
]

function eventCount(net) {
  return (networkEvents.value[net] || []).length
}

function getPrice(id) {
  return prices.value[id] ?? null
}
</script>

<template>
  <div class="net-panel">
    <div class="panel-header">
      <span class="section-title" style="margin-bottom:0">Network Status</span>
      <span class="badge badge-teal">Live</span>
    </div>

    <!-- Network cards -->
    <div id="tour-networks" class="net-cards">
      <div v-for="net in networks" :key="net.key" class="net-card">
        <div class="net-card-left">
          <div class="net-icon" :style="{ background: net.color + '20', color: net.color }">
            {{ net.ticker[0] }}
          </div>
          <div class="net-info">
            <div class="net-name">{{ net.label }}</div>
            <div class="net-ticker">{{ net.ticker }}</div>
          </div>
        </div>
        <div class="net-card-right">
          <template v-if="getPrice(net.id)">
            <div class="net-price" :class="getPrice(net.id).change_24h >= 0 ? 'price-up' : 'price-down'">
              {{ getPrice(net.id).price >= 1
                  ? `$${getPrice(net.id).price.toFixed(2)}`
                  : `$${getPrice(net.id).price.toFixed(4)}` }}
            </div>
            <div class="net-change" :class="getPrice(net.id).change_24h >= 0 ? 'price-up' : 'price-down'">
              {{ getPrice(net.id).change_24h >= 0 ? '+' : '' }}{{ getPrice(net.id).change_24h?.toFixed(2) }}%
            </div>
          </template>
          <div class="event-count">
            <span class="label">Events</span>
            <span class="count-val">{{ eventCount(net.key) }}</span>
          </div>
        </div>
      </div>
    </div>

    <hr class="divider" />

    <div class="section-title">Protocol Prices</div>
    <div id="tour-prices"><PricesFeed /></div>

    <hr class="divider" />

    <div class="section-title">Live Events</div>
    <div id="tour-events"><EventFeed /></div>
  </div>
</template>

<style scoped>
.net-panel { display: flex; flex-direction: column; }

.panel-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 14px;
}

.net-cards { display: flex; flex-direction: column; gap: 8px; }

.net-card {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: var(--raised);
  border: 1px solid var(--border);
  border-radius: var(--r-sm);
  padding: 12px 14px;
  transition: border-color 0.15s, background 0.15s;
}
.net-card:hover { border-color: var(--border2); background: var(--hover); }

.net-card-left { display: flex; align-items: center; gap: 10px; }

.net-icon {
  width: 36px;
  height: 36px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  font-weight: 700;
  flex-shrink: 0;
}

.net-name { font-size: 14px; font-weight: 700; color: var(--text1); }
.net-ticker { font-size: 12px; font-weight: 500; color: var(--text2); margin-top: 1px; }

.net-card-right { display: flex; flex-direction: column; align-items: flex-end; gap: 3px; }
.net-price { font-size: 16px; font-weight: 800; }
.net-change { font-size: 12px; font-weight: 600; }
.event-count { display: flex; align-items: center; gap: 5px; margin-top: 4px; }
.count-val { font-size: 13px; font-weight: 700; color: var(--accent); }
</style>
