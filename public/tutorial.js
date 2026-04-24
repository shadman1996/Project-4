/**
 * Project 4 — Top Navigation Bar & Interactive Tutorial v4
 * Features: Top Navbar, click-driven walkthrough, HITL preview, pipeline preview.
 */

// ── 1. Inject Top Navigation Bar ──────────────────────────────────────────────
(function () {
  "use strict";
  if (document.getElementById("p4-navbar")) return; // Already injected

  const style = document.createElement("style");
  style.textContent = `
    #p4-navbar {
      position: fixed; top: 0; left: 0; right: 0; min-height: 50px;
      background: rgba(9, 16, 36, 0.85); backdrop-filter: blur(8px);
      border-bottom: 1px solid rgba(99, 102, 241, 0.3);
      z-index: 99999; display: flex; align-items: center; justify-content: center;
      gap: clamp(0.2rem, 1vw, 1rem); font-family: 'Inter', sans-serif;
      box-shadow: 0 4px 20px rgba(0, 0, 0, 0.4);
      padding: clamp(0.2rem, 1vw, 0.5rem); flex-wrap: wrap;
      pointer-events: auto !important;
    }
    .p4-nav-btn {
      background: transparent; color: #cbd5e1; border: none;
      padding: clamp(0.3rem, 1vw, 0.8rem); 
      font-size: clamp(0.65rem, 1.8vw, 0.85rem); font-weight: 600;
      border-radius: 6px; cursor: pointer; transition: all 0.2s;
    }
    @media (max-width: 650px) {
      #p4-navbar { justify-content: space-evenly; }
      .p4-nav-btn { flex: 1 1 auto; text-align: center; justify-content: center; display: flex; }
    }
    .p4-nav-btn:hover { background: rgba(99, 102, 241, 0.15); color: #fff; }
    .p4-nav-btn.red:hover { background: rgba(239, 68, 68, 0.15); color: #fca5a5; }
    .p4-nav-btn.green:hover { background: rgba(16, 185, 129, 0.15); color: #6ee7b7; }
    
    /* Push chainlit body down slightly so navbar doesn't cover header */
    #root { padding-top: 50px !important; height: 100vh !important; box-sizing: border-box !important; }

    /* Hide specific native buttons to avoid duplicates, but keep header for navigation */
    .cl-header button[id="new-chat-button"],
    .cl-header button[id="readme-button"],
    .cl-header button[id="theme-toggle"] { display: none !important; }

    /* Dynamic Theme Toggle Icons */
    .sun-icon { display: none; }
    .moon-icon { display: inline; }
    [data-theme="light"] .moon-icon, .light .moon-icon { display: none !important; }
    [data-theme="light"] .sun-icon, .light .sun-icon { display: inline !important; }

    /* Make Chainlit header sleek and compact */
    .cl-header { height: 40px !important; min-height: 40px !important; border-bottom: none !important; }

    /* Light Mode Overrides for Navbar */
    [data-theme="light"] #p4-navbar, .light #p4-navbar {
      background: rgba(255, 255, 255, 0.85);
      border-bottom: 1px solid rgba(99, 102, 241, 0.2);
    }
    [data-theme="light"] .p4-nav-btn, .light .p4-nav-btn {
      color: #475569;
    }
    [data-theme="light"] .p4-nav-btn:hover, .light .p4-nav-btn:hover {
      color: #0f172a;
      background: rgba(99, 102, 241, 0.1);
    }
  `;
  document.head.appendChild(style);

  const nav = document.createElement("div");
  nav.id = "p4-navbar";
  nav.innerHTML = `
    <img id="p4-nav-logo" src="/public/logo_secured.png" style="height: 34px; border-radius: 6px; margin-left: 0.2rem; margin-right: auto; object-fit: contain; box-shadow: 0 0 12px rgba(16, 185, 129, 0.4); transition: all 0.4s ease;" alt="System Logo">
    <button class="p4-nav-btn red" data-cmd="red team" title="Run 4 live prompt injection attacks against an unguarded AI system to see data get leaked">🔴 Vulnerable Demo</button>
    <button class="p4-nav-btn green" data-cmd="defence demo" title="Run the same 4 attacks against the system protected by a Human-in-the-Loop Security Interceptor">🛡️ Secured Demo</button>
    <button class="p4-nav-btn" onclick="window.location.reload()" title="Clear chat history and start over">💬 New Chat</button>
    <button class="p4-nav-btn" id="p4-tut-btn" onclick="if(window.startP4Tutorial) window.startP4Tutorial()" title="Restart the Interactive Tutorial">🎓 Tutorial</button>
    <button class="p4-nav-btn" id="p4-readme-btn" title="View Instructions">📖 Readme</button>
    <button class="p4-nav-btn" id="p4-theme-btn" onclick="document.getElementById('theme-toggle')?.click()" title="Toggle Light/Dark Theme">
      <span class="moon-icon">🌙 Dark</span><span class="sun-icon">☀️ Light</span>
    </button>
    <button class="p4-nav-btn" onclick="window.open('https://github.com/shadman1996/Project-4', '_blank')" title="View source code and official CYBR 500 reports on GitHub">🔗 GitHub Repo</button>
  `;
  document.body.appendChild(nav);

  // Auto-fade the initial Readme screen (the intro screen)
  let hasAutoFaded = false;
  const introFadeInterval = setInterval(() => {
    if (hasAutoFaded) {
      clearInterval(introFadeInterval);
      return;
    }
    const dialog = document.querySelector('[role="dialog"], .MuiDialog-root');
    const closeBtn = document.querySelector('[role="dialog"] button[aria-label="Close"], .MuiDialog-root button:first-of-type');
    
    // Only fade if the dialog exists and we haven't clicked a navbar button manually
    if (dialog && closeBtn) {
      hasAutoFaded = true; 
      setTimeout(() => {
        dialog.style.transition = "opacity 1.5s ease-out";
        dialog.style.opacity = "0";
        setTimeout(() => {
          closeBtn.click();
          dialog.style.opacity = "1"; // Reset for future manual opens
        }, 1500);
      }, 5000); // Wait 5 seconds before fading
    }
  }, 500);

  nav.addEventListener("click", () => { hasAutoFaded = true; }, { once: true });

  // Capture phase listener to bypass Radix UI modal click traps
  window.addEventListener("click", (e) => {
    const rBtn = e.target.closest("#p4-readme-btn");
    if (rBtn) {
      if (rBtn.innerHTML.includes("Back")) {
        // Forcefully close modal natively, or refresh
        e.stopPropagation();
        e.preventDefault();
        const nativeClose = document.querySelector('[role="dialog"] button[aria-label="Close"], .MuiDialog-root button:first-of-type');
        if (nativeClose) {
          nativeClose.click();
        } else {
          window.location.href = '/';
        }
      } else {
        document.getElementById('readme-button')?.click();
      }
    }
  }, true);

  setInterval(() => {
    // Chainlit uses a Radix UI Dialog or MUI Dialog for the Readme modal
    const isReadme = window.location.pathname.includes('/readme') || document.querySelector('[role="dialog"]') !== null || document.querySelector('.MuiDialog-root') !== null;
    
    const rBtn = document.getElementById("p4-readme-btn");
    const tBtn = document.getElementById("p4-tut-btn");
    const c = document.getElementById("p4c");
    const spt = document.getElementById("p4spt");
    const arr = document.getElementById("p4arr");
    
    if (rBtn) {
      if (isReadme) {
        rBtn.innerHTML = "🔙 Back to Chat";
        rBtn.style.background = "rgba(99, 102, 241, 0.2)";
        if (tBtn) { tBtn.style.opacity = "0.3"; tBtn.style.pointerEvents = "none"; }
        if (c) c.style.display = "none";
        if (spt) spt.style.display = "none";
        if (arr) arr.style.display = "none";
      } else {
        rBtn.innerHTML = "📖 Readme";
        rBtn.style.background = "";
        if (tBtn) { tBtn.style.opacity = "1"; tBtn.style.pointerEvents = "auto"; }
        if (c) c.style.display = "block";
        if (spt) spt.style.display = "block";
        if (arr) arr.style.display = "block";
      }
    }
  }, 200);

  // Send command to Chainlit via hidden input
  nav.addEventListener("click", (e) => {
    if (e.target.tagName !== "BUTTON") return;
    const cmd = e.target.getAttribute("data-cmd");
    if (!cmd) return;

    // Update Logo based on selected system
    const logo = document.getElementById("p4-nav-logo");
    if (logo) {
      if (cmd === "red team") {
        logo.src = "/public/logo_vulnerable.png";
        logo.style.boxShadow = "0 0 15px rgba(239, 68, 68, 0.6)";
      } else if (cmd === "defence demo") {
        logo.src = "/public/logo_secured.png";
        logo.style.boxShadow = "0 0 15px rgba(16, 185, 129, 0.6)";
      }
    }

    // Helper to send message natively in React
    const ta = document.querySelector("textarea");
    if (ta) {
      const nativeInputValueSetter = Object.getOwnPropertyDescriptor(window.HTMLTextAreaElement.prototype, "value").set;
      nativeInputValueSetter.call(ta, cmd);
      ta.dispatchEvent(new Event('input', { bubbles: true }));
      setTimeout(() => {
        const sendBtn = document.querySelector("#ask-button, button[id*='submit']");
        if (sendBtn) sendBtn.click();
      }, 50);
    }
  });

})();

// ── 2. Interactive Tutorial ───────────────────────────────────────────────────
(function () {
  "use strict";

  const KEY = "p4_tut_v5";

  // ── Inject CSS ──────────────────────────────────────────────────────────────
  const style = document.createElement("style");
  style.textContent = `
  #p4b{position:fixed;inset:0;z-index:9988;background:transparent;pointer-events:none;animation:p4fi .4s ease both}
  #p4spt{position:fixed;z-index:9989;border-radius:8px;box-shadow:0 0 0 9999px rgba(5,10,22,.65);transition:all .4s ease;pointer-events:none}
  @keyframes p4fi{from{opacity:0}to{opacity:1}}
  #p4c{position:fixed;z-index:9999;background:rgba(9,16,36,.93);border:1px solid rgba(99,102,241,.5);border-radius:20px;padding:clamp(1rem,3vw,1.5rem) clamp(1.2rem,3.5vw,1.7rem) clamp(0.9rem,2.5vw,1.3rem);max-width:370px;width:91vw;box-shadow:0 0 80px rgba(99,102,241,.18),0 20px 60px rgba(0,0,0,.7),inset 0 1px 0 rgba(255,255,255,.06);font-family:'Inter',system-ui,sans-serif;color:#e2e8f0;transition:top .42s cubic-bezier(.4,0,.2,1),left .42s cubic-bezier(.4,0,.2,1),bottom .42s cubic-bezier(.4,0,.2,1)}
  #p4badge{display:inline-block;background:linear-gradient(90deg,#6366f1,#00d4ff);color:#fff;font-size:clamp(0.55rem,1.2vw,0.63rem);font-weight:700;letter-spacing:.07em;text-transform:uppercase;padding:.18em .72em;border-radius:99px;margin-bottom:.65rem}
  #p4ttl{font-size:clamp(0.85rem,2vw,1rem);font-weight:700;color:#f8fafc;line-height:1.3;margin-bottom:.45rem}
  #p4bdy{font-size:clamp(0.75rem,1.8vw,0.84rem);line-height:1.65;color:#94a3b8;margin-bottom:.9rem}
  #p4bdy strong{color:#e2e8f0}#p4bdy em{color:#7dd3fc;font-style:normal}
  #p4bdy code{background:rgba(0,212,255,.12);color:#00d4ff;padding:1px 5px;border-radius:4px;font-family:'JetBrains Mono',monospace;font-size:.77rem}
  #p4pt{height:3px;background:rgba(255,255,255,.07);border-radius:99px;margin-bottom:.85rem;overflow:hidden}
  #p4pf{height:100%;background:linear-gradient(90deg,#6366f1,#00d4ff);border-radius:99px;transition:width .4s cubic-bezier(.4,0,.2,1)}
  #p4hint{display:none;background:rgba(239,68,68,.11);border:1px solid rgba(239,68,68,.3);border-radius:9px;padding:.55rem .85rem;font-size:.79rem;font-weight:600;color:#fca5a5;text-align:center;margin-bottom:.85rem;animation:p4ph 1.8s ease-in-out infinite}
  #p4hint.blue{background:rgba(99,102,241,.11);border-color:rgba(99,102,241,.3);color:#a5b4fc;animation:p4pb 1.8s ease-in-out infinite}
  @keyframes p4ph{0%,100%{box-shadow:0 0 0 0 rgba(239,68,68,.2)}50%{box-shadow:0 0 0 6px rgba(239,68,68,0)}}
  @keyframes p4pb{0%,100%{box-shadow:0 0 0 0 rgba(99,102,241,.2)}50%{box-shadow:0 0 0 6px rgba(99,102,241,0)}}
  #p4btns{display:flex;gap:.5rem;align-items:center}
  .p4btn{flex:1;padding:.52rem .9rem;border:none;border-radius:10px;font-family:'Inter',sans-serif;font-weight:600;font-size:.81rem;cursor:pointer;transition:transform .15s,box-shadow .15s,opacity .2s}
  .p4btn:hover:not(:disabled){transform:translateY(-2px)}.p4btn:disabled{opacity:.35;cursor:default}
  #p4prev{flex:0 0 auto;padding:.52rem .7rem;background:rgba(255,255,255,.05);color:#64748b;border:1px solid rgba(255,255,255,.08)!important}
  #p4next{background:linear-gradient(135deg,#4f46e5,#6366f1);color:#fff;box-shadow:0 0 16px rgba(99,102,241,.4)}
  #p4next:hover:not(:disabled){box-shadow:0 0 30px rgba(99,102,241,.65)}
  #p4skip{flex:0 0 auto;padding:.52rem .7rem;background:transparent;color:#475569;font-size:.74rem;border:none!important}
  #p4skip:hover{color:#94a3b8}
  #p4cur{position:fixed;z-index:9993;pointer-events:none;width:38px;height:38px;border:2.5px solid #00d4ff;border-radius:50%;background:rgba(0,212,255,.1);box-shadow:0 0 26px rgba(0,212,255,.5);transition:top .5s cubic-bezier(.4,0,.2,1),left .5s cubic-bezier(.4,0,.2,1),opacity .3s;transform:translate(-50%,-50%)}
  #p4cur::after{content:'';position:absolute;inset:6px;background:rgba(0,212,255,.5);border-radius:50%;animation:p4ping 1.4s ease-in-out infinite}
  @keyframes p4ping{0%,100%{transform:scale(.5);opacity:.9}50%{transform:scale(1.3);opacity:.2}}
  #p4spt{position:fixed;z-index:9989;border:2px solid rgba(99,102,241,.7);border-radius:13px;box-shadow:0 0 0 4000px rgba(5,10,22,.48),0 0 45px rgba(99,102,241,.38);pointer-events:none;transition:top .4s cubic-bezier(.4,0,.2,1),left .4s cubic-bezier(.4,0,.2,1),width .4s cubic-bezier(.4,0,.2,1),height .4s cubic-bezier(.4,0,.2,1),opacity .3s}
  #p4spt.red{border-color:rgba(239,68,68,.8);box-shadow:0 0 0 4000px rgba(5,10,22,.48),0 0 45px rgba(239,68,68,.45)}
  #p4arr{position:fixed;z-index:9994;pointer-events:none;transition:top .4s cubic-bezier(.4,0,.2,1),left .4s cubic-bezier(.4,0,.2,1),opacity .3s;animation:p4bnc .85s ease-in-out infinite alternate;font-size:2rem;filter:drop-shadow(0 4px 6px rgba(0,0,0,0.5))}
  @keyframes p4bnc{from{transform:translateY(-5px)}to{transform:translateY(5px)}}

  /* Light Mode Overrides for Tutorial Box */
  [data-theme="light"] #p4c, .light #p4c {
    background: rgba(255, 255, 255, 0.98);
    border-color: rgba(99, 102, 241, 0.3);
    color: #1e293b;
    box-shadow: 0 10px 40px rgba(0, 0, 0, 0.15);
  }
  [data-theme="light"] #p4ttl, .light #p4ttl { color: #0f172a; }
  [data-theme="light"] #p4bdy, .light #p4bdy { color: #475569; }
  [data-theme="light"] #p4bdy strong, .light #p4bdy strong { color: #0f172a; }
  [data-theme="light"] .p4term, .light .p4term { background: #f8fafc; border-color: rgba(239, 68, 68, 0.3); box-shadow: 0 4px 12px rgba(239, 68, 68, 0.08); }
  [data-theme="light"] .p4tbody, .light .p4tbody { color: #059669; }
  [data-theme="light"] .p4hrow span, .light .p4hrow span { color: #1e293b; }
  /* Terminal widget */
  .p4term{background:#080808;border:1px solid rgba(239,68,68,.4);border-radius:10px;overflow:hidden;margin:.7rem 0 .85rem;box-shadow:0 0 18px rgba(239,68,68,.15),inset 0 1px 0 rgba(255,255,255,.03)}
  .p4tbar{background:rgba(239,68,68,.13);border-bottom:1px solid rgba(239,68,68,.22);padding:.3rem .65rem;display:flex;align-items:center;gap:.35rem}
  .p4tdot{width:9px;height:9px;border-radius:50%}
  .p4tlbl{font-family:'JetBrains Mono',monospace;font-size:.62rem;color:rgba(239,68,68,.75);margin-left:auto}
  .p4tbody{padding:.65rem .85rem;font-family:'JetBrains Mono','Fira Code',monospace;font-size:.73rem;line-height:1.75;color:#4ade80}
  .p4tp{color:#f87171}.p4tc{color:#86efac}.p4tcmt{color:#475569}
  .p4tblink{display:inline-block;width:6px;height:12px;background:#4ade80;vertical-align:middle;animation:p4bl 1s step-end infinite}
  @keyframes p4bl{0%,100%{opacity:1}50%{opacity:0}}
  .p4copy{display:block;width:100%;background:rgba(239,68,68,.13);border:none;border-top:1px solid rgba(239,68,68,.22);color:#fca5a5;font-family:'Inter',sans-serif;font-size:.71rem;font-weight:600;padding:.38rem;cursor:pointer;transition:background .15s;letter-spacing:.04em}
  .p4copy:hover{background:rgba(239,68,68,.24)}
  /* Agent pipeline preview */
  .p4pipe{display:flex;flex-direction:column;gap:.28rem;margin:.7rem 0 .85rem}
  .p4pa{display:flex;align-items:center;gap:.55rem;padding:.35rem .6rem;border-radius:8px;font-size:.73rem;font-weight:600;border-left:3px solid;animation:p4sl .3s ease both}
  @keyframes p4sl{from{opacity:0;transform:translateX(-8px)}to{opacity:1;transform:translateX(0)}}
  .p4pa .p4picon{font-size:.85rem;flex-shrink:0}
  .p4pa .p4pname{flex:1}
  .p4pa .p4parrow{color:rgba(255,255,255,.2);font-size:.65rem}
  .p4pa .p4pstatus{font-size:.67rem;font-weight:700;padding:.1em .4em;border-radius:4px;letter-spacing:.05em}
  /* HITL preview */
  .p4hitl{background:rgba(239,68,68,.07);border:1px solid rgba(239,68,68,.25);border-radius:10px;padding:.7rem .85rem;margin:.7rem 0 .85rem;font-size:.77rem}
  .p4halt{color:#fca5a5;font-weight:700;margin-bottom:.4rem;font-size:.8rem}
  .p4hrow{color:#94a3b8;margin-bottom:.22rem}
  .p4hrow span{color:#e2e8f0}
  .p4hbtns{display:flex;gap:.4rem;margin-top:.55rem}
  .p4hap{flex:1;background:rgba(16,185,129,.18);border:1px solid rgba(16,185,129,.4);color:#6ee7b7;border-radius:7px;padding:.28rem .4rem;font-size:.71rem;font-weight:600;cursor:default;text-align:center}
  .p4hdn{flex:1;background:rgba(239,68,68,.18);border:1px solid rgba(239,68,68,.4);color:#fca5a5;border-radius:7px;padding:.28rem .4rem;font-size:.71rem;font-weight:600;cursor:default;text-align:center}
  `;
  document.head.appendChild(style);

  // ── Step definitions ────────────────────────────────────────────────────────
  const STEPS = [
    {
      badge: "Welcome",
      title: "👋 Welcome to Project 4",
      body: `A <strong>Graduate-Level Academic Research Pipeline</strong> and live AI security demo built for CYBR 500.<br><br>
You'll see a <strong>7-agent AI pipeline</strong> get attacked by prompt injection — then a security interceptor block every attack in real time.<br><br>
Use <strong>← →</strong> keys or buttons to navigate. Let's go!`,
      target: null, waitForClick: false,
    },
    {
      badge: "Step 1 of 6",
      title: "🔴 The Vulnerable System Demo",
      body: `This button runs <strong>4 live prompt injection attacks</strong> against this unguarded AI system.<br><br>
The agents will leak <code>/etc/passwd</code>, <code>.env</code> secrets, and SSH keys — with <strong>zero authentication</strong>.<br><br>
<strong>👇 Click the Vulnerable Demo button now — the tutorial continues automatically.</strong>`,
      target: "#p4-navbar .p4-nav-btn.red",
      targetIndex: 0,
      waitForClick: true,
      spotlightClass: "red",
      arrowClass: "ard",
      clickHint: "👆 Click the Vulnerable Demo button above — tour continues automatically",
      clickHintStyle: "red",
    },
    {
      badge: "Step 2 of 6",
      title: "⚡ The Agent Pipeline — Live",
      body: `Watch the <strong>attack messages</strong> appearing in the chat.<br><br>
Each block shows exactly: what was injected → what the agent did → what got leaked.<br><br>
The agents pass results to each other in real time:`,
      target: null, waitForClick: false,
      extra: "pipeline",
    },
    {
      badge: "Step 3 of 6",
      title: "🛡️ The Defence Demo",
      body: `You can also run the <strong>Secured System</strong> using the 🛡️ button on the top navigation bar.<br><br>
This version has a Human-in-the-Loop security gate protecting it.<br><br>
<strong>👇 Click the green Secured Demo button now.</strong>`,
      target: "#p4-navbar .p4-nav-btn.green",
      targetIndex: 0,
      waitForClick: true,
      arrowClass: "au",
      clickHint: "👆 Click the Secured Demo button to continue",
      clickHintStyle: "blue",
    },
    {
      badge: "Step 4 of 6",
      title: "🚨 The HITL Security Gate",
      body: `When the interceptor is active, every dangerous agent action triggers a <strong>Security Alert</strong> in the chat. You decide: allow or block.`,
      target: null, waitForClick: false,
      extra: "hitl",
    },
    {
      badge: "Step 5 of 5",
      title: "📄 Official Reports & Code",
      body: `Your professor can find the <strong>fully populated CYBR 500 Conference Report (.docx)</strong>, instructions, and all source code directly in the GitHub repository.<br><br>
Just click the <strong>🔗 GitHub Repo & Reports</strong> button on the navigation bar!`,
      target: "#p4-navbar button:nth-child(3)",
      targetIndex: 0,
      waitForClick: false,
      arrowClass: "au",
    }
  ];

  const total = STEPS.length;
  let cur = 0;
  let removeClickInterceptor = null;

  // ── Agent pipeline data ─────────────────────────────────────────────────────
  const AGENTS = [
    { icon:"🎯", name:"Coordinator",  color:"#6366f1", bg:"rgba(99,102,241,.12)",  status:"PLANNING",  delay:0   },
    { icon:"🔍", name:"Search-A",     color:"#f59e0b", bg:"rgba(245,158,11,.12)",  status:"SEARCHING", delay:150 },
    { icon:"🔎", name:"Search-B",     color:"#fb923c", bg:"rgba(251,146,60,.12)",  status:"SEARCHING", delay:300 },
    { icon:"✅", name:"Verifier",     color:"#10b981", bg:"rgba(16,185,129,.12)",  status:"VERIFYING", delay:450 },
    { icon:"📊", name:"Ranker",       color:"#a78bfa", bg:"rgba(167,139,250,.12)", status:"RANKING",   delay:600 },
    { icon:"📝", name:"Synthesizer",  color:"#f472b6", bg:"rgba(244,114,182,.12)", status:"WRITING",   delay:750 },
    { icon:"💾", name:"Data Agent",   color:"#22d3ee", bg:"rgba(34,211,238,.12)",  status:"SAVING",    delay:900 },
  ];

  // ── Build extra widgets ─────────────────────────────────────────────────────
  function buildPipeline() {
    return AGENTS.map((a, i) => `
      <div class="p4pa" style="border-left-color:${a.color};background:${a.bg};animation-delay:${a.delay}ms">
        <span class="p4picon">${a.icon}</span>
        <span class="p4pname" style="color:${a.color}">${a.name}</span>
        ${i < AGENTS.length-1 ? '<span class="p4parrow">→ passes to next ↓</span>' : ''}
        <span class="p4pstatus" style="background:${a.bg};color:${a.color}">${a.status}</span>
      </div>`).join('');
  }

  function buildTerminal(cmd) {
    return `
      <div class="p4term">
        <div class="p4tbar">
          <div class="p4tdot" style="background:#ef4444"></div>
          <div class="p4tdot" style="background:#f59e0b"></div>
          <div class="p4tdot" style="background:#10b981"></div>
          <span class="p4tlbl">RED TEAM PC — bash</span>
        </div>
        <div class="p4tbody">
          <div class="p4tcmt"># Stop current app first (Ctrl+C), then:</div>
          <div><span class="p4tp">shadman@cybr500:~$</span> <span class="p4tc">${cmd}</span></div>
          <div><span class="p4tp">shadman@cybr500:~$</span> <span class="p4tblink"></span></div>
        </div>
        <button class="p4copy" id="p4copyBtn">📋 Copy Command</button>
      </div>`;
  }

  function buildHITL() {
    return `
      <div class="p4hitl">
        <div class="p4halt">🛡️ Security Alert — 🔴 CRITICAL RISK</div>
        <div class="p4hrow">📁 Wants to access: <span>/etc/passwd</span></div>
        <div class="p4hrow">⚠️ Reason: <span>Sensitive system file — matches blocklist</span></div>
        <div class="p4hrow" style="margin-top:.3rem;color:#94a3b8;font-size:.73rem">Should the agent be allowed to do this?</div>
        <div class="p4hbtns">
          <div class="p4hap">✅ Approve</div>
          <div class="p4hdn">❌ Deny — Block</div>
        </div>
      </div>`;
  }

  // ── DOM helpers ─────────────────────────────────────────────────────────────
  function $id(id) { return document.getElementById(id); }

  function findTarget(step) {
    if (!step.target) return null;
    const els = document.querySelectorAll(step.target);
    return els[step.targetIndex || 0] || null;
  }

  let activePoll = null;

  function render(idx) {
    if (activePoll) { clearInterval(activePoll); activePoll = null; }
    const s = STEPS[idx];

    if (removeClickInterceptor) { removeClickInterceptor(); removeClickInterceptor = null; }

    const applyRender = () => {
      $id("p4badge").textContent = s.badge;
      $id("p4ttl").textContent = s.title;

      let bodyHTML = s.body;
      if (s.extra === "pipeline") bodyHTML += `<div class="p4pipe">${buildPipeline()}</div>`;
      if (s.extra === "terminal") bodyHTML += buildTerminal(s.termCmd || "");
      if (s.extra === "hitl")     bodyHTML += buildHITL();
      $id("p4bdy").innerHTML = bodyHTML;

      const copyBtn = $id("p4copyBtn");
      if (copyBtn && s.termCmd) {
        copyBtn.onclick = () => {
          navigator.clipboard.writeText(s.termCmd).catch(() => {});
          copyBtn.textContent = "✅ Copied!";
          setTimeout(() => { copyBtn.textContent = "📋 Copy Command"; }, 1800);
        };
      }

      $id("p4pf").style.width = `${Math.round(((idx + 1) / total) * 100)}%`;
      $id("p4next").textContent = idx === total - 1 ? "🚀 Launch Demo" : "Next →";
      $id("p4prev").disabled = idx === 0;

      const hint = $id("p4hint");
      if (s.clickHint) {
        hint.textContent = s.clickHint;
        hint.className = s.clickHintStyle === "red" ? "" : "blue";
        hint.style.display = "block";
        $id("p4next").disabled = true;
      } else {
        hint.style.display = "none";
        $id("p4next").disabled = false;
      }

      position(s);
      $id("p4c").style.opacity = "1";

      if (s.waitForClick) {
        const tgt = findTarget(s);
        if (tgt) {
          const handler = () => { 
            tgt.click();
            advance(); 
          };
          $id("p4int").onclick = handler;
        }
      }
    };

    if (s.target && !findTarget(s)) {
      $id("p4c").style.opacity = "0";
      $id("p4spt").style.opacity = "0";
      $id("p4cur").style.opacity = "0";
      $id("p4arr").style.opacity = "0";
      activePoll = setInterval(() => {
        if (findTarget(s)) {
          clearInterval(activePoll);
          activePoll = null;
          applyRender();
        }
      }, 100);
    } else {
      applyRender();
    }
  }

  function position(s) {
    const card = $id("p4c");
    const spt  = $id("p4spt");
    const cur  = $id("p4cur");
    const arr  = $id("p4arr");
    const vw = window.innerWidth, vh = window.innerHeight;
    const PAD = 16;

    const tgt = findTarget(s);

    // Spotlight class
    spt.className = s.spotlightClass === "red" ? "red" : "";
    arr.className = "";

    if (tgt) {
      const r = tgt.getBoundingClientRect();

      spt.style.cssText += `;opacity:1;top:${r.top-8}px;left:${r.left-8}px;width:${r.width+16}px;height:${r.height+16}px`;

      cur.style.cssText += `;opacity:1;left:${r.left+r.width/2}px;top:${r.top+r.height/2}px`;

      // Update Interceptor
      if (s.waitForClick) {
        $id("p4int").style.cssText = `position:fixed;z-index:99999;cursor:pointer;left:${r.left-8}px;top:${r.top-8}px;width:${r.width+16}px;height:${r.height+16}px;display:block`;
      } else {
        $id("p4int").style.display = "none";
      }

      // Card: below or above
      const spaceBelow = vh - r.bottom - PAD;
      const cardH = 300;
      const actualCardW = Math.min(370, vw * 0.91);
      let cardLeft = Math.max(PAD, Math.min(r.left + r.width/2 - actualCardW/2, vw - actualCardW - PAD));
      
      if (spaceBelow > cardH || spaceBelow >= r.top - PAD) {
        // Target is above card -> finger points UP to target
        arr.innerHTML = "👆";
        arr.style.cssText += `;opacity:1;top:${r.bottom+2}px;left:${r.left+r.width/2-16}px;transform:none`;
        card.style.cssText += `;top:${r.bottom+18}px;bottom:auto;left:${cardLeft}px;right:auto;transform:none`;
      } else {
        // Target is below card -> finger points DOWN to target
        arr.innerHTML = "👇";
        arr.style.cssText += `;opacity:1;top:${r.top-36}px;left:${r.left+r.width/2-16}px;transform:none`;
        card.style.cssText += `;bottom:${vh-r.top+18}px;top:auto;left:${cardLeft}px;right:auto;transform:none`;
      }

    } else {
      spt.style.opacity = "0";
      cur.style.opacity = "0";
      arr.style.opacity = "0";
      $id("p4int").style.display = "none";
      const actualCardW = Math.min(370, vw * 0.91);
      const rightPad = Math.max(16, vw * 0.03);
      card.style.cssText += `;top:80px;right:${rightPad}px;left:auto;bottom:auto;transform:none`;
    }
  }

  // ── Navigation ──────────────────────────────────────────────────────────────
  function advance() {
    if (removeClickInterceptor) { removeClickInterceptor(); removeClickInterceptor = null; }
    if (cur < total - 1) { cur++; render(cur); }
    else { destroy(); }
  }

  function back() {
    if (cur > 0) { cur--; render(cur); }
  }

  // ── Build DOM ───────────────────────────────────────────────────────────────
  function init() {
    const backdrop = Object.assign(document.createElement("div"), { id: "p4b" });

    const card = document.createElement("div");
    card.id = "p4c";
    card.innerHTML = `
      <div id="p4badge"></div>
      <div id="p4ttl"></div>
      <div id="p4bdy"></div>
      <div id="p4hint"></div>
      <div id="p4pt"><div id="p4pf" style="width:0%"></div></div>
      <div id="p4btns">
        <button class="p4btn" id="p4prev">← Back</button>
        <button class="p4btn" id="p4next">Next →</button>
        <button class="p4btn" id="p4skip">Skip</button>
      </div>`;

    const cursor = Object.assign(document.createElement("div"), { id: "p4cur" });
    const spotlight = Object.assign(document.createElement("div"), { id: "p4spt" });
    const arrow = Object.assign(document.createElement("div"), { id: "p4arr" });
    const interceptor = Object.assign(document.createElement("div"), { id: "p4int" });

    document.body.append(backdrop, spotlight, cursor, arrow, card, interceptor);

    $id("p4next").onclick = advance;
    $id("p4prev").onclick = back;
    $id("p4skip").onclick = destroy;

    document.addEventListener("keydown", onKey);
    window.addEventListener("resize", handleResize);
    document.body.addEventListener("click", agenticObserver);
    render(0);
    makeDraggable(card);
  }

  function agenticObserver(e) {
    if (!document.getElementById("p4c") || !e.isTrusted) return;
    let targetBtn = e.target.closest("button");
    if (!targetBtn) return;

    const ttl = document.getElementById("p4ttl");
    const bdy = document.getElementById("p4bdy");
    if (!ttl || !bdy) return;

    if (targetBtn.classList.contains("green")) {
      if (cur < 3) {
        cur = 4; // Jump straight to HITL demo
        render(cur);
        ttl.innerHTML = "🧠 Agentic Reaction!";
        bdy.innerHTML = "I see you skipped ahead and clicked the <strong>Secured Demo</strong>! Excellent choice.<br><br>Watch the chat: the security interceptor is about to catch the rogue agent in real time.";
      }
    } else if (targetBtn.classList.contains("red")) {
      if (cur > 2) {
        ttl.innerHTML = "🧠 Agentic Reaction!";
        bdy.innerHTML = "Running the <strong>Vulnerable Demo</strong> again! Notice how fast the OpenClaw agents execute when there are no security guards in place.";
      }
    } else if (targetBtn.innerText && targetBtn.innerText.includes("Readme")) {
        ttl.innerHTML = "🧠 Agentic Reaction!";
        bdy.innerHTML = "Ah, studying the documentation! Good call.<br><br>The Readme explains the full 7-agent OpenClaw architecture. Close it to continue.";
    } else if (targetBtn.innerText && targetBtn.innerText.includes("GitHub")) {
        ttl.innerHTML = "🧠 Agentic Reaction!";
        bdy.innerHTML = "Checking out the GitHub! The CYBR 500 reports and source code are fully populated there.";
    }
  }

  function makeDraggable(el) {
    let isDown = false, startX, startY, startLeft, startTop;
    el.style.cursor = "grab";
    
    el.addEventListener("mousedown", (e) => {
      if (e.target.tagName === "BUTTON") return;
      isDown = true;
      el.style.cursor = "grabbing";
      el.style.transition = "none";
      startX = e.clientX;
      startY = e.clientY;
      const rect = el.getBoundingClientRect();
      startLeft = rect.left;
      startTop = rect.top;
    });

    window.addEventListener("mousemove", (e) => {
      if (!isDown) return;
      e.preventDefault();
      const dx = e.clientX - startX;
      const dy = e.clientY - startY;
      el.style.left = startLeft + dx + "px";
      el.style.top = startTop + dy + "px";
      el.style.right = "auto";
      el.style.bottom = "auto";
      el.style.transform = "none";
    });

    window.addEventListener("mouseup", () => {
      isDown = false;
      el.style.cursor = "grab";
      el.style.transition = "top .42s cubic-bezier(.4,0,.2,1), left .42s cubic-bezier(.4,0,.2,1)";
    });
  }

  function handleResize() {
    if ($id("p4c")) position(STEPS[cur]);
  }

  function onKey(e) {
    if (e.key === "Escape")                        { destroy(); return; }
    if (e.key === "ArrowRight" || e.key === "Enter") advance();
    if (e.key === "ArrowLeft")                       back();
  }

  function destroy() {
    document.removeEventListener("keydown", onKey);
    window.removeEventListener("resize", handleResize);
    document.body.removeEventListener("click", agenticObserver);
    ["p4b","p4c","p4cur","p4spt","p4arr","p4int"].forEach(id => $id(id)?.remove());
  }

  window.startP4Tutorial = function() {
    destroy();
    cur = 0;
    init();
  };

  // ── Launch after Chainlit mounts ────────────────────────────────────────────
  let attempts = 0;
  const poll = setInterval(() => {
    attempts++;
    const ready = document.querySelector("textarea") ||
                  document.querySelector("[class*='message']") ||
                  attempts > 35;
    if (ready) { clearInterval(poll); setTimeout(init, 900); }
  }, 200);

  // ── Hack to hide "System" from the theme dropdown ───────────────────────────
  document.addEventListener("click", () => {
    setTimeout(() => {
      document.querySelectorAll("li[role='menuitem']").forEach(el => {
        if(el.textContent.trim() === "System") {
          el.style.display = "none";
        }
      });
    }, 50);
  });

})();
