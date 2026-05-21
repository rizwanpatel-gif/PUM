<script setup>
import { useDashboardStore } from '../stores/dashboard.js'
import { storeToRefs } from 'pinia'

const store = useDashboardStore()
const { prices } = storeToRefs(store)

const tokenMeta = {
  aave:     { name: 'Aave',     ticker: 'AAVE', color: '#B6509E', initial: 'A' },
  uniswap:  { name: 'Uniswap',  ticker: 'UNI',  color: '#FF007A', initial: 'U' },
  compound: { name: 'Compound', ticker: 'COMP', color: '#00D395', initial: 'C' },
  curve:    { name: 'Curve',    ticker: 'CRV',  color: '#FFD700', initial: 'C' },
  balancer: { name: 'Balancer', ticker: 'BAL',  color: '#1E1E1E', initial: 'B' },
  rari:     { name: 'Rari',     ticker: 'RARI', color: '#6C5CE7', initial: 'R' },
  ethereum: { name: 'Ethereum', ticker: 'ETH',  color: '#627EEA', initial: 'E' },
  'matic-network': { name: 'Polygon', ticker: 'MATIC', color: '#8247E5', initial: 'M' },
  arbitrum: { name: 'Arbitrum', ticker: 'ARB',  color: '#28A0F0', initial: 'A' },
}

function getMeta(id) {
  return tokenMeta[id] ?? { name: id, ticker: id.toUpperCase(), color: '#00c9a7', initial: id[0].toUpperCase() }
}

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
      <div class="token-icon" :style="{ background: getMeta(token).color + '20', color: getMeta(token).color }">
        {{ getMeta(token).initial }}
      </div>
      <div class="token-info">
        <div class="token-name">{{ getMeta(token).name }}</div>
        <div class="token-ticker">{{ getMeta(token).ticker }}</div>
      </div>
      <div class="price-info">
        <div class="price-val">{{ fmt(data.price) }}</div>
        <div class="price-change" :class="data.change_24h >= 0 ? 'price-up' : 'price-down'">
          {{ data.change_24h >= 0 ? '+' : '' }}{{ data.change_24h?.toFixed(2) ?? '0.00' }}%
        </div>
      </div>
      <div class="vol-info">
        <span class="vol-label">Vol</span>
        <span class="vol-val">{{ fmtVol(data.volume_24h) }}</span>
      </div>
    </div>
    <div v-if="!Object.keys(prices).length" class="empty-state">
      Loading prices<span class="blink">_</span>
    </div>
  </div>
</template>

<style scoped>
.prices { display: flex; flex-direction: column; gap: 6px; }

.price-row {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 12px;
  background: var(--raised);
  border: 1px solid var(--border);
  border-radius: var(--r-sm);
  transition: border-color 0.15s;
}
.price-row:hover { border-color: var(--border2); }

.token-icon {
  width: 32px;
  height: 32px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 13px;
  font-weight: 700;
  flex-shrink: 0;
}

.token-info { flex: 1; min-width: 0; }
.token-name { font-size: 13px; font-weight: 700; color: var(--text1); }
.token-ticker { font-size: 11px; font-weight: 500; color: var(--text2); }

.price-info { text-align: right; flex-shrink: 0; }
.price-val { font-size: 15px; font-weight: 800; color: var(--text1); }
.price-change { font-size: 12px; font-weight: 600; margin-top: 1px; }

.vol-info { text-align: right; min-width: 52px; flex-shrink: 0; }
.vol-label { font-size: 10px; font-weight: 600; color: var(--text3); display: block; text-transform: uppercase; letter-spacing: 0.05em; }
.vol-val { font-size: 12px; font-weight: 500; color: var(--text2); }

.empty-state { font-size: 13px; color: var(--text3); padding: 4px 0; }
</style>
