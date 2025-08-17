# module/moving_Wumpus.py
import random
from copy import deepcopy

def move_wumpus(game_map, current_position, pit_positions, other_wumpus_positions):
    """
    Move Wumpus to a valid cell - Wumpuses have limited local knowledge
    They can sense adjacent pits but don't have perfect map knowledge
    """
    directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]
    random.shuffle(directions)

    for move in directions:
        new_position = (current_position[0] + move[0], current_position[1] + move[1])
        if is_valid_move(game_map, new_position, pit_positions, current_position, other_wumpus_positions):
            # Wumpuses avoid starting position (0,0) by instinct
            if new_position == (0, 0):
                continue
            return new_position
    
    # If no valid moves, stay in place
    return current_position


def is_valid_move(game_map, position, pit_positions, old_pos, other_wumpus_positions):
    """Check if Wumpus can move to this position with limited knowledge"""
    x, y = position
    
    # Basic boundary check
    if not (0 <= x < len(game_map) and 0 <= y < len(game_map[0])):
        return False
    
    # Don't stay in same place
    if position == old_pos:
        return False
    
    # Avoid other Wumpuses (they can sense each other nearby)
    if position in other_wumpus_positions:
        return False
    
    # Wumpuses can sense and avoid pits adjacent to their current position
    for pit_pos in pit_positions:
        if position == pit_pos:
            return False
    
    return True


def update_wumpus_position(agent, environment, wumpus_positions, pit_positions, wumpus_alive=None):
    """Update Wumpus positions using environment interface"""
    if not agent.alive or not wumpus_positions:
        return wumpus_positions

    if wumpus_alive is None:
        wumpus_alive = [True] * len(wumpus_positions)

    new_positions = list(wumpus_positions)  # Start with current positions

    # Move each living Wumpus
    for idx, w_pos in enumerate(wumpus_positions):
        if not wumpus_alive[idx]:
            continue

        # Get other living Wumpus positions (INCLUDING already moved ones!)
        other_wumpus = [new_positions[jdx] for jdx in range(len(new_positions)) 
                       if jdx != idx and wumpus_alive[jdx]]
        
        # Move Wumpus with limited knowledge
        new_pos = move_wumpus(environment.game_map, w_pos, pit_positions, other_wumpus)
        
        # Double-check for collision with already moved Wumpuses
        while new_pos in other_wumpus and new_pos != w_pos:
            print(f"🚨 Collision detected at {new_pos}, trying alternative move...")
            # Try all other valid positions
            directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]
            alternative_found = False
            for direction in directions:
                alt_pos = (w_pos[0] + direction[0], w_pos[1] + direction[1])
                if (is_valid_move(environment.game_map, alt_pos, pit_positions, w_pos, other_wumpus) 
                    and alt_pos not in other_wumpus and alt_pos != (0, 0)):
                    new_pos = alt_pos
                    alternative_found = True
                    break
            
            if not alternative_found:
                print(f"⚠️ No collision-free move found for Wumpus {idx}, staying at {w_pos}")
                new_pos = w_pos
                break
        
        if new_pos != w_pos:
            print(f"Wumpus moved from {w_pos} to {new_pos}")
            
            # Update environment through proper interface
            # Remove Wumpus from old position
            if 'W' in environment.game_map[w_pos[0]][w_pos[1]]:
                environment.game_map[w_pos[0]][w_pos[1]].remove('W')
            
            # Add Wumpus to new position
            if 'W' not in environment.game_map[new_pos[0]][new_pos[1]]:
                environment.game_map[new_pos[0]][new_pos[1]].append('W')
            
            # Update stench patterns through environment
            update_stench_patterns(environment, w_pos, new_pos)
        
        # Update the position in our tracking list
        new_positions[idx] = new_pos

    print("Wumpus positions updated:", new_positions)
    return new_positions


def update_stench_patterns(environment, old_pos, new_pos):
    """Update stench patterns when Wumpus moves"""
    N = len(environment.game_map)
    
    # Remove stench around old position (if no other Wumpus there)
    old_adjacent = get_adjacent_positions(old_pos, N)
    for adj_pos in old_adjacent:
        i, j = adj_pos
        if 'S' not in environment.game_map[i][j]:
            continue  # No stench to remove
            
        # Check if any other Wumpus can cause stench here
        has_other_wumpus_nearby = False
        other_adjacent = get_adjacent_positions(adj_pos, N)
        for other_adj in other_adjacent:
            if other_adj != old_pos and 'W' in environment.game_map[other_adj[0]][other_adj[1]]:
                has_other_wumpus_nearby = True
                break
        
        # Remove stench only if no other Wumpus causes it
        if not has_other_wumpus_nearby:
            environment.game_map[i][j].remove('S')
            print(f"Removed stench at {adj_pos} (no more Wumpus nearby)")
    
    # Add stench around new position
    new_adjacent = get_adjacent_positions(new_pos, N)
    for adj_pos in new_adjacent:
        i, j = adj_pos
        if 'S' not in environment.game_map[i][j]:
            environment.game_map[i][j].append('S')
            print(f"Added stench at {adj_pos} (Wumpus moved nearby)")
        # If stench already exists, no need to add again


def get_adjacent_positions(position, N):
    """Get valid adjacent positions"""
    i, j = position
    adjacent = []
    for di, dj in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
        ni, nj = i + di, j + dj
        if 0 <= ni < N and 0 <= nj < N:
            adjacent.append((ni, nj))
    return adjacent
