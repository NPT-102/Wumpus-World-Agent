# Quick debugging test to check KB
from agent.intelligent_agent import IntelligentAgent
from agent.safe_first_intelligent_agent import SafeFirstIntelligentAgent
from agent.agent import Agent2
from visualization.display import Display
import random

# Create a small test
agent2 = Agent2()
display = Display(agent2)

# Check KB facts
print("=== KB FACTS CHECK ===")
print(f"Agent at: {agent2.position}")
facts = agent2.kb.current_facts()
print(f"Total facts: {len(facts)}")
for i, fact in enumerate(facts[:20]):  # Show first 20 facts
    print(f"{i+1:2d}: {fact}")

# Check safe positions
print("\n=== SAFETY CHECK ===")
for row in range(4):
    for col in range(4):
        safe = agent2.kb.is_safe(row, col)
        print(f"({row},{col}): {'SAFE' if safe else 'RISKY'}", end="  ")
    print()
