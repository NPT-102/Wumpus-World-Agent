from env_simulator.generateMap import WumpusWorldGenerator, print_map
from env_simulator.environment import WumpusEnvironment
from env_simulator.kb import KnowledgeBase
from agent.agent import Agent
from agent.kb_safe_agent import KnowledgeBaseSafeAgent

def test_kb_agent_8x8(test_rounds=5):
    """Test KB-Safe Agent multiple times on 8x8 maps"""
    
    print("=== TESTING KB-SAFE AGENT ON 8x8 MAPS ===\n")
    
    total_positions_explored = []
    survival_rate = 0
    
    for round_num in range(1, test_rounds + 1):
        print(f"=== TEST ROUND {round_num} ===")
        
        # Generate 8x8 map
        generator = WumpusWorldGenerator(N=8)
        game_map, wumpus_position, pit_positions = generator.generate_map()
        
        # Convert single wumpus to list if needed
        if isinstance(wumpus_position, tuple):
            wumpus_position = [wumpus_position]
        elif isinstance(wumpus_position, list):
            wumpus_position = list(wumpus_position)
        
        print(f"Generated 8x8 Game Map (Round {round_num}):")
        print_map(game_map)
        print(f"Wumpus at: {wumpus_position}")
        print(f"Pits at: {pit_positions}")
        
        # Create environment and agent
        environment = WumpusEnvironment(game_map, wumpus_position, pit_positions)
        base_agent = Agent(environment=environment, N=8)  # 8x8 map
        kb_agent = KnowledgeBaseSafeAgent(base_agent, max_risk_threshold=1.0)
        
        print(f"\nStarting KB-Safe agent (Round {round_num})...")
        step_count = 0
        max_steps = 500  # More steps for 8x8 map
        
        while step_count < max_steps:
            success, message = kb_agent.step()
            step_count += 1
            
            print(f"Step {step_count}: {message}")
            
            if not success:
                print("Agent completed exploration!")
                break
            
            if not base_agent.alive:
                print("Agent died!")
                break
        
        # Print results for this round
        final_result = kb_agent.get_final_result()
        positions_explored = len(kb_agent.visited_positions)
        
        print(f"\n--- ROUND {round_num} RESULTS ---")
        print(f"Position: {final_result['final_position']}")
        print(f"Score: {final_result['score']}")
        print(f"Gold obtained: {final_result['gold']}")
        print(f"Alive: {final_result['alive']}")
        print(f"Steps taken: {step_count}")
        print(f"Positions explored: {positions_explored}")
        print(f"Visited positions: {sorted(list(kb_agent.visited_positions))}")
        
        if final_result['alive']:
            survival_rate += 1
        
        total_positions_explored.append(positions_explored)
        
        print("\n" + "="*60 + "\n")
    
    # Summary statistics
    print("=== FINAL SUMMARY ===")
    print(f"Total test rounds: {test_rounds}")
    print(f"Survival rate: {survival_rate}/{test_rounds} ({100*survival_rate/test_rounds:.1f}%)")
    print(f"Average positions explored: {sum(total_positions_explored)/len(total_positions_explored):.1f}")
    print(f"Min positions explored: {min(total_positions_explored)}")
    print(f"Max positions explored: {max(total_positions_explored)}")
    print(f"Positions explored per round: {total_positions_explored}")
    
    # Calculate theoretical maximum safe positions
    total_cells = 8 * 8  # 64 cells in 8x8 map
    print(f"\nTheoretical analysis:")
    print(f"Total cells in 8x8 map: {total_cells}")
    print(f"Average percentage explored: {100*sum(total_positions_explored)/len(total_positions_explored)/total_cells:.1f}%")

if __name__ == "__main__":
    test_kb_agent_8x8(5)  # Test 5 rounds
