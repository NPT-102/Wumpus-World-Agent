#!/usr/bin/env python3
"""
Final test with enhanced KB-Safe agent using different pathfinding algorithms
"""

from agent.kb_safe_agent import KnowledgeBaseSafeAgent
from env_simulator.generateMap import WumpusWorldGenerator 
from env_simulator.environment import WumpusEnvironment
from agent.agent import Agent

def test_all_algorithms_main():
    """Test all pathfinding algorithms in a single comprehensive test"""
    
    print("=== COMPREHENSIVE PATHFINDING TEST ===\n")
    
    # Test with a consistent map
    generator = WumpusWorldGenerator(4)
    game_map, wumpus_positions, pit_positions = generator.generate_map()
    
    print(f"Test Map Configuration:")
    print(f"  Grid Size: 4x4")
    print(f"  Wumpus at: {wumpus_positions}")
    print(f"  Pits at: {pit_positions}")
    print(f"  Gold position: Check during exploration\n")
    
    algorithms = ['astar', 'dijkstra', 'bfs']
    
    for algorithm in algorithms:
        print(f"🔬 Testing {algorithm.upper()} Algorithm:")
        print("-" * 40)
        
        # Create fresh environment and agent for each test
        environment = WumpusEnvironment(game_map, wumpus_positions, pit_positions)
        agent = Agent(environment)
        kb_agent = KnowledgeBaseSafeAgent(agent, pathfinding_algorithm=algorithm)
        
        step_count = 0
        max_steps = 25
        
        while agent.alive and step_count < max_steps:
            step_count += 1
            
            success, message = kb_agent.step()
            print(f"  Step {step_count:2d}: {message}")
            
            # Show pathfinding algorithm usage
            if "via" in message.lower() and algorithm.upper() in message.upper():
                print(f"    🗺️ Used {algorithm.upper()} pathfinding!")
            
            if not success or "Final score" in message:
                break
        
        print(f"\n📊 {algorithm.upper()} Final Results:")
        print(f"  Steps: {step_count}")
        print(f"  Score: {agent.score}")
        print(f"  Gold: {'Yes' if agent.gold_obtain else 'No'}")
        print(f"  Alive: {'Yes' if agent.alive else 'No'}")
        print(f"  Position: {agent.position}")
        print(f"  Explored: {len(kb_agent.visited_positions)} positions")
        print(f"  Algorithm: {algorithm.upper()}")
        print("=" * 50)
        print()

if __name__ == "__main__":
    test_all_algorithms_main()
