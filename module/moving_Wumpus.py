import random

def move_wumpus(gam_map, wumpus_position, pit_positions):
    """
    Randomly moves the Wumpus to an adjacent cell.
    """
    directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]
    random.shuffle(directions)

    for move in directions:
        new_position = (wumpus_position[0] + move[0], wumpus_position[1] + move[1])
        if is_valid_move(gam_map, new_position, pit_positions, wumpus_position):
            return new_position
    return wumpus_position  # Stay in place if no valid move found

def is_valid_move(gam_map, position, pit_positions, wumpus_position):
    x, y = position
    return 0 <= x < len(gam_map) and 0 <= y < len(gam_map[0]) and not gam_map[x][y] and position not in pit_positions and position != wumpus_position

def update_wumpus_position(agent, gam_map, wumpus_position, pit_positions):
    """
    Updates the Wumpus position based on the agent's actions and the game map.
    """
    if agent.alive:
        new_wumpus_position = move_wumpus(gam_map, wumpus_position, pit_positions)
        if new_wumpus_position != wumpus_position:
            print(f"Wumpus moved from {wumpus_position} to {new_wumpus_position}")
            return new_wumpus_position
    return wumpus_position  # No movement if agent is not alive

