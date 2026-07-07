<script setup>
import { computed } from 'vue'
import { useDashboardStore } from '../stores/dashboard.js'
import { storeToRefs } from 'pinia'

const store = useDashboardStore()
const { riskScores, recentUpgrades, avgRisk, riskLevel } = storeToRefs(store)

const gaugeOption = computed(() => {
  const val = avgRisk.value
  const color = val >= 70 ? '#ef4444' : val >= 40 ? '#f59e0b' : '#00c9a7'
  return {
    backgroundColor: 'transparent',
    series: [{
      type: 'gauge',
      startAngle: 200,
      endAngle: -20,
      min: 0,
      max: 100,
      radius: '88%',
      center: ['50%', '60%'],
      axisLine: {
        lineStyle: {
          width: 12,
          color: [[0.3, '#00c9a7'], [0.7, '#f59e0b'], [1, '#ef4444']],
        },
      },
      pointer: {
        itemStyle: { color },
        length: '60%',
        width: 4,
      },
      axisTick: { show: false },
      splitLine: { show: false },
      axisLabel: {
        color: '#7070a0',
        fontSize: 9,
        distance: 16,
        fontFamily: 'Plus Jakarta Sans',
        formatter: (v) => v === 0 ? '0' : v === 50 ? '50' : v === 100 ? '100' : '',
      },
      detail: {
        valueAnimation: true,
        formatter: '{value}',
        color,
        fontSize: 30,
        fontWeight: 700,
        fontFamily: 'Plus Jakarta Sans',
        offsetCenter: [0, '12%'],
      },
      data: [{ value: Math.round(val), name: 'RISK SCORE' }],
      title: { color: '#7070a0', fontSize: 10, fontFamily: 'Plus Jakarta Sans', offsetCenter: [0, '34%'] },
    }],
  }
})

const sparkOption = computed(() => ({
  backgroundColor: 'transparent',
  grid: { top: 4, bottom: 4, left: 4, right: 4 },
  xAxis: { show: false, type: 'category', data: riskScores.value.map((_, i) => i) },
  yAxis: { show: false, type: 'value', min: 0, max: 100 },
  series: [{
    type: 'line',
    data: [...riskScores.value].reverse(),
    smooth: true,
    lineStyle: { color: '#00c9a7', width: 2 },
    itemStyle: { opacity: 0 },
    areaStyle: {
      color: {
        type: 'linear', x: 0, y: 0, x2: 0, y2: 1,
        colorStops: [
          { offset: 0, color: 'rgba(0,201,167,0.25)' },
          { offset: 1, color: 'rgba(0,201,167,0)' },
        ],
      },
    },
  }],
  tooltip: {
    trigger: 'axis',
    backgroundColor: '#181826',
    borderColor: '#1e1e2e',
    textStyle: { color: '#e4e4f0', fontSize: 11, fontFamily: 'Inter' },
  },
}))

const pieOption = computed(() => {
  const low    = riskScores.value.filter(r => r < 30).length
  const medium = riskScores.value.filter(r => r >= 30 && r < 70).length
  const high   = riskScores.value.filter(r => r >= 70).length
  return {
    backgroundColor: 'transparent',
    tooltip: {
      trigger: 'item',
      backgroundColor: '#181826',
      borderColor: '#1e1e2e',
      textStyle: { color: '#e4e4f0', fontSize: 11, fontFamily: 'Inter' },
    },
    legend: {
      bottom: 4,
      textStyle: { color: '#7070a0', fontSize: 10, fontFamily: 'Inter' },
    },
    series: [{
      type: 'pie',
      radius: ['44%', '68%'],
      center: ['50%', '46%'],
      data: [
        { value: low,    name: 'Low',      itemStyle: { color: '#00c9a7' } },
        { value: medium, name: 'Medium',   itemStyle: { color: '#f59e0b' } },
        { value: high,   name: 'Critical', itemStyle: { color: '#ef4444' } },
      ],
      label: { show: false },
      emphasis: { itemStyle: { shadowBlur: 8, shadowColor: 'rgba(0,0,0,0.4)' } },
    }],
  }
})

function badgeClass(status) {
  if (!status) return 'badge-dim'
  const s = status.toLowerCase()
  if (s.includes('active') || s.includes('approved')) return 'badge-teal'
  if (s.includes('pending') || s.includes('voting'))  return 'badge-amber'
  if (s.includes('failed') || s.includes('reject'))   return 'badge-red'
  return 'badge-dim'
}
</script>

<template>
  <div class="risk-panel">
    <div class="section-title">Risk Assessment</div>

    <!-- Gauge -->
    <div id="tour-risk-gauge" class="card-accent gauge-card" style="margin-bottom:10px;">
      <v-chart :option="gaugeOption" style="height:190px;" autoresize />
      <div class="gauge-badge">
        <span
          class="badge"
          :class="riskLevel === 'CRITICAL' ? 'badge-red' : riskLevel === 'ELEVATED' ? 'badge-amber' : 'badge-teal'"
        >
          {{ riskLevel }}
        </span>
      </div>
    </div>

    <!-- Sparkline -->
    <div id="tour-risk-chart" class="card spark-card" style="margin-bottom:10px;">
      <div class="spark-label">
        <span class="label">Risk Over Time</span>
        <span class="spark-val" :class="avgRisk >= 70 ? 'text-negative' : avgRisk >= 40 ? 'text-warn' : 'text-accent'">
          {{ avgRisk.toFixed(1) }}
        </span>
      </div>
      <v-chart :option="sparkOption" style="height:64px;" autoresize />
    </div>

    <!-- Pie -->
    <div id="tour-risk-dist" class="card" style="margin-bottom:12px;">
      <div class="label" style="margin-bottom:6px;">Risk Distribution</div>
      <v-chart :option="pieOption" style="height:150px;" autoresize />
    </div>

    <!-- Recent upgrades -->
    <div class="section-title">Recent Upgrades</div>
    <div id="tour-upgrades" class="upgrade-list">
      <div
        v-for="(up, i) in recentUpgrades.slice(0, 5)"
        :key="i"
        class="upgrade-row fade-in"
      >
        <div class="upgrade-left">
          <div class="upgrade-name">{{ up.protocol_name || 'Unknown' }}</div>
          <div class="upgrade-title">{{ up.title || 'No title' }}</div>
        </div>
        <span class="badge" :class="badgeClass(up.status)">{{ up.status || 'N/A' }}</span>
      </div>
      <div v-if="!recentUpgrades.length" class="empty-state">
        No upgrades found<span class="blink">_</span>
      </div>
    </div>
  </div>
</template>

<style scoped>
.risk-panel { display: flex; flex-direction: column; }

.gauge-card { padding: 8px 10px 10px; }
.gauge-badge { text-align: center; margin-top: -6px; }

.spark-card { padding: 12px 14px 10px; }
.spark-label { display: flex; align-items: center; justify-content: space-between; margin-bottom: 6px; }
.spark-val { font-size: 15px; font-weight: 700; }

.upgrade-list { display: flex; flex-direction: column; gap: 6px; }
.upgrade-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: var(--raised);
  border: 1px solid var(--border);
  border-radius: var(--r-sm);
  padding: 10px 12px;
  gap: 10px;
  transition: border-color 0.15s;
}
.upgrade-row:hover { border-color: var(--border2); }
.upgrade-left { flex: 1; min-width: 0; }
.upgrade-name { font-size: 13px; font-weight: 700; color: var(--text1); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.upgrade-title { font-size: 12px; font-weight: 400; color: var(--text2); margin-top: 2px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }

.empty-state { font-size: 13px; color: var(--text3); padding: 8px 0; }
</style>
