<script setup>
import { useDashboardStore } from '../stores/dashboard.js'
import { storeToRefs } from 'pinia'

const store = useDashboardStore()
const { prices } = storeToRefs(store)

function fmt(price) {
  if (!price && price !== 0) return '—'
  return price >= 1 ? `$${price.toFixed(2)}` : `$${price.toFixed(4)}`
}

function fmtVol(v) {
  if (!v) return '—'
  if (v >= 1e9) return `$${(v/1e9).toFixed(1)}B`
  if (v >= 1e6) return `$${(v/1e6).toFixed(1)}M`
  if (v >= 1e3) return `$${(v/1e3).toFixed(1)}K`
  return `$${v.toFixed(0)}`
}
</script>

<template>
  <div class="prices">
    <div
      v-for="(data, token) in prices"
      :key="token"
      class="price-row"
    >
      <span class="token-name">{{ token.toUpperCase() }}</span>
      <span class="price-val">{{ fmt(data.price) }}</span>
      <span
        class="change"
        :class="data.change_24h >= 0 ? 'price-up' : 'price-down'"
      >
        {{ data.change_24h >= 0 ? '+' : '' }}{{ data.change_24h?.toFixed(2) ?? '0.00' }}%
      </span>
      <span class="vol text-dim">{{ fmtVol(data.volume_24h) }}</span>
    </div>
    <div v-if="!Object.keys(prices).length" class="text-dim" style="font-size:11px; padding:4px 0;">
      Loading prices<span class="blink">_</span>
    </div>
  </div>
</template>

<style scoped>
.prices { display: flex; flex-direction: column; gap: 4px; max-height: 160px; overflow-y: auto; }
.price-row { display: flex; align-items: center; gap: 10px; font-size: 11px; padding: 4px 8px; border-radius: 3px; background: #0a0a0a; border: 1px solid #111; }
.token-name { font-weight: 700; color: #E5E7EB; min-width: 60px; letter-spacing: 0.05em; }
.price-val { font-weight: 700; color: #E5E7EB; min-width: 70px; }
.change { min-width: 55px; font-weight: 600; font-size: 10px; }
.vol { font-size: 10px; margin-left: auto; }
</style>
