<script setup>
import { computed, ref } from 'vue'
import { useDashboardStore } from '../stores/dashboard.js'
import { storeToRefs } from 'pinia'
import { analyzeSentiment, fetchTwitter } from '../api/index.js'

const store = useDashboardStore()
const { recentUpgrades, tradingRecs } = storeToRefs(store)

const sentimentText = ref('')
const sentimentResult = ref(null)
const twitterQuery = ref('')
const twitterResults = ref([])
const loadingSentiment = ref(false)
const loadingTwitter = ref(false)

// Volatility bar chart
const volOption = computed(() => {
  const data = recentUpgrades.value
    .slice(0, 6)
    .filter(u => u.volatility_prediction)
    .map(u => ({
      name: u.protocol_name || 'Unknown',
      vol: u.volatility_prediction?.predicted_volatility || 0,
    }))

  if (!data.length) {
    return {
      backgroundColor: 'transparent',
      graphic: [{ type: 'text', left: 'center', top: 'center', style: { text: 'No volatility data', fill: '#333', fontFamily: 'JetBrains Mono', fontSize: 11 } }],
    }
  }

  return {
    backgroundColor: 'transparent',
    grid: { top: 20, bottom: 30, left: 40, right: 10 },
    tooltip: {
      trigger: 'axis',
      backgroundColor: '#0a0a0a',
      borderColor: '#1a1a1a',
      textStyle: { color: '#E5E7EB', fontSize: 10, fontFamily: 'JetBrains Mono' },
    },
    xAxis: {
      type: 'category',
      data: data.map(d => d.name),
      axisLabel: { color: '#555', fontSize: 9, fontFamily: 'JetBrains Mono', rotate: 20 },
      axisLine: { lineStyle: { color: '#1a1a1a' } },
    },
    yAxis: {
      type: 'value',
      axisLabel: { color: '#555', fontSize: 9, fontFamily: 'JetBrains Mono' },
      splitLine: { lineStyle: { color: '#111' } },
    },
    series: [{
      type: 'bar',
      data: data.map(d => ({
        value: d.vol,
        itemStyle: {
          color: d.vol > 0.3 ? '#FF0040' : d.vol > 0.15 ? '#FFB800' : '#00FF41',
          borderRadius: [2, 2, 0, 0],
        },
      })),
      barMaxWidth: 32,
    }],
  }
})

function riskColor(level) {
  if (!level) return 'badge-dim'
  const l = level.toLowerCase()
  if (l === 'high')   return 'badge-red'
  if (l === 'medium') return 'badge-amber'
  return 'badge-neon'
}

async function doSentiment() {
  if (!sentimentText.value.trim()) return
  loadingSentiment.value = true
  sentimentResult.value = null
  try {
    const { data } = await analyzeSentiment(sentimentText.value)
    sentimentResult.value = data
  } catch (e) {
    sentimentResult.value = { error: e.message }
  } finally {
    loadingSentiment.value = false
  }
}

async function doTwitter() {
  if (!twitterQuery.value.trim()) return
  loadingTwitter.value = true
  twitterResults.value = []
  try {
    const { data } = await fetchTwitter(twitterQuery.value)
    twitterResults.value = data.results || []
  } catch (e) {
    twitterResults.value = []
  } finally {
    loadingTwitter.value = false
  }
}

function sentimentColor(s) {
  if (!s) return '#555'
  const l = s.toLowerCase()
  if (l === 'positive') return '#00FF41'
  if (l === 'negative') return '#FF0040'
  return '#FFB800'
}
</script>

<template>
  <div class="exec-panel">
    <div class="section-title">Execution Guidance</div>

    <!-- Volatility chart -->
    <div class="card-cyan" style="margin-bottom:10px;">
      <div class="label" style="margin-bottom:6px;">Predicted Volatility</div>
      <v-chart :option="volOption" style="height:160px;" autoresize />
    </div>

    <!-- Execution timing -->
    <div class="card" style="margin-bottom:10px;">
      <div class="label" style="margin-bottom:8px;">Execution Timing</div>
      <div class="timing-row">
        <span class="timing-key text-cyan">ENTRY WINDOW</span>
        <span class="timing-val">Within 24h of upgrade</span>
      </div>
      <div class="timing-row">
        <span class="timing-key text-cyan">EXIT STRATEGY</span>
        <span class="timing-val">Monitor vol for 7 days</span>
      </div>
      <div class="timing-row">
        <span class="timing-key text-red">STOP LOSS</span>
        <span class="timing-val">5% below entry</span>
      </div>
    </div>

    <!-- Trading recs -->
    <div class="section-title">Trading Signals</div>
    <div class="recs-list" style="margin-bottom:10px;">
      <div
        v-for="(rec, i) in tradingRecs.slice(0, 4)"
        :key="i"
        class="rec-row fade-in"
      >
        <div class="rec-header">
          <span class="rec-name">{{ rec.protocol }}</span>
          <span class="badge" :class="riskColor(rec.risk_level)">{{ rec.risk_level }}</span>
        </div>
        <div class="rec-text">{{ rec.recommendation }}</div>
      </div>
      <div v-if="!tradingRecs.length" class="text-dim" style="font-size:11px; padding:6px 0;">
        No signals<span class="blink">_</span>
      </div>
    </div>

    <!-- Sentiment -->
    <div class="section-title">Sentiment Analysis</div>
    <div class="card" style="margin-bottom:10px;">
      <div class="input-row">
        <input
          v-model="sentimentText"
          class="hacker-input"
          placeholder="Enter text to analyze..."
          @keyup.enter="doSentiment"
        />
        <button class="btn-neon" @click="doSentiment" :disabled="loadingSentiment">
          {{ loadingSentiment ? '...' : 'RUN' }}
        </button>
      </div>
      <div v-if="sentimentResult && !sentimentResult.error" class="sentiment-result">
        <div class="s-row">
          <span class="label">Sentiment</span>
          <span :style="{ color: sentimentColor(sentimentResult.sentiment), fontWeight: 700 }">
            {{ sentimentResult.sentiment?.toUpperCase() }}
          </span>
        </div>
        <div class="s-row">
          <span class="label">Polarity</span>
          <span class="text-neon">{{ sentimentResult.polarity?.toFixed(3) }}</span>
        </div>
        <div class="s-row">
          <span class="label">Subjectivity</span>
          <span class="text-dim">{{ sentimentResult.subjectivity?.toFixed(3) }}</span>
        </div>
      </div>
      <div v-if="sentimentResult?.error" class="text-red" style="font-size:11px; margin-top:6px;">
        Error: {{ sentimentResult.error }}
      </div>
    </div>

    <!-- Twitter -->
    <div class="section-title">Twitter Feed</div>
    <div class="card">
      <div class="input-row">
        <input
          v-model="twitterQuery"
          class="hacker-input"
          placeholder="#ethereum, uniswap..."
          @keyup.enter="doTwitter"
        />
        <button class="btn-cyan" @click="doTwitter" :disabled="loadingTwitter">
          {{ loadingTwitter ? '...' : 'FETCH' }}
        </button>
      </div>
      <div v-if="twitterResults.length" class="twitter-results">
        <div
          v-for="(tw, i) in twitterResults"
          :key="i"
          class="tw-row"
        >
          <div class="tw-text">{{ tw.text?.slice(0, 100) }}</div>
          <span class="badge" :class="tw.polarity > 0 ? 'badge-neon' : tw.polarity < 0 ? 'badge-red' : 'badge-dim'" style="font-size:9px;">
            {{ tw.sentiment }}
          </span>
        </div>
      </div>
      <div v-if="!twitterResults.length && !loadingTwitter" class="text-dim" style="font-size:10px; margin-top:6px;">
        Enter a query and press FETCH
      </div>
    </div>
  </div>
</template>

<style scoped>
.exec-panel { display: flex; flex-direction: column; height: 100%; overflow-y: auto; }
.timing-row { display: flex; align-items: baseline; gap: 10px; padding: 3px 0; font-size: 11px; }
.timing-key { font-weight: 700; letter-spacing: 0.1em; font-size: 10px; min-width: 110px; }
.timing-val { color: #6B7280; }
.recs-list { display: flex; flex-direction: column; gap: 6px; }
.rec-row { background: #0a0a0a; border: 1px solid #1a1a1a; border-radius: 4px; padding: 8px 10px; }
.rec-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 3px; }
.rec-name { font-size: 12px; font-weight: 700; color: #E5E7EB; }
.rec-text { font-size: 10px; color: #6B7280; }
.input-row { display: flex; gap: 8px; align-items: center; margin-bottom: 8px; }
.hacker-input { flex: 1; background: #000; border: 1px solid #1a1a1a; color: #00FF41; padding: 5px 10px; font-family: 'JetBrains Mono', monospace; font-size: 11px; border-radius: 2px; outline: none; transition: border-color 0.15s; }
.hacker-input:focus { border-color: #00FF41; box-shadow: 0 0 6px rgba(0,255,65,0.2); }
.hacker-input::placeholder { color: #333; }
.sentiment-result { display: flex; flex-direction: column; gap: 4px; padding-top: 6px; border-top: 1px solid #1a1a1a; margin-top: 6px; }
.s-row { display: flex; align-items: center; gap: 10px; font-size: 11px; }
.twitter-results { display: flex; flex-direction: column; gap: 5px; max-height: 160px; overflow-y: auto; }
.tw-row { background: #000; border: 1px solid #111; border-radius: 3px; padding: 5px 8px; display: flex; align-items: flex-start; justify-content: space-between; gap: 6px; }
.tw-text { font-size: 10px; color: #6B7280; flex: 1; }
</style>
