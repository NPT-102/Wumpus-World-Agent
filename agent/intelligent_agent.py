"""
Intelligent Risk-Based Agent for Wumpus World
Uses probability calculations to make safe decisions and explore efficiently
"""

from agent.agent import Agent2

class IntelligentAgent:
    def __init__(self, base_agent, max_risk_threshold=0.3):
        self.agent = base_agent
        self.risk_threshold = max_risk_threshold
        self.visited_positions = {(0, 0)}
        self.exploration_targets = []
        self.returning_home = False
        self.recent_moves = []  # Track recent moves to detect loops
        self.stuck_counter = 0
        self.last_position = None
        
    def step(self):
        """Execute one intelligent step"""
        if not self.agent.alive:
            return False, "Agent is dead"
        
        # Track recent moves to detect loops
        current_position = self.agent.position
        if current_position == self.last_position:
            self.stuck_counter += 1
        else:
            self.stuck_counter = 0
            self.recent_moves.append(current_position)
            if len(self.recent_moves) > 10:  # Keep only recent moves
                self.recent_moves.pop(0)
        
        self.last_position = current_position
        
        # Detect loop - if stuck in same position or oscillating
        if self.stuck_counter > 3 or self._detect_loop():
            print("Loop detected - trying to break free")
            return self._break_free_from_loop()
        
        # Update visited positions
        self.visited_positions.add(self.agent.position)
        
        # Check for gold at current position
        percepts = self.agent.environment.get_percept(self.agent.position)
        if "Glitter" in percepts and not self.agent.gold_obtain:
            if self.agent.grab_gold():
                self.returning_home = True
                return True, f"Grabbed gold at {self.agent.position}! Now returning home."
        
        # Check if reached home with gold
        if self.returning_home and self.agent.position == (0, 0):
            self.agent.score += 1000  # Escape bonus
            return False, f"Successfully returned home with gold! Final score: {self.agent.score}"
        
        # Decide on action based on current state
        if self.returning_home:
            return self._return_home()
        else:
            return self._explore_intelligently()
    
    def _detect_loop(self):
        """Detect if agent is stuck in a loop"""
        if len(self.recent_moves) < 6:
            return False
        
        # Check for simple oscillation pattern (A-B-A-B...)
        last_4_moves = self.recent_moves[-4:]
        if (last_4_moves[0] == last_4_moves[2] and 
            last_4_moves[1] == last_4_moves[3]):
            return True
        
        # Check if agent has been moving in small area repeatedly
        unique_positions = set(self.recent_moves[-8:])
        if len(unique_positions) <= 2:
            return True
        
        return False
    
    def _break_free_from_loop(self):
        """Try to break free from detected loop"""
        print(f"Breaking free from loop at {self.agent.position}")
        
        # Try shooting first if available
        if self.agent.arrow_hit == 0:
            shoot_result = self._try_intelligent_shot()
            if shoot_result[0]:
                self.stuck_counter = 0
                self.recent_moves.clear()
                return shoot_result
        
        # Try a high-risk move to break free
        safe_moves = self.agent.get_safe_moves()
        
        # Prioritize moves to completely unexplored areas
        unexplored_moves = [(pos, direction, risk) for pos, direction, risk in safe_moves 
                           if pos not in self.visited_positions and pos not in self.recent_moves]
        
        if unexplored_moves:
            # Take the least risky unexplored move
            pos, direction, risk = unexplored_moves[0]
            self.stuck_counter = 0
            self.recent_moves.clear()
            return self._move_to_direction(direction), f"Breaking loop - exploring {direction} (risk: {risk:.3f})"
        
        # If no unexplored moves, try a calculated high-risk move
        risky_moves = [(pos, direction, risk) for pos, direction, risk in safe_moves 
                      if risk <= 0.8 and pos not in self.recent_moves[-4:]]  # Avoid very recent positions
        
        if risky_moves:
            pos, direction, risk = risky_moves[0]
            self.stuck_counter = 0
            self.recent_moves.clear()
            return self._move_to_direction(direction), f"Breaking loop - risky move {direction} (risk: {risk:.3f})"
        
        # Last resort - try shooting in a random direction
        if self.agent.arrow_hit == 0:
            import random
            directions = ["N", "S", "E", "W"]
            target_dir = random.choice(directions)
            turns_needed = self._turn_to_direction(target_dir)
            self.agent.shoot()
            self.stuck_counter = 0
            self.recent_moves.clear()
            return True, f"Breaking loop - random shot {target_dir}"
        
        return False, "Cannot break free from loop - no options available"
    
    def _return_home(self):
        """Return home with gold using safest path"""
        current_pos = self.agent.position
        home_pos = (0, 0)
        
        # Calculate best move toward home
        best_move = None
        best_score = float('-inf')
        
        safe_moves = self.agent.get_safe_moves()
        for pos, direction, risk in safe_moves:
            if risk <= self.risk_threshold:
                # Calculate distance to home
                distance_to_home = abs(pos[0] - home_pos[0]) + abs(pos[1] - home_pos[1])
                # Prefer moves that get closer to home with lower risk
                score = -distance_to_home - (risk * 10)
                
                if score > best_score:
                    best_score = score
                    best_move = (pos, direction, risk)
        
        if best_move:
            pos, direction, risk = best_move
            return self._move_to_direction(direction), f"Moving home via {direction} (risk: {risk:.3f})"
        else:
            # All moves are risky - choose least risky
            if safe_moves:
                pos, direction, risk = safe_moves[0]  # Already sorted by risk
                if risk < 0.8:  # Emergency threshold
                    return self._move_to_direction(direction), f"Emergency move home via {direction} (risk: {risk:.3f})"
            
            return False, "Cannot find safe path home!"
    
    def _explore_intelligently(self):
        """Explore the world intelligently using risk calculations"""
        # Try to shoot if there's a good target
        if self.agent.arrow_hit == 0:  # Still has arrow
            shoot_result = self._try_intelligent_shot()
            if shoot_result[0]:  # Successfully shot
                return shoot_result
        
        # Find next exploration move
        exploration_move = self._find_exploration_move()
        if exploration_move:
            pos, direction, risk = exploration_move
            return self._move_to_direction(direction), f"Exploring via {direction} (risk: {risk:.3f})"
        
        # If no good exploration moves, try shooting to clear path
        if self.agent.arrow_hit == 0:
            shoot_result = self._try_intelligent_shot()
            if shoot_result[0]:
                return shoot_result
        
        # If no safe exploration and no shooting, try calculated risk
        calculated_risk_move = self._try_calculated_risk()
        if calculated_risk_move:
            pos, direction, risk = calculated_risk_move
            return self._move_to_direction(direction), f"Calculated risk move via {direction} (risk: {risk:.3f})"
        
        return False, "No safe moves available!"
    
    def _find_exploration_move(self):
        """Find the best exploration move"""
        safe_moves = self.agent.get_safe_moves()
        
        # Filter moves with acceptable risk
        acceptable_moves = [(pos, direction, risk) for pos, direction, risk in safe_moves 
                          if risk <= self.risk_threshold]
        
        if not acceptable_moves:
            return None
        
        # Score moves based on exploration value
        scored_moves = []
        for pos, direction, risk in acceptable_moves:
            exploration_value = self._calculate_exploration_value(pos)
            score = exploration_value - (risk * 2)  # Prefer high exploration value, low risk
            scored_moves.append((pos, direction, risk, score))
        
        # Sort by score (highest first)
        scored_moves.sort(key=lambda x: x[3], reverse=True)
        
        return scored_moves[0][:3]  # Return (pos, direction, risk)
    
    def _calculate_exploration_value(self, position):
        """Calculate exploration value of a position"""
        if position in self.visited_positions:
            return -10  # Strong negative value to avoid revisiting
        
        # Value based on information gain potential
        adjacent_unknown = 0
        adjacent_positions = self.agent.risk_calculator.get_adjacent_cells(position)
        
        for adj_pos in adjacent_positions:
            if adj_pos not in self.visited_positions:
                adjacent_unknown += 1
        
        # Higher value for positions that can reveal more unknown cells
        exploration_value = adjacent_unknown * 3
        
        # Bonus for positions that might have gold (center area)
        center_x, center_y = self.agent.N // 2, self.agent.N // 2
        distance_from_center = abs(position[0] - center_x) + abs(position[1] - center_y)
        center_bonus = max(0, 8 - distance_from_center)  # Higher value near center
        
        # Add some randomness to break ties and avoid loops
        import random
        randomness = random.uniform(-1, 1)
        
        return exploration_value + center_bonus + randomness
    
    def _try_calculated_risk(self):
        """Try a calculated risk move when no safe options exist"""
        safe_moves = self.agent.get_safe_moves()
        
        if not safe_moves:
            return None
        
        # Find moves with acceptable calculated risk (higher threshold for desperate situations)
        emergency_threshold = min(0.7, self.risk_threshold * 3)  # Dynamic threshold
        emergency_moves = [(pos, direction, risk) for pos, direction, risk in safe_moves 
                          if risk <= emergency_threshold and pos not in self.visited_positions]
        
        if emergency_moves:
            # Choose the move with best risk/reward ratio
            best_move = None
            best_ratio = float('-inf')
            
            for pos, direction, risk in emergency_moves:
                exploration_value = self._calculate_exploration_value(pos)
                if exploration_value > 0:  # Only consider moves that provide new information
                    ratio = exploration_value / (1 + risk)  # Higher exploration value, lower risk is better
                    if ratio > best_ratio:
                        best_ratio = ratio
                        best_move = (pos, direction, risk)
            
            return best_move
        
        # If no unvisited emergency moves, allow revisiting with very high threshold
        desperate_moves = [(pos, direction, risk) for pos, direction, risk in safe_moves 
                          if risk <= 0.9]  # Very desperate threshold
        
        if desperate_moves:
            # Choose least risky move even if visited
            return desperate_moves[0]  # Already sorted by risk
        
        return None
    
    def _try_intelligent_shot(self):
        """Try to shoot if there's a high-probability Wumpus target"""
        if self.agent.arrow_hit != 0:
            return False, "No arrow available"
        
        # Create planning agent to check shooting options
        plan_agent = Agent2(
            position=self.agent.position,
            direction=self.agent.direction,
            alive=self.agent.alive,
            arrow_hit=self.agent.arrow_hit,
            gold_obtain=self.agent.gold_obtain,
            N=self.agent.N,
            kb=self.agent.kb,
            risk_calculator=self.agent.risk_calculator
        )
        
        # Check all directions for shooting opportunities
        best_direction = None
        best_probability = 0
        
        for direction in ["N", "S", "E", "W"]:
            temp_agent = plan_agent.clone()
            temp_agent.direction = direction
            
            potential_targets = temp_agent.possible_wumpus_in_line()
            if potential_targets:
                # Calculate total probability of hitting a Wumpus in this direction
                total_probability = 0
                for target_pos in potential_targets:
                    prob = temp_agent.risk_calculator.calculate_wumpus_probability(target_pos)
                    total_probability += prob
                
                if total_probability > best_probability:
                    best_probability = total_probability
                    best_direction = direction
        
        # Shoot if probability is high enough
        if best_probability > 0.5:  # Threshold for shooting
            # Turn to best direction
            turns_needed = self._turn_to_direction(best_direction)
            self.agent.shoot()
            return True, f"Shot arrow toward {best_direction} (Wumpus probability: {best_probability:.3f})"
        
        return False, f"No good shooting target (best probability: {best_probability:.3f})"
    
    def _move_to_direction(self, target_direction):
        """Move in the specified direction"""
        turns_needed = self._turn_to_direction(target_direction)
        success = self.agent.move_forward()
        return success
    
    def _turn_to_direction(self, target_direction):
        """Turn agent to face target direction"""
        directions = ["E", "S", "W", "N"]
        current_idx = directions.index(self.agent.direction)
        target_idx = directions.index(target_direction)
        
        turns_needed = 0
        while current_idx != target_idx:
            # Choose shortest rotation
            clockwise_distance = (target_idx - current_idx) % 4
            counter_clockwise_distance = (current_idx - target_idx) % 4
            
            if clockwise_distance <= counter_clockwise_distance:
                self.agent.turn_right()
                current_idx = (current_idx + 1) % 4
            else:
                self.agent.turn_left()
                current_idx = (current_idx - 1) % 4
            
            turns_needed += 1
            
            # Safety check to prevent infinite loops
            if turns_needed > 4:
                break
        
        return turns_needed
    
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
            'risk_threshold': self.risk_threshold,
            'returning_home': self.returning_home,
            'state': 'returning' if self.returning_home else 'exploring'
        }
    
    def get_final_result(self):
        """Get final game result"""
        return {
            'final_position': self.agent.position,
            'score': self.agent.score,
            'gold': self.agent.gold_obtain,
            'alive': self.agent.alive
        }
