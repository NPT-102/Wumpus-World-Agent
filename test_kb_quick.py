from env_simulator.generateMap import WumpusWorldGenerator, print_map
from env_simulator.environment import WumpusEnvironment
from env_simulator.kb import KnowledgeBase
from agent.agent import Agent
from agent.kb_safe_agent import KnowledgeBaseSafeAgent

def test_kb_agent_quick():
    """Quick test of KB-Safe Agent with step limit"""
    
    print("=== QUICK TEST KB-SAFE AGENT ===\n")
    
    # Generate 8x8 map
    generator = WumpusWorldGenerator(N=8)
    game_map, wumpus_position, pit_positions = generator.generate_map()
    
    # Convert single wumpus to list if needed
    if isinstance(wumpus_position, tuple):
        wumpus_position = [wumpus_position]
    elif isinstance(wumpus_position, list):
        wumpus_position = list(wumpus_position)
    
    print(f"Generated 8x8 Game Map:")
    print_map(game_map)
    print(f"Wumpus at: {wumpus_position}")
    print(f"Pits at: {pit_positions}")
    
    # Create environment and agent
    environment = WumpusEnvironment(game_map, wumpus_position, pit_positions)
    base_agent = Agent(environment=environment, N=8)  # 8x8 map
    kb_agent = KnowledgeBaseSafeAgent(base_agent, max_risk_threshold=1.0)
    
    print(f"\nStarting KB-Safe agent...")
    step_count = 0
    max_steps = 50  # Limited steps to avoid infinite loops
    
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
    
    # Print results
    final_result = kb_agent.get_final_result()
    positions_explored = len(kb_agent.visited_positions)
    
    print(f"\n--- RESULTS ---")
    print(f"Position: {final_result['final_position']}")
    print(f"Score: {final_result['score']}")
    print(f"Gold obtained: {final_result['gold']}")
    print(f"Alive: {final_result['alive']}")
    print(f"Steps taken: {step_count}")
    print(f"Positions explored: {positions_explored}")
    print(f"Visited positions: {sorted(list(kb_agent.visited_positions))}")
    
    # Calculate exploration percentage
    total_cells = 8 * 8
    exploration_percentage = (positions_explored / total_cells) * 100
    print(f"Exploration percentage: {exploration_percentage:.1f}%")

if __name__ == "__main__":
    test_kb_agent_quick()
