#!/usr/bin/env python3
# test_wumpus_movement_safety.py

"""
Test agent's ability to detect and avoid Wumpus after movement
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from env_simulator.generateMap import WumpusWorldGenerator, print_map
from env_simulator.environment import WumpusEnvironment
from agent.agent import Agent
from agent.kb_safe_moving_wumpus_agent import KnowledgeBaseSafeMovingWumpusAgent

def print_safety_analysis(agent, environment, step_num):
    """Print safety analysis after Wumpus movement"""
    print(f"\n=== Safety Analysis - Step {step_num} ===")
    
    # Current Wumpus positions
    current_wumpus = []
    all_stench = []
    
    for i in range(environment.N):
        for j in range(environment.N):
            if 'W' in environment.game_map[i][j]:
                current_wumpus.append((i, j))
            if 'S' in environment.game_map[i][j]:
                all_stench.append((i, j))
    
    print(f"Current Wumpus positions: {current_wumpus}")
    print(f"Current stench positions: {all_stench}")
    
    # Agent's KB facts about stench
    kb_stench_facts = [fact for fact in agent.agent.kb.facts if fact.startswith('S(')]
    kb_no_stench_facts = [fact for fact in agent.agent.kb.facts if fact.startswith('~S(')]
    
    print(f"KB stench facts: {len(kb_stench_facts)}")
    print(f"KB no-stench facts: {len(kb_no_stench_facts)}")
    
    # Dangerous positions according to KB
    dangerous_positions = agent.agent.kb.get_dangerous_cells()
    print(f"KB considers dangerous: {len(dangerous_positions)} positions")
    if dangerous_positions:
        print(f"   Dangerous positions: {dangerous_positions[:5]}{'...' if len(dangerous_positions) > 5 else ''}")
    
    # Current agent position safety
    agent_pos = agent.agent.position
    is_safe = agent._is_kb_safe(agent_pos)
    print(f"Agent position {agent_pos} is KB-safe: {is_safe}")

def test_wumpus_movement_safety():
    """Test agent's safety assessment after Wumpus movement"""
    print("🎯 Testing Wumpus Movement Safety Assessment")
    print("=" * 60)
    
    # Generate test map
    generator = WumpusWorldGenerator(N=6, wumpus=2, pits_probability=0.1)
    game_map, wumpus_positions, pit_positions = generator.generate_map()
    
    print("Initial map layout:")
    for i in range(6):
        row_display = []
        for j in range(6):
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
    base_agent = Agent(environment=environment, N=6)
    moving_wumpus_agent = KnowledgeBaseSafeMovingWumpusAgent(base_agent, 'dijkstra')
    
    print_safety_analysis(moving_wumpus_agent, environment, 0)
    
    # Run steps to trigger Wumpus movement
    for step in range(7):  # Run enough steps to trigger movement
        if not base_agent.alive:
            print(f"💀 Agent died at step {step}")
            break
            
        print(f"\n🏃 Step {step + 1}")
        
        # Get positions agent considers safe before action
        test_positions = [(1, 1), (2, 0), (0, 2), (2, 2)]
        safe_before = {pos: moving_wumpus_agent._is_kb_safe(pos) for pos in test_positions}
        
        action = moving_wumpus_agent.step()
        
        # Check safety assessment after action
        safe_after = {pos: moving_wumpus_agent._is_kb_safe(pos) for pos in test_positions}
        
        # Report safety changes
        for pos in test_positions:
            if safe_before[pos] != safe_after[pos]:
                status = "SAFE → UNSAFE" if safe_before[pos] else "UNSAFE → SAFE"
                print(f"   🔄 Position {pos}: {status}")
        
        state = moving_wumpus_agent.get_current_state()
        if state.get('action_count', 0) % 5 == 0 and state.get('action_count', 0) > 0:
            print(f"🐺 WUMPUS MOVEMENT OCCURRED!")
            print_safety_analysis(moving_wumpus_agent, environment, step + 1)
            
            # Test if agent would avoid newly dangerous areas
            print("\n🛡️ Testing post-movement safety assessment:")
            for pos in [(1, 1), (2, 0), (0, 2), (2, 2)]:
                is_safe = moving_wumpus_agent._is_kb_safe(pos)
                in_dangerous = pos in moving_wumpus_agent.agent.kb.get_dangerous_cells()
                print(f"   Position {pos}: Safe={is_safe}, In_dangerous_list={in_dangerous}")
        
        if action == "DEAD":
            break
    
    print(f"\n📋 Safety Assessment Test Summary:")
    print(f"✅ Agent should detect stench pattern changes when Wumpus moves")
    print(f"✅ Agent should update dangerous positions list accordingly")
    print(f"✅ Agent should avoid newly dangerous areas")
    print(f"✅ Agent should maintain safety for previously safe areas (if still safe)")
    print(f"⚠️  Agent should be more cautious in dynamic environment")
    
    print(f"\n✅ Wumpus movement safety test completed!")

if __name__ == "__main__":
    test_wumpus_movement_safety()
