<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useDashboardStore } from '../stores/dashboard.js'
import { storeToRefs } from 'pinia'

const store = useDashboardStore()
const { riskLevel, avgRisk, wsConnected } = storeToRefs(store)

const clock = ref('')
let timer = null

function tick() {
  const now = new Date()
  clock.value = now.toISOString().replace('T', ' ').slice(0, 19) + ' UTC'
}

onMounted(() => { tick(); timer = setInterval(tick, 1000) })
onUnmounted(() => clearInterval(timer))
</script>

<template>
  <header class="header">
    <div class="header-left">
      <span class="logo">PUM</span>
      <span class="logo-sub">PROTOCOL UPGRADE MONITOR</span>
      <span class="version">v1.0</span>
    </div>

    <div class="header-center">
      <div class="net-pill" v-for="net in ['ETH', 'MATIC', 'ARB']" :key="net">
        <span class="dot-live"></span>
        <span>{{ net }}</span>
      </div>
    </div>

    <div class="header-right">
      <div class="risk-chip" :class="riskLevel === 'CRITICAL' ? 'chip-red' : riskLevel === 'ELEVATED' ? 'chip-amber' : 'chip-neon'">
        RISK {{ riskLevel }} {{ avgRisk.toFixed(0) }}/100
      </div>
      <div class="ws-status">
        <span :class="wsConnected ? 'dot-live' : 'dot-dead'"></span>
        <span class="text-dim" style="font-size:10px">{{ wsConnected ? 'WS LIVE' : 'WS OFF' }}</span>
      </div>
      <span class="clock">{{ clock }}</span>
    </div>
  </header>
</template>

<style scoped>
.header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 16px;
  height: 52px;
  background: #000;
  border-bottom: 1px solid #00FF41;
  box-shadow: 0 1px 20px rgba(0,255,65,0.15);
}

.header-left { display: flex; align-items: center; gap: 10px; }
.logo { font-size: 18px; font-weight: 700; color: #00FF41; text-shadow: 0 0 12px rgba(0,255,65,0.9); letter-spacing: 0.1em; }
.logo-sub { font-size: 9px; color: #333; letter-spacing: 0.2em; text-transform: uppercase; }
.version { font-size: 9px; color: #333; border: 1px solid #1a1a1a; padding: 1px 5px; border-radius: 2px; }

.header-center { display: flex; align-items: center; gap: 8px; }
.net-pill { display: flex; align-items: center; gap: 5px; font-size: 10px; color: #6B7280; border: 1px solid #1a1a1a; padding: 3px 8px; border-radius: 2px; }

.header-right { display: flex; align-items: center; gap: 14px; }
.risk-chip { font-size: 10px; font-weight: 700; letter-spacing: 0.12em; padding: 3px 10px; border-radius: 2px; }
.chip-neon  { color: #00FF41; border: 1px solid rgba(0,255,65,0.4);  background: rgba(0,255,65,0.06);  }
.chip-amber { color: #FFB800; border: 1px solid rgba(255,184,0,0.4); background: rgba(255,184,0,0.06); }
.chip-red   { color: #FF0040; border: 1px solid rgba(255,0,64,0.4);  background: rgba(255,0,64,0.06);  animation: flicker 2s infinite; }

@keyframes flicker { 0%,100%{opacity:1} 92%{opacity:1} 93%{opacity:0.4} 94%{opacity:1} }

.ws-status { display: flex; align-items: center; gap: 5px; }
.clock { font-size: 10px; color: #333; letter-spacing: 0.05em; }
</style>
