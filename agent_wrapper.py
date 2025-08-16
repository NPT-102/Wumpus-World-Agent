"""
Wrapper classes for different agent types to work with the step-by-step UI
"""
import random
from agent.agent import Agent, Agent2 as PlanningAgent, MOVE, DIRECTION
from agent.hybrid_agent import hybrid_agent_action
from search.dijkstra import dijkstra
from copy import deepcopy

class BaseAgentWrapper:
    """Base class for agent wrappers"""
    def __init__(self, agent, game_map, wumpus_positions, pit_positions):
        self.agent = agent
        self.game_map = game_map  # This is the environment map reference
        self.wumpus_positions = wumpus_positions
        self.pit_positions = pit_positions
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
            'pit_positions': self.pit_positions[:],
            'action_count': self.action_count,
            'state': self.current_state,
            'target': self.target_position
        }
    
    def get_final_result(self):
        """Get final game result"""
        return {
            'final_position': self.agent.position,
            'score': self.agent.score,
            'gold': self.agent.gold_obtain,
            'alive': self.agent.alive,
            'actions': self.action_count
        }

class RandomAgentWrapper(BaseAgentWrapper):
    """Wrapper for random agent with step-by-step execution"""
    
    def __init__(self, agent, game_map, wumpus_positions, pit_positions):
        super().__init__(agent, game_map, wumpus_positions, pit_positions)
        self.current_state = "random_exploring"
    
    def step(self):
        """Execute one step of random agent logic"""
        if not self.agent.alive or self.action_count >= self.max_actions:
            return False, "Game Over"
        
        self.visited.add(self.agent.position)
        self.agent.perceive()
        
        if not self.agent.alive:
            return False, "Agent died"
        
        # Check for gold
        if 'G' in self.game_map[self.agent.position[0]][self.agent.position[1]] and not self.agent.gold_obtain:
            self.agent.grab_gold()
            # Remove gold from the map after grabbing it
            self.game_map[self.agent.position[0]][self.agent.position[1]].remove('G')
            self.current_state = "returning"
            return True, f"Grabbed gold at {self.agent.position}!"
        
        # Check if agent reached home with gold
        if self.agent.gold_obtain and self.agent.position == (0, 0):
            self.agent.score += 1000
            self.current_state = "won"
            return False, f"Agent successfully returned home with gold! +1000 points! Final score: {self.agent.score}"
        
        # Random action selection
        actions = ["move", "turn", "shoot", "grab"]
        action = random.choice(actions)
        
        if action == "move":
            # Try to move forward
            if self._try_move_forward():
                self.action_count += 1
                return True, f"Moved to {self.agent.position}"
            else:
                # If can't move forward, turn randomly
                if random.choice([True, False]):
                    self.agent.turn_left()
                else:
                    self.agent.turn_right()
                self.action_count += 1
                return True, f"Turned to face {self.agent.direction}"
        
        elif action == "turn":
            if random.choice([True, False]):
                self.agent.turn_left()
            else:
                self.agent.turn_right()
            self.action_count += 1
            return True, f"Turned to face {self.agent.direction}"
        
        elif action == "shoot":
            if self.agent.arrow_hit == 0:  # Has arrow
                self.agent.shoot()
                self.action_count += 1
                return True, "Shot arrow"
            else:
                # No arrow, do a random turn instead
                if random.choice([True, False]):
                    self.agent.turn_left()
                else:
                    self.agent.turn_right()
                self.action_count += 1
                return True, f"No arrow - turned to {self.agent.direction}"
        
        elif action == "grab":
            if self.agent.grab_gold():
                self.game_map[self.agent.position[0]][self.agent.position[1]].remove('G')
                return True, f"Grabbed gold at {self.agent.position}!"
            else:
                # No gold, move randomly
                if self._try_move_forward():
                    self.action_count += 1
                    return True, f"No gold - moved to {self.agent.position}"
                else:
                    if random.choice([True, False]):
                        self.agent.turn_left()
                    else:
                        self.agent.turn_right()
                    self.action_count += 1
                    return True, f"No gold - turned to {self.agent.direction}"
        
        return True, "Random action completed"
    
    def _try_move_forward(self):
        """Try to move forward, return True if successful"""
        move = MOVE[self.agent.direction]
        i, j = (self.agent.position[0] + move[0], self.agent.position[1] + move[1])
        
        # Check bounds
        if not (0 <= i < self.N and 0 <= j < self.N):
            return False
        
        # Move (random agent doesn't check for dangers)
        return self.agent.move_forward()


class HybridAgentWrapper(BaseAgentWrapper):
    """Wrapper for hybrid agent with step-by-step execution"""
    
    def __init__(self, agent, game_map, wumpus_positions, pit_positions):
        super().__init__(agent, game_map, wumpus_positions, pit_positions)
        self.current_state = "hybrid_exploring"
        self.path_states = []
        self.current_path_index = 0
        
    def step(self):
        """Execute one step of hybrid agent logic"""
        if not self.agent.alive or self.action_count >= self.max_actions:
            return False, "Game Over"
        
        self.visited.add(self.agent.position)
        self.agent.perceive()
        
        if not self.agent.alive:
            return False, "Agent died"
        
        # Check for gold
        if 'G' in self.game_map[self.agent.position[0]][self.agent.position[1]] and not self.agent.gold_obtain:
            self.agent.grab_gold()
            # Remove gold from the map after grabbing it
            self.game_map[self.agent.position[0]][self.agent.position[1]].remove('G')
            self.current_state = "returning"
            self.path_states = []  # Reset path
            return True, f"Grabbed gold at {self.agent.position}!"
        
        # Check if agent reached home with gold
        if self.agent.gold_obtain and self.agent.position == (0, 0):
            self.agent.score += 1000
            self.current_state = "won"
            return False, f"Agent successfully returned home with gold! +1000 points! Final score: {self.agent.score}"
        
        # Create planning agent
        plan_agent = PlanningAgent(
            position=self.agent.position,
            direction=self.agent.direction,
            alive=self.agent.alive,
            arrow_hit=self.agent.arrow_hit,
            gold_obtain=self.agent.gold_obtain,
            N=self.N,
            kb=deepcopy(self.agent.kb)
        )
        
        # Try shooting if beneficial
        if self._try_shoot_if_beneficial(plan_agent):
            self.action_count += 1
            return True, "Agent shot arrow"
        
        # Get or continue following path
        if not self.path_states or self.current_path_index >= len(self.path_states):
            self.path_states = dijkstra(self.game_map, plan_agent)
            self.current_path_index = 0
        
        if self.path_states and len(self.path_states) >= 2:
            # Move along the path
            self.current_path_index += 1
            if self.current_path_index < len(self.path_states):
                next_state = self.path_states[self.current_path_index]
                action_msg = self._move_to_state(next_state)
                return True, action_msg
            else:
                self.path_states = []  # Path completed, recalculate next time
                return True, "Path completed"
        else:
            # No safe path found - try exploration or shooting strategies
            if self._try_exploration_before_desperate_shot(plan_agent):
                self.action_count += 1
                return True, "Exploring to gather more information"
            
            # Dead end situation - try shooting as last resort
            if self._try_desperate_shot(plan_agent):
                self.action_count += 1
                return True, "Desperate shot - no safe path available!"
            
            self.current_state = "stuck"
            return False, "No safe path found and no shooting options"
    
    def _try_shoot_if_beneficial(self, plan_agent):
        """Try to shoot if it's beneficial - using knowledge-based reasoning only"""
        if self.agent.arrow_hit != 0:
            return False
        
        # Use knowledge-based reasoning instead of direct map access
        potential_wumpus = plan_agent.possible_wumpus_in_line()
        
        if potential_wumpus:
            # Calculate cost with current knowledge
            path_with_wumpus = dijkstra(self.game_map, plan_agent)
            
            # Create temporary agent with assumption that Wumpus is shot
            temp_agent = PlanningAgent(
                position=self.agent.position,
                direction=self.agent.direction,
                alive=self.agent.alive,
                arrow_hit=1,  # Simulate having shot
                gold_obtain=self.agent.gold_obtain,
                N=self.N,
                kb=deepcopy(self.agent.kb)
            )
            
            # Mark potential Wumpus locations as safe in temp KB
            for wx, wy in potential_wumpus:
                temp_agent.kb.add_fact(f"~W({wx}, {wy})")
                temp_agent.kb.add_fact(f"Safe({wx}, {wy})")
            temp_agent.kb.forward_chain()
            
            path_no_wumpus = dijkstra(self.game_map, temp_agent)
            
            # Simple cost comparison (number of steps)
            cost_with = len(path_with_wumpus) if path_with_wumpus else float('inf')
            cost_no = len(path_no_wumpus) + 1 if path_no_wumpus else float('inf')  # +1 for shooting
            
            if cost_no < cost_with:
                print(f"Shooting beneficial: Path cost {cost_with} vs Shoot+Path cost {cost_no}")
                self.agent.shoot()
                return True
        
        return False
    
    def _try_exploration_before_desperate_shot(self, plan_agent):
        """Try to explore unknown safe cells to gather more information before shooting"""
        if self.agent.arrow_hit != 0:
            return False
        
        # Look for unknown cells that are likely safe based on knowledge
        current_pos = self.agent.position
        
        for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:  # Check adjacent cells
            nx, ny = current_pos[0] + dx, current_pos[1] + dy
            
            if (0 <= nx < self.N and 0 <= ny < self.N and 
                (nx, ny) not in self.visited):
                
                # Check if this cell is likely safe
                safe_status = plan_agent.kb.is_premise_true(f"Safe({nx}, {ny})")
                pit_status = plan_agent.kb.is_premise_true(f"P({nx}, {ny})")
                wumpus_status = plan_agent.kb.is_premise_true(f"W({nx}, {ny})")
                
                # Move to cell if it's confirmed safe OR unknown but no danger indicators
                if (safe_status is True or 
                    (safe_status is None and pit_status is not True and wumpus_status is not True)):
                    
                    # Additional safety check: avoid cells near unknown stench/breeze if possible
                    is_risky = False
                    for vi, vj in self.visited:
                        if abs(vi - nx) + abs(vj - ny) == 1:  # Adjacent to visited cell
                            if (plan_agent.kb.is_premise_true(f"B({vi}, {vj})") is True or
                                plan_agent.kb.is_premise_true(f"S({vi}, {vj})") is True):
                                is_risky = True
                                break
                    
                    if not is_risky:
                        # Move to this exploration target
                        desired_dir = self._direction_from_delta(dx, dy)
                        if desired_dir:
                            self._rotate_towards(desired_dir)
                            self.agent.move_forward()
                            self.visited.add((nx, ny))
                            return True
        
        # If no safe adjacent exploration, look for stench cells to approach for shooting
        for x in range(self.N):
            for y in range(self.N):
                if ((x, y) not in self.visited and 
                    plan_agent.kb.is_premise_true(f"S({x}, {y})") is True):
                    
                    # Try to move towards this stench cell
                    dx_stench = x - current_pos[0] 
                    dy_stench = y - current_pos[1]
                    
                    # Move one step towards stench cell if safe
                    if abs(dx_stench) > abs(dy_stench):
                        step_dir = "S" if dx_stench > 0 else "N"
                        step_dx, step_dy = (1, 0) if dx_stench > 0 else (-1, 0)
                    else:
                        step_dir = "E" if dy_stench > 0 else "W" 
                        step_dx, step_dy = (0, 1) if dy_stench > 0 else (0, -1)
                    
                    next_x, next_y = current_pos[0] + step_dx, current_pos[1] + step_dy
                    
                    if (0 <= next_x < self.N and 0 <= next_y < self.N):
                        # Check safety of next step
                        if (plan_agent.kb.is_premise_true(f"P({next_x}, {next_y})") is not True and
                            plan_agent.kb.is_premise_true(f"W({next_x}, {next_y})") is not True):
                            
                            self._rotate_towards(step_dir)
                            self.agent.move_forward()
                            self.visited.add((next_x, next_y))
                            return True
        
        return False
    
    def _try_desperate_shot(self, plan_agent):
        """Try shooting as a last resort when no safe path exists"""
        if self.agent.arrow_hit != 0:
            return False
        
        # Look for any potential Wumpus in shooting range
        potential_wumpus = plan_agent.possible_wumpus_in_line()
        
        if potential_wumpus:
            print(f"Desperate situation: Shooting at potential Wumpus {potential_wumpus}")
            self.agent.shoot()
            return True
        
        return False
    
    def _move_to_state(self, target_state):
        """Move agent towards target state"""
        if target_state.position == self.agent.position:
            # Just turn
            self._rotate_towards(target_state.direction)
            return f"Turned to face {target_state.direction}"
        else:
            # Move forward after turning if needed
            di = target_state.position[0] - self.agent.position[0]
            dj = target_state.position[1] - self.agent.position[1]
            desired_dir = self._direction_from_delta(di, dj)
            
            if desired_dir:
                self._rotate_towards(desired_dir)
                self.agent.move_forward()
                self.action_count += 1
                return f"Moved to {self.agent.position}"
        
        return "Could not move"
    
    def _rotate_towards(self, desired_dir):
        """Rotate agent towards desired direction"""
        dir_list = ["E", "S", "W", "N"]
        
        while self.agent.direction != desired_dir:
            cur_idx = dir_list.index(self.agent.direction)
            des_idx = dir_list.index(desired_dir)
            
            if (cur_idx + 1) % 4 == des_idx:
                self.agent.turn_right()
            else:
                self.agent.turn_left()
            
            self.action_count += 1
    
    def _direction_from_delta(self, di, dj):
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


class DynamicAgentWrapper(BaseAgentWrapper):
    """Wrapper for dynamic agent (existing stepwise agent with Wumpus movement)"""
    
    def __init__(self, agent, game_map, wumpus_positions, pit_positions):
        super().__init__(agent, game_map, wumpus_positions, pit_positions)
        self.wumpus_alive = [True] * len(wumpus_positions)
        self.current_state = "dynamic_exploring"
        
    def step(self):
        """Execute one step of the dynamic agent logic (with Wumpus movement)"""
        # Import here to avoid circular imports
        from stepwise_agent import StepByStepHybridAgent
        
        # Create a temporary stepwise agent if not already done
        if not hasattr(self, 'stepwise_agent'):
            self.stepwise_agent = StepByStepHybridAgent(
                self.agent, self.game_map, self.wumpus_positions, self.pit_positions
            )
        
        # Use the existing stepwise agent logic
        result, message = self.stepwise_agent.step()
        
        # Update our state from the stepwise agent
        self.action_count = self.stepwise_agent.action_count
        self.current_state = self.stepwise_agent.current_state
        self.wumpus_positions = self.stepwise_agent.wumpus_positions
        self.visited = self.stepwise_agent.visited
        
        return result, message
