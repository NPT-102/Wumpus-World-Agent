# module/moving_Wumpus.py
import random
from copy import deepcopy
from env_simulator.generateMap import print_map

def move_wumpus(game_map, current_position, pit_positions, wumpus_positions):
    """
    Di chuyển Wumpus sang một ô hợp lệ, không trùng với pit hoặc Wumpus khác.
    Không cho Wumpus đi vào ô (0,0).
    """
    directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]
    random.shuffle(directions)

    for move in directions:
        new_position = (current_position[0] + move[0], current_position[1] + move[1])
        if is_valid_move(game_map, new_position, pit_positions, current_position, wumpus_positions):
            # Không cho Wumpus đi vào ô (0,0)
            if new_position == (0, 0):
                continue
            return new_position
    return current_position


def is_valid_move(game_map, position, old_pos, wumpus_positions, pit_positions):
    x, y = position
    return (
        0 <= x < len(game_map)
        and 0 <= y < len(game_map[0])
        and position not in pit_positions
        and position != old_pos
        and position not in wumpus_positions  # tránh trùng với Wumpus khác
        and 'G' not in game_map[x][y]        # tránh đi vào ô có vàng
    )


# Trong module/moving_Wumpus.py
def update_wumpus_position(agent, game_map, wumpus_positions, pit_positions, wumpus_alive=None):
    if not agent.alive or not wumpus_positions:
        return wumpus_positions

    if wumpus_alive is None:
        wumpus_alive = [True]*len(wumpus_positions)

    new_positions = []

    # --- XOÁ W và tín hiệu xung quanh W cũ ---
    for i, j in wumpus_positions:
        # Xoá W
        game_map[i][j] = [c for c in game_map[i][j] if c != 'W']
        # Xoá tín hiệu S/B/P xung quanh
        for di in [-1,0,1]:
            for dj in [-1,0,1]:
                ni, nj = i+di, j+dj
                if 0<=ni<len(game_map) and 0<=nj<len(game_map[0]):
                    game_map[ni][nj] = [c for c in game_map[ni][nj] if c not in ['S','B','P']]

    # Di chuyển Wumpus
    for idx, w_pos in enumerate(wumpus_positions):
        if not wumpus_alive[idx]:
            new_positions.append(w_pos)
            continue

        other_wumpus = [p for jdx, p in enumerate(wumpus_positions) if jdx != idx and wumpus_alive[jdx]]
        new_pos = move_wumpus(game_map, w_pos, pit_positions, other_wumpus)
        if new_pos != w_pos:
            print(f"Wumpus moved from {w_pos} to {new_pos}")
        new_positions.append(new_pos)

    # --- Thêm W và tín hiệu xung quanh vị trí mới ---
    for idx, (i,j) in enumerate(new_positions):
        if wumpus_alive[idx]:
            if 'W' not in game_map[i][j]:
                game_map[i][j].append('W')
            # Thêm tín hiệu S/B/P quanh W mới
            for di,dj in [(-1,0),(1,0),(0,-1),(0,1)]:
                ni,nj = i+di,j+dj
                if 0<=ni<len(game_map) and 0<=nj<len(game_map[0]):
                    if 'S' not in game_map[ni][nj]:
                        game_map[ni][nj].append('S')

    print("Before Wumpus move:", wumpus_positions)
    print("After Wumpus move:", new_positions)
    print_map(game_map)

    return new_positions
