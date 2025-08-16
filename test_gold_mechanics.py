#!/usr/bin/env python3
"""Test the gold grabbing and home return scoring."""

from env_simulator.generateMap import WumpusWorldGenerator, print_map
from agent.agent import Agent
from stepwise_agent import StepByStepHybridAgent

def test_gold_mechanics():
    """Test that gold is removed from map and 1000 points awarded for returning home."""
    print("Testing gold mechanics...")
    
    # Create a simple map with gold easily accessible
    game_map = [
        [[], [], [], []],           # . . . .
        [[], [], [], []],           # . . . .
        [[], [], ['G'], []],        # . . G .
        [[], [], [], []]            # . . . .
    ]
    
    wumpus_positions = []  # No Wumpuses for this test
    pit_positions = []     # No pits for this test
    
    print("Test Map:")
    print_map(game_map)
    
    agent = Agent(map=game_map, N=4)
    step_agent = StepByStepHybridAgent(agent, game_map, wumpus_positions, pit_positions)
    
    print(f"Initial score: {agent.score}")
    print(f"Initial gold status: {agent.gold_obtain}")
    print(f"Gold in map at (2,2): {'G' in game_map[2][2]}")
    
    # Manually move agent to gold position
    agent.position = (2, 2)
    print(f"\nAgent moved to gold position: {agent.position}")
    
    # Execute step - should grab gold
    can_continue, message = step_agent.step()
    print(f"Step result: {message}")
    print(f"Score after grabbing: {agent.score}")
    print(f"Gold status: {agent.gold_obtain}")
    print(f"Gold still in map at (2,2): {'G' in game_map[2][2]}")
    
    # Move agent home
    agent.position = (0, 0)
    print(f"\nAgent moved home: {agent.position}")
    
    # Execute step - should get home bonus
    can_continue, message = step_agent.step()
    print(f"Step result: {message}")
    print(f"Final score: {agent.score}")
    
    final_result = step_agent.get_final_result()
    print(f"Final result: {final_result}")

if __name__ == "__main__":
    test_gold_mechanics()
