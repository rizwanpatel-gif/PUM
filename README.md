# Protocol Upgrade Monitor

Real-time monitoring system for blockchain protocol upgrades across Ethereum, Polygon, and Arbitrum. Tracks on-chain events, scores upgrade risk, forecasts volatility, and surfaces execution guidance through a live dashboard.

**Live demo:** https://pum.vercel.app
**API docs:** https://your-app.railway.app/docs

---

## Stack

| Layer | Technology |
|---|---|
| Backend API | FastAPI, Python 3.12 |
| Frontend | Vue 3, Vite, Tailwind CSS |
| Charts | Apache ECharts (vue-echarts) |
| State | Pinia |
| Database | SQLite (dev) / PostgreSQL (prod) |
| Real-time | WebSocket |
| ML / Analytics | GARCH, ARIMA, scikit-learn, TextBlob |
| Blockchain | Web3.py, Etherscan API |
| Deployment | Railway (API) + Vercel (frontend) |

---

## Architecture

```
frontend/           Vue 3 + Vite (port 5173 in dev)
  src/
    api/            Axios client — proxies to FastAPI in dev
    stores/         Pinia state + WebSocket connection
    components/     HackerHeader, NetworkPanel, RiskPanel, ExecutionPanel
    views/          Dashboard

app/                FastAPI application (port 8000)
  api/              REST routes + WebSocket handler
  core/             blockchain.py, risk_models.py, volatility.py,
                    liquidity.py, sentiment.py, governance.py
  database/         SQLAlchemy models + SQLite connection
  ml/               Training pipeline, model evaluation

railway.json        Backend deploy config (Railway)
frontend/vercel.json  Frontend deploy config (Vercel)
```

---

## Local Development

**Prerequisites:** Python 3.10+, Node 18+

**1. Backend**

```bash
git clone https://github.com/your-username/pum
cd pum

python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

pip install -r requirements.txt

cp .env.example .env            # fill in your API keys

python -c "from app.database.database import init_db; init_db()"

uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**2. Frontend**

```bash
cd frontend
npm install
npm run dev
```

Open `http://localhost:5173`

> The Vite dev server proxies `/api` and `/ws` to `localhost:8000` automatically.

---

## Environment Variables

Copy `.env.example` to `.env` and fill in values. Required keys:

| Variable | Description |
|---|---|
| `ETHERSCAN_API_KEY` | Etherscan Multichain API key |
| `POLYGONSCAN_API_KEY` | PolygonScan API key |
| `ARBISCAN_API_KEY` | Arbiscan API key |
| `COINGECKO_API_KEY` | CoinGecko API key |
| `TWITTER_BEARER_TOKEN` | Twitter API v2 bearer token |
| `ETHEREUM_RPC_URL` | Infura / Alchemy RPC endpoint |
| `SECRET_KEY` | JWT signing secret (change in production) |
| `DATABASE_URL` | SQLite path or PostgreSQL connection string |

---

## API Reference

Base URL: `http://localhost:8000/api/v1`

| Method | Endpoint | Description |
|---|---|---|
| GET | `/networks` | Supported blockchain networks |
| GET | `/protocols` | Monitored protocol list |
| GET | `/upgrades` | Recent protocol upgrades |
| GET | `/upgrades/{id}/risk` | Risk assessment for an upgrade |
| GET | `/upgrades/{id}/volatility` | Volatility forecast |
| GET | `/events/{network}` | On-chain events (last 24h) |
| GET | `/prices/protocols` | Protocol token prices |
| GET | `/dashboard/bulk-data` | Aggregated dashboard payload |
| POST | `/sentiment/analyze` | Analyze text sentiment |
| GET | `/sentiment/twitter` | Fetch and score tweets |
| WS | `/ws` | Real-time event stream |

Full interactive docs at `/docs` when the server is running.

---

## Deployment

**Backend — Railway**

1. Connect your GitHub repo to [railway.app](https://railway.app)
2. Railway detects Python via `requirements.txt` and uses `railway.json` for the start command
3. Add all environment variables in the Railway dashboard
4. Add a volume mounted at `/app` for SQLite persistence
5. Note your Railway public URL

**Frontend — Vercel**

1. Import repo at [vercel.com](https://vercel.com), set root directory to `frontend`
2. Add environment variables:
   ```
   VITE_API_URL=https://your-app.railway.app/api/v1
   VITE_WS_URL=wss://your-app.railway.app/ws
   ```
3. Deploy — Vercel handles the Vite build automatically via `frontend/vercel.json`

---

## Testing

```bash
pytest
pytest --cov=app tests/
```

---

## License

MIT
