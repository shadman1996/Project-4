# Software Requirements Specification (SRS) & Work Breakdown Structure

**Project:** Multi-Agent AI Security Research System (CYBR 500 - Project 4)  
**Author:** Shadman Ahsan  
**Date:** April 2026  

---

## 1. Software Requirements Specification (SRS)

### 1.1 Purpose
The purpose of this system is to demonstrate the systemic vulnerabilities of LLM-based autonomous agent pipelines to prompt injection attacks, and to evaluate the effectiveness of a Human-in-the-Loop (HITL) mitigation strategy. 

### 1.2 Scope
The project encompasses a full-stack AI web application featuring a 7-agent academic research pipeline. The application provides two interactive demonstrations: an unguarded "Vulnerable Demo" that leaks sensitive system data, and a "Secured Demo" that intercepts and blocks unauthorized actions.

### 1.3 Functional Requirements
* **FR-1:** The system shall implement a 7-stage agent pipeline (Coordinator, Search-A, Search-B, Verifier, Ranker, Synthesis, Data).
* **FR-2:** The system shall provide an interactive Chat UI using Chainlit for real-time observation of agent tasks.
* **FR-3:** The system shall include a "Vulnerable System Demo" that automatically executes four sophisticated prompt injection attacks, demonstrating unauthorized file reads and environment variable leaks.
* **FR-4:** The system shall include a "Secured System Demo" utilizing a Python-based HITL security interceptor.
* **FR-5:** The security interceptor shall pause execution and prompt the user (Approve/Deny) when sensitive resources (e.g., `/etc/passwd`, `.env`) are accessed.
* **FR-6:** The UI shall feature an interactive, draggable tutorial overlay for onboarding new users.

### 1.4 Non-Functional Requirements
* **NFR-1 (Usability):** The web interface must be 100% mobile-responsive across all viewports.
* **NFR-2 (Deployment):** The application must be containerized and successfully deployed to a cloud platform (Railway) for grading.
* **NFR-3 (Aesthetics):** The UI shall implement a premium dark theme with custom glassmorphism components.

---

## 2. Work Breakdown Structure (WBS) & Hours Log

The development of this project utilized a hybrid approach of manual software engineering and AI-assisted pair programming. 

| Phase | Task Description | Manual Coding (Shadman) | AI-Assisted Coding | Total Hours |
| :--- | :--- | :---: | :---: | :---: |
| **Phase 1** | **Architecture & Threat Modeling** <br> Defining the 7-agent pipeline, selecting prompt injection vectors, and designing the HITL interceptor logic. | 4.0 hrs | 1.5 hrs | 5.5 hrs |
| **Phase 2** | **Core Backend Development** <br> Writing Python logic for OpenClaw agents, Gemini API integration, and standardizing JSON schemas. | 3.5 hrs | 5.5 hrs | 9.0 hrs |
| **Phase 3** | **Security Interceptor & Payloads** <br> Crafting the 4 specific attack payloads and developing the security middleware to intercept file/env access. | 5.0 hrs | 3.0 hrs | 8.0 hrs |
| **Phase 4** | **Chainlit UI & Custom Theming** <br> Integrating Chainlit, developing the premium Dark Mode CSS tokens, and rendering the pipeline visualizations. | 2.5 hrs | 6.5 hrs | 9.0 hrs |
| **Phase 5** | **Interactive Tutorial Engine** <br> Building the custom JS tutorial overlay, draggable components, and resolving mobile responsiveness limits. | 1.5 hrs | 5.0 hrs | 6.5 hrs |
| **Phase 6** | **Deployment & Testing** <br> Configuring Railway deployment, testing edge cases, resolving scrollbar UI bugs, and testing payloads. | 3.0 hrs | 2.5 hrs | 5.5 hrs |
| **Phase 7** | **CYBR 500 Documentation** <br> Writing the final 15-section academic report, capturing screenshots, and formatting grading deliverables. | 6.5 hrs | 2.0 hrs | 8.5 hrs |
| | **TOTAL PROJECT HOURS** | **26.0 hrs** | **26.0 hrs** | **52.0 hrs** |

> *Note on AI Collaboration: AI-assisted coding was primarily utilized for rapid prototyping of CSS/JS UI components, accelerating boilerplate generation, and debugging complex DOM manipulation for the interactive tutorial. All architectural security decisions, threat modeling, and academic report writing were manually directed and verified by Shadman Ahsan.*
