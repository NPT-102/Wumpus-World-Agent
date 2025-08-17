#!/usr/bin/env python3
# test_stench_update.py

"""
Test stench pattern updates when Wumpus moves or dies
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from env_simulator.generateMap import WumpusWorldGenerator, print_map
from env_simulator.environment import WumpusEnvironment
from agent.agent import Agent
from agent.kb_safe_moving_wumpus_agent import KnowledgeBaseSafeMovingWumpusAgent

def print_environment_state(environment, title="Environment State"):
    """Print current environment state focusing on Wumpus and stench"""
    print(f"\n=== {title} ===")
    
    # Find Wumpus and stench positions
    wumpus_positions = []
    stench_positions = []
    
    for i in range(environment.N):
        for j in range(environment.N):
            cell = environment.game_map[i][j]
            if 'W' in cell:
                wumpus_positions.append((i, j))
            if 'S' in cell:
                stench_positions.append((i, j))
    
    print(f"Wumpus positions: {wumpus_positions}")
    print(f"Stench positions: {stench_positions}")
    
    # Print visual map
    print("Map visualization:")
    for i in range(environment.N):
        row_display = []
        for j in range(environment.N):
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
            elif 'G' in cell:
                row_display.append(' G')
            else:
                row_display.append(' .')
        print(' '.join(row_display))

def test_stench_updates():
    """Test stench pattern updates with Moving Wumpus Agent"""
    
    print("🧪 Testing Stench Pattern Updates")
    print("=" * 50)
    
    # Generate a small map for easier testing
    generator = WumpusWorldGenerator(N=5, wumpus=2, pits_probability=0.1)
    game_map, wumpus_positions, pit_positions = generator.generate_map()
    
    # Create environment and agent
    environment = WumpusEnvironment(game_map, wumpus_positions, pit_positions)
    base_agent = Agent(environment=environment, N=5)
    moving_wumpus_agent = KnowledgeBaseSafeMovingWumpusAgent(base_agent, 'dijkstra')
    
    print_environment_state(environment, "Initial State")
    
    # Simulate some steps to trigger Wumpus movement
    print(f"\n🏃 Running steps to trigger Wumpus movement...")
    
    step_count = 0
    for step in range(8):  # Run 8 steps to trigger movement at step 5
        if not base_agent.alive:
            print(f"💀 Agent died at step {step}")
            break
            
        step_count += 1
        action = moving_wumpus_agent.step()
        
        state = moving_wumpus_agent.get_current_state()
        print(f"\nStep {step + 1}: Pos={state['position']}, Actions={state['action_count']}")
        
        # Check if Wumpus movement occurred
        if step > 0 and state['action_count'] % 5 == 0:
            print(f"🐺 WUMPUS MOVEMENT OCCURRED!")
            print_environment_state(environment, f"After Step {step + 1} - Wumpus Movement")
        
        if action == "DEAD":
            break
    
    # Test arrow shooting if agent is still alive
    if base_agent.alive and len(moving_wumpus_agent.current_wumpus_positions) > 0:
        print(f"\n🏹 Testing arrow shot...")
        
        # Simulate arrow hit
        original_arrow_status = base_agent.arrow_hit
        base_agent.arrow_hit = True
        
        # Trigger status update
        moving_wumpus_agent._update_wumpus_alive_status()
        
        print_environment_state(environment, "After Arrow Shot")
        
        # Reset for next movement test
        base_agent.arrow_hit = original_arrow_status
    
    # Final state
    final_result = moving_wumpus_agent.get_final_result()
    print(f"\n📊 Final Statistics:")
    print(f"  - Living Wumpuses: {final_result['wumpus_alive_count']}")
    print(f"  - Total Wumpus Movements: {final_result['wumpus_movements']}")
    print(f"  - Movement Cycles: {final_result['wumpus_move_cycles']}")
    
    print_environment_state(environment, "Final State")
    
    print(f"\n✅ Stench update test completed!")

if __name__ == "__main__":
    test_stench_updates()
