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


def is_valid_move(game_map, position, pit_positions, old_pos, wumpus_positions):
    """Check if Wumpus can move to this position"""
    x, y = position
    return (
        0 <= x < len(game_map)
        and 0 <= y < len(game_map[0])
        and position not in pit_positions  # Don't move into pits
        and position != old_pos            # Don't stay in same place
        and position not in wumpus_positions  # Don't overlap with other Wumpus
        and 'G' not in game_map[x][y]      # Don't move into gold cell
    )


# Trong module/moving_Wumpus.py
def update_wumpus_position(agent, game_map, wumpus_positions, pit_positions, wumpus_alive=None):
    if not agent.alive or not wumpus_positions:
        return wumpus_positions

    if wumpus_alive is None:
        wumpus_alive = [True]*len(wumpus_positions)

    new_positions = []

    # --- XOÁ W và tín hiệu STENCH xung quanh W cũ ---
    for i, j in wumpus_positions:
        # Xoá W
        game_map[i][j] = [c for c in game_map[i][j] if c != 'W']
        # Chỉ xoá tín hiệu STENCH (S) xung quanh, KHÔNG xoá pit (P) hoặc breeze (B)
        # CHỈ XOÁ STENCH TỪ CÁC Ô ADJACENT, KHÔNG XOÁ TỪ TẤT CẢ
        for di, dj in [(-1,0), (1,0), (0,-1), (0,1)]:  # Chỉ adjacent, không diagonal
            ni, nj = i+di, j+dj
            if 0<=ni<len(game_map) and 0<=nj<len(game_map[0]):
                # CHỈ xoá stench, giữ nguyên pit và breeze
                game_map[ni][nj] = [c for c in game_map[ni][nj] if c != 'S']

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

    # --- Thêm W và CHỈ STENCH xung quanh vị trí mới ---
    for idx, (i,j) in enumerate(new_positions):
        if wumpus_alive[idx]:
            if 'W' not in game_map[i][j]:
                game_map[i][j].append('W')
            # CHỈ thêm stench (S) quanh W mới, KHÔNG thêm pit hoặc breeze
            for di,dj in [(-1,0),(1,0),(0,-1),(0,1)]:
                ni,nj = i+di,j+dj
                if 0<=ni<len(game_map) and 0<=nj<len(game_map[0]):
                    if 'S' not in game_map[ni][nj]:
                        game_map[ni][nj].append('S')

    # Note: Removed restore_pit_indicators call to prevent potential hanging
    # Pits should remain stable as we only remove/add stench, not pit indicators

    print("Before Wumpus move:", wumpus_positions)
    print("After Wumpus move:", new_positions)
    print_map(game_map)

    return new_positions


def restore_pit_indicators(game_map, pit_positions):
    """Ensure pits and their breezes are properly maintained"""
    if not pit_positions:  # Safety check
        return
        
    # First, ensure all pit positions have 'P'
    for i, j in pit_positions:
        if 0 <= i < len(game_map) and 0 <= j < len(game_map[0]):  # Bounds check
            if 'P' not in game_map[i][j]:
                game_map[i][j].append('P')
    
    # Then, ensure breeze around pits
    for i, j in pit_positions:
        if 0 <= i < len(game_map) and 0 <= j < len(game_map[0]):  # Bounds check
            for di, dj in [(-1,0), (1,0), (0,-1), (0,1)]:
                ni, nj = i + di, j + dj
                if 0 <= ni < len(game_map) and 0 <= nj < len(game_map[0]):
                    if 'B' not in game_map[ni][nj]:
                        game_map[ni][nj].append('B')
