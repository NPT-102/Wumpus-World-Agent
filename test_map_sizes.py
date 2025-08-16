#!/usr/bin/env python3
"""
Test script to verify that different map sizes work correctly
"""

from env_simulator.generateMap import WumpusWorldGenerator
from agent.agent import Agent
from stepwise_agent import StepByStepHybridAgent

def test_map_size(size):
    """Test a specific map size"""
    print(f"\n=== Testing Map Size: {size}x{size} ===")
    
    try:
        # Generate map
        generator = WumpusWorldGenerator(N=size)
        game_map, wumpus_positions, pit_positions = generator.generate_map()
        
        # Check map dimensions
        assert len(game_map) == size, f"Expected {size} rows, got {len(game_map)}"
        assert len(game_map[0]) == size, f"Expected {size} columns, got {len(game_map[0])}"
        
        print(f"✓ Map generated successfully: {size}x{size}")
        print(f"  Wumpus positions: {wumpus_positions}")
        print(f"  Pit positions: {pit_positions}")
        
        # Convert single wumpus to list if needed
        if isinstance(wumpus_positions, tuple):
            wumpus_positions = [wumpus_positions]
        
        # Create agent
        agent = Agent(map=game_map, N=size)
        step_agent = StepByStepHybridAgent(agent, game_map, wumpus_positions, pit_positions)
        
        print(f"✓ Agent created successfully")
        
        # Test a few moves
        for i in range(3):
            if not step_agent.step():
                break
            state = step_agent.get_current_state()
            print(f"  Step {i+1}: Position {state['position']}, Score: {state['score']}")
        
        print(f"✓ Agent movement test passed")
        return True
        
    except Exception as e:
        print(f"✗ Error testing size {size}: {e}")
        return False

def main():
    """Test various map sizes"""
    print("Testing Custom Map Sizes")
    print("=" * 50)
    
    test_sizes = [4, 5, 6, 7, 8, 10]
    results = {}
    
    for size in test_sizes:
        results[size] = test_map_size(size)
    
    print(f"\n=== Test Results ===")
    for size, passed in results.items():
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"Size {size}x{size}: {status}")
    
    all_passed = all(results.values())
    print(f"\nOverall: {'All tests passed!' if all_passed else 'Some tests failed!'}")

if __name__ == "__main__":
    main()
