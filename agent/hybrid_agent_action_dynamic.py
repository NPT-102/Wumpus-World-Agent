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
                kb.mark_safe(target_i, target_j)
                increment_counter()
                continue

        # --- Tìm đường safe ---
        path_states = dijkstra(game_map, plan_agent)
        if not path_states or len(path_states) < 2:
            # Không còn đường safe
            if agent.arrow_hit == 0 and not agent.gold_obtain:  # Still have arrow and no gold
                # First, try to find cells with stench directly from the game map
                stench_cells = []
                for x in range(N):
                    for y in range(N):
                        if (x, y) not in visited and 'S' in game_map[x][y]:
                            stench_cells.append((x, y))
                
                # If no direct stench cells, fall back to KB possible wumpus cells
                if not stench_cells:
                    stench_cells = [(x, y) for x in range(N) for y in range(N)
                                    if kb.is_possible_wumpus(x, y) and (x, y) not in visited]
                
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
                                # Check if the next position is safe from pits and known dangers
                                if not kb.is_safe(next_pos[0], next_pos[1]):
                                    # Check if it's a pit specifically
                                    if 'P' in game_map[next_pos[0]][next_pos[1]]:
                                        print(f"Cannot move to {next_pos} - pit detected! Trying different stench cell.")
                                        break  # Try a different stench cell
                                    elif 'W' in game_map[next_pos[0]][next_pos[1]]:
                                        print(f"Cannot move to {next_pos} - Wumpus detected! Trying different stench cell.")
                                        break
                                    # If not confirmed dangerous but not safe either, proceed with caution for stench cells
                                    elif not ('S' in game_map[next_pos[0]][next_pos[1]]):
                                        print(f"Avoiding potentially unsafe cell {next_pos}")
                                        break
                                
                                agent.move_forward()
                                increment_counter()
                                
                                # Check if agent died during the move
                                if not agent.alive:
                                    print(f"Agent died while moving to {agent.position}! Stopping exploration.")
                                    break
                                    
                                agent.perceive()
                                
                                # If we reached a stench cell or adjacent to target, try shooting
                                if ('S' in game_map[agent.position[0]][agent.position[1]] or 
                                    agent.position == target or
                                    abs(agent.position[0] - target[0]) + abs(agent.position[1] - target[1]) <= 1):
                                    
                                    print(f"Near stench at {agent.position}, attempting to shoot towards Wumpus.")
                                    
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
                                        
                                        # Reset agent direction
                                        agent.direction = original_dir
                                    
                                    # Face the best direction if found
                                    if best_shot_dir:
                                        turns = rotate_towards(agent, best_shot_dir)
                                        increment_counter(turns)
                                        # Check if agent is still alive after turning
                                        if not agent.alive:
                                            break
                                        print(f"Aiming towards {best_shot_dir} direction with {max_wumpus_potential} potential Wumpus")
                                    else:
                                        print("No clear Wumpus target found, shooting in current direction")
                                    
                                    agent.shoot()
                                    increment_counter()
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
                # Find stench cells to shoot towards
                stench_cells = []
                for x in range(N):
                    for y in range(N):
                        if (x, y) not in visited and 'S' in game_map[x][y]:
                            stench_cells.append((x, y))
                
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
                            # Check if the next position is safe from pits and known dangers
                            if not kb.is_safe(next_pos[0], next_pos[1]):
                                # Check if it's a pit specifically
                                if 'P' in game_map[next_pos[0]][next_pos[1]]:
                                    print(f"Cannot move to {next_pos} - pit detected! Finding alternative route.")
                                    break  # Stop this direction, try to find another path
                                elif 'W' in game_map[next_pos[0]][next_pos[1]]:
                                    print(f"Cannot move to {next_pos} - Wumpus detected! Finding alternative route.")
                                    break
                                # If not confirmed dangerous but not safe either, proceed with caution for stench cells
                                elif not ('S' in game_map[next_pos[0]][next_pos[1]]):
                                    print(f"Avoiding potentially unsafe cell {next_pos}")
                                    break
                            
                            agent.move_forward()
                            increment_counter()
                            
                            # Check if agent died during the move
                            if not agent.alive:
                                print(f"Agent died while moving to {agent.position}! Game over.")
                                break
                                
                            agent.perceive()
                            
                            # If we reached a stench cell or adjacent to target, try shooting
                            if ('S' in game_map[agent.position[0]][agent.position[1]] or 
                                agent.position == target or
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
