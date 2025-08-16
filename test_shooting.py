from env_simulator.generateMap import WumpusWorldGenerator, print_map
from env_simulator.kb import KnowledgeBase
from agent.agent import Agent
from agent.hybrid_agent_action_dynamic import hybrid_agent_action_dynamic

def main():
    # Recreate the problematic scenario where agent falls into pit going to stench
    # Layout similar to your example:
    # . B SB W
    # B P P SB  
    # S B P B
    # W S GB .
    
    game_map = [
        [[], ['B'], ['S', 'B'], ['W']],
        [['B'], ['P'], ['P'], ['S', 'B']],
        [['S'], ['B'], ['P'], ['B']],
        [['W'], ['S'], ['G', 'B'], []]
    ]
    
    wumpus_positions = [(0,3), (3,0)]  # Two wumpuses
    pit_positions = [(1,1), (1,2), (2,2)]  # Pits that caused the problem
    
    print("Test Game Map:")
    print_map(game_map)
    print(f"Wumpus positions: {wumpus_positions}")
    print(f"Pit positions: {pit_positions}")
    
    # Create agent
    agent = Agent(map=game_map, N=4)
    
    # Run the hybrid agent
    result = hybrid_agent_action_dynamic(agent, game_map, wumpus_positions, pit_positions)
    print("\nFinal result:", result)
    print(f"Arrow status: {agent.arrow_hit} (0=not shot, 1=hit, -1=missed)")

if __name__ == "__main__":
    main()
