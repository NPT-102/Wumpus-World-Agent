#!/usr/bin/env python3
# test_anti_cheat_stench.py

"""
Test anti-cheat functionality - stench should only show at visited positions
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from env_simulator.generateMap import WumpusWorldGenerator, print_map
from env_simulator.environment import WumpusEnvironment
from agent.agent import Agent
from agent.kb_safe_moving_wumpus_agent import KnowledgeBaseSafeMovingWumpusAgent

def check_stench_visibility(environment, visited_positions, step_num):
    """Check which stench positions should be visible vs actual environment"""
    print(f"\n=== Stench Visibility Check - Step {step_num} ===")
    
    # All stench positions in environment
    all_stench = []
    for i in range(environment.N):
        for j in range(environment.N):
            if 'S' in environment.game_map[i][j]:
                all_stench.append((i, j))
    
    # Stench at visited positions only
    visible_stench = [pos for pos in all_stench if pos in visited_positions]
    hidden_stench = [pos for pos in all_stench if pos not in visited_positions]
    
    print(f"All stench positions: {all_stench}")
    print(f"Visited positions: {list(visited_positions)}")
    print(f"✅ Should be visible: {visible_stench}")
    print(f"❌ Should be hidden: {hidden_stench}")
    
    return visible_stench, hidden_stench

def simulate_ui_display(environment, visited_positions, agent_position):
    """Simulate what UI should display based on anti-cheat rules"""
    print(f"\n📺 UI Display Simulation:")
    
    for i in range(environment.N):
        row_display = []
        for j in range(environment.N):
            cell = environment.game_map[i][j]
            display_char = ' '
            
            # Agent position
            if (i, j) == agent_position:
                display_char = 'A'
            # Visited positions
            elif (i, j) in visited_positions:
                if 'S' in cell and 'B' in cell:
                    display_char = 'X'  # Both stench and breeze
                elif 'S' in cell:
                    display_char = 'S'  # Stench
                elif 'B' in cell:
                    display_char = 'B'  # Breeze
                else:
                    display_char = 'v'  # Visited but no percepts
            # Unvisited positions (should show nothing)
            else:
                display_char = '.'  # Hidden
            
            row_display.append(display_char)
        print(' '.join(row_display))
    
    print("Legend: A=Agent, S=Stench(visible), B=Breeze(visible), X=Both, v=Visited, .=Hidden")

def test_anti_cheat_stench():
    """Test that stench is only shown at visited positions"""
    print("🔒 Testing Anti-Cheat Stench Display")
    print("=" * 50)
    
    # Generate test map
    generator = WumpusWorldGenerator(N=6, wumpus=2, pits_probability=0.1)
    game_map, wumpus_positions, pit_positions = generator.generate_map()
    
    # Create environment and agent
    environment = WumpusEnvironment(game_map, wumpus_positions, pit_positions)
    base_agent = Agent(environment=environment, N=6)
    moving_wumpus_agent = KnowledgeBaseSafeMovingWumpusAgent(base_agent, 'dijkstra')
    
    print("Initial environment:")
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
    
    # Run few steps and check visibility
    for step in range(4):
        print(f"\n🏃 Step {step + 1}")
        
        if not base_agent.alive:
            print("💀 Agent died")
            break
            
        # Get state before action
        state = moving_wumpus_agent.get_current_state()
        visited_before = set(state.get('visited', []))
        
        # Execute step
        action = moving_wumpus_agent.step()
        
        # Get state after action
        state = moving_wumpus_agent.get_current_state()
        visited_after = set(state.get('visited', []))
        agent_pos = state['position']
        
        print(f"Agent position: {agent_pos}")
        print(f"Newly visited: {visited_after - visited_before}")
        
        # Check what stench should be visible
        visible_stench, hidden_stench = check_stench_visibility(environment, visited_after, step + 1)
        
        # Simulate UI display
        simulate_ui_display(environment, visited_after, agent_pos)
        
        if action == "DEAD":
            break
    
    print(f"\n📋 Anti-Cheat Test Summary:")
    print(f"✅ Stench should ONLY appear at visited positions")
    print(f"❌ Stench should be HIDDEN at unvisited positions")  
    print(f"🔄 When Wumpus moves, stench pattern updates but visibility rules remain")
    print(f"🎯 This maintains fair gameplay - no cheating by seeing unexplored areas")
    
    print(f"\n✅ Anti-cheat stench test completed!")

if __name__ == "__main__":
    test_anti_cheat_stench()
