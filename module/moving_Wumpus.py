# module/moving_Wumpus.py
import random
from copy import deepcopy
from env_simulator.generateMap import print_map

def move_wumpus(game_map, current_position, pit_positions, wumpus_positions):
    """
    Di chuyển Wumpus sang một ô hợp lệ, không trùng với pit hoặc Wumpus khác.
    """
    directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]
    random.shuffle(directions)

    for move in directions:
        new_position = (current_position[0] + move[0], current_position[1] + move[1])
        if is_valid_move(game_map, new_position, pit_positions, current_position, wumpus_positions):
            return new_position
    return current_position

def is_valid_move(game_map, position, pit_positions, old_pos, wumpus_positions):
    x, y = position
    return (
        0 <= x < len(game_map)
        and 0 <= y < len(game_map[0])
        and position not in pit_positions
        and position != old_pos
        and position not in wumpus_positions  # tránh trùng với Wumpus khác
    )

def update_wumpus_position(agent, game_map, wumpus_positions, pit_positions, wumpus_alive=None):
    """
    Cập nhật vị trí tất cả Wumpus còn sống. Chỉ di chuyển khi được gọi (5 hành động).
    """
    if not agent.alive or not wumpus_positions:
        return wumpus_positions

    if wumpus_alive is None:
        wumpus_alive = [True] * len(wumpus_positions)

    new_positions = []

    # Xóa tất cả Wumpus cũ khỏi map nhưng giữ các ký hiệu khác
    for i in range(len(game_map)):
        for j in range(len(game_map[0])):
            game_map[i][j] = [c for c in game_map[i][j] if c != 'W']

    # Di chuyển từng Wumpus còn sống
    for idx, w_pos in enumerate(wumpus_positions):
        if not wumpus_alive[idx]:
            new_positions.append(w_pos)
            continue

        # copy map tạm để tránh Wumpus khác đi vào ô này
        temp_map = deepcopy(game_map)
        # tạo danh sách Wumpus khác để kiểm tra ô trùng
        other_wumpus_positions = [p for jdx, p in enumerate(wumpus_positions) if jdx != idx and wumpus_alive[jdx]]
        new_pos = move_wumpus(temp_map, w_pos, pit_positions, other_wumpus_positions)
        if new_pos != w_pos:
            print(f"Wumpus moved from {w_pos} to {new_pos}")
        new_positions.append(new_pos)

    # Thêm lại tất cả Wumpus còn sống vào map
    for idx, pos in enumerate(new_positions):
        if wumpus_alive[idx] and 'W' not in game_map[pos[0]][pos[1]]:
            game_map[pos[0]][pos[1]].append('W')

    print("Before Wumpus move:", wumpus_positions)
    print("After Wumpus move:", new_positions)
    print_map(game_map)

    return new_positions
