import { defineStore } from 'pinia'
import { fetchBulkData, fetchEvents, fetchPrices } from '../api/index.js'

const DEMO_PRICES = {
  ethereum:      { symbol: 'ETH',  price: 3241.50, change_24h: 2.14, volume_24h: 18400000000 },
  'matic-network': { symbol: 'MATIC', price: 0.8820, change_24h: -1.03, volume_24h: 412000000 },
  arbitrum:      { symbol: 'ARB',  price: 0.6540, change_24h: 3.27, volume_24h: 198000000 },
  'aave':        { symbol: 'AAVE', price: 89.16,  change_24h: 1.72, volume_24h: 161800000 },
  'uniswap':     { symbol: 'UNI',  price: 3.65,   change_24h: 2.88, volume_24h: 200100000 },
  'balancer':    { symbol: 'BAL',  price: 0.1420, change_24h: 0.13, volume_24h: 261400 },
  'curve-dao-token': { symbol: 'CRV', price: 0.3100, change_24h: -1.12, volume_24h: 42000000 },
  'compound-governance-token': { symbol: 'COMP', price: 34.21, change_24h: -0.54, volume_24h: 14200000 },
}

const DEMO_BULK = {
  risk_scores: [42, 58, 35, 71, 48, 62, 39, 55, 67, 44],
  risk_distribution: { low: 3, medium: 5, high: 2 },
  trading_recommendations: [
    { protocol: 'Aave V3', recommendation: 'Medium risk - Monitor closely', risk_level: 'Medium' },
    { protocol: 'Uniswap V3', recommendation: 'Low risk - Consider accumulating', risk_level: 'Low' },
    { protocol: 'Compound V3', recommendation: 'High risk - Exercise caution', risk_level: 'High' },
  ],
  recent_upgrades: [
    {
      id: 1, protocol_name: 'Aave V3', title: 'Oracle upgrade to Chainlink v2',
      description: 'Migrating price oracles to Chainlink v2 for improved reliability.',
      status: 'active', upgrade_type: 'implementation_upgrade', created_at: new Date(Date.now() - 86400000).toISOString(),
      risk_assessment: { overall_risk_score: 42, technical_risk: 38, governance_risk: 45, market_risk: 41, liquidity_risk: 44 },
      volatility_prediction: { predicted_volatility: 0.18, confidence_interval_lower: 0.14, confidence_interval_upper: 0.22 },
    },
    {
      id: 2, protocol_name: 'Uniswap V3', title: 'Fee tier adjustment for stable pools',
      description: 'Reducing fee tiers on stablecoin pairs to improve capital efficiency.',
      status: 'voting', upgrade_type: 'parameter_change', created_at: new Date(Date.now() - 172800000).toISOString(),
      risk_assessment: { overall_risk_score: 35, technical_risk: 30, governance_risk: 40, market_risk: 32, liquidity_risk: 38 },
      volatility_prediction: { predicted_volatility: 0.09, confidence_interval_lower: 0.07, confidence_interval_upper: 0.11 },
    },
    {
      id: 3, protocol_name: 'Compound V3', title: 'Parameter update: liquidation threshold',
      description: 'Adjusting liquidation thresholds to reduce bad debt risk.',
      status: 'pending', upgrade_type: 'parameter_change', created_at: new Date(Date.now() - 259200000).toISOString(),
      risk_assessment: { overall_risk_score: 71, technical_risk: 68, governance_risk: 75, market_risk: 72, liquidity_risk: 69 },
      volatility_prediction: { predicted_volatility: 0.41, confidence_interval_lower: 0.33, confidence_interval_upper: 0.49 },
    },
    {
      id: 4, protocol_name: 'Curve Finance', title: 'Smart contract security patch',
      description: 'Critical security patch addressing reentrancy vulnerability.',
      status: 'approved', upgrade_type: 'security_patch', created_at: new Date(Date.now() - 345600000).toISOString(),
      risk_assessment: { overall_risk_score: 58, technical_risk: 62, governance_risk: 50, market_risk: 61, liquidity_risk: 59 },
      volatility_prediction: { predicted_volatility: 0.29, confidence_interval_lower: 0.23, confidence_interval_upper: 0.35 },
    },
    {
      id: 5, protocol_name: 'Balancer', title: 'Governance module migration',
      description: 'Migrating to new on-chain governance module with timelock.',
      status: 'failed', upgrade_type: 'governance_proposal', created_at: new Date(Date.now() - 432000000).toISOString(),
      risk_assessment: { overall_risk_score: 48, technical_risk: 44, governance_risk: 55, market_risk: 46, liquidity_risk: 47 },
      volatility_prediction: { predicted_volatility: 0.22, confidence_interval_lower: 0.18, confidence_interval_upper: 0.26 },
    },
  ],
}

const DEMO_EVENTS = {
  ethereum: [
    { id: 1, event_type: 'UpgradeProposed', transaction_hash: '0xabc...001', block_number: 19800001, timestamp: new Date(Date.now() - 3600000).toISOString() },
    { id: 2, event_type: 'VoteCast', transaction_hash: '0xabc...002', block_number: 19800042, timestamp: new Date(Date.now() - 7200000).toISOString() },
    { id: 3, event_type: 'ProposalExecuted', transaction_hash: '0xabc...003', block_number: 19800088, timestamp: new Date(Date.now() - 10800000).toISOString() },
  ],
  polygon: [
    { id: 4, event_type: 'ParameterChanged', transaction_hash: '0xdef...001', block_number: 52000001, timestamp: new Date(Date.now() - 5400000).toISOString() },
    { id: 5, event_type: 'VoteCast', transaction_hash: '0xdef...002', block_number: 52000055, timestamp: new Date(Date.now() - 9000000).toISOString() },
  ],
  arbitrum: [
    { id: 6, event_type: 'UpgradeProposed', transaction_hash: '0xghi...001', block_number: 180000001, timestamp: new Date(Date.now() - 4800000).toISOString() },
    { id: 7, event_type: 'EmergencyPause', transaction_hash: '0xghi...002', block_number: 180000099, timestamp: new Date(Date.now() - 8400000).toISOString() },
  ],
}

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
        const upgrades = data.recent_upgrades || []
        if (upgrades.length) {
          this.riskScores       = data.risk_scores || []
          this.recentUpgrades   = upgrades
          this.tradingRecs      = data.trading_recommendations || []
          this.riskDistribution = data.risk_distribution || {}
          this.lastUpdate       = new Date()
        } else {
          this._loadDemoBulk()
        }
      } catch (e) {
        console.warn('bulk-data fetch failed, using demo data:', e.message)
        this._loadDemoBulk()
      } finally {
        this.loading = false
      }
    },

    _loadDemoBulk() {
      this.riskScores       = DEMO_BULK.risk_scores
      this.recentUpgrades   = DEMO_BULK.recent_upgrades
      this.tradingRecs      = DEMO_BULK.trading_recommendations
      this.riskDistribution = DEMO_BULK.risk_distribution
    },

    async loadEvents() {
      for (const net of ['ethereum', 'polygon', 'arbitrum']) {
        try {
          const { data } = await fetchEvents(net)
          const events = data.events || []
          this.networkEvents[net] = events.length ? events : DEMO_EVENTS[net]
        } catch {
          this.networkEvents[net] = DEMO_EVENTS[net]
        }
      }
    },

    async loadPrices() {
      try {
        const { data } = await fetchPrices()
        const prices = data.prices || {}
        this.prices = Object.keys(prices).length ? prices : DEMO_PRICES
      } catch {
        this.prices = DEMO_PRICES
      }
    },

    connectWS() {
      // In dev: proxy handles ws → localhost:8000
      // In prod: VITE_WS_URL=wss://your-app.railway.app/ws
      const apiBase = import.meta.env.VITE_API_URL || ''
      const wsUrl = import.meta.env.VITE_WS_URL ||
        (apiBase
          ? apiBase.replace(/^http/, 'ws').replace(/\/api\/v1\/?$/, '') + '/ws'
          : (() => {
              const proto = location.protocol === 'https:' ? 'wss' : 'ws'
              return `${proto}://${location.host}/ws`
            })()
        )
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
