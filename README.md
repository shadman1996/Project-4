# Security Risks of AI-Supported Cloud Applications

**CYBR 500 — Advanced Cybersecurity Research (Project 4)**  
**Authors:** Shadman Ahsan, Samson N. Tadesse  
**Date:** May 2026  
**Topic:** Security Risks of AI-Supported Cloud Applications (MITRE ATLAS, STRIDE, RAG Attack Surfaces)

## Live Deployment
This project is live and deployed on Railway Cloud:
**[https://web-production-bc354.up.railway.app](https://web-production-bc354.up.railway.app)**

---

## For the Professor / Grading
All official documentation required for the CYBR 500 Project 4 submission can be found in the **[`report/`](./report)** folder of this repository:
1. `CYBR500_Project4_Report.md` — The fully populated 12-section final report, including the AI-Assisted Learning Appendix.

This project is a 7-agent AI research assistant system built with OpenClaw and Google Gemini, featuring a Chainlit dashboard. It investigates the security risks of autonomous AI agents by demonstrating 8 live prompt injection attacks against an unguarded AI pipeline, followed by a secured version demonstrating a Human-in-the-Loop (HITL) Security Interceptor.

## Features
- **Live Agent Pipeline:** Run a full 7-agent academic research pipeline (Coordinator, Search-A, Search-B, Verifier, Ranker, Synthesis, Data).
- **Vulnerable Demo:** Run 8 live prompt injection attacks — including environment variable exfiltration, system file leaks, RAG Knowledge Base poisoning, and Multi-Turn Sleeper exploitation.
- **Secured Demo:** Runs the exact same attacks against a Human-in-the-Loop Security Interceptor, showing the attacks being blocked in real-time.
- **Threat Taxonomy:** All attacks are explicitly mapped to **MITRE ATLAS** techniques and **STRIDE** threat categories in the live UI.
- **Security Audit Logging:** The secured demo automatically exports a `security_audit_log.json` file detailing all intercepted threats.

## Local Development Setup

```bash
# 1. Setup virtual environment
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt

# 2. Add API Key
cp .env.example .env
# Edit .env and add your GEMINI_API_KEY

# 3. Run the App
chainlit run app.py
```

## Project Structure
- `app.py`: The main unified Chainlit dashboard containing both vulnerable and secured demos.
- `src/`: Core agent logic, Pydantic schemas, and Gemini integration
- `src/security/`: The Security Interceptor and HITL logic
- `attacks/`: Prompt injection payloads (including RAG corpus poisoning)
- `report/`: The final CYBR 500 conference-style research paper
- `public/`: Custom JavaScript and CSS
