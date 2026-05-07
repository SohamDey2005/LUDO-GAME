# 🎲 LUDO GAME - Professional Web Edition

[![React](https://img.shields.io/badge/React-18-blue.svg)](https://reactjs.org/)
[![Phaser](https://img.shields.io/badge/Phaser-3.8-orange.svg)](https://phaser.io/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109-green.svg)](https://fastapi.tiangolo.com/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5-blue.svg)](https://www.typescriptlang.org/)

A production-grade, full-stack Ludo game engine built for high-performance web play. Featuring **strict official rules**, **real-time multiplayer synchronization**, and **adaptive AI** with a stunning responsive UI.

---

## ✨ Key Features

### 🏆 Official Ruleset Implementation
*   **Strict Board Entry**: Tokens enter the board ONLY on a roll of 6.
*   **Token Stacking (Blocks)**: If a player occupies a cell with 2+ tokens, it forms a **BLOCK**. Opponents cannot land on, capture, or pass through blocks.
*   **Rule 6 (3-Six Penalty)**: Rolling three consecutive sixes triggers a **full turn rollback**, restoring the board to its exact state before the turn began.
*   **Capture Bonus**: Capturing an opponent's token (outside safe zones) grants an immediate bonus turn.
*   **Exact Roll to Finish**: Tokens require a precise roll to reach the final home square.
*   **Configurable Safe Zones**: 8 designated star-marked cells provide immunity from capture.

### 🤖 Advanced AI Opponents
*   **Heuristic Engine**: AI simulates multiple outcomes and scores moves based on risk, progress, and capture opportunities.
*   **Three Difficulty Levels**: Choose between Easy (random), Medium (aggressive), and Hard (defensive/strategic).

### 🌐 Real-time Multiplayer
*   **WebSocket Sync**: Instant state broadcasts ensure every move is seen by all players at 60fps.
*   **Cloud Persistence**: Games survive server restarts, allowing for high-availability deployments.
*   **Fully Responsive**: Adapts seamlessly to mobile phones, tablets, and desktop monitors with touch-optimized controls.

---

## 🛠 Tech Stack

| Component | Technologies |
| :--- | :--- |
| **Frontend** | React 18, Phaser 3 (Engine), Tailwind CSS, Vite |
| **Backend** | Python 3.11+, FastAPI, WebSockets (Pydantic models) |
| **AI** | Custom Heuristic Simulation & Expectiminimax |
| **Infrastructure** | Docker, Google Cloud Run, Vercel |

---

## 📂 Project Architecture

```text
LUDO-GAME/
├── frontend/                   # React UI & Phaser Graphics
│   ├── src/
│   │   ├── scenes/             # Phaser Canvas Rendering (LudoBoardScene)
│   │   ├── services/           # Socket & API orchestration
│   │   └── components/         # React HUD & Menu components
├── backend/                    # FastAPI High-Performance Server
│   ├── app/
│   │   ├── core/               # Authoritative Rules Engine & Paths
│   │   ├── ai/                 # Simulation & Heuristics
│   │   ├── services/           # Game State & Orchestration
│   └── tests/                  # Pytest Validation Suite
```

---

## 🚀 Getting Started

### Prerequisites
*   Node.js (v18+)
*   Python (3.11+)

### 1. Backend Setup
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```

### 2. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

---

## ☁️ Deployment

### Backend (Cloud Run)
```bash
cd backend
gcloud run deploy ludo-backend --source . --platform managed --allow-unauthenticated
```

### Frontend (Vercel)
1. Push to your GitHub repo.
2. Connect to Vercel.
3. Set root directory to `frontend/`.
4. Deploy!

---

## 📄 License
Created & Developed by **SOHAM DEY**. 
Built for high-performance casual gaming and AI experimentation.
