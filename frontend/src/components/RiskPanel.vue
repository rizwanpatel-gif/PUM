<script setup>
import { computed } from 'vue'
import { useDashboardStore } from '../stores/dashboard.js'
import { storeToRefs } from 'pinia'

const store = useDashboardStore()
const { riskScores, recentUpgrades, avgRisk, riskLevel } = storeToRefs(store)

// ECharts gauge option
const gaugeOption = computed(() => {
  const val = avgRisk.value
  const color = val >= 70 ? '#FF0040' : val >= 40 ? '#FFB800' : '#00FF41'
  return {
    backgroundColor: 'transparent',
    series: [{
      type: 'gauge',
      startAngle: 200,
      endAngle: -20,
      min: 0,
      max: 100,
      radius: '85%',
      center: ['50%', '60%'],
      axisLine: {
        lineStyle: {
          width: 14,
          color: [
            [0.3, '#00FF41'],
            [0.7, '#FFB800'],
            [1,   '#FF0040'],
          ],
        },
      },
      pointer: {
        itemStyle: { color },
        length: '60%',
        width: 5,
      },
      axisTick: { show: false },
      splitLine: { show: false },
      axisLabel: {
        color: '#555',
        fontSize: 9,
        distance: 18,
        formatter: (v) => v === 0 ? '0' : v === 50 ? '50' : v === 100 ? '100' : '',
      },
      detail: {
        valueAnimation: true,
        formatter: '{value}',
        color,
        fontSize: 28,
        fontWeight: 700,
        fontFamily: 'JetBrains Mono',
        offsetCenter: [0, '15%'],
      },
      data: [{ value: Math.round(val), name: 'RISK SCORE' }],
      title: { color: '#555', fontSize: 10, fontFamily: 'JetBrains Mono', offsetCenter: [0, '35%'] },
    }],
  }
})

// Sparkline
const sparkOption = computed(() => ({
  backgroundColor: 'transparent',
  grid: { top: 4, bottom: 4, left: 4, right: 4 },
  xAxis: { show: false, type: 'category', data: riskScores.value.map((_, i) => i) },
  yAxis: { show: false, type: 'value', min: 0, max: 100 },
  series: [{
    type: 'line',
    data: [...riskScores.value].reverse(),
    smooth: true,
    lineStyle: { color: '#00FF41', width: 2 },
    itemStyle: { opacity: 0 },
    areaStyle: { color: { type: 'linear', x: 0, y: 0, x2: 0, y2: 1, colorStops: [{ offset: 0, color: 'rgba(0,255,65,0.2)' }, { offset: 1, color: 'transparent' }] } },
  }],
  tooltip: { trigger: 'axis', backgroundColor: '#0a0a0a', borderColor: '#1a1a1a', textStyle: { color: '#E5E7EB', fontSize: 10, fontFamily: 'JetBrains Mono' } },
}))

// Pie breakdown
const pieOption = computed(() => {
  const low    = riskScores.value.filter(r => r < 30).length
  const medium = riskScores.value.filter(r => r >= 30 && r < 70).length
  const high   = riskScores.value.filter(r => r >= 70).length
  return {
    backgroundColor: 'transparent',
    tooltip: { trigger: 'item', backgroundColor: '#0a0a0a', borderColor: '#1a1a1a', textStyle: { color: '#E5E7EB', fontSize: 10, fontFamily: 'JetBrains Mono' } },
    legend: { bottom: 4, textStyle: { color: '#555', fontSize: 9, fontFamily: 'JetBrains Mono' } },
    series: [{
      type: 'pie',
      radius: ['42%', '68%'],
      center: ['50%', '45%'],
      data: [
        { value: low,    name: 'LOW',      itemStyle: { color: '#00FF41' } },
        { value: medium, name: 'MEDIUM',   itemStyle: { color: '#FFB800' } },
        { value: high,   name: 'CRITICAL', itemStyle: { color: '#FF0040' } },
      ],
      label: { show: false },
      emphasis: { itemStyle: { shadowBlur: 10, shadowColor: 'rgba(0,0,0,0.5)' } },
    }],
  }
})

function badgeClass(status) {
  if (!status) return 'badge-dim'
  const s = status.toLowerCase()
  if (s.includes('active') || s.includes('approved')) return 'badge-neon'
  if (s.includes('pending') || s.includes('voting'))  return 'badge-amber'
  if (s.includes('failed') || s.includes('reject'))   return 'badge-red'
  return 'badge-dim'
}
</script>

<template>
  <div class="risk-panel">
    <div class="section-title">Risk Assessment</div>

    <!-- Gauge -->
    <div class="card-neon scanlines" style="padding:10px; margin-bottom:10px;">
      <v-chart :option="gaugeOption" style="height:200px;" autoresize />
      <div style="text-align:center; margin-top:-8px;">
        <span class="badge" :class="riskLevel === 'CRITICAL' ? 'badge-red' : riskLevel === 'ELEVATED' ? 'badge-amber' : 'badge-neon'">
          {{ riskLevel }}
        </span>
      </div>
    </div>

    <!-- Sparkline -->
    <div class="card" style="margin-bottom:10px;">
      <div class="label" style="margin-bottom:4px;">Risk Over Time</div>
      <v-chart :option="sparkOption" style="height:70px;" autoresize />
    </div>

    <!-- Pie -->
    <div class="card" style="margin-bottom:10px;">
      <div class="label" style="margin-bottom:4px;">Distribution</div>
      <v-chart :option="pieOption" style="height:160px;" autoresize />
    </div>

    <!-- Recent upgrades -->
    <div class="section-title">Recent Upgrades</div>
    <div class="upgrade-list">
      <div
        v-for="(up, i) in recentUpgrades.slice(0, 5)"
        :key="i"
        class="upgrade-row fade-in"
      >
        <div class="upgrade-header">
          <span class="upgrade-name">{{ up.protocol_name || 'Unknown' }}</span>
          <span class="badge" :class="badgeClass(up.status)">{{ up.status || 'N/A' }}</span>
        </div>
        <div class="upgrade-title">{{ up.title || 'No title' }}</div>
      </div>
      <div v-if="!recentUpgrades.length" class="text-dim" style="font-size:11px; padding:6px 0;">
        No upgrades found<span class="blink">_</span>
      </div>
    </div>
  </div>
</template>

<style scoped>
.risk-panel { display: flex; flex-direction: column; height: 100%; overflow-y: auto; }
.upgrade-list { display: flex; flex-direction: column; gap: 6px; }
.upgrade-row { background: #0a0a0a; border: 1px solid #1a1a1a; border-radius: 4px; padding: 8px 10px; transition: border-color 0.2s; }
.upgrade-row:hover { border-color: #1f1f1f; }
.upgrade-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 3px; }
.upgrade-name { font-size: 12px; font-weight: 700; color: #E5E7EB; letter-spacing: 0.05em; }
.upgrade-title { font-size: 10px; color: #6B7280; }
</style>
