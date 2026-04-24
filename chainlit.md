# 🔬 Project 4 — Securing AI Agent Ecosystems

**CYBR 500 — Advanced Cybersecurity Research** | Student: Shadman | April 2026

---

## 🎯 What This Project Is About

AI systems are increasingly built as networks of **autonomous agents** — individual AI "workers" that each handle a specific task (searching, verifying, writing, saving files). These agents communicate in plain English, which creates a serious security problem: **anyone who can send a message can potentially hijack what an agent does**.

This project:
1. **Builds** a 7-agent AI research assistant (the system you're looking at)
2. **Attacks** it using prompt injection — a technique where a crafted message tricks an agent into leaking files or secrets
3. **Defends** it with a Human-in-the-Loop (HITL) security interceptor that asks *you* to approve or deny dangerous operations

---

## 🏗️ The 7-Agent Pipeline

Every research question flows through this chain:

| Step | Agent | What it does |
|------|-------|--------------|
| 1 | 🎯 **Coordinator** | Reads your question and creates a research plan |
| 2 | 🔍 **Search-A** | Searches academic papers and web sources |
| 3 | 🔎 **Search-B** | Searches CVE databases and technical advisories |
| 4 | ✅ **Verification** | Cross-checks facts and removes unreliable sources |
| 5 | 📊 **Ranking** | Scores findings by relevance, credibility, and recency |
| 6 | 📝 **Synthesis** | Writes the final research report |
| — | 💾 **Data** | Reads/writes files — the **attack target** in this demo |

---

## ⚠️ Two Versions of This System

| Version | File | What to expect |
|---------|------|----------------|
| 🔴 **Vulnerable** | `app.py` | No guardrails — agents can be tricked into reading any file |
| 🛡️ **Secured** | `app_secured.py` | Security interceptor blocks dangerous operations and asks your approval |

**You are currently running:** check the browser tab title to confirm which version is active.

---

## 🚀 Getting Started

Use the **buttons below** in the chat to:
- 🔴 **Run Red Team Attack Demo** — watch a live prompt injection attack succeed
- 🛡️ **Run Defence Demo** — watch the same attacks get blocked (in `app_secured.py`)
- 🔬 **Ask a research question** — use the pipeline for real cybersecurity research

**Example research questions:**
- *"Analyze prompt injection defenses in LLM-based systems"*
- *"Research supply chain attacks on AI model registries"*
- *"Compare detection methods for adversarial machine learning attacks"*

---

*Powered by Google Gemini API (9-model fallback chain) + Chainlit dashboard*
