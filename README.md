# Wos_Battle_Simulator

## Backend (FastAPI)

```bash
pip install -r requirements.txt
uvicorn backend.api.main:app --reload
```

- `GET /health` — health check
- `POST /simulate` — run battle simulations (JSON body: `attacker`, `defender`, `attacker_joiners`, `defender_joiners`, `num_sims`)

## Frontend (React + Vite + Tailwind)

```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:5173 — UI uses dummy data until wired to the API.