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
            self.wumpus_positions = update_wumpus_position(
                self.agent, self.game_map, self.wumpus_positions, 
                self.pit_positions, self.wumpus_alive
            )
            
            # Check if agent was killed by moving Wumpus
            for idx, w_pos in enumerate(self.wumpus_positions):
                if self.wumpus_alive[idx] and self.agent.position == w_pos:
                    print(f"Agent killed by Wumpus at {w_pos}!")
                    self.agent.alive = False
                    return False, f"Killed by Wumpus at {w_pos}"
        
        # Check for gold
        if 'G' in self.game_map[self.agent.position[0]][self.agent.position[1]] and not self.agent.gold_obtain:
            self.agent.grab_gold()
            self.current_state = "returning"
            return True, f"Grabbed gold at {self.agent.position}!"
        
        # Check if agent reached home with gold
        if self.agent.gold_obtain and self.agent.position == (0, 0):
            self.current_state = "won"
            return False, "Agent successfully returned home with gold!"
        
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
            # No safe path - try to reach stench cells to shoot
            if self.agent.arrow_hit == 0:
                stench_target = self.find_stench_target()
                if stench_target:
                    self.target_position = stench_target
                    self.current_state = "seeking_stench"
                    action_msg = self.move_towards_target(stench_target)
                    return True, action_msg
            
            # No options left
            self.current_state = "stuck"
            return False, "No safe moves available"
    
    def update_knowledge_base(self):
        """Update knowledge base with current information"""
        pos = self.agent.position
        # Mark current position as safe
        self.kb.add_fact(f"~P({pos[0]}, {pos[1]})")
        self.kb.add_fact(f"~W({pos[0]}, {pos[1]})")
        self.kb.forward_chain()
    
    def try_shoot(self, plan_agent):
        """Try to shoot if conditions are met"""
        if self.agent.arrow_hit != 0 or self.agent.gold_obtain:
            return False
        
        potential_wumpus = plan_agent.possible_wumpus_in_line()
        if potential_wumpus:
            target_i, target_j = potential_wumpus[0]
            print(f"Shooting Wumpus at predicted position ({target_i},{target_j})")
            self.agent.shoot()
            
            # Update wumpus_alive array
            for idx, w_pos in enumerate(self.wumpus_positions):
                if self.wumpus_alive[idx] and 'W' not in self.game_map[w_pos[0]][w_pos[1]]:
                    self.wumpus_alive[idx] = False
                    print(f"Wumpus {idx} at {w_pos} marked as dead")
            
            self.kb.mark_safe(target_i, target_j)
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
        """Move one step towards target position"""
        ci, cj = self.agent.position
        ti, tj = target
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
            # Only avoid confirmed dangers
            if (self.kb.is_premise_true(f"P({next_pos[0]},{next_pos[1]})") or
                self.kb.is_premise_true(f"W({next_pos[0]},{next_pos[1]})")):
                return "Cannot move - danger detected"
        
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
