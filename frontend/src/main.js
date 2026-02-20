import { createApp } from 'vue'
import { createPinia } from 'pinia'
import { createRouter, createWebHistory } from 'vue-router'
import ECharts from 'vue-echarts'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { GaugeChart, BarChart, LineChart, CandlestickChart, PieChart } from 'echarts/charts'
import {
  GridComponent, TooltipComponent, LegendComponent,
  TitleComponent, DataZoomComponent, MarkLineComponent,
} from 'echarts/components'

import './style.css'
import App from './App.vue'
import Dashboard from './views/Dashboard.vue'

use([
  CanvasRenderer,
  GaugeChart, BarChart, LineChart, CandlestickChart, PieChart,
  GridComponent, TooltipComponent, LegendComponent,
  TitleComponent, DataZoomComponent, MarkLineComponent,
])

const router = createRouter({
  history: createWebHistory(),
  routes: [{ path: '/', component: Dashboard }],
})

const app = createApp(App)
app.use(createPinia())
app.use(router)
app.component('v-chart', ECharts)
app.mount('#app')
