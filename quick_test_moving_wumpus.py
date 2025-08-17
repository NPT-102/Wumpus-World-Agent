#!/usr/bin/env python3
# quick_test_moving_wumpus.py

"""
Quick test for KB-Safe Moving Wumpus Agent
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from env_simulator.generateMap import WumpusWorldGenerator
from env_simulator.environment import WumpusEnvironment
from agent.agent import Agent
from agent.kb_safe_moving_wumpus_agent import KnowledgeBaseSafeMovingWumpusAgent

def quick_test():
    """Quick test of Moving Wumpus Agent"""
    
    print("🐺 Quick Test - KB-Safe Moving Wumpus Agent")
    print("=" * 50)
    
    # Generate a simple 6x6 map
    generator = WumpusWorldGenerator(N=6, pits_probability=0.1)
    game_map, wumpus_positions, pit_positions = generator.generate_map()
    
    print(f"Generated map:")
    print(f"  - Wumpus positions: {wumpus_positions}")
    print(f"  - Pit positions: {len(pit_positions)} pits")
    
    # Create environment and agent
    environment = WumpusEnvironment(game_map, wumpus_positions, pit_positions)
    base_agent = Agent(environment=environment, N=6)
    moving_wumpus_agent = KnowledgeBaseSafeMovingWumpusAgent(base_agent, 'dijkstra')
    
    # Run a few steps
    print("\nRunning first 15 steps:")
    for step in range(15):
        if not base_agent.alive:
            print(f"  💀 Agent died at step {step}")
            break
            
        action = moving_wumpus_agent.step()
        state = moving_wumpus_agent.get_current_state()
        
        print(f"  Step {step + 1:2d}: Pos={state['position']}, Actions={state['action_count']}, "
              f"Next Wumpus Move={state['next_wumpus_move']}")
        
        if step > 0 and state['action_count'] % 5 == 0:
            print(f"    🐺 Wumpus movement occurred!")
        
        if action == "DEAD":
            break
            
        if base_agent.position == (0, 0) and base_agent.gold_obtain:
            print(f"  🏆 Mission completed!")
            break
    
    # Final stats
    final_result = moving_wumpus_agent.get_final_result()
    print(f"\n📊 Final Results:")
    print(f"  - Score: {final_result['score']}")
    print(f"  - Alive: {final_result['alive']}")
    print(f"  - Gold: {final_result['gold']}")
    print(f"  - Total Actions: {final_result['total_actions']}")
    print(f"  - Wumpus Movements: {final_result['wumpus_movements']}")
    print(f"  - Wumpus Move Cycles: {final_result['wumpus_move_cycles']}")
    
    print("\n✅ Quick test completed!")

if __name__ == "__main__":
    quick_test()
