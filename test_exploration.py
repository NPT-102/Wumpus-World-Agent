#!/usr/bin/env python3
"""Test exploration behavior with different scenarios."""

from env_simulator.generateMap import print_map
from agent.agent import Agent
from agent.hybrid_agent_action_dynamic import hybrid_agent_action_dynamic

def test_stench_exploration():
    """Test that agent explores stench cells when no safe path exists."""
    print("Testing stench exploration behavior...")
    
    # Custom map with gold blocked by dangers but stench cells available
    game_map = [
        [[], ['B'], ['P'], ['W']],      # . B P W
        [['B'], ['P'], ['P'], ['S']],   # B P P S  
        [['S'], ['B'], ['G', 'B'], ['B']],  # S B GB B
        [['W'], ['S'], ['B'], []]       # W S B .
    ]
    
    wumpus_positions = [(0,3), (3,0)]
    pit_positions = [(0,2), (1,1), (1,2)]
    
    print("Test Map - Stench Exploration:")
    print_map(game_map)
    print(f"Wumpus positions: {wumpus_positions}")
    print(f"Pit positions: {pit_positions}")
    
    agent = Agent(map=game_map, N=4)
    result = hybrid_agent_action_dynamic(agent, game_map, wumpus_positions, pit_positions)
    
    print(f"\nResult: {result}")
    print(f"Arrow used: {agent.arrow_hit}")
    
    return result

def test_gold_collection_with_shooting():
    """Test agent collecting gold and shooting when needed."""
    print("\nTesting gold collection with shooting...")
    
    # Map where agent can reach gold but may need to shoot
    game_map = [
        [[], ['S'], [], []],           # . S . .
        [['B'], ['P'], ['S'], []],     # B P S .
        [[], ['S'], ['G'], []],        # . S G .
        [[], [], [], ['W']]            # . . . W
    ]
    
    wumpus_positions = [(3,3)]
    pit_positions = [(1,1)]
    
    print("Test Map - Gold Collection:")
    print_map(game_map)
    print(f"Wumpus positions: {wumpus_positions}")
    print(f"Pit positions: {pit_positions}")
    
    agent = Agent(map=game_map, N=4)
    result = hybrid_agent_action_dynamic(agent, game_map, wumpus_positions, pit_positions)
    
    print(f"\nResult: {result}")
    print(f"Arrow used: {agent.arrow_hit}")
    
    return result

if __name__ == "__main__":
    test1_result = test_stench_exploration()
    test2_result = test_gold_collection_with_shooting()
    
    print("\n" + "="*50)
    print("SUMMARY:")
    print(f"Test 1 - Stench exploration: Score {test1_result['score']}, Gold: {test1_result['gold']}")
    print(f"Test 2 - Gold with shooting: Score {test2_result['score']}, Gold: {test2_result['gold']}")
