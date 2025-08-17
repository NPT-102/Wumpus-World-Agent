"""
Debug Wumpus hunting logic
"""
from agent.safe_first_intelligent_agent import SafeFirstIntelligentAgent
from env_simulator.generateMap import WumpusWorldGenerator, print_map
from env_simulator.environment import WumpusEnvironment
from agent.agent import Agent

def debug_wumpus_hunting():
    print("=== DEBUGGING WUMPUS HUNTING LOGIC ===")
    
    # Create a specific map for testing
    game_map = [
        ['.', '.', 'S', 'W'],
        ['B', 'S', 'W', 'S'],  
        ['P', 'GB', 'SB', '.'],
        ['P', 'B', 'P', 'B']
    ]
    wumpus_positions = [(1, 2), (0, 3)]
    pit_positions = [(2, 0), (3, 0), (3, 2)]
    
    print("Map:")
    for row in game_map:
        print(row)
    
    # Create environment and agent
    environment = WumpusEnvironment(game_map, wumpus_positions, pit_positions)
    base_agent = Agent(environment=environment, N=4)
    agent = SafeFirstIntelligentAgent(base_agent, max_risk_threshold=0.3)
    
    # Test Wumpus detection logic manually
    print("\n=== Manual KB Analysis ===")
    if hasattr(base_agent, 'kb'):
        facts = base_agent.kb.current_facts()
        print(f"Initial KB facts: {facts}")
        
        # Simulate some steps to build KB
        for i in range(8):  # Take some steps
            success, message = agent.step()
            print(f"Step {i+1}: {message}")
            if not success:
                break
        
        # Check KB again
        facts = base_agent.kb.current_facts()
        print(f"\nKB facts after exploration: {facts}")
        
        # Test Wumpus detection
        known_wumpus = agent._get_known_wumpus_positions()
        print(f"Known Wumpus positions: {known_wumpus}")
        
        # Check each position manually
        for row in range(4):
            for col in range(4):
                is_possible = base_agent.kb.is_possible_wumpus(row, col)
                if is_possible:
                    print(f"Position ({row}, {col}) might have Wumpus")

if __name__ == "__main__":
    debug_wumpus_hunting()
