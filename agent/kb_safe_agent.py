from agent.intelligent_agent import IntelligentAgent

class KnowledgeBaseSafeAgent(IntelligentAgent):
    """Pure Knowledge Base agent - only moves to cells that KB confirms as safe"""

    def __init__(self, base_agent, max_risk_threshold=1.0):  # High threshold, not used
        super().__init__(base_agent, max_risk_threshold)
        self.agent_type_name = 'KB-Safe Agent'
        self.visited_positions = set()
        self.exploration_complete = False
        self.navigation_attempts = 0
        self.max_navigation_attempts = 50  # Increased for better pathfinding
        
    def step(self):
        if not self.agent.alive or self.exploration_complete:
            return False, "Agent dead or exploration complete"
            
        current_pos = self.agent.position
        self.visited_positions.add(current_pos)
        
        # Force perception update at current position
        self.agent.perceive()
        
        # Update KB with current percepts and deduce new safe positions
        self._update_kb_with_current_percepts()
        self._deduce_safe_positions_from_kb()
        
        # Get current percepts
        percepts = []
        current_percepts = self.agent.environment.get_percept(current_pos)
        if current_percepts:
            percepts = current_percepts
            
        print(f"At {current_pos}, percepts: {percepts}")
        
        # Check for gold at current position
        if "Glitter" in percepts and not self.agent.gold_obtain:
            if self.agent.grab_gold():
                self.returning_home = True
                print(f"🏆 FOUND AND GRABBED GOLD at {self.agent.position}!")
                return True, f"Grabbed gold at {self.agent.position}! Now returning home safely."
        
        # Check if reached home with gold
        if self.returning_home and self.agent.position == (0, 0):
            print(f"🏠 Successfully returned home with gold! Final score: {self.agent.score}")
            return False, f"Successfully returned home with gold! Final score: {self.agent.score}"
        
        # If returning home, use safe path finding to get back to (0,0)
        if self.returning_home:
            return self._return_home_safely()
        
        return self._explore_with_kb()
        
    def _explore_with_kb(self):
        """Explore using only KB-confirmed safe positions"""
        
        # Get all adjacent positions
        actions = self.agent.get_safe_moves()  # This gives us all adjacent moves
        
        if not actions:
            print("NO ADJACENT MOVES AVAILABLE - STOPPING")
            self.exploration_complete = True
            return False, "No adjacent moves available"
        
        print(f"Analyzing moves from {self.agent.position}...")
        
        # First priority: KB-confirmed safe unvisited positions
        kb_safe_unvisited = []
        for pos, direction, risk in actions:
            if pos not in self.visited_positions and self._is_kb_safe(pos):
                kb_safe_unvisited.append((pos, direction, risk))
                print(f"  {pos} -> KB SAFE & UNVISITED")
            elif pos not in self.visited_positions:
                print(f"  {pos} -> UNVISITED but not KB-confirmed safe")
            else:
                print(f"  {pos} -> VISITED")
        
        if kb_safe_unvisited:
            pos, direction, risk = kb_safe_unvisited[0]
            success = self._move_direction(direction)
            self.navigation_attempts = 0  # Reset navigation attempts when finding new safe positions
            print(f"Moving to KB-safe unvisited {pos}")
            return success, f"Moving to KB-safe unvisited {pos}"
        
        # Check if we can reach other KB-safe positions by using pathfinding
        print("Checking for KB-safe positions to navigate to...")
        target_pos, path = self._find_path_to_kb_safe_positions()
        
        if target_pos and path and self.navigation_attempts < self.max_navigation_attempts:
            print(f"Found path to unvisited KB-safe position {target_pos}: {path}")
            # Move to the first position in the path
            next_pos = path[0]
            for pos, direction, risk in actions:
                if pos == next_pos:
                    success = self._move_direction(direction)
                    self.navigation_attempts += 1
                    print(f"  Following path: moving to {next_pos} (step {self.navigation_attempts}/{len(path)})")
                    return success, f"Following path to KB-safe {target_pos}: step {self.navigation_attempts}"
        
        if target_pos and path:
            print(f"  Found path but navigation attempts exhausted ({self.navigation_attempts}/{self.max_navigation_attempts})")
        else:
            print(f"  No path found to unvisited KB-safe positions")
        
        # Second priority: Navigation through visited KB-safe positions to reach unvisited ones
        if self._has_reachable_kb_safe_positions() and self.navigation_attempts < self.max_navigation_attempts:
            print("Searching for path through KB-safe visited positions...")
            kb_safe_visited = []
            for pos, direction, risk in actions:
                if pos in self.visited_positions and self._is_kb_safe(pos):
                    kb_safe_visited.append((pos, direction, risk))
                    print(f"  {pos} -> KB SAFE & VISITED (for navigation)")
            
            if kb_safe_visited:
                pos, direction, risk = kb_safe_visited[0]
                success = self._move_direction(direction)
                self.navigation_attempts += 1
                print(f"Navigating via KB-safe visited {pos} [attempt {self.navigation_attempts}]")
                return success, f"Navigating via KB-safe visited {pos}"
        
        # Try shooting Wumpus to open new paths
        if hasattr(self.agent, 'arrow_hit') and self.agent.arrow_hit == 0:
            print("Trying to shoot Wumpus to open new KB-safe paths...")
            if self._try_shoot_wumpus():
                return True, "Shot arrow at Wumpus"
        
        print("NO MORE KB-SAFE EXPLORATION OPTIONS - STOPPING")
        print(f"Final visited positions: {sorted(list(self.visited_positions))}")
        print(f"Total positions explored: {len(self.visited_positions)}")
        
        self._analyze_kb_state()
        
        self.exploration_complete = True
        return False, "Exploration complete - no more KB-safe options"
        
    def _return_home_safely(self):
        """Return to (0,0) using only KB-confirmed safe positions"""
        print(f"🏠 Returning home safely from {self.agent.position} to (0,0)")
        
        # Use BFS to find safe path to (0,0)
        from collections import deque
        
        start_pos = self.agent.position
        target_pos = (0, 0)
        
        if start_pos == target_pos:
            return False, "Already at home!"
        
        queue = deque([(start_pos, [])])
        visited = {start_pos}
        
        while queue:
            current_pos, path = queue.popleft()
            
            # Get adjacent positions
            i, j = current_pos
            adjacent = [(i-1, j), (i+1, j), (i, j-1), (i, j+1)]
            
            for adj_pos in adjacent:
                # Skip out of bounds
                adj_i, adj_j = adj_pos
                if (adj_i < 0 or adj_i >= self.agent.environment.N or 
                    adj_j < 0 or adj_j >= self.agent.environment.N):
                    continue
                    
                if adj_pos in visited:
                    continue
                
                # Only move through KB-confirmed safe positions
                if self._is_kb_safe(adj_pos):
                    new_path = path + [adj_pos]
                    
                    # If we found home, return the first step
                    if adj_pos == target_pos:
                        if new_path:
                            next_pos = new_path[0]
                            # Find direction to next position
                            actions = self.agent.get_safe_moves()
                            for pos, direction, risk in actions:
                                if pos == next_pos:
                                    success = self._move_direction(direction)
                                    print(f"  Moving home: {current_pos} -> {next_pos} (remaining path: {len(new_path)-1} steps)")
                                    return success, f"Returning home safely: step {len(path)+1} of path to (0,0)"
                        else:
                            # Direct adjacent to home
                            actions = self.agent.get_safe_moves()
                            for pos, direction, risk in actions:
                                if pos == target_pos:
                                    success = self._move_direction(direction)
                                    print(f"  Final step home: {current_pos} -> {target_pos}")
                                    return success, f"Final step: returning home to (0,0)"
                    
                    # Continue searching
                    queue.append((adj_pos, new_path))
                    visited.add(adj_pos)
        
        # No safe path found - stay put and end game
        print("⚠️ No safe path home found! Staying at current position.")
        self.exploration_complete = True
        return False, "No safe path home available - mission incomplete"

    def _find_path_to_kb_safe_positions(self):
        """Use BFS to find if there's a path to any unvisited KB-safe position through visited KB-safe positions"""
        all_kb_safe_positions = self._get_all_kb_safe_positions()
        unvisited_kb_safe = [pos for pos in all_kb_safe_positions if pos not in self.visited_positions]
        
        if not unvisited_kb_safe:
            return None, None  # No unvisited KB-safe positions
            
        # BFS to find shortest path to any unvisited KB-safe position
        from collections import deque
        
        queue = deque([(self.agent.position, [])])  # (position, path)
        visited = {self.agent.position}
        
        while queue:
            current_pos, path = queue.popleft()
            
            # Get adjacent positions
            i, j = current_pos
            adjacent = [(i-1, j), (i+1, j), (i, j-1), (i, j+1)]
            
            for adj_pos in adjacent:
                # Skip out of bounds
                adj_i, adj_j = adj_pos
                if (adj_i < 0 or adj_i >= self.agent.environment.N or 
                    adj_j < 0 or adj_j >= self.agent.environment.N):
                    continue
                    
                if adj_pos in visited:
                    continue
                    
                # Check if this position is KB-safe
                if self._is_kb_safe(adj_pos):
                    new_path = path + [adj_pos]
                    
                    # If we found an unvisited KB-safe position, return the path
                    if adj_pos in unvisited_kb_safe:
                        return adj_pos, new_path
                    
                    # Otherwise, continue searching through this KB-safe position
                    queue.append((adj_pos, new_path))
                    visited.add(adj_pos)
        
        return None, None  # No path found

    def _get_all_kb_safe_positions(self):
        """Get all positions that KB has confirmed as safe"""
        kb_safe_positions = []
        
        # Check all positions within reasonable range
        for i in range(max(0, self.agent.position[0] - 3), min(self.agent.environment.N, self.agent.position[0] + 4)):
            for j in range(max(0, self.agent.position[1] - 3), min(self.agent.environment.N, self.agent.position[1] + 4)):
                if self._is_kb_safe((i, j)):
                    kb_safe_positions.append((i, j))
        
        return kb_safe_positions
    
    def _update_kb_with_current_percepts(self):
        """Update KB with current position's percepts"""
        current_pos = self.agent.position
        i, j = current_pos
        
        # Get current percepts
        current_percepts = self.agent.environment.get_percept(current_pos)
        if not current_percepts:
            return
            
        # Add percept facts to KB
        if 'Stench' in current_percepts:
            self.agent.kb.add_fact(f"S({i},{j})")
        elif 'NoStench' in current_percepts:
            self.agent.kb.add_fact(f"~S({i},{j})")
            
        if 'Breeze' in current_percepts:
            self.agent.kb.add_fact(f"B({i},{j})")
        elif 'NoBreeze' in current_percepts:
            self.agent.kb.add_fact(f"~B({i},{j})")
            
        # Mark current position as safe (we survived here)
        self.agent.kb.add_fact(f"Safe({i},{j})")
        self.agent.kb.add_fact(f"~W({i},{j})")
        self.agent.kb.add_fact(f"~P({i},{j})")
        
        # Run forward chaining to deduce new facts
        self.agent.kb.forward_chain()
        
    def _deduce_safe_positions_from_kb(self):
        """Use KB facts to deduce additional safe positions"""
        current_pos = self.agent.position
        i, j = current_pos
        
        # Check adjacent positions and deduce safety based on percepts
        adjacent_positions = [
            (i-1, j), (i+1, j), (i, j-1), (i, j+1)
        ]
        
        for adj_i, adj_j in adjacent_positions:
            # Skip out of bounds positions
            if (adj_i < 0 or adj_i >= self.agent.environment.N or 
                adj_j < 0 or adj_j >= self.agent.environment.N):
                continue
                
            # If current position has NoStench, adjacent positions don't have Wumpus
            if self.agent.kb.is_premise_true(f"~S({i},{j})") == True:
                self.agent.kb.add_fact(f"~W({adj_i},{adj_j})")
                
            # If current position has NoBreeze, adjacent positions don't have Pit
            if self.agent.kb.is_premise_true(f"~B({i},{j})") == True:
                self.agent.kb.add_fact(f"~P({adj_i},{adj_j})")
                
            # If position has both ~W and ~P, it's safe
            no_wumpus = self.agent.kb.is_premise_true(f"~W({adj_i},{adj_j})") == True
            no_pit = self.agent.kb.is_premise_true(f"~P({adj_i},{adj_j})") == True
            
            if no_wumpus and no_pit:
                self.agent.kb.add_fact(f"Safe({adj_i},{adj_j})")
                print(f"  Deduced ({adj_i},{adj_j}) is SAFE from KB inference")
        
        # Run forward chaining again after deductions
        self.agent.kb.forward_chain()

    def _is_kb_safe(self, position):
        """Check if position is confirmed safe by Knowledge Base"""
        i, j = position
        
        # Visited positions are automatically considered safe (we survived there)
        if position in self.visited_positions:
            return True
        
        # ONLY use KB's definitive safe conclusions
        # Check if KB has explicitly concluded this position is safe
        if f"Safe({i},{j})" in self.agent.kb.facts:
            return True
            
        # Check if KB has definitive negative facts about both dangers
        no_wumpus = self.agent.kb.is_premise_true(f"~W({i},{j})") == True
        no_pit = self.agent.kb.is_premise_true(f"~P({i},{j})") == True
        
        if no_wumpus and no_pit:
            return True
        
        # For starting position neighbors with no danger signals, allow movement
        if position in [(0, 1), (1, 0)] and self.agent.position == (0, 0):
            current_percepts = self.agent.environment.get_percept((0, 0))
            if current_percepts and 'NoStench' in current_percepts and 'NoBreeze' in current_percepts:
                # KB should have concluded these are safe, but let's help it along
                self.agent.kb.add_fact(f"~W({i},{j})")
                self.agent.kb.add_fact(f"~P({i},{j})")
                self.agent.kb.forward_chain()
                print(f"  {position} -> KB UPDATED SAFE (no danger signals at start)")
                return True
        
        return False

        
    def _has_reachable_kb_safe_positions(self):
        """Check if there are unvisited KB-safe positions reachable through visited KB-safe positions"""
        
        # Simple BFS to find reachable unvisited KB-safe positions
        queue = [self.agent.position]
        checked = set()
        
        while queue:
            current = queue.pop(0)
            if current in checked:
                continue
            checked.add(current)
            
            # Get adjacent positions
            i, j = current
            for di, dj in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                ni, nj = i + di, j + dj
                next_pos = (ni, nj)
                
                # Skip if out of bounds or already checked
                if not (0 <= ni < 4 and 0 <= nj < 4) or next_pos in checked:
                    continue
                
                # If KB-safe and unvisited, we found a reachable target
                if self._is_kb_safe(next_pos) and next_pos not in self.visited_positions:
                    return True
                
                # If KB-safe and visited, add to queue for further exploration
                if self._is_kb_safe(next_pos) and next_pos in self.visited_positions:
                    queue.append(next_pos)
        
        return False
        
    def _try_shoot_wumpus(self):
        """Try to shoot Wumpus in a promising direction"""
        # Look for adjacent cells with possible Wumpus based on KB
        current_pos = self.agent.position
        i, j = current_pos
        
        for direction, (di, dj) in [('E', (0, 1)), ('W', (0, -1)), ('N', (-1, 0)), ('S', (1, 0))]:
            ni, nj = i + di, j + dj
            if 0 <= ni < 4 and 0 <= nj < 4:
                if self.agent.kb.is_possible_wumpus(ni, nj):
                    # Face the direction and shoot
                    self._face_direction(direction)
                    if hasattr(self.agent, 'shoot_arrow') and self.agent.arrow_hit == 0:
                        success = self.agent.shoot_arrow()
                        if success:
                            # Update KB - Wumpus might be dead
                            self.agent.kb.remove_wumpus(ni, nj)
                            return True
        return False
        
    def _analyze_kb_state(self):
        """Analyze current KB state and show safe/dangerous positions"""
        print("\n=== KB STATE ANALYSIS ===")
        
        kb_safe_positions = []
        kb_dangerous_positions = []
        kb_unknown_positions = []
        
        for i in range(4):  # Assume 4x4 grid
            for j in range(4):
                pos = (i, j)
                if pos in self.visited_positions:
                    kb_safe_positions.append((pos, "VISITED"))
                elif self._is_kb_safe(pos):
                    kb_safe_positions.append((pos, "KB_SAFE"))
                elif self.agent.kb.is_possible_wumpus(i, j) or f"P({i},{j})" in self.agent.kb.facts:
                    kb_dangerous_positions.append((pos, "KB_DANGEROUS"))
                else:
                    kb_unknown_positions.append((pos, "UNKNOWN"))
        
        print("KB-Safe positions:")
        for pos, status in kb_safe_positions:
            print(f"  {pos}: {status}")
        
        print("KB-Dangerous positions:")
        for pos, status in kb_dangerous_positions:
            print(f"  {pos}: {status}")
            
        print("KB-Unknown positions:")
        for pos, status in kb_unknown_positions:
            print(f"  {pos}: {status}")
        
        print(f"\nSummary:")
        print(f"  KB-Safe: {len(kb_safe_positions)}")
        print(f"  KB-Dangerous: {len(kb_dangerous_positions)}")
        print(f"  KB-Unknown: {len(kb_unknown_positions)}")
        print(f"  Visited: {len(self.visited_positions)}")
        
    def _face_direction(self, target_direction):
        """Turn to face the target direction"""
        directions = ['N', 'E', 'S', 'W']
        current_idx = directions.index(self.agent.direction)
        target_idx = directions.index(target_direction)
        
        # Calculate shortest rotation
        while current_idx != target_idx:
            self.agent.turn_right()
            current_idx = (current_idx + 1) % 4
    
    def _move_direction(self, direction):
        """Move in specified direction"""
        self._face_direction(direction)
        return self.agent.move_forward()

# Alias for backwards compatibility
SafeFirstIntelligentAgent = KnowledgeBaseSafeAgent
