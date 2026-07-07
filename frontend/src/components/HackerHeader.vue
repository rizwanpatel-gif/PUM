<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useDashboardStore } from '../stores/dashboard.js'
import { storeToRefs } from 'pinia'

const emit = defineEmits(['start-tour'])

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
  <header class="topbar">
    <!-- Left: title -->
    <div class="topbar-left">
      <div class="page-title">Dashboard</div>
      <div class="page-sub">Protocol Upgrade Monitor</div>
    </div>

    <!-- Center: network pills -->
    <div class="topbar-center">
      <div class="net-pill" v-for="net in ['ETH', 'MATIC', 'ARB']" :key="net">
        <span class="dot-live pulse-dot"></span>
        <span>{{ net }}</span>
      </div>
    </div>

    <!-- Right: risk + ws + clock -->
    <div class="topbar-right">
      <div
        class="risk-chip"
        :class="{
          'risk-critical': riskLevel === 'CRITICAL',
          'risk-elevated': riskLevel === 'ELEVATED',
          'risk-normal':   riskLevel === 'NORMAL',
        }"
      >
        <span class="risk-label">Risk</span>
        <span class="risk-val">{{ riskLevel }}</span>
        <span class="risk-num">{{ avgRisk.toFixed(0) }}</span>
      </div>

      <div id="tour-header" class="ws-pill" :class="wsConnected ? 'ws-live' : 'ws-off'">
        <span :class="wsConnected ? 'dot-live' : 'dot-dead'"></span>
        <span>{{ wsConnected ? 'Live' : 'Offline' }}</span>
      </div>

      <div class="clock">{{ clock }}</div>

      <button class="help-btn" @click="emit('start-tour')" title="Start tour">?</button>
    </div>
  </header>
</template>

<style scoped>
.topbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 24px;
  height: 64px;
  background: var(--surface);
  border-bottom: 1px solid var(--border);
  gap: 16px;
  flex-shrink: 0;
}

.topbar-left { display: flex; flex-direction: column; gap: 2px; }
.page-title { font-size: 18px; font-weight: 800; color: var(--text1); letter-spacing: -0.02em; }
.page-sub   { font-size: 12px; font-weight: 500; color: var(--text2); }

.topbar-center { display: flex; align-items: center; gap: 8px; }
.net-pill {
  display: flex;
  align-items: center;
  gap: 7px;
  font-size: 12px;
  font-weight: 700;
  color: var(--text2);
  background: var(--raised);
  border: 1px solid var(--border);
  padding: 5px 12px;
  border-radius: 20px;
  letter-spacing: 0.03em;
}
.pulse-dot { animation: pulse-dot 2s ease-in-out infinite; }

.topbar-right { display: flex; align-items: center; gap: 10px; }

.risk-chip {
  display: flex;
  align-items: center;
  gap: 7px;
  padding: 6px 14px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 700;
  border: 1px solid transparent;
}
.risk-label { color: var(--text2); font-weight: 500; }
.risk-val   { font-weight: 800; letter-spacing: 0.03em; }
.risk-num   { font-size: 14px; font-weight: 800; }
.risk-normal   { background: rgba(0,201,167,0.1);   border-color: rgba(0,201,167,0.2);   color: #00c9a7; }
.risk-elevated { background: rgba(245,158,11,0.1);  border-color: rgba(245,158,11,0.2);  color: #f59e0b; }
.risk-critical { background: rgba(239,68,68,0.1);   border-color: rgba(239,68,68,0.2);   color: #ef4444; }

.ws-pill {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  font-weight: 600;
  padding: 5px 12px;
  border-radius: 20px;
  border: 1px solid var(--border);
  background: var(--raised);
}
.ws-live { color: var(--green); border-color: rgba(34,197,94,0.2); background: rgba(34,197,94,0.07); }
.ws-off  { color: var(--text2); }

.clock {
  font-size: 12px;
  font-weight: 500;
  color: var(--text2);
  font-variant-numeric: tabular-nums;
  white-space: nowrap;
}

@media (max-width: 900px) {
  .topbar-center { display: none; }
  .clock { display: none; }
}
@media (max-width: 600px) {
  .topbar { padding: 0 14px; }
  .page-sub { display: none; }
}

.help-btn {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  border: 1px solid var(--border2);
  background: var(--raised);
  color: var(--text2);
  font-size: 14px;
  font-weight: 700;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.15s;
  flex-shrink: 0;
}
.help-btn:hover {
  background: var(--accent);
  color: #0d0d15;
  border-color: var(--accent);
}
</style>
