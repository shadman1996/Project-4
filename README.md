# Project 4 — Securing Multi-Agent AI Ecosystems

**Course:** CYBR 500 — Advanced Cybersecurity Research  
**Student:** Shadman  
**Submission Date:** April 2026  
**Repository:** [github.com/shadman1996/Project-4](https://github.com/shadman1996/Project-4)

---

## What This Project Does (Plain English)

This project builds a **7-agent AI research assistant** and then **attacks it** to prove it is vulnerable — and then **defends it** with a Human-in-the-Loop (HITL) security system.

Think of it like this:
- 7 AI "employees" (agents) work together to answer cybersecurity research questions
- A red-team attacker sends a crafted message that tricks one agent into leaking the system's password file (`/etc/passwd`)
- A Security Interceptor is then installed that forces a human to click **Approve** or **Deny** before any dangerous file access happens

There are **two separate programs** to demonstrate the before/after:
- `app.py` → The **vulnerable** system (no guardrails)
- `app_secured.py` → The **secured** system (with HITL approval gate)

---

## How to Run It (Step-by-Step)

### Step 1 — Prerequisites
Make sure you have the following installed on your machine:
- Python 3.12 or newer
- `pip` (Python package manager)
- A terminal (Command Prompt, PowerShell, or Linux/macOS Terminal)

You will also need a **Google Gemini API key**. A free key from [ai.google.dev](https://ai.google.dev) is sufficient.

---

### Step 2 — Download the Project
```bash
git clone https://github.com/shadman1996/Project-4.git
cd "Project-4"
```

---

### Step 3 — Create a Python Virtual Environment
```bash
python3 -m venv .venv
source .venv/bin/activate        # On Linux / macOS
# OR
.venv\Scripts\activate           # On Windows
```

---

### Step 4 — Install Dependencies
```bash
pip install -r requirements.txt
```

---

### Step 5 — Configure the API Key
Create a file named `.env` in the project root folder and paste the following inside it:
```
GEMINI_API_KEY=YOUR_GEMINI_API_KEY_HERE
GEMINI_MODEL=gemini-3.1-flash-lite-preview
PROJECT_DIR=/absolute/path/to/Project-4
```
Replace `YOUR_GEMINI_API_KEY_HERE` with your actual key.

---

### Step 6 — Run the Vulnerable Dashboard (Phase 1 & 2 "Before")
```bash
chainlit run app.py
```
Open your browser and go to: **http://localhost:8000**

You will see the 7-agent research system. Type a question like:
> *"Analyze prompt injection defenses in LLM systems"*

Watch the agent handoffs happen in real time — each agent (Coordinator → Search → Verification → Ranking → Synthesis) is color-coded.

---

### Step 7 — Run the Red-Team Attacks (Phase 2 "Before" Evidence)
```bash
python attacks/run_attack.py
```
This runs 4 crafted prompt injection attacks. Look at the output — one attack successfully reads `/etc/passwd` and returns the system user list. This proves the vulnerability.

Results are saved to `attack_results/before_mitigation.json`.

---

### Step 8 — Run the Secured Dashboard (Phase 2 "After")
Open a new terminal and run:
```bash
chainlit run app_secured.py
```
Open your browser and go to: **http://localhost:8000**

Now try the same question again. When the system attempts any dangerous file operation, it will **pause and show you two buttons**:
- ✅ **Approve** — Allow the operation
- ❌ **Deny** — Block the operation

This is the Human-in-the-Loop (HITL) gate in action.

---

### Step 9 — Verify the Defense (Phase 2 "After" Evidence)
```bash
python attacks/verify_defense.py
```
Re-runs all 4 attacks against the secured system. All HIGH and CRITICAL operations are blocked by the interceptor.

Results are saved to `attack_results/after_mitigation.json`.

---

## Project Structure (What Each File Does)

```
Project-4/
│
├── app.py                     ← PROGRAM 1: Vulnerable dashboard (run first)
├── app_secured.py             ← PROGRAM 2: Secured dashboard with HITL gate
├── requirements.txt           ← All Python dependencies
├── .env.example               ← Template for your API key configuration
│
├── src/                       ← Core system code
│   ├── agents/
│   │   ├── coordinator.py     ← The "manager" agent that routes tasks
│   │   ├── search.py          ← Two search agents (academic + technical)
│   │   ├── verification.py    ← Checks accuracy of search results
│   │   ├── ranking.py         ← Ranks findings by relevance
│   │   ├── synthesis.py       ← Writes the final research report
│   │   └── data.py            ← File I/O agent (the attack target)
│   ├── security/
│   │   ├── interceptor.py     ← Blocks dangerous tool calls (HIGH/CRITICAL)
│   │   └── policies.py        ← Rules for what paths/commands are blocked
│   ├── llm.py                 ← Gemini API wrapper with 9-model fallback
│   ├── schemas.py             ← Structured output definitions (Pydantic)
│   └── config.py              ← API keys, model list, agent color codes
│
├── attacks/
│   ├── prompt_injection.py    ← The 4 attack payloads
│   ├── run_attack.py          ← Script to run attacks (no protection)
│   └── verify_defense.py      ← Script to run attacks (with protection)
│
├── attack_results/
│   ├── before_mitigation.json ← EVIDENCE: /etc/passwd successfully leaked
│   └── after_mitigation.json  ← EVIDENCE: All 6 dangerous ops blocked
│
└── report/
    ├── project4_report.md     ← Full CYBR 500 conference-style paper
    └── appendix_ai_learning.md← AI-Assisted Learning log
```

---

## Key Security Results

| Attack Vector | Before Mitigation | After Mitigation |
|---|---|---|
| Environment variable exfiltration | ⚠️ Attempted | 🛑 **BLOCKED** |
| `/etc/passwd` read via social engineering | 🔓 **LEAKED** | 🛑 **BLOCKED** |
| `/etc/shadow` read | 🔓 **Attempted** | 🛑 **BLOCKED** |
| `~/.ssh/id_rsa` (SSH private key) read | 🔓 **Attempted** | 🛑 **BLOCKED** |
| `.env` file (API keys) read | 🔓 **Attempted** | 🛑 **BLOCKED** |
| Chained cross-agent attack | ⚠️ Attempted | 🛑 **BLOCKED** |

**Result: The Security Interceptor blocked 100% of HIGH and CRITICAL risk operations.**

---

## How the System Works (Non-Technical Overview)

```
You type a question
        │
        ▼
🎯 COORDINATOR  →  Reads your question and makes a plan
        │
   ┌────┴────┐
   ▼         ▼
🔍 SEARCH-A  🔎 SEARCH-B  →  Two agents research the topic in parallel
        │
        ▼
✅ VERIFICATION  →  Checks facts and removes unreliable sources
        │
        ▼
📊 RANKING  →  Ranks the findings by quality and relevance
        │
        ▼
📝 SYNTHESIS  →  Writes a structured research report
        │
        ▼
  Your answer appears in the chat window

💾 DATA AGENT  →  Handles file reading/writing (the attack surface)
   + 🛡️ SECURITY INTERCEPTOR  →  Guards every file operation
```

---

## Technologies Used

| Technology | Purpose |
|---|---|
| **Google Gemini API** | The AI "brain" powering all 7 agents |
| **OpenClaw / CMDOP SDK** | Agent orchestration and tool execution framework |
| **Chainlit** | The visual web interface (dashboard) |
| **Python 3.12** | Core programming language |
| **Pydantic** | Structured, type-safe data between agents |

---

## Read the Full Report

The complete CYBR 500 conference-style paper is at:  
📄 [`report/project4_report.md`](report/project4_report.md)
