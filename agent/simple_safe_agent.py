from agent.intelligent_agent import IntelligentAgent

class SafeFirstIntelligentAgent(IntelligentAgent):
    """Ultra-safe agent that only explores safe positions and stops when done"""

    def __init__(self, base_agent, max_risk_threshold=0.25):
        super().__init__(base_agent, max_risk_threshold)
        self.agent_type_name = 'Safe-First Intelligent'
        self.stuck_counter = 0
        self.position_history = []
        self.exploration_complete = False
        self.navigation_attempts = 0  # Track navigation between visited positions
        self.fallback_threshold = 0.5  # More generous fallback threshold
        
    def step(self):
        if not self.agent.alive or self.exploration_complete:
            return False, "Agent dead or exploration complete"
            
        current_pos = self.agent.position
        self.visited_positions.add(current_pos)
        
        # Track position for loop detection 
        self.position_history.append(current_pos)
        if len(self.position_history) > 8:
            self.position_history.pop(0)
        
        # Check for stuck loop - but only stop if no more unvisited safe positions exist
        if len(self.position_history) >= 6:
            recent_positions = set(self.position_history[-6:])
            if len(recent_positions) <= 2:
                # Check if there are still unvisited safe positions available
                actions = self.agent.get_safe_moves()
                safe_unvisited = [(pos, direction, risk) for pos, direction, risk in actions
                                 if risk <= 0.15 and pos not in self.visited_positions]  # Ultra safe threshold
                
                if not safe_unvisited:  # Only stop if no unvisited safe positions
                    self.stuck_counter += 1
                    if self.stuck_counter >= 3:
                        print(" STUCK LOOP DETECTED - NO MORE SAFE UNVISITED - STOPPING")
                        self.exploration_complete = True
                        return False, "Exploration complete - agent stuck in loop"
                else:
                    # Reset counter if there are still unvisited positions
                    self.stuck_counter = 0
            else:
                self.stuck_counter = 0
        
        # Check for gold
        percepts = self.agent.environment.get_percept(current_pos)
        if "Glitter" in percepts and not self.agent.gold_obtain:
            if self.agent.grab_gold():
                self.returning_home = True
                return True, f"Grabbed gold at {current_pos}! Now returning home."
        
        if self.returning_home:
            return self._navigate_home()
            
        return self._explore_safely()
    
    def _explore_safely(self):
        """Prioritize completely safe positions (risk=0), then consider low-risk positions"""
        actions = self.agent.get_safe_moves()
        
        # print(f" Available actions from {self.agent.position}: {actions}")  # DEBUG
        
        if not actions:
            print(" NO SAFE MOVES - STOPPING EXPLORATION")
            self.exploration_complete = True
            return False, "Exploration complete - no safe moves available"
        
        # First priority: Perfectly safe unvisited positions (risk = 0)
        perfectly_safe_unvisited = [(pos, direction, risk) for pos, direction, risk in actions
                                   if risk == 0.0 and pos not in self.visited_positions]
        
        if perfectly_safe_unvisited:
            pos, direction, risk = perfectly_safe_unvisited[0]
            success = self._move_direction(direction)
            self.navigation_attempts = 0  # Reset navigation counter when finding new position
            print(f"Exploring perfectly safe unvisited {pos} (risk: {risk:.3f})")
            return success, f"Exploring perfectly safe unvisited {pos}"
        
        # Second priority: Low risk unvisited positions (risk <= threshold)
        safe_unvisited = [(pos, direction, risk) for pos, direction, risk in actions
                         if risk <= self.risk_threshold and pos not in self.visited_positions]
        
        if safe_unvisited:
            # Choose the safest unvisited move (lowest risk)
            pos, direction, risk = min(safe_unvisited, key=lambda x: x[2])
            success = self._move_direction(direction)
            self.navigation_attempts = 0  # Reset navigation counter when finding new position
            print(f"Exploring safe unvisited {pos} (risk: {risk:.3f})")
            return success, f"Exploring safe unvisited {pos}"
        
        # Check for navigation loop - if we keep navigating between same positions, stop
        if len(self.position_history) >= 4:
            recent_moves = self.position_history[-4:]
            if len(set(recent_moves)) <= 2:  # Only 2 unique positions in last 4 moves
                print("Navigation loop detected - stopping navigation")
                self.navigation_attempts = 10  # Force stop navigation
        
        # Check if there are any unvisited positions we might be able to reach
        # by going through visited safe positions - but limit attempts to prevent infinite loops
        if self._has_reachable_unvisited_positions() and self.navigation_attempts < 5:  # Reduced from 10 to 5
            print("Has reachable unvisited positions - continuing navigation")
            # Try any visited safe positions (for navigation to reach unvisited ones)
            safe_visited = [(pos, direction, risk) for pos, direction, risk in actions
                           if risk <= self.risk_threshold and pos in self.visited_positions]
            
            if safe_visited:
                pos, direction, risk = min(safe_visited, key=lambda x: x[2])
                success = self._move_direction(direction)
                self.navigation_attempts += 1  # Increment navigation counter
                print(f"Navigating via safe visited {pos} (risk: {risk:.3f}) [attempt {self.navigation_attempts}]")
                return success, f"Navigating via safe visited {pos}"
        
        # No primary threshold moves, try fallback threshold if defined
        if hasattr(self, 'fallback_threshold'):
            print(f"Trying fallback threshold {self.fallback_threshold}")
            
            # Try fallback unvisited positions
            fallback_unvisited = [(pos, direction, risk) for pos, direction, risk in actions
                                 if risk <= self.fallback_threshold and pos not in self.visited_positions]
            
            if fallback_unvisited:
                pos, direction, risk = min(fallback_unvisited, key=lambda x: x[2])
                success = self._move_direction(direction)
                self.navigation_attempts = 0
                print(f"Exploring fallback unvisited {pos} (risk: {risk:.3f})")
                return success, f"Exploring fallback unvisited {pos}"
        
        # No safe moves - try shooting Wumpus
        if hasattr(self.agent, 'arrow_hit') and self.agent.arrow_hit == 0:
            print("Trying to shoot Wumpus to open new paths...")
            if self._try_shoot_wumpus():
                return True, "Shot arrow at Wumpus"
        
        print("NO MORE SAFE EXPLORATION OPTIONS - STOPPING")
        print(f"Final visited positions: {sorted(list(self.visited_positions))}")
        print(f"Total positions explored: {len(self.visited_positions)}")
        
        # Show all safe positions that could theoretically be explored
        self._analyze_all_safe_positions()
        
        self.exploration_complete = True
        return False, "Exploration complete - no more safe options"
    
    def _has_reachable_unvisited_positions(self):
        """Check if there are unvisited positions reachable through safe paths"""
        # First check for direct unvisited safe moves
        actions = self.agent.get_safe_moves()
        direct_unvisited = [(pos, direction, risk) for pos, direction, risk in actions
                           if risk <= self.risk_threshold and pos not in self.visited_positions]
        
        if direct_unvisited:
            return True
        
        # Then do BFS through visited safe positions to find reachable unvisited positions
        # But limit search depth to avoid infinite loops
        queue = [self.agent.position]
        checked = set()
        search_depth = 0
        max_depth = 5  # Limit search depth
        
        while queue and search_depth < max_depth:
            current = queue.pop(0)
            if current in checked:
                continue
            checked.add(current)
            search_depth += 1
            
            # Temporarily move agent to check available moves from this position
            original_pos = self.agent.position
            self.agent.position = current
            
            try:
                actions = self.agent.get_safe_moves()
                for pos, direction, risk in actions:
                    if risk <= 0.15:  # Ultra safe threshold for pathfinding
                        if pos not in self.visited_positions:
                            # Found unvisited reachable position
                            self.agent.position = original_pos  # Restore position
                            return True
                        elif pos in self.visited_positions and pos not in checked:
                            queue.append(pos)
            finally:
                # Restore original position
                self.agent.position = original_pos
        
        return False
    
    def _try_shoot_wumpus(self):
        """Try to shoot a Wumpus"""
        # Simple shooting logic - shoot in any direction with stench
        current_pos = self.agent.position
        percepts = self.agent.environment.get_percept(current_pos)
        
        if "Stench" in percepts:
            # Try shooting in all directions
            directions = ["N", "E", "S", "W"]
            for direction in directions:
                self._face_direction(direction)
                if self.agent.shoot():
                    print(f" Shot arrow {direction}")
                    return True
        
        return False
    
    def _navigate_home(self):
        """Navigate back to (0,0) safely using only safe moves"""
        current_pos = self.agent.position
        if current_pos == (0, 0):
            return False, "Agent reached home!"
        
        # Use safe pathfinding instead of direct movement
        actions = self.agent.get_safe_moves()
        
        if not actions:
            print(" NO SAFE MOVES AVAILABLE - CANNOT RETURN HOME SAFELY")
            return False, "Cannot return home safely - no safe moves"
        
        # Find safe moves that get us closer to (0,0)
        target_pos = (0, 0)
        current_distance = abs(current_pos[0] - target_pos[0]) + abs(current_pos[1] - target_pos[1])
        
        safe_home_moves = []
        for pos, direction, risk in actions:
            new_distance = abs(pos[0] - target_pos[0]) + abs(pos[1] - target_pos[1])
            # Only consider perfectly safe moves (risk = 0) when returning home
            if risk == 0.0 and new_distance < current_distance:
                safe_home_moves.append((pos, direction, risk, new_distance))
        
        if safe_home_moves:
            # Choose the move that gets us closest to home
            pos, direction, risk, distance = min(safe_home_moves, key=lambda x: x[3])
            success = self._move_direction(direction)
            print(f" Returning home safely via {direction} to {pos} (risk: {risk:.3f})")
            return success, f"Moving home safely to {pos}"
        
        # If no perfectly safe direct path, try safe moves through visited positions
        safe_visited_moves = [(pos, direction, risk) for pos, direction, risk in actions
                             if risk == 0.0 and pos in self.visited_positions]
        
        if safe_visited_moves:
            pos, direction, risk = safe_visited_moves[0]
            success = self._move_direction(direction)
            print(f" Returning home via safe visited {pos} (risk: {risk:.3f})")
            return success, f"Moving home via safe visited {pos}"
        
        # Emergency: No perfectly safe moves available
        print(" WARNING: No perfectly safe path home - stopping to avoid danger")
        return False, "Cannot return home safely"
    
    def _face_direction(self, target_direction):
        """Turn to face target direction"""
        direction_map = {"N": 0, "E": 1, "S": 2, "W": 3}
        current_idx = direction_map[self.agent.direction]
        target_idx = direction_map[target_direction]
        
        while current_idx != target_idx:
            self.agent.turn_right()
            current_idx = (current_idx + 1) % 4
    
    def _move_direction(self, direction):
        """Move in specified direction"""
        self._face_direction(direction)
        return self.agent.move_forward()
    
    def _analyze_all_safe_positions(self):
        """Analyze all positions in the grid to see which ones are truly safe"""
        print("\n=== ANALYZING ALL SAFE POSITIONS ===")
        grid_size = 4  # Assume 4x4 grid
        all_safe_positions = []
        
        for row in range(grid_size):
            for col in range(grid_size):
                pos = (row, col)
                # Get risk for this position by simulating being there
                # This is a rough estimate since we can't actually go there
                if pos in self.visited_positions:
                    risk = 0.0  # Already visited, so it's safe
                    all_safe_positions.append((pos, risk, "VISITED"))
                else:
                    # Try to estimate risk from current knowledge
                    # This is approximation based on available actions from visited positions
                    estimated_risk = self._estimate_position_risk(pos)
                    if estimated_risk <= self.risk_threshold:
                        all_safe_positions.append((pos, estimated_risk, "SAFE_UNVISITED"))
                    elif estimated_risk <= self.fallback_threshold:
                        all_safe_positions.append((pos, estimated_risk, "FALLBACK_SAFE"))
                    else:
                        all_safe_positions.append((pos, estimated_risk, "UNSAFE"))
        
        print("All positions analysis:")
        for pos, risk, status in sorted(all_safe_positions):
            print(f"  {pos}: risk={risk:.3f} - {status}")
        
        safe_count = len([x for x in all_safe_positions if x[2] in ["VISITED", "SAFE_UNVISITED"]])
        fallback_count = len([x for x in all_safe_positions if x[2] == "FALLBACK_SAFE"])
        print(f"\nSummary:")
        print(f"  Safe positions (≤{self.risk_threshold}): {safe_count}")
        print(f"  Fallback safe (≤{self.fallback_threshold}): {fallback_count}")
        print(f"  Visited: {len(self.visited_positions)}")
        
    def _estimate_position_risk(self, target_pos):
        """Estimate risk of a position based on current knowledge"""
        # This is a simplified estimation
        # In reality, we'd need full game state to calculate accurate risk
        # For now, return high risk for unvisited positions that weren't directly accessible
        return 0.8  # Conservative high estimate for unvisited positions
