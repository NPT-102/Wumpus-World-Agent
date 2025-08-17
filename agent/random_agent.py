"""
Random Agent for Wumpus World - makes random decisions
"""
import random
from agent.agent import MOVE

class RandomAgent:
    def __init__(self, base_agent):
        self.agent = base_agent
        self.visited_positions = {(0, 0)}
        self.action_count = 0
        self.max_actions = 200
        
    def step(self):
        """Execute one random step"""
        if not self.agent.alive or self.action_count >= self.max_actions:
            return False, "Game Over"
        
        self.visited_positions.add(self.agent.position)
        
        # Check for gold
        percepts = self.agent.environment.get_percept(self.agent.position)
        if "Glitter" in percepts and not self.agent.gold_obtain:
            if self.agent.grab_gold():
                return True, f"Grabbed gold at {self.agent.position}!"
        
        # Check if reached home with gold
        if self.agent.gold_obtain and self.agent.position == (0, 0):
            self.agent.score += 1000
            return False, f"Successfully returned home with gold! Final score: {self.agent.score}"
        
        # Random action selection
        actions = ["move", "turn_left", "turn_right", "shoot"]
        
        # Weight actions - prefer movement for exploration
        action_weights = [3, 1, 1, 1]  # Move 3x more likely than other actions
        action = random.choices(actions, weights=action_weights)[0]
        
        self.action_count += 1
        
        if action == "move":
            # Try to move forward
            if self._try_move_forward():
                return True, f"Moved to {self.agent.position}"
            else:
                # If can't move forward, turn randomly
                if random.choice([True, False]):
                    self.agent.turn_left()
                else:
                    self.agent.turn_right()
                return True, f"Blocked - turned to face {self.agent.direction}"
        
        elif action == "turn_left":
            self.agent.turn_left()
            return True, f"Turned left to face {self.agent.direction}"
        
        elif action == "turn_right":
            self.agent.turn_right()
            return True, f"Turned right to face {self.agent.direction}"
        
        elif action == "shoot":
            if self.agent.arrow_hit == 0:  # Has arrow
                self.agent.shoot()
                return True, "Shot arrow randomly"
            else:
                # No arrow, do a random turn instead
                if random.choice([True, False]):
                    self.agent.turn_left()
                else:
                    self.agent.turn_right()
                return True, f"No arrow - turned to {self.agent.direction}"
        
        return True, "Random action completed"
    
    def _try_move_forward(self):
        """Try to move forward, return True if successful"""
        move = MOVE[self.agent.direction]
        next_pos = (self.agent.position[0] + move[0], self.agent.position[1] + move[1])
        
        # Check bounds
        if not self.agent.environment.is_valid_position(next_pos):
            return False
        
        # Random agent doesn't care about safety - just moves
        return self.agent.move_forward()
    
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
            'state': 'random_exploring',
            'agent_type': 'Random'
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