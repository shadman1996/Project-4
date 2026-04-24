/**
 * Project 4 — Top Navigation Bar
 * Injects a top navbar with hints (tooltips) for different views.
 */

(function () {
  "use strict";
  if (document.getElementById("p4-navbar")) return; // Already injected

  const style = document.createElement("style");
  style.textContent = `
    #p4-navbar {
      position: fixed; top: 0; left: 0; right: 0; height: 50px;
      background: rgba(9, 16, 36, 0.85); backdrop-filter: blur(8px);
      border-bottom: 1px solid rgba(99, 102, 241, 0.3);
      z-index: 9999; display: flex; align-items: center; justify-content: center;
      gap: 1rem; font-family: 'Inter', sans-serif;
      box-shadow: 0 4px 20px rgba(0, 0, 0, 0.4);
    }
    .p4-nav-btn {
      background: transparent; color: #cbd5e1; border: none;
      padding: 0.4rem 0.8rem; font-size: 0.85rem; font-weight: 600;
      border-radius: 6px; cursor: pointer; transition: all 0.2s;
    }
    .p4-nav-btn:hover { background: rgba(99, 102, 241, 0.15); color: #fff; }
    .p4-nav-btn.red:hover { background: rgba(239, 68, 68, 0.15); color: #fca5a5; }
    .p4-nav-btn.green:hover { background: rgba(16, 185, 129, 0.15); color: #6ee7b7; }
    
    /* Push chainlit body down slightly so navbar doesn't cover header */
    #root { padding-top: 50px !important; }
  `;
  document.head.appendChild(style);

  const nav = document.createElement("div");
  nav.id = "p4-navbar";
  nav.innerHTML = `
    <button class="p4-nav-btn red" data-cmd="red team" title="Run 4 live prompt injection attacks against an unguarded AI system to see data get leaked">🔴 Vulnerable Demo</button>
    <button class="p4-nav-btn green" data-cmd="defence demo" title="Run the same 4 attacks against the system protected by a Human-in-the-Loop Security Interceptor">🛡️ Secured Demo</button>
    <button class="p4-nav-btn" data-cmd="/show_report" title="Read the final CYBR 500 Conference Report covering the threat model and mitigation results">📄 Research Report</button>
  `;
  document.body.appendChild(nav);

  // Send command to Chainlit via hidden input
  nav.addEventListener("click", (e) => {
    if (e.target.tagName !== "BUTTON") return;
    const cmd = e.target.getAttribute("data-cmd");
    if (!cmd) return;

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


