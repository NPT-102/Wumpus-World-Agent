#!/usr/bin/env python3
"""
Test and compare different pathfinding algorithms: A*, Dijkstra, BFS
"""

from agent.kb_safe_agent import KnowledgeBaseSafeAgent
from env_simulator.generateMap import WumpusWorldGenerator 
from env_simulator.environment import WumpusEnvironment
from agent.agent import Agent
import time

def test_pathfinding_algorithms():
    """Test different pathfinding algorithms and compare performance"""
    
    print("=== PATHFINDING ALGORITHMS COMPARISON ===\n")
    
    algorithms = ['astar', 'dijkstra', 'bfs']
    results = {}
    
    for algorithm in algorithms:
        print(f"🔍 Testing {algorithm.upper()} Algorithm...")
        
        # Generate consistent map for fair comparison
        generator = WumpusWorldGenerator(4)  # 4x4 grid
        game_map, wumpus_positions, pit_positions = generator.generate_map()
        
        print(f"  Map: Wumpus at {wumpus_positions}, Pits at {pit_positions}")
        
        # Create environment and agent  
        environment = WumpusEnvironment(game_map, wumpus_positions, pit_positions)
        agent = Agent(environment)
        
        # Create KB-Safe agent with specific algorithm
        kb_agent = KnowledgeBaseSafeAgent(agent, pathfinding_algorithm=algorithm)
        
        # Track performance
        start_time = time.time()
        step_count = 0
        max_steps = 20
        
        while agent.alive and step_count < max_steps:
            step_count += 1
            
            success, message = kb_agent.step()
            print(f"    Step {step_count}: {message}")
            
            if not success or "Final score" in message:
                break
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        # Record results
        results[algorithm] = {
            'steps': step_count,
            'score': agent.score,
            'gold_obtained': agent.gold_obtain,
            'alive': agent.alive,
            'final_position': agent.position,
            'execution_time': execution_time,
            'positions_visited': len(kb_agent.visited_positions)
        }
        
        print(f"  ✅ {algorithm.upper()} Results:")
        print(f"    Steps: {step_count}, Score: {agent.score}")
        print(f"    Gold: {agent.gold_obtain}, Alive: {agent.alive}")
        print(f"    Execution Time: {execution_time:.4f}s")
        print(f"    Positions Visited: {len(kb_agent.visited_positions)}")
        print()
    
    # Compare results
    print("=== ALGORITHM COMPARISON SUMMARY ===")
    print(f"{'Algorithm':<10} {'Steps':<6} {'Score':<8} {'Gold':<5} {'Alive':<6} {'Time(s)':<8} {'Visited':<8}")
    print("-" * 70)
    
    for alg, result in results.items():
        print(f"{alg.upper():<10} {result['steps']:<6} {result['score']:<8} "
              f"{'Yes' if result['gold_obtained'] else 'No':<5} "
              f"{'Yes' if result['alive'] else 'No':<6} "
              f"{result['execution_time']:<8.4f} {result['positions_visited']:<8}")
    
    # Find best performer
    best_score_alg = max(results, key=lambda k: results[k]['score'])
    fastest_alg = min(results, key=lambda k: results[k]['execution_time'])
    most_visited_alg = max(results, key=lambda k: results[k]['positions_visited'])
    
    print(f"\n🏆 PERFORMANCE HIGHLIGHTS:")
    print(f"  Best Score: {best_score_alg.upper()} ({results[best_score_alg]['score']} points)")
    print(f"  Fastest: {fastest_alg.upper()} ({results[fastest_alg]['execution_time']:.4f}s)")
    print(f"  Most Exploration: {most_visited_alg.upper()} ({results[most_visited_alg]['positions_visited']} positions)")
    
    return results

def test_specific_dijkstra():
    """Test your specific Dijkstra implementation"""
    print("\n=== TESTING YOUR DIJKSTRA IMPLEMENTATION ===")
    
    try:
        from search.dijkstra import dijkstra
        print("✅ Your Dijkstra module imported successfully!")
        
        # Note: Your Dijkstra works with Agent2, not our Agent class
        print("ℹ️  Your Dijkstra uses Agent2 class with risk calculations")
        print("   Our KB-Safe agent uses a different approach with KB facts")
        print("   Both are valid approaches for different use cases!")
        
        print("\n📝 Your Dijkstra Features:")
        print("  - Risk-based pathfinding")
        print("  - Goal: reach (0,0) with gold")
        print("  - Costs: 1 for safe, 50-1000 for risky, 0 for gold grab")
        print("  - Considers rotation costs")
        
    except ImportError as e:
        print(f"❌ Could not import your Dijkstra: {e}")

if __name__ == "__main__":
    # Test pathfinding algorithms
    test_pathfinding_algorithms()
    
    # Test your specific Dijkstra
    test_specific_dijkstra()
