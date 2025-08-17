#!/usr/bin/env python3

"""
Test script for KB-Safe Agent with built-in Dijkstra pathfinding
"""

from env_simulator.generateMap import WumpusWorldGenerator
from env_simulator.environment import WumpusEnvironment
from agent.agent import Agent
from agent.kb_safe_agent import KnowledgeBaseSafeAgent

def test_kb_safe_dijkstra():
    """Test KB-Safe agent with built-in Dijkstra pathfinding"""
    print("=== Testing KB-Safe Agent with Built-in Dijkstra Pathfinding ===\n")
    
    # Generate a test map
    print("🗺️  Generating test map...")
    generator = WumpusWorldGenerator(N=4, num_pits=3, num_wumpus=1)
    game_map, wumpus_positions, pit_positions, gold_position = generator.generate()
    
    print(f"📍 Map generated:")
    print(f"   Wumpus positions: {wumpus_positions}")
    print(f"   Pit positions: {pit_positions}")
    print(f"   Gold position: {gold_position}")
    
    # Create environment and agent
    environment = WumpusEnvironment(game_map, wumpus_positions, pit_positions, gold_position)
    base_agent = Agent(environment)
    kb_safe_agent = KnowledgeBaseSafeAgent(base_agent)
    
    print(f"\n🤖 Agent created with pathfinding: {kb_safe_agent.pathfinding_algorithm}")
    print(f"   Starting position: {base_agent.position}")
    print(f"   Starting direction: {base_agent.direction}")
    
    # Run exploration
    print(f"\n🚀 Starting exploration...")
    step_count = 0
    max_steps = 100
    
    while step_count < max_steps and base_agent.alive and not kb_safe_agent.exploration_complete:
        step_count += 1
        
        # Get current state
        current_pos = base_agent.position
        percepts = environment.get_percept(current_pos)
        
        print(f"\n--- Step {step_count} ---")
        print(f"Position: {current_pos}")
        print(f"Percepts: {percepts if percepts else 'None'}")
        print(f"Score: {base_agent.score}")
        print(f"Has Gold: {base_agent.gold_obtain}")
        
        # Take a step
        try:
            continue_exploration, message = kb_safe_agent.step()
            print(f"Step result: {message}")
            
            if not continue_exploration:
                print(f"🏁 Exploration finished: {message}")
                break
                
        except Exception as e:
            print(f"❌ Error during step: {e}")
            break
    
    # Final results
    print(f"\n=== FINAL RESULTS ===")
    print(f"🏁 Exploration completed after {step_count} steps")
    print(f"💰 Gold collected: {base_agent.gold_obtain}")
    print(f"🏠 Final position: {base_agent.position}")
    print(f"💯 Final score: {base_agent.score}")
    print(f"❤️  Agent survived: {base_agent.alive}")
    print(f"🗺️  Positions visited: {len(kb_safe_agent.visited_positions)}")
    print(f"📍 Visited positions: {sorted(list(kb_safe_agent.visited_positions))}")
    print(f"🔍 Pathfinding used: {kb_safe_agent.pathfinding_algorithm.upper()}")
    
    # Calculate coverage percentage
    total_safe_positions = sum(1 for i in range(4) for j in range(4) 
                             if (i, j) not in pit_positions and (i, j) not in wumpus_positions)
    coverage = (len(kb_safe_agent.visited_positions) / total_safe_positions) * 100
    print(f"📊 Safe area coverage: {coverage:.1f}% ({len(kb_safe_agent.visited_positions)}/{total_safe_positions})")
    
    return base_agent.score, len(kb_safe_agent.visited_positions), base_agent.gold_obtain

if __name__ == "__main__":
    try:
        score, visited_count, got_gold = test_kb_safe_dijkstra()
        
        print(f"\n🎯 SUMMARY")
        print(f"   Score: {score}")
        print(f"   Positions Explored: {visited_count}")
        print(f"   Gold Collected: {'✅' if got_gold else '❌'}")
        print(f"   Pathfinding: Dijkstra (built-in)")
        
    except KeyboardInterrupt:
        print(f"\n⚠️ Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
