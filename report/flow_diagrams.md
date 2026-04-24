# Project 4 — System Flow Diagrams

## 1. Normal Research Pipeline (7-Agent Flow)

```mermaid
flowchart TD
    U["👤 User\n(Chainlit UI)"]
    C["🎯 Coordinator\nReads query, builds plan"]
    SA["🔍 Search-A\nAcademic research"]
    SB["🔎 Search-B\nCVE / Technical research"]
    V["✅ Verification\nFact-check findings"]
    R["📊 Ranking\nScore by relevance + credibility"]
    SY["📝 Synthesis\nWrite final report"]
    D["💾 Data Agent\nFile I/O — attack surface"]
    OUT["📄 Final Research Report\n→ returned to user"]

    U -->|"research question"| C
    C -->|"task A"| SA
    C -->|"task B"| SB
    SA -->|SearchResult| V
    SB -->|SearchResult| V
    V -->|VerificationResult| R
    R -->|RankedResults| SY
    SY -->|SynthesisReport| OUT

    C -.->|"file ops"| D

    style C fill:#4f46e5,color:#fff,stroke:#6366f1
    style SA fill:#b45309,color:#fff,stroke:#f59e0b
    style SB fill:#c2410c,color:#fff,stroke:#fb923c
    style V fill:#047857,color:#fff,stroke:#10b981
    style R fill:#6d28d9,color:#fff,stroke:#a78bfa
    style SY fill:#9d174d,color:#fff,stroke:#f472b6
    style D fill:#0e7490,color:#fff,stroke:#22d3ee
    style OUT fill:#1e293b,color:#94a3b8,stroke:#334155
```

---

## 2. Attack Flow — Vulnerable System (`app.py`)

```mermaid
flowchart LR
    ATK["☠️ Attacker\nCrafts malicious prompt"]
    U["👤 User Input\n(appears legitimate)"]
    DA["💾 Data Agent\nNO guardrails"]
    FS["🗂️ Filesystem\n/etc/passwd\n.env\n~/.bashrc\n~/.ssh/id_rsa"]
    LEAK["🔓 Data LEAKED\nReturned to attacker\nvia chat response"]

    ATK -->|"inject payload"| U
    U -->|"forwarded as task"| DA
    DA -->|"os.open() — unrestricted"| FS
    FS -->|"file contents"| DA
    DA -->|"no filter applied"| LEAK

    style ATK fill:#7f1d1d,color:#fff,stroke:#dc2626
    style U fill:#1e293b,color:#94a3b8,stroke:#475569
    style DA fill:#0e7490,color:#fff,stroke:#22d3ee
    style FS fill:#292524,color:#fca5a5,stroke:#ef4444
    style LEAK fill:#450a0a,color:#fca5a5,stroke:#b91c1c
```

**Attacked in this demo:**
| Attack | Target | What Gets Leaked |
|--------|--------|-----------------|
| ENV_EXFIL | Search-A | API keys from `os.environ` |
| FILE_EXFIL | Search-A | `/etc/passwd` via fake admin directive |
| DATA_AGENT | Data Agent | `/etc/passwd`, `.env`, `~/.bashrc` |
| CHAINED | Search-A → Data | Cross-agent relay to dump secrets |

---

## 3. Defence Flow — Secured System (`app_secured.py`)

```mermaid
flowchart TD
    ATK["☠️ Attacker\nSame malicious prompt"]
    DA["💾 Data Agent\nreceives task"]
    SI["🛡️ Security Interceptor\ncheck_file_read(path)\ncheck_env_access()"]
    RISK{"Risk Level?"}
    LOW["🟢 LOW / MEDIUM\nLog and allow"]
    HIGH["🔴 HIGH / CRITICAL\nBlock — raise HITL gate"]
    HITL["👤 Human-in-the-Loop\n✅ Approve   ❌ Deny"]
    ALLOW["✅ Approved\nAgent executes"]
    BLOCK["🛑 Blocked\nAgent gets error\nNothing leaked"]
    SCAN["🔍 Output Scanner\ncheck_output(result)\nRedact leaks post-execution"]

    ATK -->|"injected prompt"| DA
    DA -->|"before any file op"| SI
    SI --> RISK
    RISK -->|"low / medium"| LOW
    RISK -->|"high / critical"| HIGH
    HIGH --> HITL
    HITL -->|"user clicks Approve"| ALLOW
    HITL -->|"user clicks Deny"| BLOCK
    LOW --> SCAN
    ALLOW --> SCAN

    style ATK fill:#7f1d1d,color:#fff,stroke:#dc2626
    style DA fill:#0e7490,color:#fff,stroke:#22d3ee
    style SI fill:#1e3a8a,color:#fff,stroke:#6366f1
    style RISK fill:#1e293b,color:#e2e8f0,stroke:#334155
    style HIGH fill:#7f1d1d,color:#fff,stroke:#dc2626
    style LOW fill:#064e3b,color:#fff,stroke:#10b981
    style HITL fill:#312e81,color:#fff,stroke:#818cf8
    style ALLOW fill:#064e3b,color:#fff,stroke:#10b981
    style BLOCK fill:#450a0a,color:#fca5a5,stroke:#dc2626
    style SCAN fill:#1e3a8a,color:#c7d2fe,stroke:#6366f1
```

---

## 4. End-to-End: Attack vs Defence Side-by-Side

```mermaid
flowchart LR
    subgraph BEFORE["❌ WITHOUT Security — app.py"]
        direction TB
        B1["Attacker injects prompt"] --> B2["Data Agent receives it"]
        B2 --> B3["os.open('/etc/passwd')"]
        B3 --> B4["🔓 File contents returned\nto attacker — no warning"]
    end

    subgraph AFTER["✅ WITH Security — app_secured.py"]
        direction TB
        A1["Same attacker prompt"] --> A2["Data Agent receives it"]
        A2 --> A3["🛡️ Interceptor checks path"]
        A3 --> A4["🔴 CRITICAL — blocked\nHITL gate shown"]
        A4 --> A5["User clicks ❌ Deny"]
        A5 --> A6["🛑 Error returned\nFilesystem never touched"]
    end

    style BEFORE fill:#1c0a0a,stroke:#dc2626,color:#fca5a5
    style AFTER fill:#0a1c0e,stroke:#10b981,color:#86efac
```

---

## 5. The 9-Model Fallback Chain

```mermaid
flowchart LR
    Q["LLM call\nrequested"]
    M1["gemini-3.1-flash-lite-preview\n⭐ Primary"]
    M2["gemini-2.5-flash-lite"]
    M3["gemini-3-flash-preview"]
    M4["gemma-4-31b-it"]
    M5["gemma-3-27b-it\n14,400 RPD"]
    M6["gemma-3-12b-it"]
    M7["gemma-3-4b-it"]
    M8["gemma-3-1b-it\n🆘 Last resort"]
    OK["✅ Response returned"]

    Q --> M1
    M1 -->|"429 / 503"| M2
    M2 -->|"quota"| M3
    M3 -->|"quota"| M4
    M4 -->|"quota"| M5
    M5 -->|"quota"| M6
    M6 -->|"quota"| M7
    M7 -->|"quota"| M8
    M1 -->|"success"| OK
    M2 -->|"success"| OK
    M3 -->|"success"| OK
    M4 -->|"success"| OK
    M5 -->|"success"| OK

    style M1 fill:#1e3a8a,color:#fff,stroke:#6366f1
    style OK fill:#064e3b,color:#fff,stroke:#10b981
    style M8 fill:#292524,color:#94a3b8,stroke:#57534e
```
