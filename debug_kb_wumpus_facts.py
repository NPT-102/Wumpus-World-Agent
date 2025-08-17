#!/usr/bin/env python3
# debug_kb_wumpus_facts.py

"""
Debug KB facts about Wumpus positions after movement
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from env_simulator.generateMap import WumpusWorldGenerator, print_map
from env_simulator.environment import WumpusEnvironment
from agent.agent import Agent
from agent.kb_safe_moving_wumpus_agent import KnowledgeBaseSafeMovingWumpusAgent

def analyze_kb_facts(agent, title="KB Analysis"):
    """Analyze KB facts in detail"""
    print(f"\n=== {title} ===")
    
    kb_facts = agent.agent.kb.facts
    
    # Categorize facts
    wumpus_facts = [f for f in kb_facts if 'W(' in f]
    stench_facts = [f for f in kb_facts if 'S(' in f and not f.startswith('~S(')]
    no_stench_facts = [f for f in kb_facts if f.startswith('~S(')]
    safe_facts = [f for f in kb_facts if f.startswith('Safe(')]
    
    print(f"Wumpus facts ({len(wumpus_facts)}):")
    for fact in sorted(wumpus_facts):
        print(f"  {fact}")
    
    print(f"Stench facts ({len(stench_facts)}):")
    for fact in sorted(stench_facts):
        print(f"  {fact}")
    
    print(f"No-stench facts ({len(no_stench_facts)}):")
    for fact in sorted(no_stench_facts)[:10]:  # Show first 10
        print(f"  {fact}")
    if len(no_stench_facts) > 10:
        print(f"  ... and {len(no_stench_facts) - 10} more")
    
    print(f"Safe facts ({len(safe_facts)}):")
    for fact in sorted(safe_facts):
        print(f"  {fact}")

def compare_reality_vs_kb(environment, agent, title="Reality vs KB"):
    """Compare actual environment state with KB knowledge"""
    print(f"\n=== {title} ===")
    
    # Reality - actual environment state
    actual_wumpus = []
    actual_stench = []
    
    for i in range(environment.N):
        for j in range(environment.N):
            if 'W' in environment.game_map[i][j]:
                actual_wumpus.append((i, j))
            if 'S' in environment.game_map[i][j]:
                actual_stench.append((i, j))
    
    print(f"🌍 REALITY:")
    print(f"  Actual Wumpus positions: {actual_wumpus}")
    print(f"  Actual stench positions: {actual_stench}")
    
    # KB knowledge - what agent believes
    kb_wumpus_positions = []
    kb_stench_positions = []
    kb_no_wumpus_positions = []
    
    kb_facts = agent.agent.kb.facts
    
    for fact in kb_facts:
        if fact.startswith('W('):
            # Extract position from W(i,j)
            import re
            match = re.match(r'W\((\d+),\s*(\d+)\)', fact)
            if match:
                kb_wumpus_positions.append((int(match.group(1)), int(match.group(2))))
        elif fact.startswith('S('):
            # Extract position from S(i,j)
            import re
            match = re.match(r'S\((\d+),\s*(\d+)\)', fact)
            if match:
                kb_stench_positions.append((int(match.group(1)), int(match.group(2))))
        elif fact.startswith('~W('):
            # Extract position from ~W(i,j)
            import re
            match = re.match(r'~W\((\d+),\s*(\d+)\)', fact)
            if match:
                kb_no_wumpus_positions.append((int(match.group(1)), int(match.group(2))))
    
    print(f"🧠 KB BELIEVES:")
    print(f"  KB thinks Wumpus at: {kb_wumpus_positions}")
    print(f"  KB knows stench at: {sorted(kb_stench_positions)}")
    print(f"  KB believes NO Wumpus at: {len(kb_no_wumpus_positions)} positions")
    
    # Compare
    print(f"🔍 COMPARISON:")
    
    # Wumpus position accuracy
    correct_wumpus = set(actual_wumpus) == set(kb_wumpus_positions)
    print(f"  Wumpus positions match: {correct_wumpus}")
    if not correct_wumpus:
        missing_wumpus = set(actual_wumpus) - set(kb_wumpus_positions)
        extra_wumpus = set(kb_wumpus_positions) - set(actual_wumpus)
        if missing_wumpus:
            print(f"  ❌ KB missing Wumpus at: {missing_wumpus}")
        if extra_wumpus:
            print(f"  ❌ KB thinks extra Wumpus at: {extra_wumpus}")
    
    # Stench accuracy
    correct_stench = set(actual_stench) == set(kb_stench_positions)
    print(f"  Stench positions match: {correct_stench}")
    if not correct_stench:
        missing_stench = set(actual_stench) - set(kb_stench_positions)
        extra_stench = set(kb_stench_positions) - set(actual_stench)
        if missing_stench:
            print(f"  ❌ KB missing stench at: {missing_stench}")
        if extra_stench:
            print(f"  ❌ KB thinks extra stench at: {extra_stench}")

def debug_kb_wumpus_facts():
    """Debug KB facts about Wumpus positions"""
    print("🐛 Debugging KB Wumpus Facts")
    print("=" * 50)
    
    # Generate test map
    generator = WumpusWorldGenerator(N=5, wumpus=2, pits_probability=0.1)
    game_map, wumpus_positions, pit_positions = generator.generate_map()
    
    print("Initial environment:")
    for i in range(5):
        row_display = []
        for j in range(5):
            cell = game_map[i][j]
            if 'W' in cell and 'S' in cell:
                row_display.append('WS')
            elif 'W' in cell:
                row_display.append(' W')
            elif 'S' in cell:
                row_display.append(' S')
            elif 'P' in cell:
                row_display.append(' P')
            elif 'B' in cell:
                row_display.append(' B')
            else:
                row_display.append(' .')
        print(' '.join(row_display))
    
    # Create environment and agent
    environment = WumpusEnvironment(game_map, wumpus_positions, pit_positions)
    base_agent = Agent(environment=environment, N=5)
    moving_wumpus_agent = KnowledgeBaseSafeMovingWumpusAgent(base_agent, 'dijkstra')
    
    analyze_kb_facts(moving_wumpus_agent, "Initial KB State")
    compare_reality_vs_kb(environment, moving_wumpus_agent, "Initial Reality vs KB")
    
    # Run steps to trigger Wumpus movement
    print(f"\n🏃 Running steps to trigger Wumpus movement...")
    
    for step in range(6):  # Run enough steps to trigger movement
        if not base_agent.alive:
            print(f"💀 Agent died at step {step}")
            break
            
        action = moving_wumpus_agent.step()
        
        state = moving_wumpus_agent.get_current_state()
        if state.get('action_count', 0) % 5 == 0 and state.get('action_count', 0) > 0:
            print(f"\n🐺 WUMPUS MOVEMENT OCCURRED at step {step + 1}!")
            
            print(f"\nEnvironment after movement:")
            for i in range(5):
                row_display = []
                for j in range(5):
                    cell = environment.game_map[i][j]
                    if 'W' in cell and 'S' in cell:
                        row_display.append('WS')
                    elif 'W' in cell:
                        row_display.append(' W')
                    elif 'S' in cell:
                        row_display.append(' S')
                    elif 'P' in cell:
                        row_display.append(' P')
                    elif 'B' in cell:
                        row_display.append(' B')
                    else:
                        row_display.append(' .')
                print(' '.join(row_display))
            
            analyze_kb_facts(moving_wumpus_agent, f"KB State After Movement (Step {step + 1})")
            compare_reality_vs_kb(environment, moving_wumpus_agent, f"Post-Movement Reality vs KB (Step {step + 1})")
            break
        
        if action == "DEAD":
            break
    
    print(f"\n🔍 Debug Summary:")
    print(f"✅ Check if KB correctly updates Wumpus position facts")
    print(f"✅ Check if KB correctly updates stench facts")  
    print(f"✅ Check if KB reasoning matches actual environment")
    print(f"❌ Identify discrepancies between reality and KB beliefs")
    
    print(f"\n✅ KB debug completed!")

if __name__ == "__main__":
    debug_kb_wumpus_facts()
