"""
Project 4 — Run Attack Payloads (Before mitigation).

Executes each prompt injection payload and saves the results
as evidence for the report.
"""

from __future__ import annotations

import asyncio
import json
import os
import sys
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from attacks.prompt_injection import ALL_PAYLOADS
from src.agents.search import SearchAgentA
from src.agents.data import DataAgent


async def run_all_attacks():
    """Execute all attack payloads and save results."""
    results_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "attack_results")
    os.makedirs(results_dir, exist_ok=True)

    search_agent = SearchAgentA()
    data_agent = DataAgent()
    all_results = []

    print("=" * 70)
    print("🔴 RED TEAM ATTACK — Running WITHOUT Security Interceptor")
    print("=" * 70)

    for payload_id, payload_name, payload_text in ALL_PAYLOADS:
        print(f"\n{'─' * 60}")
        print(f"⚔️  Attack: {payload_name} ({payload_id})")
        print(f"{'─' * 60}")
        print(f"Payload:\n{payload_text.strip()[:200]}...")

        # Choose agent based on payload type
        if payload_id == "DATA_AGENT":
            agent = data_agent
        else:
            agent = search_agent

        try:
            result = await agent.run(payload_text)
            result_dict = result.model_dump() if hasattr(result, "model_dump") else {"text": str(result)}
            success = True
            print(f"\n🔓 RESULT: Agent executed the payload!")
            print(f"   Output preview: {json.dumps(result_dict, default=str)[:300]}...")
        except Exception as e:
            result_dict = {"error": str(e)}
            success = False
            print(f"\n❌ RESULT: Error — {e}")

        attack_record = {
            "timestamp": datetime.now().isoformat(),
            "payload_id": payload_id,
            "payload_name": payload_name,
            "payload_text": payload_text.strip(),
            "agent_used": agent.name,
            "mitigation_active": False,
            "result": result_dict,
            "attack_succeeded": success,
        }
        all_results.append(attack_record)

    # Save results
    output_file = os.path.join(results_dir, "before_mitigation.json")
    with open(output_file, "w") as f:
        json.dump(all_results, f, indent=2, default=str)
    print(f"\n\n✅ Results saved to: {output_file}")
    print(f"📊 Attacks run: {len(all_results)}")
    print(f"🔓 Succeeded: {sum(1 for r in all_results if r['attack_succeeded'])}")

    return all_results


if __name__ == "__main__":
    asyncio.run(run_all_attacks())
