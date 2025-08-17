#!/usr/bin/env python3
# debug_wumpus_movement.py

"""
Debug Wumpus movement logic specifically
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from env_simulator.generateMap import WumpusWorldGenerator
from env_simulator.environment import WumpusEnvironment
from module.moving_Wumpus import update_wumpus_position, move_wumpus, is_valid_move

def test_wumpus_collision():
    """Test if Wumpuses can collide when moving"""
    print("🐺 Testing Wumpus Movement Collision")
    print("=" * 40)
    
    # Create simple 5x5 map with 2 adjacent Wumpuses
    game_map = [[[] for _ in range(5)] for _ in range(5)]
    
    # Place 2 Wumpuses next to each other
    wumpus_positions = [(0, 3), (1, 3)]  # Adjacent vertically
    pit_positions = []
    
    # Add Wumpuses to map
    game_map[0][3].append('W')
    game_map[1][3].append('W')
    
    # Add stenches around Wumpuses
    for pos in [(0, 2), (0, 4), (1, 2), (1, 4), (2, 3)]:
        if 0 <= pos[0] < 5 and 0 <= pos[1] < 5:
            game_map[pos[0]][pos[1]].append('S')
    
    print("Initial state:")
    print("Wumpus positions:", wumpus_positions)
    
    # Print map
    for i in range(5):
        row = ""
        for j in range(5):
            cell = game_map[i][j]
            if 'W' in cell:
                row += "W "
            elif 'S' in cell:
                row += "S "
            else:
                row += ". "
        print(row)
    
    # Test movement logic
    print("\nTesting movement for each Wumpus:")
    
    for idx, w_pos in enumerate(wumpus_positions):
        print(f"\nWumpus {idx} at {w_pos}:")
        
        # Get other Wumpuses
        other_wumpus = [p for jdx, p in enumerate(wumpus_positions) 
                       if jdx != idx]
        print(f"  Other Wumpuses: {other_wumpus}")
        
        # Test all possible moves
        directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]
        for direction in directions:
            new_pos = (w_pos[0] + direction[0], w_pos[1] + direction[1])
            valid = is_valid_move(game_map, new_pos, pit_positions, w_pos, other_wumpus)
            print(f"    Move to {new_pos}: {'✅ Valid' if valid else '❌ Invalid'}")
        
        # Get actual move
        new_pos = move_wumpus(game_map, w_pos, pit_positions, other_wumpus)
        print(f"  🎯 Chosen move: {w_pos} → {new_pos}")

def test_concurrent_movement():
    """Test what happens when both Wumpuses move at same time"""
    print("\n🔄 Testing Concurrent Movement")
    print("=" * 40)
    
    # Scenario: 2 Wumpuses adjacent, both want to move to same spot
    wumpus_positions = [(1, 1), (1, 2)]  # Horizontally adjacent
    pit_positions = []
    
    # Create environment
    game_map = [[[] for _ in range(5)] for _ in range(5)]
    game_map[1][1].append('W')
    game_map[1][2].append('W')
    
    environment = WumpusEnvironment(game_map, wumpus_positions, pit_positions)
    
    print("Before movement:")
    print(f"Wumpus positions: {wumpus_positions}")
    
    # Test sequential movement (current implementation)
    print("\nSequential movement:")
    new_positions = []
    
    for idx, w_pos in enumerate(wumpus_positions):
        other_wumpus = [p for jdx, p in enumerate(wumpus_positions) 
                       if jdx != idx]
        new_pos = move_wumpus(game_map, w_pos, pit_positions, other_wumpus)
        new_positions.append(new_pos)
        print(f"  Wumpus {idx}: {w_pos} → {new_pos}")
        
        # Update other_wumpus for next iteration (this is where bug might be)
        # Current implementation doesn't update the positions for next Wumpus
    
    print(f"Final positions: {new_positions}")
    
    # Check for collisions
    if len(set(new_positions)) != len(new_positions):
        print("🚨 COLLISION DETECTED!")
        from collections import Counter
        position_counts = Counter(new_positions)
        collisions = {pos: count for pos, count in position_counts.items() if count > 1}
        print(f"Collisions: {collisions}")

if __name__ == "__main__":
    test_wumpus_collision()
    test_concurrent_movement()
