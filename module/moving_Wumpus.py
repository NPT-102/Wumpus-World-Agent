# module/moving_Wumpus.py
import random
from copy import deepcopy
from env_simulator.generateMap import print_map

def move_wumpus(gam_map, current_position, pit_positions, wumpus_positions):
    """
    Di chuyển Wumpus sang một ô hợp lệ, không trùng với pit hoặc Wumpus khác.
    """
    directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]
    random.shuffle(directions)

    for move in directions:
        new_position = (current_position[0] + move[0], current_position[1] + move[1])
        if is_valid_move(gam_map, new_position, pit_positions, current_position, wumpus_positions):
            return new_position
    return current_position

def is_valid_move(gam_map, position, pit_positions, old_pos, wumpus_positions):
    x, y = position
    return (
        0 <= x < len(gam_map)
        and 0 <= y < len(gam_map[0])
        and position not in pit_positions
        and position != old_pos
        and position not in wumpus_positions  # tránh trùng với Wumpus khác
    )

def update_wumpus_position(agent, gam_map, wumpus_positions, pit_positions):
    """
    Cập nhật vị trí Wumpus. Chỉ di chuyển khi được gọi (file 1 đảm bảo 5 hành động).
    """
    if not agent.alive:
        return wumpus_positions

    new_positions = []
    moved = False

    # Dùng deepcopy map tạm để tránh xung đột khi di chuyển nhiều Wumpus
    temp_map = deepcopy(gam_map)
    for w_pos in wumpus_positions:
        new_pos = move_wumpus(temp_map, w_pos, pit_positions, wumpus_positions)
        if new_pos != w_pos:
            print(f"Wumpus moved from {w_pos} to {new_pos}")
            if "W" in gam_map[w_pos[0]][w_pos[1]]:
                gam_map[w_pos[0]][w_pos[1]].remove("W")
            gam_map[new_pos[0]][new_pos[1]].append("W")
            moved = True
            new_positions.append(new_pos)
        else:
            new_positions.append(w_pos)

        # Cập nhật temp_map để Wumpus tiếp theo không đi vào ô này
        temp_map[w_pos[0]][w_pos[1]] = [cell for cell in temp_map[w_pos[0]][w_pos[1]] if cell != "W"]
        temp_map[new_pos[0]][new_pos[1]].append("W")

    if moved:
        print("Updated Game Map:")
        print_map(gam_map)

    return new_positions
