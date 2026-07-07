import { onUnmounted } from 'vue'
import Shepherd from 'shepherd.js'
import 'shepherd.js/dist/css/shepherd.css'

function highlight(selector) {
  document.querySelectorAll('.tour-highlight').forEach(el => el.classList.remove('tour-highlight'))
  if (selector) {
    const el = document.querySelector(selector)
    if (el) el.classList.add('tour-highlight')
  }
}

const isMobile = () => window.innerWidth < 768

export function useOnboarding() {
  let tour = null

  function startTour() {
    if (tour) tour.cancel()

    tour = new Shepherd.Tour({
      useModalOverlay: true,
      defaultStepOptions: {
        cancelIcon: { enabled: true },
        scrollTo: { behavior: 'smooth', block: 'center' },
        popperOptions: {
          modifiers: [
            { name: 'offset', options: { offset: [0, 16] } },
            { name: 'preventOverflow', options: { padding: 12 } },
            { name: 'flip', options: { fallbackPlacements: ['bottom', 'top'] } },
          ],
        },
      },
    })

    const steps = [
      {
        id: 'header',
        target: '#tour-header',
        on: 'bottom',
        title: '📡 Live Status',
        text: 'Shows real-time WebSocket connection status. <b>Green = streaming live</b> from the blockchain. Goes offline when backend sleeps.',
      },
      {
        id: 'networks',
        target: '#tour-networks',
        on: 'right',
        title: '🌐 Network Status',
        text: 'Monitors <b>Ethereum, Polygon, and Arbitrum</b> simultaneously. Shows live token prices and on-chain event counts per network.',
      },
      {
        id: 'prices',
        target: '#tour-prices',
        on: 'right',
        title: '💰 Protocol Prices',
        text: 'Live prices for DeFi protocols pulled from <b>CoinGecko API</b>. Green = price up, red = price down in the last 24h.',
      },
      {
        id: 'events',
        target: '#tour-events',
        on: 'right',
        title: '⚡ Live Events',
        text: 'Real-time blockchain events — governance proposals, votes cast, parameter changes, and security patches as they happen.',
      },
      {
        id: 'risk-gauge',
        target: '#tour-risk-gauge',
        on: 'left',
        title: '🎯 Risk Score',
        text: 'ML model scores protocol upgrade risk <b>0–100</b>. <span style="color:#00c9a7">Green = safe</span>, <span style="color:#f59e0b">amber = elevated</span>, <span style="color:#ef4444">red = critical</span>.',
      },
      {
        id: 'risk-chart',
        target: '#tour-risk-chart',
        on: 'left',
        title: '📈 Risk Over Time',
        text: 'Historical risk score trend. Helps identify if protocol risk is <b>increasing or stabilizing</b> over time.',
      },
      {
        id: 'risk-dist',
        target: '#tour-risk-dist',
        on: 'left',
        title: '🥧 Risk Distribution',
        text: 'Breakdown of upgrades into <b>Low / Medium / Critical</b> buckets. Mostly green = healthy ecosystem.',
      },
      {
        id: 'upgrades',
        target: '#tour-upgrades',
        on: 'left',
        title: '🔄 Recent Upgrades',
        text: 'Latest governance proposals and smart contract upgrades. Badges show <b>Active, Pending, Voting, or Failed</b> status.',
      },
      {
        id: 'volatility',
        target: '#tour-volatility',
        on: 'left',
        title: '📊 Predicted Volatility',
        text: '<b>GARCH model</b> forecasts price volatility per protocol. Taller bars = more expected price movement post-upgrade.',
      },
      {
        id: 'signals',
        target: '#tour-signals',
        on: 'left',
        title: '🚦 Trading Signals',
        text: 'AI-generated guidance based on risk score. <b>Low = accumulate, Medium = monitor, High = caution.</b>',
      },
      {
        id: 'sentiment',
        target: '#tour-sentiment',
        on: 'left',
        title: '🧠 Sentiment Analysis',
        text: 'Paste any crypto text for instant <b>NLP sentiment scoring</b>. Also fetches live Twitter/X sentiment for any query.',
      },
    ]

    steps.forEach((s, i) => {
      const isFirst = i === 0
      const isLast  = i === steps.length - 1
      const position = isMobile() ? 'bottom' : s.on

      const buttons = []
      if (!isFirst) buttons.push({ text: '← Back', action: () => tour.back(), classes: 'shepherd-btn-back' })
      buttons.push({ text: isLast ? 'Done ✓' : 'Next →', action: () => isLast ? tour.complete() : tour.next(), classes: 'shepherd-btn-next' })

      tour.addStep({
        id: s.id,
        attachTo: { element: s.target, on: position },
        title: s.title,
        text: s.text,
        buttons,
        when: {
          show: () => highlight(s.target),
          hide: () => highlight(null),
        },
      })
    })

    tour.on('complete', () => highlight(null))
    tour.on('cancel',   () => highlight(null))

    tour.start()
    localStorage.setItem('pum-tour-done', '1')
  }

  function checkAutoStart() {
    if (!localStorage.getItem('pum-tour-done')) {
      setTimeout(startTour, 1200)
    }
  }

  onUnmounted(() => {
    if (tour) tour.cancel()
  })

  return { startTour, checkAutoStart }
}
