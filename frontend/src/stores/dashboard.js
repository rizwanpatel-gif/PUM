import { defineStore } from 'pinia'
import { fetchBulkData, fetchEvents, fetchPrices } from '../api/index.js'

export const useDashboardStore = defineStore('dashboard', {
  state: () => ({
    riskScores: [],
    recentUpgrades: [],
    tradingRecs: [],
    riskDistribution: {},
    networkEvents: { ethereum: [], polygon: [], arbitrum: [] },
    prices: {},
    wsMessages: [],
    loading: false,
    lastUpdate: null,
    wsConnected: false,
  }),

  getters: {
    avgRisk: (s) => s.riskScores.length ? (s.riskScores.reduce((a, b) => a + b, 0) / s.riskScores.length) : 0,
    highRiskCount: (s) => s.riskScores.filter(r => r >= 70).length,
    riskLevel: (s) => {
      const avg = s.riskScores.length ? s.riskScores.reduce((a, b) => a + b, 0) / s.riskScores.length : 0
      if (avg >= 70) return 'CRITICAL'
      if (avg >= 40) return 'ELEVATED'
      return 'NOMINAL'
    },
  },

  actions: {
    async loadBulkData() {
      this.loading = true
      try {
        const { data } = await fetchBulkData()
        this.riskScores       = data.risk_scores || []
        this.recentUpgrades   = data.recent_upgrades || []
        this.tradingRecs      = data.trading_recommendations || []
        this.riskDistribution = data.risk_distribution || {}
        this.lastUpdate       = new Date()
      } catch (e) {
        console.warn('bulk-data fetch failed:', e.message)
      } finally {
        this.loading = false
      }
    },

    async loadEvents() {
      for (const net of ['ethereum', 'polygon', 'arbitrum']) {
        try {
          const { data } = await fetchEvents(net)
          this.networkEvents[net] = data.events || []
        } catch {}
      }
    },

    async loadPrices() {
      try {
        const { data } = await fetchPrices()
        this.prices = data.prices || {}
      } catch {}
    },

    connectWS() {
      // In dev: proxy handles ws → localhost:8000
      // In prod: VITE_WS_URL=wss://your-app.railway.app/ws
      const wsUrl = import.meta.env.VITE_WS_URL || (() => {
        const proto = location.protocol === 'https:' ? 'wss' : 'ws'
        return `${proto}://${location.host}/ws`
      })()
      const ws = new WebSocket(wsUrl)
      ws.onopen  = () => { this.wsConnected = true }
      ws.onclose = () => { this.wsConnected = false; setTimeout(() => this.connectWS(), 5000) }
      ws.onmessage = (e) => {
        try {
          const msg = JSON.parse(e.data)
          this.wsMessages.unshift({ ...msg, ts: new Date().toLocaleTimeString() })
          if (this.wsMessages.length > 50) this.wsMessages.pop()
        } catch {}
      }
    },
  },
})
