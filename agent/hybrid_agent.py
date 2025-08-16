"""
Hybrid Agent for Wumpus World - combines basic logic with some randomness
"""
import random
from agent.agent import MOVE, DIRECTION

class HybridAgent:
    def __init__(self, base_agent):
        self.agent = base_agent
        self.visited_positions = {(0, 0)}
        self.action_count = 0
        self.max_actions = 300
        self.known_safe = {(0, 0)}  # Simple safe position tracking
        self.known_dangerous = set()
        self.exploring = True
        self.returning_home = False
        self.last_actions = []  # Track recent actions to avoid loops
        
    def step(self):
        """Execute one hybrid step combining logic and randomness"""
        if not self.agent.alive or self.action_count >= self.max_actions:
            return False, "Game Over"
        
        self.visited_positions.add(self.agent.position)
        
        # Get current percepts
        percepts = self.agent.environment.get_percept(self.agent.position)
        
        # Check for gold
        if "Glitter" in percepts and not self.agent.gold_obtain:
            if self.agent.grab_gold():
                self.returning_home = True
                self.exploring = False
                return True, f"Grabbed gold at {self.agent.position}! Now returning home."
        
        # Check if reached home with gold
        if self.agent.gold_obtain and self.agent.position == (0, 0):
            self.agent.score += 1000
            return False, f"Successfully returned home with gold! Final score: {self.agent.score}"
        
        # Update knowledge based on percepts
        self._update_knowledge(percepts)
        
        # Choose action with hybrid approach
        action = self._choose_hybrid_action(percepts)
        
        self.action_count += 1
        self._track_action(action)
        
        return self._execute_action(action)
    
    def _update_knowledge(self, percepts):
        """Simple knowledge update based on percepts"""
        current_pos = self.agent.position
        
        # Current position is safe if we're here and alive
        self.known_safe.add(current_pos)
        
        # If no breeze or stench, adjacent positions might be safer
        if "Breeze" not in percepts and "Stench" not in percepts:
            directions = ["N", "E", "S", "W"]
            for direction in directions:
                move = MOVE[direction]
                adj_pos = (current_pos[0] + move[0], current_pos[1] + move[1])
                if self.agent.environment.is_valid_position(adj_pos):
                    self.known_safe.add(adj_pos)
        
        # If there's danger, be more cautious about adjacent positions
        if "Breeze" in percepts or "Stench" in percepts:
            directions = ["N", "E", "S", "W"]
            for direction in directions:
                move = MOVE[direction]
                adj_pos = (current_pos[0] + move[0], current_pos[1] + move[1])
                if (self.agent.environment.is_valid_position(adj_pos) and 
                    adj_pos not in self.visited_positions):
                    self.known_dangerous.add(adj_pos)
    
    def _choose_hybrid_action(self, percepts):
        """Choose action with hybrid logic - 60% logic, 40% randomness"""
        if random.random() < 0.6:  # 60% logical decisions
            return self._logical_action(percepts)
        else:  # 40% random decisions
            return self._random_action()
    
    def _logical_action(self, percepts):
        """Make a logical decision"""
        current_pos = self.agent.position
        
        # If returning home, try to go towards (0,0)
        if self.returning_home:
            if self._can_move_towards_home():
                return "move_home"
            elif random.choice([True, False]):
                return "turn_left"
            else:
                return "turn_right"
        
        # If exploring and detect loop, try to break it
        if self._is_in_loop():
            if random.choice([True, False]):
                return "turn_left"
            else:
                return "turn_right"
        
        # If there's danger and we have arrow, consider shooting
        if ("Stench" in percepts and self.agent.arrow_hit == 0 and 
            random.random() < 0.3):  # 30% chance to shoot when sensing Wumpus
            return "shoot"
        
        # Try to move to safe unvisited position
        if self._can_move_to_safe_unvisited():
            return "move_safe"
        
        # Try to move forward if seems safe
        if self._is_forward_reasonably_safe():
            return "move_forward"
        
        # Otherwise turn to explore new direction
        if random.choice([True, False]):
            return "turn_left"
        else:
            return "turn_right"
    
    def _random_action(self):
        """Make a random decision"""
        actions = ["move_forward", "turn_left", "turn_right"]
        if self.agent.arrow_hit == 0:  # Add shoot if has arrow
            actions.append("shoot")
        return random.choice(actions)
    
    def _execute_action(self, action):
        """Execute the chosen action"""
        if action == "move_home":
            if self._try_move_towards_home():
                return True, f"Moving towards home, now at {self.agent.position}"
            else:
                self.agent.turn_left()
                return True, "Blocked moving home, turned left"
        
        elif action == "move_safe":
            if self._try_move_to_safe_position():
                return True, f"Moved to safe position {self.agent.position}"
            else:
                self.agent.turn_right()
                return True, "No safe move available, turned right"
        
        elif action == "move_forward":
            if self.agent.move_forward():
                return True, f"Moved forward to {self.agent.position}"
            else:
                self.agent.turn_left()
                return True, "Blocked moving forward, turned left"
        
        elif action == "turn_left":
            self.agent.turn_left()
            return True, f"Turned left to face {self.agent.direction}"
        
        elif action == "turn_right":
            self.agent.turn_right()
            return True, f"Turned right to face {self.agent.direction}"
        
        elif action == "shoot":
            if self.agent.arrow_hit == 0:
                self.agent.shoot()
                return True, "Shot arrow"
            else:
                self.agent.turn_left()
                return True, "No arrow, turned left instead"
        
        return True, "Action completed"
    
    def _can_move_towards_home(self):
        """Check if can move towards (0,0)"""
        current_pos = self.agent.position
        target = (0, 0)
        
        # Calculate direction towards home
        dx = target[0] - current_pos[0]
        dy = target[1] - current_pos[1]
        
        if dx == 0 and dy == 0:
            return False
        
        # Find best direction
        if abs(dx) > abs(dy):
            needed_direction = "W" if dx < 0 else "E"
        else:
            needed_direction = "N" if dy < 0 else "S"
        
        # Check if facing right direction
        if self.agent.direction == needed_direction:
            move = MOVE[self.agent.direction]
            next_pos = (current_pos[0] + move[0], current_pos[1] + move[1])
            return (self.agent.environment.is_valid_position(next_pos) and 
                    next_pos not in self.known_dangerous)
        
        return False
    
    def _try_move_towards_home(self):
        """Try to move one step towards home"""
        current_pos = self.agent.position
        target = (0, 0)
        
        dx = target[0] - current_pos[0]
        dy = target[1] - current_pos[1]
        
        if dx == 0 and dy == 0:
            return True
        
        # Turn towards home if not facing right direction
        if abs(dx) > abs(dy):
            needed_direction = "W" if dx < 0 else "E"
        else:
            needed_direction = "N" if dy < 0 else "S"
        
        if self.agent.direction != needed_direction:
            # Turn towards needed direction
            self._turn_towards(needed_direction)
            return False
        
        # Try to move
        return self.agent.move_forward()
    
    def _can_move_to_safe_unvisited(self):
        """Check if can move to a safe unvisited position"""
        move = MOVE[self.agent.direction]
        next_pos = (self.agent.position[0] + move[0], self.agent.position[1] + move[1])
        
        return (self.agent.environment.is_valid_position(next_pos) and
                next_pos not in self.visited_positions and
                next_pos in self.known_safe)
    
    def _try_move_to_safe_position(self):
        """Try to move to a safe position"""
        move = MOVE[self.agent.direction]
        next_pos = (self.agent.position[0] + move[0], self.agent.position[1] + move[1])
        
        if (self.agent.environment.is_valid_position(next_pos) and
            next_pos not in self.known_dangerous):
            return self.agent.move_forward()
        return False
    
    def _is_forward_reasonably_safe(self):
        """Check if moving forward seems reasonably safe"""
        move = MOVE[self.agent.direction]
        next_pos = (self.agent.position[0] + move[0], self.agent.position[1] + move[1])
        
        return (self.agent.environment.is_valid_position(next_pos) and
                next_pos not in self.known_dangerous)
    
    def _is_in_loop(self):
        """Simple loop detection"""
        if len(self.last_actions) >= 4:
            recent = self.last_actions[-4:]
            # Check for simple patterns like turn-turn-turn-turn
            if recent == ["turn_left", "turn_left", "turn_left", "turn_left"]:
                return True
            if recent == ["turn_right", "turn_right", "turn_right", "turn_right"]:
                return True
            # Check for back-and-forth movement patterns
            if len(set(recent)) == 2 and recent[0] == recent[2] and recent[1] == recent[3]:
                return True
        return False
    
    def _turn_towards(self, target_direction):
        """Turn towards the target direction"""
        directions = ["N", "E", "S", "W"]
        current_idx = directions.index(self.agent.direction)
        target_idx = directions.index(target_direction)
        
        diff = (target_idx - current_idx) % 4
        if diff == 1 or diff == -3:
            self.agent.turn_right()
        elif diff == 3 or diff == -1:
            self.agent.turn_left()
        elif diff == 2:
            self.agent.turn_left()  # Turn left twice (will need another call)
    
    def _track_action(self, action):
        """Track recent actions for loop detection"""
        self.last_actions.append(action)
        if len(self.last_actions) > 10:  # Keep only recent actions
            self.last_actions.pop(0)
    
    def get_current_state(self):
        """Get current state for UI display"""
        return {
            'position': self.agent.position,
            'direction': self.agent.direction,
            'score': self.agent.score,
            'alive': self.agent.alive,
            'gold': self.agent.gold_obtain,
            'arrow': self.agent.arrow_hit,
            'visited': list(self.visited_positions),
            'action_count': self.action_count,
            'safe_positions': list(self.known_safe),
            'dangerous_positions': list(self.known_dangerous),
            'state': 'returning_home' if self.returning_home else 'exploring',
            'agent_type': 'Hybrid'
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
