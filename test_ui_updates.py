#!/usr/bin/env python3
# test_ui_updates.py

"""
Test UI updates for Moving Wumpus Agent
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from env_simulator.generateMap import WumpusWorldGenerator, print_map
from env_simulator.environment import WumpusEnvironment
from agent.agent import Agent
from agent.kb_safe_moving_wumpus_agent import KnowledgeBaseSafeMovingWumpusAgent

def print_ui_debug_info(agent, environment, step_num):
    """Print debug info to verify UI data"""
    print(f"\n=== UI Debug Info - Step {step_num} ===")
    
    # Environment state
    wumpus_positions = []
    stench_positions = []
    
    for i in range(environment.N):
        for j in range(environment.N):
            cell = environment.game_map[i][j]
            if 'W' in cell:
                wumpus_positions.append((i, j))
            if 'S' in cell:
                stench_positions.append((i, j))
    
    print(f"Environment Wumpus: {wumpus_positions}")
    print(f"Environment Stench: {stench_positions}")
    
    # Agent state
    state = agent.get_current_state()
    print(f"Agent Current Wumpus: {state.get('wumpus_positions', [])}")
    print(f"Agent Wumpus Alive: {state.get('wumpus_alive', [])}")
    print(f"Agent Actions: {state.get('action_count', 0)}")
    print(f"Agent Next Move: {state.get('next_wumpus_move', 0)}")
    
    # Verify environment updated flag
    if state.get('environment_updated'):
        print("✅ Environment updated flag is set")
    else:
        print("❌ Environment updated flag NOT set")

def test_ui_updates():
    """Test UI update functionality"""
    print("🖼️ Testing UI Updates for Moving Wumpus Agent")
    print("=" * 60)
    
    # Generate test map
    generator = WumpusWorldGenerator(N=6, wumpus=2, pits_probability=0.1)
    game_map, wumpus_positions, pit_positions = generator.generate_map()
    
    # Create environment and agent
    environment = WumpusEnvironment(game_map, wumpus_positions, pit_positions)
    base_agent = Agent(environment=environment, N=6)
    moving_wumpus_agent = KnowledgeBaseSafeMovingWumpusAgent(base_agent, 'dijkstra')
    
    print_ui_debug_info(moving_wumpus_agent, environment, 0)
    
    # Run steps to trigger UI updates
    for step in range(7):  # Run 7 steps to trigger Wumpus movement at step 5
        if not base_agent.alive:
            print(f"💀 Agent died at step {step}")
            break
            
        print(f"\n🏃 Executing Step {step + 1}")
        action = moving_wumpus_agent.step()
        
        print_ui_debug_info(moving_wumpus_agent, environment, step + 1)
        
        # Check if environment was updated (for UI refresh trigger)
        state = moving_wumpus_agent.get_current_state()
        if state.get('environment_updated'):
            print("🔄 UI should refresh environment display")
            
        if action == "DEAD":
            break
    
    print(f"\n📝 UI Update Test Summary:")
    print(f"- Environment map should reflect real-time Wumpus positions")
    print(f"- Stench pattern should update when Wumpuses move")
    print(f"- Dead Wumpuses should show with X mark")
    print(f"- Stats panel should show Moving Wumpus specific info")
    print(f"- All updates should be real-time during gameplay")
    
    print(f"\n✅ UI update test completed!")

if __name__ == "__main__":
    test_ui_updates()
