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
            # Call escape to get the appropriate bonus points
            self.agent.escape()
            if self.agent.gold_obtain:
                print(f"🏠 Successfully returned home with gold! Final score: {self.agent.score}")
                return False, f"Successfully returned home with gold! Final score: {self.agent.score}"
            else:
                print(f"🏠 Successfully returned home safely! Final score: {self.agent.score}")
                return False, f"Successfully returned home safely! Final score: {self.agent.score}"
        
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
        
        # Alternative: Check for any unvisited KB-safe position we can reach
        if not target_pos or not path:
            print("Searching for any reachable KB-safe positions...")
            all_kb_safe = self._get_all_kb_safe_positions()
            unvisited_kb_safe = [pos for pos in all_kb_safe if pos not in self.visited_positions]
            
            for unvisited_pos in unvisited_kb_safe:
                found_target, found_path = self._find_path_to_specific_position(unvisited_pos)
                if found_target and found_path and self.navigation_attempts < self.max_navigation_attempts:
                    print(f"Found alternative path to {found_target}: {found_path}")
                    # Move to the first position in the path
                    next_pos = found_path[0]
                    for pos, direction, risk in actions:
                        if pos == next_pos:
                            success = self._move_direction(direction)
                            self.navigation_attempts += 1
                            print(f"  Alternative path: moving to {next_pos} (step 1/{len(found_path)})")
                            return success, f"Alternative path to KB-safe {found_target}: step 1"
        
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
        
        # Try shooting Wumpus to open new paths - Enhanced strategy
        if hasattr(self.agent, 'arrow_hit') and self.agent.arrow_hit == 0:
            print("Trying enhanced Wumpus hunting to open new KB-safe paths...")
            wumpus_hunt_result = self._try_enhanced_wumpus_hunting()
            if wumpus_hunt_result:
                return True, wumpus_hunt_result
        
        # Before stopping exploration, try to return home safely if not already at (0,0)
        if self.agent.position != (0, 0):
            print("NO MORE KB-SAFE EXPLORATION OPTIONS - ATTEMPTING TO RETURN HOME SAFELY")
            print(f"Current position: {self.agent.position}, attempting to return to (0,0)")
            
            # Check if there's a safe path home
            home_target, home_path = self._find_path_to_specific_position((0, 0))
            if home_target and home_path:
                print(f"Found safe path home: {home_path}")
                self.returning_home = True  # Set returning home flag
                return self._return_home_safely()
            else:
                print("⚠️ No safe path home found!")
                print(f"Final visited positions: {sorted(list(self.visited_positions))}")
                print(f"Total positions explored: {len(self.visited_positions)}")
                self._analyze_kb_state()
                self.exploration_complete = True
                return False, "Exploration complete - no safe path home available"
        else:
            print("NO MORE KB-SAFE EXPLORATION OPTIONS AND ALREADY AT HOME")
            print(f"Final visited positions: {sorted(list(self.visited_positions))}")
            print(f"Total positions explored: {len(self.visited_positions)}")
            self._analyze_kb_state()
            self.exploration_complete = True
            return False, "Exploration complete - already at home (0,0)"
        
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
                                    # Call escape when reaching home to get points
                                    self.agent.escape()
                                    if self.agent.gold_obtain:
                                        print(f"  Final step home: {current_pos} -> {target_pos}")
                                        print(f"🏠 Successfully reached home with gold! Final score: {self.agent.score}")
                                        return False, f"Successfully reached home with gold at (0,0)! Final score: {self.agent.score}"
                                    else:
                                        print(f"  Final step home: {current_pos} -> {target_pos}")
                                        print(f"🏠 Successfully reached home safely! Final score: {self.agent.score}")
                                        return False, f"Successfully reached home safely at (0,0)! Final score: {self.agent.score}"
                    
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
        
        # Check all positions in the grid (not just nearby ones)
        for i in range(self.agent.environment.N):
            for j in range(self.agent.environment.N):
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
            
        if 'Glitter' in current_percepts:
            self.agent.kb.add_fact(f"G({i},{j})")
        elif 'NoGlitter' in current_percepts:
            self.agent.kb.add_fact(f"~G({i},{j})")
            
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
        
        # Get all KB-safe positions and check if any unvisited ones are reachable
        all_kb_safe = self._get_all_kb_safe_positions()
        unvisited_kb_safe = [pos for pos in all_kb_safe if pos not in self.visited_positions]
        
        if not unvisited_kb_safe:
            return False
        
        # For each unvisited KB-safe position, check if there's a path to it
        for target_pos in unvisited_kb_safe:
            _, path = self._find_path_to_specific_position(target_pos)
            if path is not None:
                return True
        
        return False

    def _find_path_to_specific_position(self, target_pos):
        """Use BFS to find path to a specific position through KB-safe cells only"""
        if target_pos == self.agent.position:
            return target_pos, []
        
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
                    
                    # If we found the target, return it
                    if adj_pos == target_pos:
                        return target_pos, new_path
                    
                    # Otherwise, continue searching through this KB-safe position
                    queue.append((adj_pos, new_path))
                    visited.add(adj_pos)
        
        return None, None  # No path found
        
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
        
        for i in range(self.agent.environment.N):
            for j in range(self.agent.environment.N):
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
        
        # Show which KB-Safe positions were not visited
        unvisited_safe = [pos for pos, status in kb_safe_positions if status == "KB_SAFE"]
        if unvisited_safe:
            print(f"\n⚠️  KB-Safe positions NOT visited:")
            for pos in unvisited_safe:
                reachable_target, reachable_path = self._find_path_to_specific_position(pos)
                reachable_status = "REACHABLE" if reachable_target else "NOT REACHABLE"
                print(f"    {pos}: {reachable_status}")
        else:
            print(f"\n✅ ALL KB-Safe positions were visited!")
            
        # Show summary of Safe facts in KB  
        safe_facts = [f for f in self.agent.kb.facts if 'Safe(' in f and not f.startswith('~')]
        print(f"\nKB Safe Facts Summary: {len(safe_facts)} total")
        # Remove duplicates and show unique positions
        unique_safe_positions = set()
        for fact in safe_facts:
            import re
            match = re.search(r'Safe\((\d+)[, ]+(\d+)\)', fact)
            if match:
                pos = (int(match.group(1)), int(match.group(2)))
                unique_safe_positions.add(pos)
        print(f"Unique Safe positions in KB: {len(unique_safe_positions)}")
        for pos in sorted(unique_safe_positions):
            visited_status = "VISITED" if pos in self.visited_positions else "NOT VISITED"
            print(f"  {pos}: {visited_status}")
        
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
        
    def _try_enhanced_wumpus_hunting(self):
        """Enhanced Wumpus hunting strategy - find known Wumpus and plan to shoot it"""
        
        # Check if we have arrows left
        if self.agent.arrow_hit > 0:
            print("  🚫 No arrows left - cannot hunt Wumpus")
            return None
        
        # Step 1: Find all known Wumpus positions from KB
        known_wumpus_positions = []
        for fact in self.agent.kb.facts:
            if fact.startswith('W(') and not fact.startswith('~W('):
                import re
                match = re.search(r'W\((\d+)[, ]+(\d+)\)', fact)
                if match:
                    wumpus_pos = (int(match.group(1)), int(match.group(2)))
                    known_wumpus_positions.append(wumpus_pos)
        
        if not known_wumpus_positions:
            print("  ℹ️ No known Wumpus positions found in KB")
            return None
            
        print(f"  🎯 Found {len(known_wumpus_positions)} known Wumpus positions: {known_wumpus_positions}")
        
        # Step 2: For each known Wumpus, find safe shooting positions
        for wumpus_pos in known_wumpus_positions:
            shooting_plan = self._find_safe_shooting_position(wumpus_pos)
            if shooting_plan:
                shooting_pos, target_pos, direction = shooting_plan
                print(f"  📍 Found shooting plan: Move to {shooting_pos}, face {direction}, shoot Wumpus at {target_pos}")
                
                # Step 3: Execute the shooting plan
                if self._execute_shooting_plan(shooting_pos, target_pos, direction):
                    return f"Successfully hunted Wumpus at {target_pos} - new paths opened!"
        
        print("  ❌ No safe shooting positions found for known Wumpus")
        return None
    
    def _find_safe_shooting_position(self, wumpus_pos):
        """Find a safe position from which we can shoot the Wumpus"""
        wi, wj = wumpus_pos
        
        # Check all 4 directions from Wumpus position
        shooting_directions = [
            ((wi-1, wj), (wi, wj), 'S'),  # Shoot from North to South
            ((wi+1, wj), (wi, wj), 'N'),  # Shoot from South to North  
            ((wi, wj-1), (wi, wj), 'E'),  # Shoot from West to East
            ((wi, wj+1), (wi, wj), 'W')   # Shoot from East to West
        ]
        
        for shooting_pos, target_pos, direction in shooting_directions:
            si, sj = shooting_pos
            
            # Check if shooting position is within bounds
            if not (0 <= si < self.agent.environment.N and 0 <= sj < self.agent.environment.N):
                continue
                
            # Check if shooting position is KB-safe (either visited or KB-confirmed)
            if not self._is_kb_safe(shooting_pos):
                continue
                
            # Check if we can reach this shooting position
            path_target, path = self._find_path_to_specific_position(shooting_pos)
            if path_target:
                return (shooting_pos, target_pos, direction)
        
        return None
    
    def _execute_shooting_plan(self, shooting_pos, target_pos, shoot_direction):
        """Execute the plan to move to shooting position and shoot Wumpus"""
        
        # If not at shooting position, move there first
        if self.agent.position != shooting_pos:
            print(f"  🚶‍♂️ Moving to shooting position {shooting_pos}")
            path_target, path = self._find_path_to_specific_position(shooting_pos)
            if path and len(path) > 0:
                # Move to first position in path
                next_pos = path[0]
                actions = self.agent.get_safe_moves()
                for pos, direction, risk in actions:
                    if pos == next_pos:
                        success = self._move_direction(direction)
                        if success:
                            print(f"    ✅ Moved to {next_pos} on way to shooting position")
                            return f"Moving to shooting position {shooting_pos}"
                        break
            return None
        
        # Now at shooting position, face the Wumpus and shoot
        print(f"  🎯 At shooting position {shooting_pos}, targeting Wumpus at {target_pos}")
        self._face_direction(shoot_direction)
        
        # Shoot the arrow
        if hasattr(self.agent, 'shoot') and self.agent.arrow_hit == 0:
            shot_success = self.agent.shoot()
            if shot_success:
                print(f"  🏹 Successfully shot Wumpus at {target_pos}!")
                
                # Update KB - mark Wumpus as dead and affected areas as safe
                self._update_kb_after_wumpus_kill(target_pos)
                return True
            else:
                print(f"  ❌ Arrow missed Wumpus at {target_pos}")
                return False
        else:
            print(f"  🚫 Cannot shoot: arrow_hit={self.agent.arrow_hit}")
        
        return False
    
    def _update_kb_after_wumpus_kill(self, wumpus_pos):
        """Update Knowledge Base after killing a Wumpus"""
        wi, wj = wumpus_pos
        
        # Mark Wumpus position as no longer having Wumpus
        self.agent.kb.add_fact(f"~W({wi},{wj})")
        print(f"    📝 Updated KB: Wumpus at ({wi},{wj}) is dead")
        
        # Mark Wumpus position as safe (no Wumpus, and pits can't be in same cell as Wumpus)
        self.agent.kb.add_fact(f"~P({wi},{wj})")
        self.agent.kb.add_fact(f"Safe({wi},{wj})")
        print(f"    ✅ Updated KB: ({wi},{wj}) is now SAFE")
        
        # Update adjacent cells - remove stench caused by this Wumpus
        adjacent_positions = [
            (wi-1, wj), (wi+1, wj), (wi, wj-1), (wi, wj+1)
        ]
        
        for adj_i, adj_j in adjacent_positions:
            if (0 <= adj_i < self.agent.environment.N and 0 <= adj_j < self.agent.environment.N):
                # Check if there are other Wumpus that could cause stench at this adjacent position
                other_wumpus_nearby = False
                for other_wi, other_wj in [(adj_i-1, adj_j), (adj_i+1, adj_j), (adj_i, adj_j-1), (adj_i, adj_j+1)]:
                    if (other_wi != wi or other_wj != wj):  # Not the Wumpus we just killed
                        if f"W({other_wi},{other_wj})" in self.agent.kb.facts:
                            other_wumpus_nearby = True
                            break
                
                # If no other Wumpus nearby, remove stench
                if not other_wumpus_nearby:
                    self.agent.kb.add_fact(f"~S({adj_i},{adj_j})")
                    print(f"    📝 Updated KB: No stench at ({adj_i},{adj_j}) - Wumpus killed")
                    
                    # If no breeze either, mark as safe
                    if self.agent.kb.is_premise_true(f"~B({adj_i},{adj_j})") == True:
                        self.agent.kb.add_fact(f"~P({adj_i},{adj_j})")
                        self.agent.kb.add_fact(f"Safe({adj_i},{adj_j})")
                        print(f"    ✅ Updated KB: ({adj_i},{adj_j}) is now SAFE (no stench, no breeze)")
        
        # Run forward chaining to deduce new facts
        self.agent.kb.forward_chain()
        
        # Reset navigation attempts to allow exploring newly safe areas
        self.navigation_attempts = 0
        print(f"    🔄 Reset navigation attempts - ready to explore newly safe areas")

# Alias for backwards compatibility
SafeFirstIntelligentAgent = KnowledgeBaseSafeAgent
