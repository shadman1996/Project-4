# Securing AI Agent Ecosystems

**CYBR 500 — Advanced Cybersecurity Research**  
**Author:** Shadman Ahsan  
**Date:** April 2026  

## For the Professor / Grading
All official documentation required for the CYBR 500 Project 4 submission can be found in the **[`report/`](./report)** folder of this repository:
1. `CYBR500_Project4_Final_Report_Shadman.docx` (The fully populated 15-section final report with AI-Assisted Learning Appendix)
2. `CYBR500_Project4_Instruction_handout_April17.docx` (Reference Instructions)
3. `prj4_resources.docx` (Reference Resources)

A 7-agent AI research assistant system built with OpenClaw and Google Gemini, featuring a Chainlit dashboard. This project demonstrates 4 live prompt injection attacks against an unguarded AI pipeline, followed by a secured version demonstrating a Human-in-the-Loop (HITL) Security Interceptor.

## Features
- **Live Agent Pipeline:** Run a full 7-agent academic research pipeline (Coordinator, Search, Verifier, Ranker, Synthesis, Data).
- **Vulnerable Demo:** Run 4 live prompt injection attacks to see agents leak `/etc/passwd` and system secrets.
- **Secured Demo:** Runs the exact same attacks against a Human-in-the-Loop Security Interceptor, showing the attacks being blocked in real-time.
- **Unified Web Interface:** A custom Top Navigation bar allows seamless switching between the demos and viewing the research report directly inside the app.

## Live Deployment

This project is already **live and deployed on Railway**. 
- Any pushes to the `main` branch of this repository will automatically trigger a new deployment.
- No further configuration is required on your end, as the environment variables (`GEMINI_API_KEY`) and `Procfile` are already configured.

### Local Development Setup

```bash
# 1. Setup virtual environment
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# 2. Add API Key
cp .env.example .env
# Edit .env and add your GEMINI_API_KEY

# 3. Run Secured HITL Demo (Contains all web UI features)
chainlit run app.py
```

## Project Structure
- `app.py`: The main unified Chainlit dashboard containing both vulnerable and secured demos.
- `src/`: Core agent logic, Pydantic schemas, and Gemini integration
- `src/security/`: The Security Interceptor and HITL logic
- `attacks/`: Prompt injection payloads used in the demo
- `report/`: The final CYBR 500 conference-style research paper and grading deliverables
- `public/`: Custom JavaScript (Top Navbar injection) and CSS
