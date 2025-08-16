from env_simulator.generateMap import WumpusWorldGenerator, print_map
from env_simulator.kb import KnowledgeBase
from agent.agent import Agent
from agent.hybrid_agent_action_dynamic import hybrid_agent_action_dynamic

def main():
    # Create a challenging map where agent needs to shoot to progress
    # Layout:
    # . S P S
    # S W P G  <- Gold at (1,3), blocked by pit and wumpus
    # P S W S
    # P P S .
    
    game_map = [
        [[], ['S'], ['P', 'B'], ['S']],
        [['S'], ['W'], ['P', 'B'], ['G']],
        [['P', 'B'], ['S'], ['W'], ['S']],
        [['P', 'B'], ['P', 'B'], ['S'], []]
    ]
    
    # Add positions 
    wumpus_positions = [(1,1), (2,2)]  # Two wumpuses to block paths
    pit_positions = [(0,2), (1,2), (2,0), (3,0), (3,1)]  # Block most paths
    
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
