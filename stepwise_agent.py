"""
Modified hybrid agent for step-by-step UI visualization
"""
from agent.agent import Agent, Agent2, MOVE, DIRECTION
from search.dijkstra import dijkstra
from env_simulator.kb import KnowledgeBase as KB
from module.moving_Wumpus import update_wumpus_position
from copy import deepcopy

class StepByStepHybridAgent:
    def __init__(self, agent, game_map, wumpus_positions, pit_positions):
        self.agent = agent
        self.game_map = game_map
        self.wumpus_positions = wumpus_positions
        self.pit_positions = pit_positions
        self.wumpus_alive = [True] * len(wumpus_positions)
        self.visited = {(0, 0)}
        self.kb = agent.kb
        self.N = agent.N
        self.action_count = 0
        self.max_actions = 200
        self.current_state = "exploring"
        self.target_position = None
        
    def get_current_state(self):
        """Return current game state for visualization"""
        return {
            'position': self.agent.position,
            'direction': self.agent.direction,
            'score': self.agent.score,
            'alive': self.agent.alive,
            'gold': self.agent.gold_obtain,
            'arrow': self.agent.arrow_hit,
            'map': [row[:] for row in self.game_map],
            'visited': list(self.visited),
            'wumpus_positions': self.wumpus_positions[:],
            'wumpus_alive': self.wumpus_alive[:],
            'action_count': self.action_count,
            'state': self.current_state,
            'target': self.target_position
        }
    
    def step(self):
        """Execute one step of the agent logic"""
        if not self.agent.alive or self.action_count >= self.max_actions:
            return False, "Game Over"
        
        # Update visited locations
        self.visited.add(self.agent.position)
        
        # Process percepts - base Agent class perceive() takes no arguments
        self.agent.perceive()
        
        # Check if agent died from percepts
        if not self.agent.alive:
            return False, "Agent died"
        
        # Update knowledge base
        self.update_knowledge_base()
        
        # Move Wumpus every 5 actions
        if self.action_count > 0 and self.action_count % 5 == 0:
            old_wumpus_positions = self.wumpus_positions[:]
            self.wumpus_positions = update_wumpus_position(
                self.agent, self.game_map, self.wumpus_positions, 
                self.pit_positions, self.wumpus_alive
            )
            
            # Update knowledge base after Wumpus movement
            # Clear outdated negative Wumpus facts that might conflict with new positions
            for old_pos, new_pos in zip(old_wumpus_positions, self.wumpus_positions):
                if old_pos != new_pos and self.wumpus_alive[old_wumpus_positions.index(old_pos)]:
                    # Remove conflicting negative facts about new Wumpus position
                    conflicting_facts = [
                        f"~W({new_pos[0]}, {new_pos[1]})",
                        f"Safe({new_pos[0]}, {new_pos[1]})"
                    ]
                    for fact in conflicting_facts:
                        if fact in self.agent.kb.facts:
                            self.agent.kb.facts.remove(fact)
                    
                    print(f"Wumpus moved from {old_pos} to {new_pos} - cleared conflicting KB facts")
            
            # Re-perceive the environment to update stench information
            self.agent.perceive()
            self.update_knowledge_base()
            
            # Check if agent was killed by moving Wumpus
            for idx, w_pos in enumerate(self.wumpus_positions):
                if self.wumpus_alive[idx] and self.agent.position == w_pos:
                    print(f"Agent killed by Wumpus at {w_pos}!")
                    self.agent.alive = False
                    return False, f"Killed by Wumpus at {w_pos}"
        
        # Check for gold
        if 'G' in self.game_map[self.agent.position[0]][self.agent.position[1]] and not self.agent.gold_obtain:
            self.agent.grab_gold()
            # Remove gold from the map after grabbing it
            self.game_map[self.agent.position[0]][self.agent.position[1]].remove('G')
            self.current_state = "returning"
            return True, f"Grabbed gold at {self.agent.position}!"
        
        # Check if agent reached home with gold
        if self.agent.gold_obtain and self.agent.position == (0, 0):
            # Add 1000 points for successfully returning home with gold
            self.agent.score += 1000
            self.current_state = "won"
            return False, f"Agent successfully returned home with gold! +1000 points! Final score: {self.agent.score}"
        
        # Create planning agent
        plan_agent = Agent2(
            position=self.agent.position,
            direction=self.agent.direction,
            alive=self.agent.alive,
            arrow_hit=self.agent.arrow_hit,
            gold_obtain=self.agent.gold_obtain,
            N=self.N,
            kb=deepcopy(self.agent.kb)
        )
        
        # Try to shoot if conditions are right
        if self.try_shoot(plan_agent):
            return True, "Agent shot arrow"
        
        # Find safe path
        path_states = dijkstra(self.game_map, plan_agent)
        
        if path_states and len(path_states) >= 2:
            # Move along safe path
            next_state = path_states[1]
            action_msg = self.move_to_state(next_state)
            return True, action_msg
        else:
            # No safe path - try exploration, then stench seeking, then desperate shots
            if self.agent.arrow_hit == 0:
                # First try safe exploration
                if self.try_safe_exploration():
                    return True, "Exploring safely to gather more information"
                
                # Handle stench seeking state specifically
                if self.current_state == "seeking_stench" and hasattr(self, 'target_position'):
                    # Check if we've reached the stench target or are close enough to shoot
                    current_pos = self.agent.position
                    target_pos = self.target_position
                    
                    # If we're at the stench target OR stuck trying to reach it, try shooting
                    if (current_pos == target_pos or 
                        abs(current_pos[0] - target_pos[0]) + abs(current_pos[1] - target_pos[1]) <= 1):
                        
                        # Try to shoot from current position
                        if self.try_desperate_shot(plan_agent):
                            self.current_state = "exploring"  # Reset state after shooting
                            return True, "Shot at Wumpus from stench position!"
                        else:
                            # Try to move towards stench target if we haven't reached it
                            action_msg = self.move_towards_target(target_pos)
                            if "Cannot move - confirmed danger detected" in action_msg:
                                # Stuck - try shooting anyway
                                if self.try_desperate_shot(plan_agent):
                                    self.current_state = "exploring"
                                    return True, "Stuck at stench - shot anyway!"
                                else:
                                    self.current_state = "stuck"
                                    return False, "Cannot move towards stench and cannot shoot"
                            return True, action_msg
                    else:
                        # Still moving towards stench target
                        action_msg = self.move_towards_target(target_pos)
                        return True, action_msg
                
                # Then try to reach stench cells to shoot
                stench_target = self.find_stench_target()
                if stench_target:
                    self.target_position = stench_target
                    self.current_state = "seeking_stench"
                    action_msg = self.move_towards_target(stench_target)
                    return True, action_msg
                
                # If no stench target, try desperate shot
                if self.try_desperate_shot(plan_agent):
                    return True, "Desperate shot - no safe path available!"
            
            # No options left
            self.current_state = "stuck"
            return False, "No safe moves available and no shooting options"
    
    def update_knowledge_base(self):
        """Update knowledge base with current information"""
        pos = self.agent.position
        # Mark current position as safe
        self.kb.add_fact(f"~P({pos[0]}, {pos[1]})")
        self.kb.add_fact(f"~W({pos[0]}, {pos[1]})")
        self.kb.forward_chain()
    
    def try_shoot(self, plan_agent):
        """Try to shoot if conditions are met with cost-benefit analysis"""
        if self.agent.arrow_hit != 0 or self.agent.gold_obtain:
            return False
        
        potential_wumpus = plan_agent.possible_wumpus_in_line()
        if potential_wumpus:
            # Simple cost-benefit analysis
            current_path = dijkstra(self.game_map, plan_agent)
            
            # Create temp agent assuming Wumpus is shot
            temp_agent = Agent2(
                position=self.agent.position,
                direction=self.agent.direction,
                alive=self.agent.alive,
                arrow_hit=1,
                gold_obtain=self.agent.gold_obtain,
                N=self.N,
                kb=deepcopy(self.agent.kb)
            )
            
            # Mark potential Wumpus as dead in temp KB
            for wx, wy in potential_wumpus:
                temp_agent.kb.add_fact(f"~W({wx}, {wy})")
                temp_agent.kb.add_fact(f"Safe({wx}, {wy})")
            temp_agent.kb.forward_chain()
            
            path_after_shot = dijkstra(self.game_map, temp_agent)
            
            # Compare path lengths (simple heuristic)
            current_cost = len(current_path) if current_path else float('inf')
            shot_cost = len(path_after_shot) + 1 if path_after_shot else float('inf')  # +1 for shooting
            
            if shot_cost < current_cost:
                target_i, target_j = potential_wumpus[0]
                print(f"Shooting Wumpus at predicted position ({target_i},{target_j}) - beneficial (cost {shot_cost} vs {current_cost})")
                self.agent.shoot()
                
                # Update wumpus_alive array
                for idx, w_pos in enumerate(self.wumpus_positions):
                    if self.wumpus_alive[idx] and 'W' not in self.game_map[w_pos[0]][w_pos[1]]:
                        self.wumpus_alive[idx] = False
                        print(f"Wumpus {idx} at {w_pos} marked as dead")
                
                self.kb.remove_wumpus(target_i, target_j)
                self.action_count += 1
                return True
        
        return False
    
    def find_stench_target(self):
        """Find a stench cell to target for shooting"""
        # Look for known stench cells
        for x in range(self.N):
            for y in range(self.N):
                if ((x, y) not in self.visited and 
                    self.kb.is_premise_true(f"S({x},{y})")):
                    return (x, y)
        
        # Look for unknown adjacent cells
        for vx, vy in self.visited:
            for dx, dy in [(0,1), (0,-1), (1,0), (-1,0)]:
                nx, ny = vx + dx, vy + dy
                if (0 <= nx < self.N and 0 <= ny < self.N and 
                    (nx, ny) not in self.visited and 
                    not self.kb.is_premise_true(f"P({nx},{ny})") and
                    not self.kb.is_premise_true(f"W({nx},{ny})")):
                    return (nx, ny)
        
        return None
    
    def try_safe_exploration(self):
        """Try to explore adjacent unknown cells that are likely safe"""
        current_pos = self.agent.position
        
        # Look for adjacent unvisited cells that might be safe
        for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            nx, ny = current_pos[0] + dx, current_pos[1] + dy
            
            if (0 <= nx < self.N and 0 <= ny < self.N and 
                (nx, ny) not in self.visited):
                
                # Check knowledge base for safety information
                safe_status = self.kb.is_premise_true(f"Safe({nx}, {ny})")
                pit_status = self.kb.is_premise_true(f"P({nx}, {ny})")
                wumpus_status = self.kb.is_premise_true(f"W({nx}, {ny})")
                
                # Move if confirmed safe OR unknown with no danger indicators
                if safe_status is True:
                    # Definitely safe - move there
                    desired_dir = self.direction_from_delta(dx, dy)
                    if desired_dir:
                        turns = self.rotate_towards(desired_dir)
                        self.action_count += turns
                        self.agent.move_forward()
                        self.action_count += 1
                        return True
                elif (safe_status is None and pit_status is not True and wumpus_status is not True):
                    # Unknown but no confirmed dangers - check for risk indicators
                    is_risky = False
                    for vi, vj in self.visited:
                        if abs(vi - nx) + abs(vj - ny) == 1:  # Adjacent to visited cell
                            # Check if visited cell has danger indicators
                            if (self.kb.is_premise_true(f"B({vi}, {vj})") is True or
                                self.kb.is_premise_true(f"S({vi}, {vj})") is True):
                                is_risky = True
                                break
                    
                    if not is_risky:
                        # Seems reasonably safe to explore
                        desired_dir = self.direction_from_delta(dx, dy)
                        if desired_dir:
                            turns = self.rotate_towards(desired_dir)
                            self.action_count += turns
                            self.agent.move_forward() 
                            self.action_count += 1
                            return True
        
        return False
    
    def try_desperate_shot(self, plan_agent):
        """Try shooting as a last resort when no safe path exists"""
        if self.agent.arrow_hit != 0:
            return False
        
        # Look for any potential Wumpus in shooting range
        potential_wumpus = plan_agent.possible_wumpus_in_line()
        
        if potential_wumpus:
            print(f"Desperate situation: Shooting at potential Wumpus {potential_wumpus}")
            self.agent.shoot()
            
            # Update wumpus tracking if shot kills a wumpus
            target_i, target_j = potential_wumpus[0]  # First target
            for idx, w_pos in enumerate(self.wumpus_positions):
                if w_pos == (target_i, target_j):
                    if self.wumpus_alive[idx]:
                        self.wumpus_alive[idx] = False
                        print(f"Wumpus {idx} at {w_pos} marked as dead")
            
            self.kb.remove_wumpus(target_i, target_j)
            self.action_count += 1
            return True
        
        return False
    
    def move_to_state(self, target_state):
        """Move agent towards target state"""
        if target_state.position == self.agent.position:
            # Just turn
            turns = self.rotate_towards(target_state.direction)
            self.action_count += turns
            return f"Turned to face {target_state.direction}"
        else:
            # Move forward after turning if needed
            di = target_state.position[0] - self.agent.position[0]
            dj = target_state.position[1] - self.agent.position[1]
            desired_dir = self.direction_from_delta(di, dj)
            
            if desired_dir:
                turns = self.rotate_towards(desired_dir)
                self.action_count += turns
                self.agent.move_forward()
                self.action_count += 1
                return f"Moved to {self.agent.position}"
            
        return "Could not move"
    
    def move_towards_target(self, target):
        """Move one step towards target position using safer pathfinding"""
        ci, cj = self.agent.position
        ti, tj = target
        
        # Try to find a safe path to the target first
        from agent.agent import Agent2
        temp_agent = Agent2(
            position=self.agent.position,
            direction=self.agent.direction,
            alive=self.agent.alive,
            arrow_hit=self.agent.arrow_hit,
            gold_obtain=self.agent.gold_obtain,
            N=self.N,
            kb=deepcopy(self.agent.kb)
        )
        
        # Temporarily mark target as safe to allow pathfinding to it
        temp_agent.kb.add_fact(f"~P({ti}, {tj})")
        temp_agent.kb.add_fact(f"~W({ti}, {tj})")
        temp_agent.kb.add_fact(f"Safe({ti}, {tj})")
        temp_agent.kb.forward_chain()
        
        # Try to find safer path
        from search.dijkstra import dijkstra
        path_to_target = dijkstra(self.game_map, temp_agent)
        
        if path_to_target and len(path_to_target) >= 2:
            # Use safe path if available
            next_state = path_to_target[1]
            action_msg = self.move_to_state(next_state)
            return f"Moving safely towards target {target}: {action_msg}"
        
        # Fallback to direct movement with better safety checks
        di = ti - ci
        dj = tj - cj
        
        # Choose direction based on largest distance component
        if abs(di) > abs(dj):
            step_dir = "S" if di > 0 else "N"
        else:
            step_dir = "E" if dj > 0 else "W"
        
        # Check if we can move safely
        next_pos = (ci + MOVE[step_dir][0], cj + MOVE[step_dir][1])
        if (0 <= next_pos[0] < self.N and 0 <= next_pos[1] < self.N):
            # Avoid confirmed dangers AND unknown risky cells
            if (self.kb.is_premise_true(f"P({next_pos[0]}, {next_pos[1]})") is True or
                self.kb.is_premise_true(f"W({next_pos[0]}, {next_pos[1]})") is True):
                return "Cannot move - confirmed danger detected"
            
            # Also avoid cells that might be dangerous (unknown + adjacent to danger indicators)
            if (next_pos not in self.visited and 
                self.kb.is_premise_true(f"Safe({next_pos[0]}, {next_pos[1]})") is not True):
                # Check if this unknown cell is adjacent to any breeze/stench
                for vi, vj in self.visited:
                    if abs(vi - next_pos[0]) + abs(vj - next_pos[1]) == 1:  # Adjacent
                        if (self.kb.is_premise_true(f"B({vi}, {vj})") is True or
                            self.kb.is_premise_true(f"S({vi}, {vj})") is True):
                            return "Cannot move - risky unknown cell near danger indicators"
        
        # Turn and move
        turns = self.rotate_towards(step_dir)
        self.action_count += turns
        self.agent.move_forward()
        self.action_count += 1
        
        return f"Moved towards target {target}"
    
    def rotate_towards(self, desired_dir):
        """Rotate agent towards desired direction"""
        turns_done = 0
        dir_list = ["E", "S", "W", "N"]
        
        while self.agent.direction != desired_dir and turns_done < 4:
            cur_idx = dir_list.index(self.agent.direction)
            des_idx = dir_list.index(desired_dir)
            
            if (cur_idx + 1) % 4 == des_idx:
                self.agent.turn_right()
                print(f"Turning right to {self.agent.direction}")
            else:
                self.agent.turn_left()
                print(f"Turning left to {self.agent.direction}")
            
            turns_done += 1
        
        return turns_done
    
    def direction_from_delta(self, di, dj):
        """Convert movement delta to direction"""
        if di == 1 and dj == 0:
            return "S"
        elif di == -1 and dj == 0:
            return "N"
        elif di == 0 and dj == 1:
            return "E"
        elif di == 0 and dj == -1:
            return "W"
        return None
    
    def get_final_result(self):
        """Get final game result"""
        return {
            'final_position': self.agent.position,
            'score': self.agent.score,
            'gold': self.agent.gold_obtain,
            'alive': self.agent.alive,
            'actions': self.action_count
        }
