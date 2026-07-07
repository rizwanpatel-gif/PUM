<script setup>
import { onMounted, onUnmounted } from 'vue'
import { useDashboardStore } from '../stores/dashboard.js'
import { useOnboarding } from '../composables/useOnboarding.js'
import HackerHeader from '../components/HackerHeader.vue'
import NetworkPanel from '../components/NetworkPanel.vue'
import RiskPanel from '../components/RiskPanel.vue'
import ExecutionPanel from '../components/ExecutionPanel.vue'

const store = useDashboardStore()
const { startTour, checkAutoStart } = useOnboarding()

let pollTimer = null

async function refresh() {
  await Promise.allSettled([
    store.loadBulkData(),
    store.loadEvents(),
    store.loadPrices(),
  ])
}

onMounted(async () => {
  await refresh()
  store.connectWS()
  pollTimer = setInterval(refresh, 15000)
  checkAutoStart()
})

onUnmounted(() => {
  clearInterval(pollTimer)
})
</script>

<template>
  <div class="app-layout">
    <HackerHeader @start-tour="startTour" />
    <div class="panel-grid">
      <div class="panel-col"><NetworkPanel /></div>
      <div class="panel-col panel-col--accent"><RiskPanel /></div>
      <div class="panel-col"><ExecutionPanel /></div>
    </div>
  </div>
</template>

<style scoped>
.app-layout {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
  background: var(--bg);
}

.panel-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 14px;
  padding: 16px 20px 20px;
  align-items: start;
  flex: 1;
}

.panel-col {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--r-lg);
  padding: 20px 18px;
  overflow-y: auto;
  max-height: calc(100vh - 76px);
}

.panel-col--accent {
  border-color: rgba(0, 201, 167, 0.2);
  box-shadow: 0 0 40px rgba(0, 201, 167, 0.04) inset;
}

/* ── Responsive ── */
@media (max-width: 1100px) {
  .panel-grid { grid-template-columns: 1fr 1fr; }
  .panel-col  { max-height: none; }
}

@media (max-width: 680px) {
  .panel-grid { grid-template-columns: 1fr; padding: 10px 12px; gap: 10px; }
  .panel-col  { max-height: none; }
}
</style>
