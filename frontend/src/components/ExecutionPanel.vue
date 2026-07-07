<script setup>
import { computed, ref } from 'vue'
import { useDashboardStore } from '../stores/dashboard.js'
import { storeToRefs } from 'pinia'
import { analyzeSentiment, fetchTwitter } from '../api/index.js'

const store = useDashboardStore()
const { recentUpgrades, tradingRecs } = storeToRefs(store)

const sentimentText   = ref('')
const sentimentResult = ref(null)
const twitterQuery    = ref('')
const twitterResults  = ref([])
const loadingSentiment = ref(false)
const loadingTwitter   = ref(false)

const volOption = computed(() => {
  const data = recentUpgrades.value
    .slice(0, 6)
    .filter(u => u.volatility_prediction)
    .map(u => ({
      name: u.protocol_name || 'Unknown',
      vol:  u.volatility_prediction?.predicted_volatility || 0,
    }))

  if (!data.length) {
    return {
      backgroundColor: 'transparent',
      graphic: [{
        type: 'text', left: 'center', top: 'center',
        style: { text: 'No volatility data', fill: '#3e3e58', fontFamily: 'Plus Jakarta Sans', fontSize: 12 },
      }],
    }
  }

  return {
    backgroundColor: 'transparent',
    grid: { top: 20, bottom: 32, left: 36, right: 8 },
    tooltip: {
      trigger: 'axis',
      backgroundColor: '#181826',
      borderColor: '#1e1e2e',
      textStyle: { color: '#e4e4f0', fontSize: 11, fontFamily: 'Inter' },
    },
    xAxis: {
      type: 'category',
      data: data.map(d => d.name),
      axisLabel: { color: '#7070a0', fontSize: 10, fontFamily: 'Plus Jakarta Sans', rotate: 20 },
      axisLine: { lineStyle: { color: '#1e1e2e' } },
    },
    yAxis: {
      type: 'value',
      axisLabel: { color: '#7070a0', fontSize: 10, fontFamily: 'Inter' },
      splitLine: { lineStyle: { color: '#1a1a28' } },
    },
    series: [{
      type: 'bar',
      data: data.map(d => ({
        value: d.vol,
        itemStyle: {
          color: d.vol > 0.3 ? '#ef4444' : d.vol > 0.15 ? '#f59e0b' : '#00c9a7',
          borderRadius: [4, 4, 0, 0],
        },
      })),
      barMaxWidth: 28,
    }],
  }
})

function riskColor(level) {
  if (!level) return 'badge-dim'
  const l = level.toLowerCase()
  if (l === 'high')   return 'badge-red'
  if (l === 'medium') return 'badge-amber'
  return 'badge-teal'
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
  if (!s) return 'var(--text2)'
  const l = s.toLowerCase()
  if (l === 'positive') return 'var(--green)'
  if (l === 'negative') return 'var(--red)'
  return 'var(--amber)'
}
</script>

<template>
  <div class="exec-panel">
    <div class="section-title">Execution Guidance</div>

    <!-- Volatility chart -->
    <div id="tour-volatility" class="card-accent" style="margin-bottom:12px; padding:12px 14px;">
      <div class="label" style="margin-bottom:8px;">Predicted Volatility</div>
      <v-chart :option="volOption" style="height:150px;" autoresize />
    </div>

    <!-- Execution timing -->
    <div class="card" style="margin-bottom:12px;">
      <div class="label" style="margin-bottom:10px;">Execution Timing</div>
      <div class="timing-list">
        <div class="timing-row">
          <div class="timing-icon timing-icon--teal">
            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="5 12 12 5 19 12"/><line x1="12" y1="19" x2="12" y2="5"/></svg>
          </div>
          <div class="timing-body">
            <span class="timing-key text-accent">Entry Window</span>
            <span class="timing-val">Within 24h of upgrade</span>
          </div>
        </div>
        <div class="timing-row">
          <div class="timing-icon timing-icon--amber">
            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="19 12 12 19 5 12"/><line x1="12" y1="5" x2="12" y2="19"/></svg>
          </div>
          <div class="timing-body">
            <span class="timing-key text-warn">Exit Strategy</span>
            <span class="timing-val">Monitor vol for 7 days</span>
          </div>
        </div>
        <div class="timing-row">
          <div class="timing-icon timing-icon--red">
            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
          </div>
          <div class="timing-body">
            <span class="timing-key text-negative">Stop Loss</span>
            <span class="timing-val">5% below entry</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Trading signals -->
    <div class="section-title">Trading Signals</div>
    <div id="tour-signals" class="recs-list" style="margin-bottom:12px;">
      <div
        v-for="(rec, i) in tradingRecs.slice(0, 4)"
        :key="i"
        class="rec-row fade-in"
      >
        <div class="rec-top">
          <span class="rec-name">{{ rec.protocol }}</span>
          <span class="badge" :class="riskColor(rec.risk_level)">{{ rec.risk_level }}</span>
        </div>
        <div class="rec-text">{{ rec.recommendation }}</div>
      </div>
      <div v-if="!tradingRecs.length" class="empty-state">
        No signals<span class="blink">_</span>
      </div>
    </div>

    <!-- Sentiment -->
    <div class="section-title">Sentiment Analysis</div>
    <div id="tour-sentiment" class="card" style="margin-bottom:12px;">
      <div class="input-row">
        <input
          v-model="sentimentText"
          class="hacker-input"
          placeholder="Enter text to analyze..."
          @keyup.enter="doSentiment"
        />
        <button class="btn-neon" @click="doSentiment" :disabled="loadingSentiment">
          {{ loadingSentiment ? '…' : 'Run' }}
        </button>
      </div>
      <div v-if="sentimentResult && !sentimentResult.error" class="sentiment-result">
        <div class="s-row">
          <span class="label">Sentiment</span>
          <span :style="{ color: sentimentColor(sentimentResult.sentiment), fontWeight: 600 }">
            {{ sentimentResult.sentiment?.toUpperCase() }}
          </span>
        </div>
        <div class="s-row">
          <span class="label">Polarity</span>
          <span style="color: var(--accent); font-weight:600;">{{ sentimentResult.polarity?.toFixed(3) }}</span>
        </div>
        <div class="s-row">
          <span class="label">Subjectivity</span>
          <span style="color: var(--text2);">{{ sentimentResult.subjectivity?.toFixed(3) }}</span>
        </div>
      </div>
      <div v-if="sentimentResult?.error" class="text-negative" style="font-size:12px; margin-top:6px;">
        Error: {{ sentimentResult.error }}
      </div>
    </div>

    <!-- Twitter -->
    <div class="section-title">Social Feed</div>
    <div class="card">
      <div class="input-row">
        <input
          v-model="twitterQuery"
          class="hacker-input"
          placeholder="#ethereum, uniswap..."
          @keyup.enter="doTwitter"
        />
        <button class="btn-cyan" @click="doTwitter" :disabled="loadingTwitter">
          {{ loadingTwitter ? '…' : 'Fetch' }}
        </button>
      </div>
      <div v-if="twitterResults.length" class="tw-results">
        <div
          v-for="(tw, i) in twitterResults"
          :key="i"
          class="tw-row"
        >
          <div class="tw-text">{{ tw.text?.slice(0, 100) }}</div>
          <span
            class="badge"
            :class="tw.polarity > 0 ? 'badge-teal' : tw.polarity < 0 ? 'badge-red' : 'badge-dim'"
            style="font-size:10px; flex-shrink:0;"
          >
            {{ tw.sentiment }}
          </span>
        </div>
      </div>
      <div v-if="!twitterResults.length && !loadingTwitter" class="empty-state" style="margin-top:6px;">
        Enter a query and press Fetch
      </div>
    </div>
  </div>
</template>

<style scoped>
.exec-panel { display: flex; flex-direction: column; }

/* Timing */
.timing-list { display: flex; flex-direction: column; gap: 10px; }
.timing-row  { display: flex; align-items: flex-start; gap: 10px; }
.timing-icon {
  width: 26px;
  height: 26px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  margin-top: 1px;
}
.timing-icon--teal   { background: rgba(0,201,167,0.12); color: #00c9a7; }
.timing-icon--amber  { background: rgba(245,158,11,0.12); color: #f59e0b; }
.timing-icon--red    { background: rgba(239,68,68,0.12);  color: #ef4444; }
.timing-body { display: flex; flex-direction: column; gap: 2px; }
.timing-key  { font-size: 12px; font-weight: 600; }
.timing-val  { font-size: 11px; color: var(--text2); }

/* Recs */
.recs-list { display: flex; flex-direction: column; gap: 6px; }
.rec-row {
  background: var(--raised);
  border: 1px solid var(--border);
  border-radius: var(--r-sm);
  padding: 10px 12px;
  transition: border-color 0.15s;
}
.rec-row:hover { border-color: var(--border2); }
.rec-top { display: flex; align-items: center; justify-content: space-between; margin-bottom: 4px; }
.rec-name { font-size: 13px; font-weight: 700; color: var(--text1); }
.rec-text { font-size: 12px; font-weight: 400; color: var(--text2); line-height: 1.55; }

/* Input row */
.input-row { display: flex; gap: 8px; align-items: center; margin-bottom: 10px; }

/* Sentiment */
.sentiment-result { display: flex; flex-direction: column; gap: 6px; padding-top: 10px; border-top: 1px solid var(--border); }
.s-row { display: flex; align-items: center; justify-content: space-between; font-size: 12px; }

/* Twitter */
.tw-results { display: flex; flex-direction: column; gap: 5px; max-height: 160px; overflow-y: auto; }
.tw-row {
  background: var(--raised);
  border: 1px solid var(--border);
  border-radius: 6px;
  padding: 7px 10px;
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 8px;
}
.tw-text { font-size: 11px; color: var(--text2); flex: 1; line-height: 1.5; }

.empty-state { font-size: 12px; color: var(--text3); }
</style>
