# Securing AI Agent Ecosystems

**CYBR 500 — Advanced Cybersecurity Research**  
**Author:** Shadman  
**Date:** April 2026  

A 7-agent AI research assistant system built with OpenClaw and Google Gemini, featuring a Chainlit dashboard. This project demonstrates 4 live prompt injection attacks against an unguarded AI pipeline, followed by a secured version demonstrating a Human-in-the-Loop (HITL) Security Interceptor.

## Features
- **Vulnerable Demo:** Runs 4 live prompt injection attacks, demonstrating how an unguarded agent can leak `/etc/passwd`.
- **Secured Demo:** Runs the exact same attacks against a Human-in-the-Loop Security Interceptor, showing the attacks being blocked in real-time.
- **Unified Web Interface:** A custom Top Navigation bar allows seamless switching between the demos and viewing the research report directly inside the app.

## Deployment on Render / Railway

To deploy this project for free on Render or Railway, follow these steps:

### Option A: Railway (Recommended)
Railway is the easiest platform for this because it auto-detects Python and just works.
1. Sign up for a free account at [railway.app](https://railway.app).
2. Click **New Project** → **Deploy from GitHub repo**.
3. Connect your GitHub and select this repository (`shadman1996/Project-4`).
4. Add the following **Environment Variables** in the Railway dashboard:
   - `GEMINI_API_KEY` = (your API key)
   - `PORT` = `8000`
5. Railway will automatically detect the `Procfile` and `requirements.txt` and deploy the app.

### Option B: Render
1. Sign up at [render.com](https://render.com).
2. Click **New** → **Web Service** → Connect your GitHub repo.
3. Configure the service:
   - **Environment:** Python 3
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `chainlit run app_secured.py --port $PORT --host 0.0.0.0`
4. Add the **Environment Variable**:
   - `GEMINI_API_KEY` = (your API key)
5. Click **Create Web Service**.

## Running Locally

```bash
# 1. Setup virtual environment
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# 2. Add API Key
cp .env.example .env
# Edit .env and add your GEMINI_API_KEY

# 3. Run Secured HITL Demo (Contains all web UI features)
chainlit run app_secured.py
```

## Project Structure
- `app_secured.py`: The main unified Chainlit dashboard containing both vulnerable and secured demos.
- `src/`: Core agent logic, Pydantic schemas, and Gemini integration
- `src/security/`: The Security Interceptor and HITL logic
- `attacks/`: Prompt injection payloads used in the demo
- `report/`: The final CYBR 500 conference-style research paper
- `docs/`: Reference documents and templates provided for the CYBR 500 course
- `public/`: Custom JavaScript (Top Navbar injection) and CSS
