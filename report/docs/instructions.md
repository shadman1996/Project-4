Total Possible Points: 20\
\
This project handout includes realistic sample application use cases and
a detailed multi-agent research-assistant example so that students can
move from zero experience to a graduate-level research report.

# Why This Project Matters

Autonomous AI agent systems are not just chatbots. They can coordinate
multiple steps, call tools, read and write files, retrieve data from
external resources, and make decisions with limited human intervention.
Because of this, they create both powerful opportunities and significant
security risks. In this project, you are not only learning how to use
OpenClaw---you are studying a class of systems that is likely to become
common in research, software engineering, cybersecurity operations, and
enterprise automation.

# Sample Application Use Cases for OpenClaw

**1.** **Research Assistant System**

A user enters a research topic. Multiple agents search papers, summarize
them, verify citation accuracy, rank the most relevant papers, draft a
paper outline, and optionally fetch dataset**s.**

**2. Security Log Investigation Assistant**

The first agent reads logs, the second agent detects anomalies, the
third describe possible attacks, the fourth verifies whether the
findings are consistent with threat intelligence, and another writes an
incident report.

**3. DevOps / System Administration Assistant**

Agents inspect system status, read configuration files, generate patches
or scripts, verify whether a change is safe, and document deployment
steps.

**4. Threat Intelligence Collection Assistant**

Agents gather reports from multiple online sources, compare claims, flag
contradictions, score source credibility, and produce a briefing
document.

**5. Compliance / Audit Assistant**

Agents collect system evidence, compare it to compliance checklists,
identify missing controls, and generate a structured audit report.

# Detailed Sample Multi-Agent Application: Research Assistant Built with OpenClaw

The following example is realistic, research-oriented, and naturally
supports security analysis. In this design, the user enters a research
topic, and a coordinated set of agents work together to collect, verify,
rank, and synthesize academic information.

## User Goal

Example user input:\
\"I want to study prompt injection defenses in multi-agent AI systems.
Find relevant academic papers, verify the references, summarize them,
identify the top 5 papers, propose a paper outline, and locate relevant
datasets if any exist.\"

## Recommended 7-Agent Architecture

**Agent 1 -- Query Planner / Coordinator**

Receives the user\'s topic and breaks it into search subtopics,
keywords, and search strategies. Coordinates other agents and tracks the
workflow.

**Agent 2 -- Academic Search Agent A**

Searches one set of sources such as Google Scholar, Semantic Scholar,
arXiv, DBLP, ACM Digital Library, IEEE Xplore, or university
repositories, depending on what tools or web connectors are available.

**Agent 3 -- Academic Search Agent B**

Searches a second set of sources independently from Agent 2 so the
system can compare results across multiple Internet resources rather
than relying on a single source.

**Agent 4 -- Reference Verification Agent**

Checks whether the candidate papers are real, whether
titles/authors/years match, and whether links, DOIs, venue names, or
abstracts are consistent. Its role is to reduce fake or hallucinated
references.

**Agent 5 -- Ranking / Selection Agent**

Scores papers by relevance, recency, source credibility, and relation to
the user\'s exact topic, then selects the top 5 candidates.

**Agent 6 -- Synthesis / Outline Agent**

Writes a literature-review style outline for a research paper based on
the verified top papers. It can organize sections such as background,
threat model, defense methods, evaluation, and open problems.

**Agent 7 -- Data / Evidence Agent**

Searches for datasets, benchmark tasks, challenge problems, code
repositories, or evaluation frameworks related to the topic so the user
can move from literature review to experimentation.

## Example Workflow

Step 1: The user enters a research topic.

Step 2: Agent 1 generates keywords, related terms, and a search plan.

Step 3: Agents 2 and 3 search different academic sources and collect
candidate papers.

Step 4: Agent 4 verifies references to reduce hallucinated or incorrect
citations.

Step 5: Agent 5 ranks the verified papers and selects the top 5.

Step 6: Agent 6 writes a structured outline for a future research paper
or survey.

Step 7: Agent 7 searches for data, benchmarks, or repositories related
to the topic.

Step 8: Agent 1 assembles the final package for the user: verified
references, summaries, top 5 list, outline, and data resources.

## What Each Agent Should Produce

To make the system concrete, each agent should output a structured
artifact.

Agent 1: search plan, keyword list, source plan

Agents 2 and 3: candidate paper list with title, author, year, link,
abstract snippet

Agent 4: verification table (verified / suspicious / rejected)

Agent 5: ranked shortlist of top 5 papers with justification

Agent 6: paper outline with section titles and short section notes

Agent 7: list of datasets, repositories, or benchmarks with relevance
notes

## Example Final Output to the User

A good final report from the system could include:

1.  Verified bibliography (10--20 candidate papers)

2.  One-paragraph summary for each verified paper

3.  Top 5 selected papers with reasons

4.  Draft outline for a research paper

5.  Datasets / code repositories / benchmarks

6.  Notes on what information could not be verified

## Security Analysis for the Research - Assistant Application

This application is powerful but risky. It creates multiple realistic
attack surfaces. For example:

- Search agents may ingest poisoned webpages or fake citations.

- A verification agent may still be fooled by prompt injection or
  misleading metadata.

- A ranking agent may over-trust recent but low-quality sources.

- A writing agent may reproduce false claims or fabricated references.

- A data agent may pull malicious files or misleading repositories.

Students can evaluate both capability and risk of the research-assistant
application.

## Security Questions Should Be Analyzed of the Research -- Assistant App

- What happens if a poisoned webpage tells the search agent to ignore
  the user\'s request and fetch secrets?

- Can the verification agent incorrectly approve fabricated references?

- Can one compromised agent influence downstream agents and corrupt the
  whole workflow?

- What if the data agent downloads a malicious script or untrusted file?

- What controls prevent the writing agent from including false claims in
  the final outline?

- How should logging, approval gates, and access control be applied
  between agents?

# Required Discussion for a Publishable Graduate-Level Report

Your final report should not only describe what you built. It should
read like a research paper. At minimum, include the following sections
and the kinds of questions they should answer.

1\. Abstract

What system did you build, what security risks did you test, and what
were your main findings?

2\. Introduction

Why do AI agent ecosystems matter? Why is OpenClaw relevant? Why is this
application worth studying?

3\. Background

Explain autonomous agents, tool use, MCP, prompt injection, data
exfiltration, and multi-agent risks. This section should be
understandable to a reader who is new to OpenClaw.

4\. System Design

Describe the architecture, the role of each agent, data flow between
agents, and what tools or resources each agent can access.

5\. Experimental Setup

What VM did you use? What version of OpenClaw? What external resources
or APIs were allowed?

6\. Multi-Agent Application Build

Explain how the sample application works, including the search,
verification, ranking, and writing pipeline.

7\. Security Analysis

Describe the threats, attack attempts, observations, and whether the
attacks succeeded or failed.

8\. Mitigation/Defense with Evaluation

Describe controls such as HITL, file access restrictions,
containerization, output verification, and logging.

9\. Discussion

What are the broader implications? What limitations did your system
have? What mistakes did the agents make?

10\. Future Work

How could this system be improved for research, education, or real-world
deployment?

11\. Conclusion

Summarize the lessons learned about both AI capability and AI agent
security.

12\. References

# AI-Assisted Learning Path for Beginners

Students starting from zero should follow this learning sequence.
Document each stage in the report.

Stage 1: Learn what an AI agent is.

Stage 2: Learn what OpenClaw is and why MCP matters.

Stage 3: Learn How to install OpenClaw on your Linux Virtual Machine
such as Labtainer VM.

• <https://www.youtube.com/watch?v=a9u2yZvsqHA>

• <https://www.youtube.com/watch?v=pSi4hAJVnxI>

• <https://www.youtube.com/watch?v=HNAv85MfGUI>

• <https://www.youtube.com/watch?v=YCD2FSvj35I>

Stage 4: Learn how multi-agent workflows differ from single-agent
chatbots.

Stage 5: Learn what tool use means in practice (file read/write, process
checks, command execution).

Stage 6: Build a very small two-agent prototype first.

Stage 7: Expand to a larger pipeline such as the 7-agent research
assistant.

Stage 8: Perform attack experiments and analyze the results.

Stage 9: Mitigation/Defense with Evaluation: Based on your findings in
Stage 8, design and implement at least one mitigation strategy. Re-run
your attack and evaluate whether the mitigation reduces or eliminates
the vulnerability. A clear before vs. after comparison discussion of
effectiveness and limitations of your approach.

## Sample Beginner Prompts to Use with AI Tools

- Explain what an AI agent is as if I have never studied it before.

- What is OpenClaw? What problem does it solve?

- What is MCP? Explain it like I am a graduate student in cybersecurity
  but new to AI agents.

- Give me a simple example of a two-agent workflow.

- Why is tool access dangerous in autonomous agents?

- What are common security failures in multi-agent AI systems?

# Detailed AI-Paired Programming Prompts for Building the Research Assistant

- Help me design a 7-agent OpenClaw system for academic paper search,
  verification, ranking, outline generation, and dataset discovery.

- Show me how to divide responsibilities among Coordinator, Search,
  Verification, Ranking, Writing, and Data agents.

- How should Agent 2 and Agent 3 search different Internet sources and
  avoid duplicate results?

- Help me design a verification rule set that checks whether a paper is
  likely real or suspicious.

- How should a ranking agent score papers by relevance, source
  credibility, and recency?

- How should an outline-writing agent convert the top 5 papers into a
  structured survey outline?

- Help me log each agent's reasoning and outputs so I can use them in a
  research report.

# Minimum Evidence Required in the Final Submission

- Screenshot of OpenClaw running in the VM

- Screenshot or logs showing at least two agents communicating

- Candidate paper list from at least two different sources

- Verification results showing accepted vs suspicious references

- Top 5 ranked paper list

- Draft research paper outline produced by an agent

- Dataset / benchmark / repository list from the data agent

- At least one attack attempt with prompt and result

- At least one mitigation with evidence or explanation

- AI prompts, tool outputs, and verification notes

# Grading Rubric (20 Points, due: 5/1/2026)

- AI-Assisted Learning & Verification -- 5 points

- OpenClaw Deployment & Working Multi-Agent System -- 5 points

- Security Investigation & Attack Analysis -- 5 points

- Mitigation + Publishable Report Quality -- 5 points

# Remark

The goal of this project is not to reward prior experience with
OpenClaw. The goal is to measure whether you can use AI-assisted
learning, build a meaningful multi-agent system, reason about security
risks, and document your work in a graduate-level report. A student who
starts from zero on AI agents and OpenClaw should still be able to
succeed with AI assisted learning and AI paired programming if they used
follow the required learning path and document their work carefully.

# Clarifications and Final Notes

**Timeline:** This project is designed to be completed within 2 weeks.
Due: 5/1/2026

**Flexibility:**\
Students may either build a custom multi-agent application using
OpenClaw\
or work on the research assistant system described in the project.\
\
**AI Usage:**\
AI tools are expected and encouraged. However, students must document:\
- Prompts used\
- AI responses\
- Verification steps\
\
**Goal:**\
The emphasis is not only on building the system but also on
understanding and analyzing:\
- Agent behavior\
- Security vulnerabilities\
- Mitigation effectiveness

