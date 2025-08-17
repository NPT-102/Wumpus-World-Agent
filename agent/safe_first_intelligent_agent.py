from agent.intelligent_agent import IntelligentAgent

class SafeFirstIntelligentAgent(IntelligentAgent):
    def __init__(self, base_agent, max_risk_threshold=0.2):
        super().__init__(base_agent, max_risk_threshold)
        self.agent_type_name = 'Safe-First Intelligent'
        self.safe_positions_found = set()
        self.position_history = []
        self.stuck_counter = 0
        
    def step(self):
        if not self.agent.alive:
            return False, "Agent is dead"
            
        current_pos = self.agent.position
        self.visited_positions.add(current_pos)
        
        # Track position history for stuck detection
        self.position_history.append(current_pos)
        if len(self.position_history) > 10:
            self.position_history.pop(0)
        
        # Check if we're repeating positions (stuck in loop)
        if len(self.position_history) >= 6:
            recent_positions = set(self.position_history[-6:])
            if len(recent_positions) <= 2:  # Only moving between 2 positions
                self.stuck_counter += 1
                if self.stuck_counter >= 3:
                    print(f" DETECTED STUCK LOOP: Repeating between {recent_positions}")
                    return self._handle_stuck_situation()
            else:
                self.stuck_counter = 0
        
        percepts = self.agent.environment.get_percept(current_pos)
        if "Glitter" in percepts and not self.agent.gold_obtain:
            if self.agent.grab_gold():
                self.returning_home = True
                return True, f"Grabbed gold at {current_pos}! Now returning home."
        
        if self.returning_home:
            return self._navigate_home()
        
        # Update safe positions from KB
        self._update_safe_positions()
            
        return self._explore_safely()
    
    def _handle_stuck_situation(self):
        """Handle when agent is stuck in a loop"""
        print(" STUCK DETECTED - Attempting Wumpus hunting to break free!")
        
        # Reset stuck counter
        self.stuck_counter = 0
        
        # Check if we have arrow to hunt Wumpus
        if hasattr(self.agent, 'arrow_hit') and self.agent.arrow_hit == 0:
            print(" Have arrow - trying to hunt Wumpus to open new paths!")
            hunt_result = self._try_hunt_wumpus_to_clear_path()
            if hunt_result[0]:
                return hunt_result
            else:
                print(" Could not hunt Wumpus from current position")
        else:
            print(" No arrow available")
        
        # If cannot hunt, try risky move to break free
        safe_moves = self.agent.get_safe_moves()
        if safe_moves:
            # Find move to unvisited position with moderate risk
            unvisited_moves = [(pos, direction, risk) for pos, direction, risk in safe_moves 
                             if pos not in self.visited_positions and risk <= 0.4]
            
            if unvisited_moves:
                pos, direction, risk = min(unvisited_moves, key=lambda x: x[2])
                success = self._move_direction(direction)
                print(f" BREAKING FREE: Moving to unvisited {pos} via {direction} (risk: {risk:.3f})")
                return success, f" Breaking free to unvisited {pos}"
            
            # Last resort: any move with reasonable risk
            moderate_moves = [(pos, direction, risk) for pos, direction, risk in safe_moves 
                            if risk <= 0.3 and not self._has_confirmed_danger(pos)]
            
            if moderate_moves:
                pos, direction, risk = min(moderate_moves, key=lambda x: x[2])
                success = self._move_direction(direction)
                print(f" DESPERATE MOVE: Risk {risk:.3f} to break loop")
                return success, f" Desperate move to break loop"
        
        print(" Completely stuck - cannot break free!")
        return False, "Agent completely stuck in loop"
    
    def _navigate_home(self):
        current_pos = self.agent.position
        if current_pos == (0, 0):
            return False, "Agent has reached home!"
            
        row, col = current_pos
        if row > 0:
            return self._move_direction("N"), "Moving home N"
        elif col > 0:
            return self._move_direction("W"), "Moving home W"
        else:
            return False, "Cannot navigate home"
    
    def _update_safe_positions(self):
        """Update safe positions from KB"""
        if hasattr(self.agent, 'kb'):
            facts = self.agent.kb.current_facts()
            new_safe = set()
            
            for row in range(self.agent.N):
                for col in range(self.agent.N):
                    pos = (row, col)
                    # Check if KB considers it safe
                    if self.agent.kb.is_safe(row, col):
                        new_safe.add(pos)
                    # Check if explicitly marked as no wumpus and no pit
                    elif f"~W({row}, {col})" in facts and f"~P({row}, {col})" in facts:
                        new_safe.add(pos)
            
            prev_count = len(self.safe_positions_found)
            self.safe_positions_found = new_safe
            
            if len(new_safe) > prev_count:
                print(f" Found {len(new_safe) - prev_count} new safe positions!")
                print(f" Safe positions: {sorted(list(new_safe))}")
    
    def _explore_safely(self):
        # Priority 1: Go to unvisited safe positions first
        unvisited_safe = self.safe_positions_found - self.visited_positions
        if unvisited_safe:
            return self._go_to_nearest_safe(unvisited_safe)
        
        # Priority 2: Get safe moves with strict safety check
        safe_moves = self.agent.get_safe_moves()
        
        truly_safe_moves = []
        for pos, direction, risk in safe_moves:
            if self._is_absolutely_safe(pos):
                truly_safe_moves.append((pos, direction, risk))
        
        # Priority 3: If no absolutely safe moves, try with low risk to unvisited
        if not truly_safe_moves:
            unvisited_moves = []
            for pos, direction, risk in safe_moves:
                if pos not in self.visited_positions and risk <= 0.25 and not self._has_confirmed_danger(pos):
                    unvisited_moves.append((pos, direction, risk))
            
            if unvisited_moves:
                pos, direction, risk = min(unvisited_moves, key=lambda x: x[2])
                success = self._move_direction(direction)
                print(f" NEW EXPLORATION: Moving to unvisited {pos} (risk: {risk:.3f})")
                return success, f" Exploring new area {pos}"
        
        # Priority 4: Use safe moves to visited positions
        if truly_safe_moves:
            # Prefer unvisited positions among safe moves
            unvisited_moves = [(pos, direction, risk) for pos, direction, risk in truly_safe_moves 
                              if pos not in self.visited_positions]
            
            if unvisited_moves:
                pos, direction, risk = min(unvisited_moves, key=lambda x: x[2])
            else:
                pos, direction, risk = min(truly_safe_moves, key=lambda x: x[2])
            
            success = self._move_direction(direction)
            return success, f" Safe move to {pos} via {direction} (risk: {risk:.3f})"
        
        # Priority 5: No safe moves - this should trigger stuck detection
        print(" NO SAFE MOVES - Should be handled by stuck detection!")
        return False, "No safe moves available"
    
    def _try_hunt_wumpus_to_clear_path(self):
        """Try to hunt Wumpus specifically to clear blocked paths"""
        if not hasattr(self.agent, 'kb') or self.agent.arrow_hit != 0:
            return False, "No arrow available"
        
        # Find confirmed Wumpus positions
        facts = self.agent.kb.current_facts()
        wumpus_positions = []
        
        # Look for explicit Wumpus facts W(i,j)
        for fact in facts:
            if fact.startswith('W(') and not fact.startswith('~W('):
                import re
                match = re.match(r'W\((\d+), (\d+)\)', fact)
                if match:
                    row, col = int(match.group(1)), int(match.group(2))
                    if 0 <= row < self.agent.N and 0 <= col < self.agent.N:
                        wumpus_positions.append((row, col))
        
        if not wumpus_positions:
            # If no explicit Wumpus facts, look for probable Wumpus using stench patterns
            print(" No explicit Wumpus facts - analyzing stench patterns...")
            wumpus_positions = self._find_probable_wumpus_from_stench()
        
        if not wumpus_positions:
            return False, "No Wumpus found to hunt"
        
        print(f" Found Wumpus to hunt: {wumpus_positions}")
        
        # Try to shoot each Wumpus from current position
        current_pos = self.agent.position
        for wumpus_pos in wumpus_positions:
            if self._can_shoot_wumpus_now(wumpus_pos):
                print(f" Can shoot Wumpus at {wumpus_pos} from current position {current_pos}")
                return self._shoot_wumpus_immediately(wumpus_pos)
        
        print(f" Cannot shoot any Wumpus from current position {current_pos}")
        print(f" Wumpus positions: {wumpus_positions}")
        
        return False, "Cannot shoot Wumpus from current position"
    
    def _find_probable_wumpus_from_stench(self):
        """Find probable Wumpus positions based on stench patterns"""
        if not hasattr(self.agent, 'kb'):
            return []
        
        facts = self.agent.kb.current_facts()
        probable_wumpus = []
        
        # Check each unvisited position for Wumpus probability
        for row in range(self.agent.N):
            for col in range(self.agent.N):
                pos = (row, col)
                
                # Skip visited positions and confirmed safe positions
                if pos in self.visited_positions:
                    continue
                if f"~W({row}, {col})" in facts:
                    continue
                
                # Check if position has strong stench indicators
                if self._has_strong_wumpus_evidence(row, col):
                    probable_wumpus.append(pos)
        
        return probable_wumpus
    
    def _has_strong_wumpus_evidence(self, row, col):
        """Check if position has strong evidence of containing Wumpus"""
        if not hasattr(self.agent, 'kb'):
            return False
        
        facts = self.agent.kb.current_facts()
        adjacent_positions = [(row-1, col), (row+1, col), (row, col-1), (row, col+1)]
        
        stench_count = 0
        visited_adjacent = 0
        
        for adj_row, adj_col in adjacent_positions:
            if 0 <= adj_row < self.agent.N and 0 <= adj_col < self.agent.N:
                if (adj_row, adj_col) in self.visited_positions:
                    visited_adjacent += 1
                    # Check for stench at adjacent visited position
                    stench_fact = f"S({adj_row}, {adj_col})"
                    if stench_fact in facts:
                        stench_count += 1
        
        # Strong evidence if most adjacent visited cells have stench
        return visited_adjacent >= 1 and stench_count >= visited_adjacent * 0.8
    
    def _can_shoot_wumpus_now(self, wumpus_pos):
        """Check if we can shoot Wumpus from current position"""
        current_pos = self.agent.position
        wrow, wcol = wumpus_pos
        crow, ccol = current_pos
        
        print(f" Checking if can shoot Wumpus at {wumpus_pos} from {current_pos}")
        
        # Can shoot if in same row or column and no obstacles
        if wrow == crow and wcol != ccol:
            print(f" Same row: can shoot {'East' if wcol > ccol else 'West'}")
            return True
        elif wcol == ccol and wrow != crow:
            print(f" Same column: can shoot {'South' if wrow > crow else 'North'}")
            return True
        
        print(f" Cannot shoot: not aligned (different row AND column)")
        return False
    
    def _shoot_wumpus_immediately(self, wumpus_pos):
        """Shoot at Wumpus from current position"""
        current_pos = self.agent.position
        wrow, wcol = wumpus_pos
        crow, ccol = current_pos
        
        # Determine direction
        if wrow == crow:
            direction = "E" if wcol > ccol else "W"
        else:
            direction = "S" if wrow > crow else "N"
        
        # Face target
        self._face_direction(direction)
        
        # Shoot
        print(f" SHOOTING at Wumpus {wumpus_pos} from {current_pos} facing {direction}")
        hit = self.agent.shoot()
        
        if hit:
            print(f" WUMPUS KILLED! {wumpus_pos} eliminated! New paths should open!")
            # Clear the area around killed Wumpus as potentially safe
            self._mark_wumpus_area_safe(wumpus_pos)
            return True, f" Successfully killed Wumpus at {wumpus_pos}!"
        else:
            print(f" ARROW MISSED! No Wumpus at {wumpus_pos} or arrow missed")
            return True, f" Arrow missed target at {wumpus_pos}"
    
    def _mark_wumpus_area_safe(self, wumpus_pos):
        """Mark area around killed Wumpus as potentially safer for future exploration"""
        wrow, wcol = wumpus_pos
        print(f" Marking area around killed Wumpus {wumpus_pos} for re-evaluation")
        
        # Add adjacent positions back to exploration queue
        adjacent_positions = [(wrow-1, wcol), (wrow+1, wcol), (wrow, wcol-1), (wrow, wcol+1)]
        for adj_pos in adjacent_positions:
            adj_row, adj_col = adj_pos
            if (0 <= adj_row < self.agent.N and 0 <= adj_col < self.agent.N and 
                adj_pos not in self.visited_positions):
                print(f" Adjacent position {adj_pos} may now be safer to explore")
    
    def _go_to_nearest_safe(self, safe_positions):
        """Go to nearest unvisited safe position"""
        current_pos = self.agent.position
        nearest = min(safe_positions, key=lambda pos: self._distance(current_pos, pos))
        
        print(f" Targeting safe position: {nearest}")
        
        # Try to move toward nearest safe position
        safe_moves = self.agent.get_safe_moves()
        best_move = None
        best_distance = float('inf')
        
        for pos, direction, risk in safe_moves:
            if self._is_absolutely_safe(pos):
                distance = self._distance(pos, nearest)
                if distance < best_distance:
                    best_distance = distance
                    best_move = (pos, direction, risk)
        
        if best_move:
            pos, direction, risk = best_move
            success = self._move_direction(direction)
            return success, f" Moving toward safe {nearest} via {direction}"
        else:
            return False, "Cannot reach safe position"
    
    def _is_absolutely_safe(self, pos):
        """Check if position is absolutely safe - no confirmed dangers"""
        row, col = pos
        if not (0 <= row < self.agent.N and 0 <= col < self.agent.N):
            return False
            
        if not hasattr(self.agent, 'kb'):
            return False
            
        facts = self.agent.kb.current_facts()
        
        # NEVER go to confirmed dangerous positions
        if f"W({row}, {col})" in facts or f"P({row}, {col})" in facts:
            print(f" DANGER AVOIDED: {pos} has confirmed Wumpus/Pit!")
            return False
        
        # Position is safe if confirmed no wumpus AND no pit
        no_wumpus = f"~W({row}, {col})" in facts
        no_pit = f"~P({row}, {col})" in facts
        
        if no_wumpus and no_pit:
            return True
            
        # Use KB safety check
        return self.agent.kb.is_safe(row, col)
    
    def _has_confirmed_danger(self, pos):
        """Check if position has confirmed Wumpus or Pit"""
        row, col = pos
        if not hasattr(self.agent, 'kb'):
            return False
            
        facts = self.agent.kb.current_facts()
        return f"W({row}, {col})" in facts or f"P({row}, {col})" in facts
    
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
    
    def _distance(self, pos1, pos2):
        """Calculate Manhattan distance"""
        return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])
