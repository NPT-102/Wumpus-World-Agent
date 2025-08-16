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

"""
Hybrid Agent Action Dynamic for Wumpus World - like hybrid agent but Wumpus moves every 5 actions
"""
import random
from agent.hybrid_agent import HybridAgent
from agent.agent import MOVE, DIRECTION

class HybridAgentDynamic(HybridAgent):
    def __init__(self, base_agent):
        super().__init__(base_agent)
        self.wumpus_move_counter = 0
        self.wumpus_move_interval = 5
        self.agent_type_name = 'Hybrid Dynamic'
        
    def step(self):
        """Execute one hybrid step with dynamic Wumpus movement"""
        if not self.agent.alive or self.action_count >= self.max_actions:
            return False, "Game Over"
        
        # Check if Wumpus should move (every 5 actions)
        if self.wumpus_move_counter >= self.wumpus_move_interval:
            self._trigger_wumpus_movement()
            self.wumpus_move_counter = 0
            
            # Check if agent got eaten by moved Wumpus
            percepts = self.agent.environment.get_percept(self.agent.position)
            if self._check_wumpus_danger():
                self.agent.alive = False
                self.agent.score -= 1000
                return False, f"Agent was eaten by moving Wumpus at {self.agent.position}!"
        
        # Execute normal hybrid step
        continue_game, message = super().step()
        
        # Increment movement counter for Wumpus
        self.wumpus_move_counter += 1
        
        return continue_game, message
    
    def _trigger_wumpus_movement(self):
        """Trigger Wumpus movement in environment"""
        # Get current percepts to understand environment state
        current_percepts = self.agent.environment.get_percept(self.agent.position)
        
        # Call environment method to move Wumpus
        if hasattr(self.agent.environment, 'move_wumpus'):
            self.agent.environment.move_wumpus()
            
            # Clear some of our knowledge since Wumpus moved
            self._update_knowledge_after_wumpus_move()
        
        print(f"Wumpus moved after {self.wumpus_move_interval} actions!")
    
    def _update_knowledge_after_wumpus_move(self):
        """Update agent's knowledge after Wumpus movement"""
        # Wumpus movement makes some of our stench-based knowledge outdated
        # Clear dangerous positions that were based on stench (but keep safe ones)
        new_dangerous = set()
        
        # Keep positions that are dangerous due to pits (breeze evidence)
        # Remove positions that were dangerous only due to Wumpus stench
        for pos in self.known_dangerous.copy():
            # If we have evidence of pit at this position, keep it dangerous
            # Otherwise, remove it since Wumpus might have moved
            percepts_at_pos = self.agent.environment.get_percept(pos) if hasattr(self.agent.environment, 'get_percept') else []
            if "Breeze" in str(percepts_at_pos):
                new_dangerous.add(pos)
        
        self.known_dangerous = new_dangerous
        
        # Update our safe positions based on current knowledge
        # Positions we've visited are still safe (no pit there)
        self.known_safe = self.visited_positions.copy()
    
    def _check_wumpus_danger(self):
        """Check if agent is in immediate danger from Wumpus"""
        percepts = self.agent.environment.get_percept(self.agent.position)
        
        # If we sense stench, there might be danger
        # But in dynamic version, agent might be surprised by moved Wumpus
        return False  # Environment will handle Wumpus encounters directly
    
    def _choose_hybrid_action(self, percepts):
        """Choose action with hybrid logic - accounting for dynamic Wumpus"""
        # If Wumpus is about to move soon, be more cautious
        if self.wumpus_move_counter >= self.wumpus_move_interval - 1:
            if random.random() < 0.8:  # 80% cautious decisions when Wumpus about to move
                return self._cautious_action(percepts)
            else:
                return self._random_action()
        else:
            # Normal hybrid behavior
            return super()._choose_hybrid_action(percepts)
    
    def _cautious_action(self, percepts):
        """Make a more cautious decision when Wumpus is about to move"""
        current_pos = self.agent.position
        
        # If returning home, prioritize getting home quickly
        if self.returning_home:
            if self._can_move_towards_home():
                return "move_home"
            else:
                return "turn_left" if random.choice([True, False]) else "turn_right"
        
        # If sensing danger and Wumpus about to move, consider shooting
        if ("Stench" in percepts and self.agent.arrow_hit == 0 and 
            random.random() < 0.5):  # 50% chance to shoot when sensing Wumpus before it moves
            return "shoot"
        
        # If in loop, break it quickly
        if self._is_in_loop():
            return "turn_left" if random.choice([True, False]) else "turn_right"
        
        # Try to move to known safe positions
        if self._can_move_to_safe_visited():
            return "move_safe_visited"
        
        # If forward seems safe, move
        if self._is_forward_reasonably_safe():
            return "move_forward"
        
        # Otherwise turn to find safer direction
        return "turn_left" if random.choice([True, False]) else "turn_right"
    
    def _can_move_to_safe_visited(self):
        """Check if can move to a previously visited safe position"""
        move = MOVE[self.agent.direction]
        next_pos = (self.agent.position[0] + move[0], self.agent.position[1] + move[1])
        
        return (self.agent.environment.is_valid_position(next_pos) and
                next_pos in self.visited_positions)  # Previously visited = definitely safe
    
    def _execute_action(self, action):
        """Execute the chosen action with dynamic considerations"""
        if action == "move_safe_visited":
            if self._try_move_to_visited_position():
                return True, f"Moved to previously visited safe position {self.agent.position}"
            else:
                self.agent.turn_right()
                return True, "No safe visited position available, turned right"
        else:
            # Use parent class execution for other actions
            return super()._execute_action(action)
    
    def _try_move_to_visited_position(self):
        """Try to move to a previously visited (safe) position"""
        move = MOVE[self.agent.direction]
        next_pos = (self.agent.position[0] + move[0], self.agent.position[1] + move[1])
        
        if (self.agent.environment.is_valid_position(next_pos) and
            next_pos in self.visited_positions):
            return self.agent.move_forward()
        return False
    
    def get_current_state(self):
        """Get current state for UI display"""
        state = super().get_current_state()
        state['agent_type'] = self.agent_type_name
        state['wumpus_move_counter'] = self.wumpus_move_counter
        state['wumpus_move_interval'] = self.wumpus_move_interval
        state['wumpus_moves_in'] = self.wumpus_move_interval - self.wumpus_move_counter
        return state
