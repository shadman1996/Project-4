# CYBR 500 Project 4: Video Presentation Script

**Title:** Security Analysis of AI Agent Ecosystems
**Presenter:** Shadman (with contributions from Samson)
**Target Duration:** ~5 Minutes

---

## Segment 1: Introduction & Threat Model (0:00 - 1:00)

**[Visual: Screen recording showing the app's main page / Tutorial Intro]**

**Shadman:** "Hello, my name is Shadman, and this is our final presentation for CYBR 500 Project 4. For this project, we built a fully functional 7-agent AI research pipeline using the OpenClaw architecture, integrated with Google Gemini. 

Our goal was to explore the vulnerabilities of multi-agent systems. When AI agents can execute code, search the web, and pass data to each other autonomously, how easily can they be exploited?

To answer this, we developed a threat model based on MITRE ATLAS and STRIDE, focusing on Prompt Injection. In total, we engineered **8 different attack payloads**, including advanced evasion techniques like Base64 encoding, multi-turn sleeper instructions, and social engineering designed to exploit Human-in-the-Loop alert fatigue."

## Segment 2: The Vulnerable Demo (1:00 - 2:30)

**[Visual: Click 'Run Vulnerable System Demo'. Scroll through the attacks as they execute.]**

**Shadman:** "Let's look at the Vulnerable Demo. Here, the system is unguarded. The agents process input blindly.

As you can see, when we run our attacks, the system fails catastrophically.
- **Attack 1 & 2** easily leak environment variables and system files like `/etc/passwd`.
- **Attack 5** demonstrates RAG poisoning: the malicious instruction isn't even typed by the user; it's hidden inside a retrieved document.
- **Attack 6** uses Base64 encoding. Because standard regex scanners only look for plaintext secrets, the agent freely exfiltrates the API key encoded in Base64.
- **Attack 7** plants a sleeper instruction that remains dormant in the agent's context window until triggered by an innocent prompt later.

The final scorecard for the unguarded system is 0 blocks. All 8 attacks succeed."

## Segment 3: The Secured Demo & Defense in Depth (2:30 - 4:15)

**[Visual: Click 'Run Secured System Demo'. The UI shows the Security Interceptor stopping attacks. Show the HITL approval gates.]**

**Shadman:** "Now, let's run the Secured Demo. To defend against these sophisticated attacks, we implemented a defense-in-depth approach centered around a **Tool-Level Security Interceptor**.

Rather than trying to perfectly sanitize the LLM's input—which is nearly impossible against adaptive attacks—we intercept the actual tool execution. 
When an agent attempts to read a file or access an environment variable, the interceptor steps in.

- Notice the **Human-in-the-Loop (HITL) gate**. For high-risk operations, the system explicitly asks the operator to Allow or Deny the action, breaking the chain of autonomous exploitation.
- Against **Attack 6 (Base64 Evasion)**, our interceptor now uses **Shannon Entropy analysis**. It detects the high randomness typical of encoded strings and obfuscated secrets, blocking the exfiltration even if regex fails.
- Against **Attack 8 (HITL Skip Exploitation)**, we implemented strict state management to prevent alert fatigue. The security gates cannot be bypassed by injecting a 'skip' command into the agent.
- We also added rate limiting to prevent automated rapid-fire exfiltration attempts.

As we reach the end of the secured demo, you can see the scorecard: 8 out of 8 attacks were successfully blocked."

## Segment 4: Conclusion (4:15 - 5:00)

**[Visual: Show the exported `security_audit_log.json` on screen briefly or the GitHub repository link]**

**Shadman:** "In conclusion, this project demonstrates that while autonomous AI agents are highly vulnerable to prompt injection and context poisoning, robust security is possible. 

By enforcing strict access controls at the tool-execution layer, applying entropy-based leak detection, and keeping humans in the loop for critical actions, we can securely deploy multi-agent systems. 

All of our code, the full security audit logs mapped to MITRE ATLAS, and our comprehensive research report are available in our GitHub repository. 

Thank you for watching."
