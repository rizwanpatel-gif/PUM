import axios from 'axios'

// In dev: Vite proxy handles /api → localhost:8000
// In prod: VITE_API_URL=https://your-app.railway.app
const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || '/api/v1',
  timeout: 15000,
})

export const fetchBulkData    = () => api.get('/dashboard/bulk-data')
export const fetchEvents      = (network) => api.get(`/events/${network}?since_hours=24`)
export const fetchPrices      = () => api.get('/prices/protocols')
export const fetchNetworks    = () => api.get('/networks')
export const fetchRiskHistory = (id, days = 30) => api.get(`/risk/history/${id}?days=${days}`)
export const fetchVolHistory  = (addr, days = 30) => api.get(`/volatility/history/${addr}?days=${days}`)
export const analyzeSentiment = (text) => api.post('/sentiment/analyze', { text })
export const fetchTwitter     = (query) => api.get('/sentiment/twitter', { params: { query, count: 10 } })

export default api
