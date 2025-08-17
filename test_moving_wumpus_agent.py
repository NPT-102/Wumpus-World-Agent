#!/usr/bin/env python3
# test_moving_wumpus_agent.py

"""
Test script for KB-Safe Moving Wumpus Agent
Tests the agent with moving Wumpuses every 5 actions
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from env_simulator.generateMap import WumpusWorldGenerator
from env_simulator.environment import WumpusEnvironment
from agent.agent import Agent
from agent.kb_safe_moving_wumpus_agent import KnowledgeBaseSafeMovingWumpusAgent

def test_moving_wumpus_agent(grid_size=8, pit_prob=0.15, num_tests=3):
    """Test Moving Wumpus Agent performance"""
    
    print("🐺 ========================================")
    print("🐺 Testing KB-Safe Moving Wumpus Agent")
    print("🐺 ========================================")
    print(f"Grid Size: {grid_size}x{grid_size}")
    print(f"Pit Probability: {pit_prob}")
    print(f"Wumpus Move Interval: 5 actions")
    print(f"Number of Tests: {num_tests}\n")
    
    total_scores = []
    survival_rate = 0
    gold_collection_rate = 0
    
    for test_num in range(num_tests):
        print(f"\n🎮 === TEST {test_num + 1}/{num_tests} ===")
        
        # Generate map
        generator = WumpusWorldGenerator(N=grid_size, pits_probability=pit_prob)
        game_map, wumpus_positions, pit_positions = generator.generate_map()
        
        print(f"Map generated:")
        print(f"  - Wumpus positions: {wumpus_positions}")
        print(f"  - Pit positions: {len(pit_positions)} pits")
        
        # Create environment and agent
        environment = WumpusEnvironment(game_map, wumpus_positions, pit_positions)
        base_agent = Agent(environment=environment, N=grid_size)
        moving_wumpus_agent = KnowledgeBaseSafeMovingWumpusAgent(base_agent, 'dijkstra')
        
        # Run simulation
        step_count = 0
        max_steps = 200  # Prevent infinite loops
        
        while base_agent.alive and step_count < max_steps:
            step_count += 1
            action = moving_wumpus_agent.step()
            
            if step_count % 25 == 0:  # Progress update every 25 steps
                state = moving_wumpus_agent.get_current_state()
                print(f"  Step {step_count}: Pos={state['position']}, Gold={state['gold']}, "
                      f"Actions={state['action_count']}, Next Wumpus Move={state['next_wumpus_move']}")
                
            if action == "DEAD" or not base_agent.alive:
                print(f"  💀 Agent died at step {step_count}")
                break
                
            # Check if returned home with gold
            if base_agent.position == (0, 0) and base_agent.gold_obtain:
                print(f"  🏆 Mission completed successfully at step {step_count}!")
                break
                
            # Check if exploration is complete
            if hasattr(moving_wumpus_agent, 'exploration_complete') and moving_wumpus_agent.exploration_complete:
                if base_agent.position == (0, 0):
                    print(f"  🏠 Returned home safely at step {step_count}")
                    break
        
        # Get final results
        final_result = moving_wumpus_agent.get_final_result()
        
        print(f"\n📊 Test {test_num + 1} Results:")
        print(f"  - Final Score: {final_result['score']}")
        print(f"  - Survived: {'Yes' if final_result['alive'] else 'No'}")
        print(f"  - Gold Collected: {'Yes' if final_result['gold'] else 'No'}")
        print(f"  - Total Actions: {final_result['total_actions']}")
        print(f"  - Wumpus Move Cycles: {final_result['wumpus_move_cycles']}")
        print(f"  - Wumpus Movements: {final_result['wumpus_movements']}")
        print(f"  - Living Wumpuses: {final_result['wumpus_alive_count']}")
        print(f"  - Visited Cells: {len(final_result['visited_cells'])}")
        
        total_scores.append(final_result['score'])
        
        if final_result['alive']:
            survival_rate += 1
            
        if final_result['gold']:
            gold_collection_rate += 1
    
    # Calculate statistics
    avg_score = sum(total_scores) / len(total_scores)
    survival_percentage = (survival_rate / num_tests) * 100
    gold_percentage = (gold_collection_rate / num_tests) * 100
    
    print(f"\n🏁 ========================================")
    print(f"🏁 FINAL RESULTS - Moving Wumpus Agent")
    print(f"🏁 ========================================")
    print(f"Average Score: {avg_score:.1f}")
    print(f"Survival Rate: {survival_rate}/{num_tests} ({survival_percentage:.1f}%)")
    print(f"Gold Collection Rate: {gold_collection_rate}/{num_tests} ({gold_percentage:.1f}%)")
    print(f"Score Range: {min(total_scores)} - {max(total_scores)}")
    print(f"🏁 ========================================")
    
    return {
        'avg_score': avg_score,
        'survival_rate': survival_percentage,
        'gold_rate': gold_percentage,
        'scores': total_scores
    }

if __name__ == "__main__":
    test_moving_wumpus_agent()
