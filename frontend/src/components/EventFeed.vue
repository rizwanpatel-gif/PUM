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
</script>

<template>
  <div class="feed">
    <!-- WS live messages -->
    <div v-if="wsMessages.length" class="ws-msgs">
      <div
        v-for="(msg, i) in wsMessages.slice(0, 5)"
        :key="i"
        class="t-line fade-in"
        style="font-size:10px; padding:1px 0;"
      >
        [{{ msg.ts }}] {{ msg.type || 'MSG' }}: {{ msg.message || JSON.stringify(msg).slice(0, 60) }}
      </div>
    </div>

    <!-- API events -->
    <div class="terminal" style="max-height:180px; overflow-y:auto;">
      <div
        v-for="(evt, i) in allEvents"
        :key="i"
        class="t-line"
      >
        [{{ evt.network?.toUpperCase() }}] {{ evt.event_type || 'EVENT' }} — blk {{ evt.block_number }}
      </div>
      <div v-if="!allEvents.length" class="t-line text-dim">
        Waiting for events<span class="blink">_</span>
      </div>
    </div>
  </div>
</template>

<style scoped>
.feed { display: flex; flex-direction: column; gap: 6px; }
.ws-msgs { background: #000; border: 1px solid #1a1a1a; padding: 6px 8px; border-radius: 4px; max-height: 80px; overflow-y: auto; }
</style>
