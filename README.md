# AI-Powered Web-Based Ludo Game

A production-quality, full-stack Ludo game featuring real-time multiplayer, a modern React/Phaser frontend, and a highly scalable Python FastAPI backend powered by advanced AI logic.

---

## 🎮 Features
- **Standard Ludo Gameplay**: Complete ruleset including safe zones, capturing, home stretching, and exact-roll wins.
- **Advanced AI Opponents**:
  - **Easy**: Randomly selects valid moves.
  - **Medium**: Heuristic-based, prioritizing captures, safe zones, and rapid advancement.
  - **Hard**: Simplified Expectiminimax algorithm that penalizes moves placing tokens at high risk of capture.
- **Real-time Multiplayer**: Powered by WebSockets for instant state synchronization across clients without polling.
- **Modern UI/UX**: Built with React, Tailwind CSS, and Phaser 3 for stunning 60fps animations, responsive glassmorphism menus, and dynamic interactions.
- **Data Persistence**: Automatic save/load system allowing games to survive server reboots, complete with global leaderboards.

---

## 🛠 Tech Stack
- **Frontend**: React 18, TypeScript, Phaser 3, Tailwind CSS, Vite.
- **Backend**: Python 3.11+, FastAPI, WebSockets, Pydantic, Uvicorn.
- **Infrastructure**: Docker, ready for Google Cloud Run (Backend) and Vercel (Frontend).

---

## 📂 Project Structure

```text
ludo-web-ai/
│
├── frontend/                     # React + Phaser UI
│   ├── public/                   # Static assets (Audio, Images)
│   ├── src/
│   │   ├── components/           # React UI components (Dice, App)
│   │   ├── game/                 # Phaser game config
│   │   ├── scenes/               # Phaser Scenes (LudoBoardScene)
│   │   ├── services/             # API client, WebSocket manager, Audio manager
│   │   └── main.tsx              # React entry point
│   ├── package.json
│   ├── vite.config.ts
│   └── tailwind.config.js
│
├── backend/                      # FastAPI Server
│   ├── app/
│   │   ├── ai/                   # AI logic (Heuristics, Minimax)
│   │   ├── api/                  # REST endpoints & WebSockets
│   │   ├── core/                 # Pure game rules & Dice logic
│   │   ├── models/               # Pydantic state models
│   │   ├── services/             # Game engine orchestrator & DB store
│   │   └── sockets/              # Connection Manager
│   ├── tests/                    # Pytest suite
│   ├── main.py                   # FastAPI entry point
│   ├── requirements.txt
│   ├── Dockerfile
│   └── .dockerignore
│
└── README.md
```

---

## 💻 Local Development

### Backend Setup
1. Open a terminal and navigate to the `backend` folder.
2. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the development server:
   ```bash
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```
   *The backend will be available at `http://localhost:8000`*

### Frontend Setup
1. Open a terminal and navigate to the `frontend` folder.
2. Install Node.js dependencies:
   ```bash
   npm install
   ```
3. Run the Vite development server:
   ```bash
   npm run dev
   ```
   *The frontend will be available at `http://localhost:3000`*

---

## 🧠 AI Architecture

The AI is built on a custom **Heuristic Evaluation Engine** (`backend/app/ai/heuristics.py`). 
The AI does not mutate the active game; it deep-copies the board state, simulates the dice roll, and scores the resulting state using configured weights:
- **Capture Enemy**: +100
- **Reach Finish**: +200
- **Reach Safe Zone**: +50
- **Escape Danger**: +40
- **Expose Token**: -60

The **Hard AI** uses a simplified **Expectiminimax** approach (`backend/app/ai/engine.py`). After simulating its own move, it calculates a *Risk Penalty* by analyzing all opponent tokens that are 1-6 squares behind its new position. It deducts this risk probability from the heuristic score, forcing the AI to play defensively while still trying to win.

---

## 🌐 Multiplayer & Sync Explanation

We use a highly scalable **Hybrid REST/WebSocket Architecture**:
1. **Actions (Writes)**: When a player rolls the dice or moves a token, the React frontend sends a standard `POST` request to the FastAPI REST endpoints. This ensures secure validation and makes rate-limiting easy.
2. **Synchronization (Reads)**: The backend calculates the new game state, saves it, and instantly broadcasts the updated JSON down the **WebSocket** (`backend/app/sockets/manager.py`) to all clients in that specific Game Room. React receives this push event, updates state, and Phaser visually renders the new truth.

---

## 🚀 Cloud Deployment Guide

### Deploying Backend to Google Cloud Run
Cloud Run is perfect for our backend because it auto-scales stateless containers.

1. Install the Google Cloud SDK (`gcloud`).
2. Authenticate and set your project:
   ```bash
   gcloud auth login
   gcloud config set project YOUR_PROJECT_ID
   ```
3. Deploy the container directly from the source:
   ```bash
   cd backend
   gcloud run deploy ludo-backend \
     --source . \
     --platform managed \
     --region us-central1 \
     --allow-unauthenticated \
     --port 8080
   ```
4. Note the deployed URL (e.g., `https://ludo-backend-xyz.run.app`). Update the `API_BASE` and WebSocket URL in `frontend/src/services/api.ts` and `socket.ts` to point to this new URL.

### Deploying Frontend to Vercel
Vercel is optimal for our Vite/React frontend.

1. Push your complete repository to GitHub.
2. Go to [Vercel.com](https://vercel.com) and click **Add New Project**.
3. Import your GitHub repository.
4. Set the **Root Directory** to `frontend`.
5. Vercel will automatically detect Vite. Leave the build commands as default (`npm run build`).
6. Click **Deploy**. Your frontend is now live!

---

## 🔮 Future Improvements
- **Database Migration**: Swap the lightweight `ludo_db.json` persistence layer in `store.py` for a managed PostgreSQL or Firebase instance.
- **Authentication**: Add JWT-based user login to track long-term Elo rankings.
- **Matchmaking Queues**: Implement a Redis-backed waiting queue for global matchmaking rather than direct room joining.
- **Reinforcement Learning**: Upgrade the Hard AI by training a Neural Network via self-play (PPO/DQN) using the existing REST architecture to simulate millions of games.
