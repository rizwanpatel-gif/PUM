<script setup>
import { computed } from 'vue'
import { useDashboardStore } from '../stores/dashboard.js'
import { storeToRefs } from 'pinia'

const store = useDashboardStore()
const { networkEvents, wsMessages } = storeToRefs(store)

const allEvents = computed(() => {
  const evts = []
  for (const [net, events] of Object.entries(networkEvents.value)) {
    for (const e of (events || []).slice(0, 4)) {
      evts.push({ ...e, network: net })
    }
  }
  return evts.slice(0, 12)
})

function netColor(net) {
  if (!net) return '#7070a0'
  const n = net.toLowerCase()
  if (n === 'ethereum') return '#627EEA'
  if (n === 'polygon')  return '#8247E5'
  if (n === 'arbitrum') return '#28A0F0'
  return '#00c9a7'
}
</script>

<template>
  <div class="feed">
    <!-- WS live messages -->
    <div v-if="wsMessages.length" class="ws-msgs">
      <div
        v-for="(msg, i) in wsMessages.slice(0, 3)"
        :key="i"
        class="ws-msg fade-in"
      >
        <span class="ws-time">{{ msg.ts }}</span>
        <span class="ws-type">{{ msg.type || 'MSG' }}</span>
        <span class="ws-body">{{ msg.message || JSON.stringify(msg).slice(0, 50) }}</span>
      </div>
    </div>

    <!-- API events -->
    <div class="event-list">
      <div v-for="(evt, i) in allEvents" :key="i" class="event-row">
        <div class="event-dot" :style="{ background: netColor(evt.network) }"></div>
        <div class="event-body">
          <span class="event-net" :style="{ color: netColor(evt.network) }">{{ evt.network?.toUpperCase() }}</span>
          <span class="event-type">{{ evt.event_type || 'EVENT' }}</span>
        </div>
        <span class="event-block">#{{ evt.block_number }}</span>
      </div>
      <div v-if="!allEvents.length" class="empty-state">
        Waiting for events<span class="blink">_</span>
      </div>
    </div>
  </div>
</template>

<style scoped>
.feed { display: flex; flex-direction: column; gap: 8px; }

.ws-msgs {
  background: var(--raised);
  border: 1px solid var(--border);
  border-radius: var(--r-sm);
  padding: 8px 10px;
  display: flex;
  flex-direction: column;
  gap: 4px;
  max-height: 80px;
  overflow-y: auto;
}
.ws-msg { display: flex; align-items: center; gap: 6px; font-size: 10px; }
.ws-time { color: var(--text3); font-variant-numeric: tabular-nums; flex-shrink: 0; }
.ws-type { color: var(--accent); font-weight: 600; flex-shrink: 0; }
.ws-body { color: var(--text2); overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }

.event-list {
  display: flex;
  flex-direction: column;
  gap: 4px;
  max-height: 180px;
  overflow-y: auto;
}
.event-row {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 6px 10px;
  background: var(--raised);
  border: 1px solid var(--border);
  border-radius: 6px;
  transition: border-color 0.15s;
}
.event-row:hover { border-color: var(--border2); }
.event-dot { width: 6px; height: 6px; border-radius: 50%; flex-shrink: 0; }
.event-body { display: flex; align-items: center; gap: 6px; flex: 1; }
.event-net { font-size: 11px; font-weight: 700; flex-shrink: 0; }
.event-type { font-size: 12px; font-weight: 400; color: var(--text2); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.event-block { font-size: 11px; font-weight: 500; color: var(--text3); flex-shrink: 0; font-variant-numeric: tabular-nums; }

.empty-state { font-size: 12px; color: var(--text3); padding: 6px 0; }
</style>
