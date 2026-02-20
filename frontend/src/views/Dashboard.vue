<script setup>
import { onMounted, onUnmounted } from 'vue'
import { useDashboardStore } from '../stores/dashboard.js'
import HackerHeader from '../components/HackerHeader.vue'
import NetworkPanel from '../components/NetworkPanel.vue'
import RiskPanel from '../components/RiskPanel.vue'
import ExecutionPanel from '../components/ExecutionPanel.vue'

const store = useDashboardStore()

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
})

onUnmounted(() => {
  clearInterval(pollTimer)
})
</script>

<template>
  <div class="dashboard">
    <HackerHeader />
    <div class="panel-grid">
      <div class="panel">
        <NetworkPanel />
      </div>
      <div class="panel panel-center">
        <RiskPanel />
      </div>
      <div class="panel">
        <ExecutionPanel />
      </div>
    </div>
    <footer class="footer">
      <span class="text-dim" style="font-size:10px; letter-spacing:0.1em;">
        PUM — PROTOCOL UPGRADE MONITOR &nbsp;|&nbsp; FastAPI :8000 &nbsp;|&nbsp; Vue :5173 &nbsp;|&nbsp; ETH / MATIC / ARB
      </span>
    </footer>
  </div>
</template>

<style scoped>
.dashboard { display: flex; flex-direction: column; min-height: 100vh; background: #000; }

.panel-grid {
  display: grid;
  grid-template-columns: 1fr 1fr 1fr;
  gap: 10px;
  padding: 10px;
  flex: 1;
}

.panel {
  background: #0a0a0a;
  border: 1px solid #1a1a1a;
  border-radius: 4px;
  padding: 14px;
  overflow-y: auto;
  max-height: calc(100vh - 90px);
}

.panel-center {
  border-color: rgba(0, 255, 65, 0.2);
  box-shadow: 0 0 20px rgba(0, 255, 65, 0.05);
}

.footer {
  border-top: 1px solid #1a1a1a;
  padding: 6px 16px;
  text-align: center;
  background: #000;
}
</style>
