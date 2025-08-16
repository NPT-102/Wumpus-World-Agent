# from agent.agent import Agent, Agent2, MOVE, DIRECTION
# from search.dijkstra import dijkstra
# from env_simulator.kb import KnowledgeBase as KB
# from module.moving_Wumpus import update_wumpus_position
# from copy import deepcopy

# SCORE = {
#     "move": -1,
#     "shoot": -10,
#     "grab": 1000,
#     "die": -1000,
#     "escape": 0
# }

# def rotate_towards(agent: Agent, desired_dir: str):
#     turns_done = 0
#     dir_list = list(DIRECTION.keys())[:4]
#     while agent.direction != desired_dir and turns_done < 4:
#         cur_idx = dir_list.index(agent.direction)
#         des_idx = dir_list.index(desired_dir)
#         if (cur_idx + 1) % 4 == des_idx:
#             agent.turn_right()
#             print(f"Turning right to {agent.direction}")
#         else:
#             agent.turn_left()
#             print(f"Turning left to {agent.direction}")
#         turns_done += 1
#     return turns_done

# def direction_from_delta(di, dj):
#     for d, (mi, mj) in MOVE.items():
#         if (di, dj) == (mi, mj):
#             return d
#     return None

# def hybrid_agent_action_dynamic(agent: Agent, game_map, wumpus_positions, pit_positions):
#     N = len(game_map)
#     visited = set()
#     kb = agent.kb if hasattr(agent, 'kb') else KB(N=N)
#     action_counter = 0
#     wumpus_alive = [True]*len(wumpus_positions)

#     def increment_counter(count=1):
#         nonlocal action_counter, wumpus_positions
#         action_counter += count
#         while action_counter >= 5:
#             wumpus_positions = update_wumpus_position(agent, game_map, wumpus_positions, pit_positions, wumpus_alive)
#             action_counter -= 5
#             # Kiểm tra agent có bị Wumpus ăn
#             for idx, w_pos in enumerate(wumpus_positions):
#                 if wumpus_alive[idx] and agent.position == w_pos:
#                     print(f"Agent killed by Wumpus at {w_pos}!")
#                     agent.alive = False
#                     agent.score += SCORE["die"]
#                     break

#     while True:
#         if not agent.alive:
#             print("Agent died! Game Over.")
#             break

#         agent.perceive()
#         visited.add(agent.position)

#         # Nhặt vàng nếu có
#         grabbed = agent.grab_gold()  
#         if grabbed:
#             print(f"Grabbed gold at {agent.position}!")  # in thông báo luôn
#             if agent.position == (0, 0):
#                 agent.escape()  # cộng điểm escape ngay
#             increment_counter()

#         # Nếu đã nhặt vàng, agent sẽ quay về (0,0)
#         goal = (0, 0) if agent.gold_obtain else None

#         plan_agent = Agent2(
#             position=agent.position,
#             direction=agent.direction,
#             alive=agent.alive,
#             arrow_hit=agent.arrow_hit,
#             gold_obtain=agent.gold_obtain,
#             N=N,
#             kb=deepcopy(agent.kb)
#         )

#         # Kiểm tra bắn Wumpus chỉ khi chưa nhặt vàng
#         if agent.arrow_hit > 0 and not agent.gold_obtain:
#             potential_wumpus = plan_agent.possible_wumpus_in_line()
#             path_states = dijkstra(game_map, plan_agent)
#             if potential_wumpus and (len(potential_wumpus) == 1 or not path_states or len(path_states) < 2):
#                 target_i, target_j = potential_wumpus[0]
#                 print(f"Shooting Wumpus at predicted position ({target_i}, {target_j})")
#                 agent.shoot()
#                 kb.mark_safe(target_i, target_j)
#                 increment_counter()
#                 continue

#         # Tìm đường đi an toàn
#         path_states = dijkstra(game_map, plan_agent)
#         if not path_states or len(path_states) < 2:
#             # Nếu còn mũi tên và chưa nhặt vàng → bắn Wumpus
#             if agent.arrow_hit > 0 and not agent.gold_obtain:
#                 candidate_wumpus = [(i,j) for i in range(N) for j in range(N) if kb.is_possible_wumpus(i,j)]
#                 if candidate_wumpus:
#                     target_i, target_j = candidate_wumpus[0]
#                     print(f"Forced shoot at possible Wumpus ({target_i}, {target_j})")
#                     agent.shoot()
#                     kb.mark_safe(target_i, target_j)
#                     increment_counter()
#                     continue

#             # Nếu có vàng rồi → trở về
#             if agent.gold_obtain:
#                 print("No safe path left, but agent has gold. Returning home.")
#                 break

#             # Nếu không có safe path, chưa nhặt vàng → mạo hiểm 1 ô Stench
#             stench_neighbors = []
#             i, j = agent.position
#             for di, dj in [(0,1),(0,-1),(1,0),(-1,0)]:
#                 ni, nj = i+di, j+dj
#                 if 0 <= ni < N and 0 <= nj < N:
#                     if "S" in game_map[ni][nj]:
#                         stench_neighbors.append((ni,nj))

#             if stench_neighbors:
#                 target_i, target_j = stench_neighbors[0]
#                 print(f"Moving to adjacent Stench at {(target_i, target_j)} and shooting")
#                 di, dj = target_i - i, target_j - j
#                 desired_dir = direction_from_delta(di, dj)
#                 rotate_towards(agent, desired_dir)
#                 agent.move_forward()
#                 increment_counter()
#                 if agent.arrow_hit == 0:
#                     agent.shoot()
#                     increment_counter()
#                 continue

#             print("No safe path and no adjacent Stench! Stopping agent.")
#             break

#         next_state = path_states[1]

#         if next_state.position == agent.position:
#             turns = rotate_towards(agent, next_state.direction)
#             increment_counter(turns)
#         else:
#             di = next_state.position[0] - agent.position[0]
#             dj = next_state.position[1] - agent.position[1]
#             desired_dir = direction_from_delta(di, dj)
#             if desired_dir is None:
#                 break
#             turns = rotate_towards(agent, desired_dir)
#             increment_counter(turns)
#             agent.move_forward()
#             increment_counter()

#         # Nếu đã nhặt vàng và về tới (0,0)
#         if agent.gold_obtain and agent.position == (0, 0):
#             agent.escape()
#             increment_counter()
#             break

#     return {
#         "final_position": agent.position,
#         "score": agent.score,
#         "gold": agent.gold_obtain,
#         "alive": agent.alive
#     }

# from agent.agent import Agent, Agent2, MOVE, DIRECTION
# from search.dijkstra import dijkstra
# from env_simulator.kb import KnowledgeBase as KB
# from module.moving_Wumpus import update_wumpus_position
# from copy import deepcopy

# SCORE = {
#     "move": -1,
#     "shoot": -10,
#     "grab": 1000,
#     "die": -1000,
#     "escape": 0
# }

# def rotate_towards(agent: Agent, desired_dir: str):
#     turns_done = 0
#     dir_list = list(DIRECTION.keys())[:4]
#     while agent.direction != desired_dir and turns_done < 4:
#         cur_idx = dir_list.index(agent.direction)
#         des_idx = dir_list.index(desired_dir)
#         if (cur_idx + 1) % 4 == des_idx:
#             agent.turn_right()
#             print(f"Turning right to {agent.direction}")
#         else:
#             agent.turn_left()
#             print(f"Turning left to {agent.direction}")
#         turns_done += 1
#     return turns_done

# def direction_from_delta(di, dj):
#     for d, (mi, mj) in MOVE.items():
#         if (di, dj) == (mi, mj):
#             return d
#     return None

# def hybrid_agent_action_dynamic(agent: Agent, game_map, wumpus_positions, pit_positions):
#     N = len(game_map)
#     visited = set()
#     kb = agent.kb if hasattr(agent, 'kb') else KB(N=N)
#     action_counter = 0
#     wumpus_alive = [True]*len(wumpus_positions)

#     def increment_counter(count=1):
#         nonlocal action_counter, wumpus_positions
#         action_counter += count
#         while action_counter >= 5:
#             wumpus_positions = update_wumpus_position(agent, game_map, wumpus_positions, pit_positions, wumpus_alive)
#             action_counter -= 5
#             # Kiểm tra agent có bị Wumpus ăn
#             for idx, w_pos in enumerate(wumpus_positions):
#                 if wumpus_alive[idx] and agent.position == w_pos:
#                     print(f"Agent killed by Wumpus at {w_pos}!")
#                     agent.alive = False
#                     agent.score += SCORE["die"]
#                     break

#     while True:
#         if not agent.alive:
#             print("Agent died! Game Over.")
#             break

#         agent.perceive()
#         visited.add(agent.position)

#         # Nhặt vàng nếu có
#         grabbed = agent.grab_gold()  
#         if grabbed:
#             print(f"Grabbed gold at {agent.position}!")
#             if agent.position == (0, 0):
#                 agent.escape()  # cộng điểm escape ngay
#             increment_counter()

#         # Nếu đã nhặt vàng, agent sẽ quay về (0,0)
#         goal = (0, 0) if agent.gold_obtain else None

#         plan_agent = Agent2(
#             position=agent.position,
#             direction=agent.direction,
#             alive=agent.alive,
#             arrow_hit=agent.arrow_hit,
#             gold_obtain=agent.gold_obtain,
#             N=N,
#             kb=deepcopy(agent.kb)
#         )

#         # Kiểm tra bắn Wumpus chỉ khi chưa nhặt vàng
#         if agent.arrow_hit > 0 and not agent.gold_obtain:
#             potential_wumpus = plan_agent.possible_wumpus_in_line()
#             path_states = dijkstra(game_map, plan_agent)
#             if potential_wumpus and (len(potential_wumpus) == 1 or not path_states or len(path_states) < 2):
#                 target_i, target_j = potential_wumpus[0]
#                 print(f"Shooting Wumpus at predicted position ({target_i}, {target_j})")
#                 agent.shoot()
#                 kb.mark_safe(target_i, target_j)
#                 increment_counter()
#                 continue

#         # Tìm đường đi an toàn
#         path_states = dijkstra(game_map, plan_agent)
#         if not path_states or len(path_states) < 2:
#             # --- Không còn đường safe ---
#             # Tìm các ô chưa biết (không chắc safe) lân cận để mạo hiểm
#             candidates = []
#             for i in range(N):
#                 for j in range(N):
#                     if (i,j) not in visited and not kb.is_safe(i,j):
#                         candidates.append((i,j))

#             if candidates:
#                 # Chọn ô gần nhất
#                 candidates.sort(key=lambda x: abs(x[0]-agent.position[0]) + abs(x[1]-agent.position[1]))
#                 target = candidates[0]
#                 ti, tj = target
#                 print(f"No safe path! Moving towards unknown cell {target} to check for Stench.")
#                 # di chuyển từng bước tới target
#                 while agent.position != target:
#                     di = target[0] - agent.position[0]
#                     dj = target[1] - agent.position[1]
#                     if abs(di) > abs(dj):
#                         step_dir = "S" if di>0 else "N"
#                     else:
#                         step_dir = "E" if dj>0 else "W"
#                     turns = rotate_towards(agent, step_dir)
#                     increment_counter(turns)
#                     agent.move_forward()
#                     increment_counter()
#                     agent.perceive()
#                     # Nếu có Stench ngay, dừng và bắn
#                     if any("S" in c for c in game_map[agent.position[0]][agent.position[1]]):
#                         print(f"Encountered Stench at {agent.position}, attempting to shoot Wumpus.")
#                         agent.shoot()
#                         increment_counter()
#                         break
#                 continue
#             else:
#                 if agent.gold_obtain:
#                     print("No safe path left, but agent has gold. Returning home.")
#                 else:
#                     print("No safe path and no adjacent Stench! Stopping agent.")
#             break

#         next_state = path_states[1]

#         if next_state.position == agent.position:
#             turns = rotate_towards(agent, next_state.direction)
#             increment_counter(turns)
#         else:
#             di = next_state.position[0] - agent.position[0]
#             dj = next_state.position[1] - agent.position[1]
#             desired_dir = direction_from_delta(di, dj)
#             if desired_dir is None:
#                 break
#             turns = rotate_towards(agent, desired_dir)
#             increment_counter(turns)
#             agent.move_forward()
#             increment_counter()

#         # Nếu đã nhặt vàng và về tới (0,0)
#         if agent.gold_obtain and agent.position == (0, 0):
#             agent.escape()
#             increment_counter()
#             break

#     return {
#         "final_position": agent.position,
#         "score": agent.score,
#         "gold": agent.gold_obtain,
#         "alive": agent.alive
#     }

from agent.agent import Agent, Agent2, MOVE, DIRECTION
from search.dijkstra import dijkstra
from env_simulator.kb import KnowledgeBase as KB
from module.moving_Wumpus import update_wumpus_position
from copy import deepcopy

SCORE = {
    "move": -1,
    "shoot": -10,
    "grab": 1000,
    "die": -1000,
    "escape": 0
}

def rotate_towards(agent: Agent, desired_dir: str):
    turns_done = 0
    dir_list = list(DIRECTION.keys())[:4]
    while agent.direction != desired_dir and turns_done < 4:
        cur_idx = dir_list.index(agent.direction)
        des_idx = dir_list.index(desired_dir)
        if (cur_idx + 1) % 4 == des_idx:
            agent.turn_right()
        else:
            agent.turn_left()
        turns_done += 1
    return turns_done

def direction_from_delta(di, dj):
    for d, (mi, mj) in MOVE.items():
        if (di, dj) == (mi, mj):
            return d
    return None

def hybrid_agent_action_dynamic(agent: Agent, game_map, wumpus_positions, pit_positions):
    N = len(game_map)
    visited = set()
    kb = agent.kb if hasattr(agent, 'kb') else KB(N=N)
    action_counter = 0
    wumpus_alive = [True]*len(wumpus_positions)

    def increment_counter(count=1):
        nonlocal action_counter, wumpus_positions
        action_counter += count
        while action_counter >= 5:
            wumpus_positions = update_wumpus_position(agent, game_map, wumpus_positions, pit_positions, wumpus_alive)
            action_counter -= 5
            for idx, w_pos in enumerate(wumpus_positions):
                if wumpus_alive[idx] and agent.position == w_pos:
                    print(f"Agent killed by Wumpus at {w_pos}!")
                    agent.alive = False
                    agent.score += SCORE["die"]
                    break

    while agent.alive:
        # --- Perceive environment ---
        agent.perceive()  # KB đã được cập nhật bên trong agent
        visited.add(agent.position)
        i, j = agent.position

        # --- Nhặt vàng nếu có ---
        if not agent.gold_obtain and 'G' in game_map[i][j]:
            grabbed = agent.grab_gold()
            if grabbed:
                print(f"Grabbed gold at {agent.position}!")
                agent.gold_obtain = True
                increment_counter()
                if agent.position == (0, 0):
                    agent.escape()
                    increment_counter()
                    break

        plan_agent = Agent2(
            position=agent.position,
            direction=agent.direction,
            alive=agent.alive,
            arrow_hit=agent.arrow_hit,
            gold_obtain=agent.gold_obtain,
            N=N,
            kb=deepcopy(agent.kb)
        )

        # --- Kiểm tra bắn Wumpus ---
        if agent.arrow_hit == 0 and not agent.gold_obtain:  # Still has arrow and hasn't got gold
            potential_wumpus = plan_agent.possible_wumpus_in_line()
            path_states = dijkstra(game_map, plan_agent)
            if potential_wumpus and (len(potential_wumpus) == 1 or not path_states or len(path_states) < 2):
                target_i, target_j = potential_wumpus[0]
                print(f"Shooting Wumpus at predicted position ({target_i},{target_j})")
                agent.shoot()
                
                # Update wumpus_alive array based on which Wumpuses were killed
                for idx, w_pos in enumerate(wumpus_positions):
                    if wumpus_alive[idx] and 'W' not in game_map[w_pos[0]][w_pos[1]]:
                        wumpus_alive[idx] = False
                        print(f"Wumpus {idx} at {w_pos} marked as dead in wumpus_alive array")
                
                kb.mark_safe(target_i, target_j)
                increment_counter()
                continue

        # --- Tìm đường safe ---
        path_states = dijkstra(game_map, plan_agent)
        if not path_states or len(path_states) < 2:
            # Không còn đường safe
            if agent.arrow_hit == 0 and not agent.gold_obtain:  # Still have arrow and no gold
                # Strategy 1: First try to find cells with stench that agent has already perceived
                stench_cells = []
                for x in range(N):
                    for y in range(N):
                        if (x, y) not in visited and kb.is_premise_true(f"S({x},{y})"):
                            stench_cells.append((x, y))
                
                print(f"Strategy 1 - Known stench cells not visited: {stench_cells}")
                
                # Strategy 2: If no known stench cells, look for unknown cells adjacent to visited cells
                # These might be stench cells worth exploring
                if not stench_cells:
                    unknown_adjacent_cells = []
                    for vx, vy in visited:
                        for dx, dy in [(0,1), (0,-1), (1,0), (-1,0)]:
                            nx, ny = vx + dx, vy + dy
                            if (0 <= nx < N and 0 <= ny < N and 
                                (nx, ny) not in visited and 
                                not kb.is_premise_true(f"P({nx},{ny})") and  # Not a known pit
                                not kb.is_premise_true(f"W({nx},{ny})")):    # Not a known Wumpus
                                unknown_adjacent_cells.append((nx, ny))
                    
                    # Remove duplicates and sort by distance
                    unknown_adjacent_cells = list(set(unknown_adjacent_cells))
                    unknown_adjacent_cells.sort(key=lambda c: abs(c[0]-i)+abs(c[1]-j))
                    stench_cells = unknown_adjacent_cells[:5]  # Limit to 5 closest cells
                    print(f"Strategy 2 - Unknown adjacent cells: {stench_cells}")
                
                # Strategy 3: If still no candidates, use KB possible wumpus cells
                if not stench_cells:
                    stench_cells = [(x, y) for x in range(N) for y in range(N)
                                    if kb.is_possible_wumpus(x, y) and (x, y) not in visited]
                    print(f"Strategy 3 - KB possible wumpus cells: {stench_cells}")
                
                if stench_cells:
                    # Sort by distance from agent
                    stench_cells.sort(key=lambda c: abs(c[0]-i)+abs(c[1]-j))
                    
                    # Try each stench cell until we find one we can reach safely
                    target_found = False
                    for target in stench_cells:
                        print(f"No safe path! Attempting to reach stench cell {target} to shoot Wumpus.")
                        
                        # Try to move step by step towards this stench cell
                        attempts = 0
                        max_attempts = 10  # Prevent infinite loops
                        
                        while agent.position != target and agent.alive and attempts < max_attempts:
                            ci, cj = agent.position
                            ti, tj = target
                            di = ti - ci
                            dj = tj - cj
                            
                            # Choose direction based on largest distance component
                            if abs(di) > abs(dj):
                                step_dir = "S" if di > 0 else "N"
                            else:
                                step_dir = "E" if dj > 0 else "W"
                            
                            turns = rotate_towards(agent, step_dir)
                            increment_counter(turns)
                            
                            # Check if agent is still alive after turning
                            if not agent.alive:
                                break
                            
                            # Check if we can move forward safely - avoid pits and known dangers
                            next_pos = (agent.position[0] + MOVE[step_dir][0], 
                                       agent.position[1] + MOVE[step_dir][1])
                            if (0 <= next_pos[0] < N and 0 <= next_pos[1] < N):
                                # Only avoid cells with confirmed dangers (pits or Wumpuses)
                                if kb.is_premise_true(f"P({next_pos[0]},{next_pos[1]})"):
                                    print(f"Cannot move to {next_pos} - pit known from KB! Trying different stench cell.")
                                    break  # Try a different stench cell
                                elif kb.is_premise_true(f"W({next_pos[0]},{next_pos[1]})"):
                                    print(f"Cannot move to {next_pos} - Wumpus known from KB! Trying different stench cell.")
                                    break
                                # For exploration, proceed to unknown cells (they might have stench to investigate)
                                
                                agent.move_forward()
                                increment_counter()
                                
                                # Check if agent died during the move
                                if not agent.alive:
                                    print(f"Agent died while moving to {agent.position}! Stopping exploration.")
                                    break
                                    
                                agent.perceive()
                                
                                # If we reached the target or found stench, or are adjacent to target, try shooting
                                if (agent.position == target or
                                    kb.is_premise_true(f"S({agent.position[0]},{agent.position[1]})") or 
                                    abs(agent.position[0] - target[0]) + abs(agent.position[1] - target[1]) <= 1):
                                    
                                    print(f"Near stench at {agent.position}, attempting to shoot towards Wumpus.")
                                    
                                    # When at a stench cell, the agent should reason that Wumpuses are nearby
                                    # Try to face towards the most likely Wumpus direction
                                    best_shot_dir = None
                                    max_wumpus_potential = 0
                                    best_score = 0
                                    
                                    for shot_dir in ["N", "S", "E", "W"]:
                                        direction_score = 0
                                        
                                        # Create temporary Agent2 for checking wumpus line
                                        temp_agent = Agent2(
                                            position=agent.position,
                                            direction=shot_dir,
                                            alive=agent.alive,
                                            arrow_hit=agent.arrow_hit,
                                            gold_obtain=agent.gold_obtain,
                                            N=N,
                                            kb=deepcopy(agent.kb)
                                        )
                                        wumpus_line = temp_agent.possible_wumpus_in_line()
                                        
                                        # Score based on KB possible wumpus
                                        kb_score = len(wumpus_line) * 10
                                        
                                        # Score based on stench pattern analysis
                                        mi, mj = MOVE[shot_dir]
                                        i, j = agent.position
                                        stench_score = 0
                                        
                                        # When at a stench cell, give bonus for shooting towards cells that might have Wumpuses
                                        # Check cells in the shooting direction
                                        for distance in range(1, 4):  # Check up to 3 cells ahead
                                            check_i = i + mi * distance
                                            check_j = j + mj * distance
                                            
                                            if 0 <= check_i < N and 0 <= check_j < N:
                                                # If we know there's a stench there, likely has Wumpus nearby
                                                if kb.is_premise_true(f"S({check_i},{check_j})"):
                                                    stench_score += (4 - distance) * 5  # Closer stench = higher score
                                                # If we visited and no stench, less likely  
                                                elif kb.is_premise_true(f"~S({check_i},{check_j})"):
                                                    stench_score -= 2
                                                # If we haven't visited this cell, it could be a Wumpus
                                                elif (check_i, check_j) not in visited:
                                                    stench_score += 2  # Unknown cells might have Wumpus
                                        
                                        # If we're at a stench cell and have no other info, 
                                        # give slight preference to shooting towards center or corners where Wumpuses are more likely
                                        if kb_score == 0 and stench_score <= 2:
                                            center_x, center_y = N//2, N//2
                                            target_i = i + mi
                                            target_j = j + mj
                                            if 0 <= target_i < N and 0 <= target_j < N:
                                                # Prefer directions that go towards unexplored areas
                                                distance_to_center = abs(target_i - center_x) + abs(target_j - center_y)
                                                stench_score += max(1, 3 - distance_to_center)
                                        
                                        direction_score = kb_score + stench_score
                                        
                                        # Debug output
                                        print(f"Direction {shot_dir}: KB_score={kb_score}, stench_score={stench_score}, total={direction_score}")
                                        
                                        if direction_score > best_score or (direction_score == best_score and len(wumpus_line) > max_wumpus_potential):
                                            best_score = direction_score
                                            max_wumpus_potential = len(wumpus_line)
                                            best_shot_dir = shot_dir
                                    
                                    # Face the best direction if found, otherwise pick a reasonable default
                                    if best_shot_dir and best_score > 0:
                                        turns = rotate_towards(agent, best_shot_dir)
                                        increment_counter(turns)
                                        # Check if agent is still alive after turning
                                        if not agent.alive:
                                            break
                                        print(f"Aiming towards {best_shot_dir} direction (score: {best_score}, KB wumpus: {max_wumpus_potential})")
                                    else:
                                        # If no clear direction, try to shoot towards the most promising quadrant
                                        # Priority order: center, then away from edges
                                        fallback_dirs = ["N", "S", "E", "W"]
                                        for fallback_dir in fallback_dirs:
                                            mi, mj = MOVE[fallback_dir]
                                            target_i = agent.position[0] + mi
                                            target_j = agent.position[1] + mj
                                            if (0 <= target_i < N and 0 <= target_j < N and 
                                                not kb.is_premise_true(f"P({target_i},{target_j})")):
                                                best_shot_dir = fallback_dir
                                                break
                                        
                                        if best_shot_dir:
                                            turns = rotate_towards(agent, best_shot_dir)
                                            increment_counter(turns)
                                            print(f"Using fallback direction {best_shot_dir} for shooting")
                                        else:
                                            print("No clear Wumpus target found, shooting in current direction")
                                    
                                    agent.shoot()
                                    increment_counter()
                                    
                                    # Update wumpus_alive array based on which Wumpuses were killed
                                    for idx, w_pos in enumerate(wumpus_positions):
                                        if wumpus_alive[idx] and 'W' not in game_map[w_pos[0]][w_pos[1]]:
                                            wumpus_alive[idx] = False
                                            print(f"Wumpus {idx} at {w_pos} marked as dead in wumpus_alive array")
                                    
                                    target_found = True
                                    break
                            else:
                                break  # Can't move further, try next stench cell
                            
                            attempts += 1
                        
                        # If we successfully shot or agent died, exit the stench cell loop
                        if target_found or not agent.alive or agent.arrow_hit != 0:
                            break
                    
                    # Check if agent died during the stench exploration
                    if not agent.alive:
                        break  # Exit the main game loop
                    
                    continue
            
            # If arrow has been used (arrow_hit != 0) or other conditions
            if agent.arrow_hit != 0:
                print("Arrow has been used and no safe path found. Stopping exploration.")
                if agent.gold_obtain:
                    print("Agent has gold but no safe path to return home.")
                else:
                    print("Agent has no arrow left and no safe path to continue exploration.")
                break
            elif agent.gold_obtain:
                # Agent has gold but no safe path - should still try to shoot if has arrow
                print("Agent has gold but no safe path found. Attempting to shoot to clear path home.")
                
                # Strategy 1: Find cells with stench that agent has already perceived
                stench_cells = []
                for x in range(N):
                    for y in range(N):
                        if (x, y) not in visited and kb.is_premise_true(f"S({x},{y})"):
                            stench_cells.append((x, y))
                
                # Strategy 2: If no known stench cells, explore unknown adjacent cells
                if not stench_cells:
                    unknown_adjacent_cells = []
                    for vx, vy in visited:
                        for dx, dy in [(0,1), (0,-1), (1,0), (-1,0)]:
                            nx, ny = vx + dx, vy + dy
                            if (0 <= nx < N and 0 <= ny < N and 
                                (nx, ny) not in visited and 
                                not kb.is_premise_true(f"P({nx},{ny})") and  # Not a known pit
                                not kb.is_premise_true(f"W({nx},{ny})")):    # Not a known Wumpus
                                unknown_adjacent_cells.append((nx, ny))
                    
                    # Remove duplicates and sort by distance
                    unknown_adjacent_cells = list(set(unknown_adjacent_cells))
                    unknown_adjacent_cells.sort(key=lambda c: abs(c[0]-i)+abs(c[1]-j))
                    stench_cells = unknown_adjacent_cells[:3]  # Limit to 3 closest for return journey
                
                # Strategy 3: Fall back to KB possible wumpus cells
                if not stench_cells:
                    stench_cells = [(x, y) for x in range(N) for y in range(N)
                                    if kb.is_possible_wumpus(x, y) and (x, y) not in visited]
                
                if stench_cells:
                    # Sort by distance from agent
                    stench_cells.sort(key=lambda c: abs(c[0]-i)+abs(c[1]-j))
                    target = stench_cells[0]
                    print(f"Moving towards stench cell {target} to shoot Wumpus and clear return path.")
                    
                    # Move step by step towards the stench cell
                    while agent.position != target and agent.alive:
                        ci, cj = agent.position
                        ti, tj = target
                        di = ti - ci
                        dj = tj - cj
                        
                        # Choose direction based on largest distance component
                        if abs(di) > abs(dj):
                            step_dir = "S" if di > 0 else "N"
                        else:
                            step_dir = "E" if dj > 0 else "W"
                        
                        turns = rotate_towards(agent, step_dir)
                        increment_counter(turns)
                        
                        # Check if agent is still alive after turning
                        if not agent.alive:
                            break
                        
                            # Check if we can move forward safely - avoid pits and known dangers
                            next_pos = (agent.position[0] + MOVE[step_dir][0], 
                                       agent.position[1] + MOVE[step_dir][1])
                            if (0 <= next_pos[0] < N and 0 <= next_pos[1] < N):
                                # Check if the next position is safe based on agent's knowledge
                                if not kb.is_safe(next_pos[0], next_pos[1]):
                                    # Check if agent knows there's a pit there
                                    if kb.is_premise_true(f"P({next_pos[0]},{next_pos[1]})"):
                                        print(f"Cannot move to {next_pos} - pit known from KB! Finding alternative route.")
                                        break  # Stop this direction, try to find another path
                                    elif kb.is_premise_true(f"W({next_pos[0]},{next_pos[1]})"):
                                        print(f"Cannot move to {next_pos} - Wumpus known from KB! Finding alternative route.")
                                        break
                                    # If not confirmed safe and not a stench cell, avoid it
                                    elif not kb.is_premise_true(f"S({next_pos[0]},{next_pos[1]})"):
                                        print(f"Avoiding potentially unsafe cell {next_pos} - not confirmed safe")
                                        break
                                
                                agent.move_forward()
                                increment_counter()
                            
                            # Check if agent died during the move
                            if not agent.alive:
                                print(f"Agent died while moving to {agent.position}! Game over.")
                                break
                                
                            agent.perceive()
                            
                            # If we reached the target or found stench, or are adjacent to target, try shooting
                            if (agent.position == target or
                                kb.is_premise_true(f"S({agent.position[0]},{agent.position[1]})") or 
                                abs(agent.position[0] - target[0]) + abs(agent.position[1] - target[1]) <= 1):
                                
                                print(f"Near stench at {agent.position}, attempting to shoot to clear return path.")
                                
                                # Try to face towards the most likely Wumpus direction
                                best_shot_dir = None
                                max_wumpus_potential = 0
                                
                                for shot_dir in ["N", "S", "E", "W"]:
                                    # Temporarily set direction to check wumpus in line
                                    original_dir = agent.direction
                                    
                                    # Create temporary Agent2 for checking wumpus line
                                    temp_agent = Agent2(
                                        position=agent.position,
                                        direction=shot_dir,
                                        alive=agent.alive,
                                        arrow_hit=agent.arrow_hit,
                                        gold_obtain=agent.gold_obtain,
                                        N=N,
                                        kb=deepcopy(agent.kb)
                                    )
                                    wumpus_line = temp_agent.possible_wumpus_in_line()
                                    
                                    if len(wumpus_line) > max_wumpus_potential:
                                        max_wumpus_potential = len(wumpus_line)
                                        best_shot_dir = shot_dir
                                
                                # Face the best direction if found
                                if best_shot_dir:
                                    turns = rotate_towards(agent, best_shot_dir)
                                    increment_counter(turns)
                                    # Check if agent is still alive after turning
                                    if not agent.alive:
                                        break
                                    print(f"Aiming towards {best_shot_dir} direction to clear return path")
                                else:
                                    print("No clear Wumpus target found, shooting in current direction")
                                
                                agent.shoot()
                                increment_counter()
                                
                                # Update wumpus_alive array based on which Wumpuses were killed
                                for idx, w_pos in enumerate(wumpus_positions):
                                    if wumpus_alive[idx] and 'W' not in game_map[w_pos[0]][w_pos[1]]:
                                        wumpus_alive[idx] = False
                                        print(f"Wumpus {idx} at {w_pos} marked as dead in wumpus_alive array")
                                
                                break
                        else:
                            break  # Can't move further
                    
                    # Check if agent died during the stench exploration
                    if not agent.alive:
                        break  # Exit the main game loop
                    
                    continue
                else:
                    print("No safe path left and no stench to clear. Agent with gold giving up return.")
                    break
            else:
                print("No safe path and no Stench to investigate! Stopping agent.")
                break

        # --- Di chuyển theo đường safe ---
        next_state = path_states[1]
        if next_state.position == agent.position:
            turns = rotate_towards(agent, next_state.direction)
            increment_counter(turns)
        else:
            di = next_state.position[0] - agent.position[0]
            dj = next_state.position[1] - agent.position[1]
            desired_dir = direction_from_delta(di, dj)
            if desired_dir is None:
                break
            turns = rotate_towards(agent, desired_dir)
            increment_counter(turns)
            agent.move_forward()
            increment_counter()

        # --- Nếu đã nhặt vàng và về tới (0,0) ---
        if agent.gold_obtain and agent.position == (0,0):
            agent.escape()
            increment_counter()
            break

    return {
        "final_position": agent.position,
        "score": agent.score,
        "gold": agent.gold_obtain,
        "alive": agent.alive
    }
