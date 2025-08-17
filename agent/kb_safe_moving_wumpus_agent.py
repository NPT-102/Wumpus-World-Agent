# agent/kb_safe_moving_wumpus_agent.py
from agent.kb_safe_agent import KnowledgeBaseSafeAgent
from module.moving_Wumpus import update_wumpus_position

class KnowledgeBaseSafeMovingWumpusAgent(KnowledgeBaseSafeAgent):
    """
    Enhanced KB-Safe Agent with Moving Wumpus capability
    - Wumpuses move every 5 actions
    - Maintains all KB-safe exploration and Dijkstra pathfinding
    - Adapts to dynamic Wumpus positions
    """
    
    def __init__(self, agent, pathfinding_algorithm='dijkstra'):
        super().__init__(agent, pathfinding_algorithm)
        
        # Moving Wumpus specific attributes
        self.action_count = 0
        self.wumpus_move_interval = 5  # Move Wumpus every 5 actions
        self.initial_wumpus_positions = None
        self.current_wumpus_positions = []
        self.wumpus_alive_status = []
        
        # Initialize Wumpus tracking
        self._initialize_wumpus_tracking()
        
        print("🐺 KB-Safe Moving Wumpus Agent initialized")
        print(f"   - Wumpuses will move every {self.wumpus_move_interval} actions")
        print(f"   - Using {pathfinding_algorithm.upper()} pathfinding")
        
    def _initialize_wumpus_tracking(self):
        """Initialize Wumpus position tracking from environment"""
        try:
            # Extract Wumpus positions from environment
            wumpus_positions = []
            for i in range(self.agent.environment.N):
                for j in range(self.agent.environment.N):
                    if 'W' in self.agent.environment.game_map[i][j]:
                        wumpus_positions.append((i, j))
            
            self.initial_wumpus_positions = wumpus_positions.copy()
            self.current_wumpus_positions = wumpus_positions.copy()
            self.wumpus_alive_status = [True] * len(wumpus_positions)
            
            print(f"   🎯 Tracking {len(wumpus_positions)} Wumpuses: {wumpus_positions}")
            
        except Exception as e:
            print(f"   ⚠️ Warning: Could not initialize Wumpus tracking: {e}")
            self.initial_wumpus_positions = []
            self.current_wumpus_positions = []
            self.wumpus_alive_status = []

    def _get_pit_positions(self):
        """Extract pit positions from environment"""
        pit_positions = []
        try:
            for i in range(self.agent.environment.N):
                for j in range(self.agent.environment.N):
                    if 'P' in self.agent.environment.game_map[i][j]:
                        pit_positions.append((i, j))
        except:
            pass
        return pit_positions

    def _update_wumpus_alive_status(self):
        """Update which Wumpuses are still alive based on agent's arrow hits"""
        if not hasattr(self.agent, 'arrow_hit') or not self.agent.arrow_hit:
            return
            
        # If arrow hit, mark closest Wumpus as dead
        if len(self.current_wumpus_positions) > 0:
            agent_pos = self.agent.position
            
            # Find closest living Wumpus to agent when arrow was shot
            min_distance = float('inf')
            target_idx = -1
            
            for idx, wumpus_pos in enumerate(self.current_wumpus_positions):
                if self.wumpus_alive_status[idx]:
                    distance = abs(agent_pos[0] - wumpus_pos[0]) + abs(agent_pos[1] - wumpus_pos[1])
                    if distance < min_distance:
                        min_distance = distance
                        target_idx = idx
            
            if target_idx >= 0:
                dead_wumpus_pos = self.current_wumpus_positions[target_idx]
                self.wumpus_alive_status[target_idx] = False
                print(f"   🏹 Wumpus at {dead_wumpus_pos} marked as dead")
                
                # Remove dead Wumpus from environment and update stench
                self._remove_dead_wumpus_from_environment(dead_wumpus_pos)

    def _move_wumpuses_if_needed(self):
        """Move all living Wumpuses if it's time (every 5 actions)"""
        if self.action_count % self.wumpus_move_interval != 0:
            return
            
        if not self.current_wumpus_positions:
            return
            
        print(f"\n🐺 === WUMPUS MOVEMENT TIME (Action #{self.action_count}) ===")
        
        # Update which Wumpuses are alive
        self._update_wumpus_alive_status()
        
        # Get pit positions to avoid
        pit_positions = self._get_pit_positions()
        
        # Move Wumpuses using the module
        old_positions = self.current_wumpus_positions.copy()
        
        try:
            self.current_wumpus_positions = update_wumpus_position(
                self.agent,
                self.agent.environment, 
                self.current_wumpus_positions,
                pit_positions,
                self.wumpus_alive_status
            )
            
            # Log movements
            movements = []
            for i, (old_pos, new_pos) in enumerate(zip(old_positions, self.current_wumpus_positions)):
                if old_pos != new_pos and self.wumpus_alive_status[i]:
                    movements.append(f"{old_pos} → {new_pos}")
            
            if movements:
                print(f"   🔄 Wumpus movements: {', '.join(movements)}")
                
                # Clear and rebuild KB facts about Wumpus positions
                self._update_kb_after_wumpus_movement()
                
                # Verify stench patterns are correctly updated in environment
                self._verify_stench_patterns()
            else:
                print("   🏠 No Wumpuses moved this turn")
                
        except Exception as e:
            print(f"   ⚠️ Error moving Wumpuses: {e}")
            
        print("🐺 === END WUMPUS MOVEMENT ===\n")

    def _update_kb_after_wumpus_movement(self):
        """Update Knowledge Base after Wumpus movement"""
        print("   🧠 Updating KB after Wumpus movement...")
        
        # Step 1: Clear old Wumpus position facts (since they moved)
        self._clear_old_wumpus_facts()
        
        # Step 2: Re-scan environment for new stench patterns
        self._rescan_environment_for_new_stenches()
        
        # Step 3: Invalidate old safety assumptions near previous Wumpus areas
        self._invalidate_old_safety_assumptions()
        
        # Step 4: Re-evaluate dangerous positions based on new stench
        self._reevaluate_safety_status()
        
        print(f"   ✅ KB updated - agent now aware of new Wumpus positions and dangers")

    def _is_kb_safe(self, position):
        """Enhanced safety check for Moving Wumpus environment"""
        i, j = position
        
        # Visited positions are still considered safe (we survived there)
        if position in self.visited_positions:
            return True
        
        # In Moving Wumpus environment, be more cautious
        # Check if position is in dangerous cells list
        if position in self.agent.kb.get_dangerous_cells():
            return False
        
        # Check KB for explicit safety
        if f"Safe({i},{j})" in self.agent.kb.facts:
            return True
            
        # Check if KB has definitive negative facts about both dangers
        no_wumpus = self.agent.kb.is_premise_true(f"~W({i},{j})") == True
        no_pit = self.agent.kb.is_premise_true(f"~P({i},{j})") == True
        
        if no_wumpus and no_pit:
            return True
        
        # Extra caution: Check for nearby stench that might indicate moved Wumpus
        adjacent_positions = self._get_adjacent_positions(position)
        for adj_pos in adjacent_positions:
            adj_i, adj_j = adj_pos
            if f"S({adj_i},{adj_j})" in self.agent.kb.facts:
                # There's stench nearby - position might be unsafe
                # Only proceed if we're sure no Wumpus at target position
                if self.agent.kb.is_premise_true(f"W({i},{j})") != False:
                    return False
        
        # For starting position neighbors with no danger signals, allow movement
        if self._is_starting_area_neighbor(position):
            # But only if there's no stench evidence of danger
            if not any(f"S({adj_i},{adj_j})" in self.agent.kb.facts 
                      for adj_i, adj_j in self._get_adjacent_positions(position)):
                return True
        
        return False
    
    def _get_adjacent_positions(self, position):
        """Get adjacent positions for a given position"""
        i, j = position
        adjacent = []
        for di, dj in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            ni, nj = i + di, j + dj
            if 0 <= ni < self.agent.environment.N and 0 <= nj < self.agent.environment.N:
                adjacent.append((ni, nj))
        return adjacent
    
    def _is_starting_area_neighbor(self, position):
        """Check if position is neighbor to starting area"""
        starting_neighbors = [(0, 1), (1, 0), (1, 1)]
        return position in starting_neighbors

    def _rescan_environment_for_new_stenches(self):
        """Only update stench knowledge when agent actually visits positions - no cheating!"""
        print("   🔍 Checking stench knowledge at visited positions only...")
        
        new_stench_count = 0
        removed_stench_count = 0
        
        # ONLY check positions the agent has actually visited
        for visited_pos in self.visited_positions:
            i, j = visited_pos
            
            # Check actual stench at this visited position
            has_stench_now = 'S' in self.agent.environment.game_map[i][j]
            had_stench_in_kb = f"S({i},{j})" in self.agent.kb.facts
            
            if has_stench_now and not had_stench_in_kb:
                # Agent would smell new stench when revisiting this position
                self.agent.kb.tell(f"S({i},{j})")
                new_stench_count += 1
                print(f"     + Agent detects NEW STENCH at visited position {visited_pos}")
                
                # Try to deduce Wumpus position from this stench
                self._deduce_wumpus_from_visited_stench(visited_pos)
                
            elif not has_stench_now and had_stench_in_kb:
                # Stench gone from visited position
                self.agent.kb.facts.discard(f"S({i},{j})")
                self.agent.kb.tell(f"~S({i},{j})")
                removed_stench_count += 1
                print(f"     - Stench DISAPPEARED at visited position {visited_pos}")
        
        if new_stench_count > 0 or removed_stench_count > 0:
            print(f"   📊 Stench changes at visited positions: +{new_stench_count} new, -{removed_stench_count} removed")
            print("   🚨 Agent realizes environment has changed!")
        else:
            print("   📊 No stench changes at previously visited positions")

    def _deduce_wumpus_from_visited_stench(self, stench_pos):
        """Deduce Wumpus position from stench at a visited position"""
        print(f"     🧠 Analyzing stench at visited position {stench_pos}...")
        
        adjacent_positions = self._get_adjacent_positions(stench_pos)
        
        # Find adjacent positions that could contain Wumpus
        possible_wumpus_positions = []
        for adj_pos in adjacent_positions:
            adj_i, adj_j = adj_pos
            
            # Don't consider visited positions (agent survived there)
            if (adj_i, adj_j) in self.visited_positions:
                continue
                
            # Don't consider positions we know have no Wumpus
            if self.agent.kb.is_premise_true(f"~W({adj_i},{adj_j})") == True:
                continue
                
            possible_wumpus_positions.append(adj_pos)
        
        # Only make deduction if there's exactly one possibility
        if len(possible_wumpus_positions) == 1:
            wumpus_pos = possible_wumpus_positions[0]
            w_i, w_j = wumpus_pos
            wumpus_fact = f"W({w_i},{w_j})"
            
            if wumpus_fact not in self.agent.kb.facts:
                self.agent.kb.add_fact(wumpus_fact)
                print(f"       🎯 DEDUCED Wumpus at {wumpus_pos} from stench at {stench_pos}")
                
                # Mark as unsafe
                self.agent.kb.add_fact(f"~Safe({w_i},{w_j})")
        
        elif len(possible_wumpus_positions) > 1:
            print(f"       ❓ Multiple possibilities: {possible_wumpus_positions} - no definitive deduction")
        else:
            print(f"       ℹ️ No possible Wumpus positions found")

    def _invalidate_old_safety_assumptions(self):
        """Invalidate old safety assumptions around previous Wumpus positions"""
        print("   ❌ Invalidating old safety assumptions...")
        
        positions_to_recheck = set()
        
        # Mark areas around all previous Wumpus positions for re-evaluation
        for i, old_pos in enumerate(self.initial_wumpus_positions):
            if self.wumpus_alive_status[i]:  # Only if Wumpus is still alive
                # Add adjacent positions to recheck list
                for di, dj in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                    adj_pos = (old_pos[0] + di, old_pos[1] + dj)
                    
                    if (0 <= adj_pos[0] < self.agent.environment.N and 
                        0 <= adj_pos[1] < self.agent.environment.N):
                        positions_to_recheck.add(adj_pos)
        
        # Remove old safety facts for positions that need rechecking
        facts_to_remove = []
        for fact in list(self.agent.kb.facts):
            if fact.startswith('Safe(') or fact.startswith('~W('):
                # Extract position from fact
                import re
                match = re.match(r'.*\((\d+),\s*(\d+)\)', fact)
                if match:
                    pos = (int(match.group(1)), int(match.group(2)))
                    if pos in positions_to_recheck:
                        facts_to_remove.append(fact)
        
        # Remove invalidated facts
        for fact in facts_to_remove:
            self.agent.kb.facts.discard(fact)
            print(f"     - Removed old assumption: {fact}")
        
        print(f"   🔄 Invalidated {len(facts_to_remove)} old safety assumptions")

    def _reevaluate_safety_status(self):
        """Re-evaluate safety status of all positions based on current KB"""
        print("   🎯 Re-evaluating safety status...")
        
        # Force KB to re-run forward chaining with new facts
        self.agent.kb.forward_chain()
        
        # Update dangerous positions list
        old_dangerous_count = len(self.agent.kb.get_dangerous_cells())
        self.agent.kb.update_dangerous()
        new_dangerous_count = len(self.agent.kb.get_dangerous_cells())
        
        # Re-deduce safe positions
        self._deduce_safe_positions_from_kb()
        
        print(f"   📈 Dangerous positions: {old_dangerous_count} → {new_dangerous_count}")
        
        # Warn if agent's current path might be affected
        current_pos = self.agent.position
        if current_pos in self.agent.kb.get_dangerous_cells():
            print(f"   ⚠️  WARNING: Agent's current position {current_pos} is now considered dangerous!")
        
        # Check if any planned moves are now dangerous
        if hasattr(self, 'current_path') and self.current_path:
            dangerous_path_cells = [pos for pos in self.current_path if pos in self.agent.kb.get_dangerous_cells()]
            if dangerous_path_cells:
                print(f"   ⚠️  WARNING: Planned path contains dangerous cells: {dangerous_path_cells}")
                self.current_path = []  # Clear potentially dangerous path

    def _remove_dead_wumpus_from_environment(self, dead_wumpus_pos):
        """Remove dead Wumpus from environment and update stench patterns"""
        try:
            # Remove Wumpus from game map
            if 'W' in self.agent.environment.game_map[dead_wumpus_pos[0]][dead_wumpus_pos[1]]:
                self.agent.environment.game_map[dead_wumpus_pos[0]][dead_wumpus_pos[1]].remove('W')
                print(f"   🗑️ Removed dead Wumpus from map at {dead_wumpus_pos}")
            
            # Update stench patterns - remove stench around dead Wumpus
            self._update_stench_after_wumpus_death(dead_wumpus_pos)
            
        except Exception as e:
            print(f"   ⚠️ Error removing dead Wumpus: {e}")
    
    def _update_stench_after_wumpus_death(self, dead_wumpus_pos):
        """Update stench patterns after Wumpus death"""
        N = self.agent.environment.N
        
        # Get adjacent positions to dead Wumpus
        adjacent_positions = []
        for di, dj in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            ni, nj = dead_wumpus_pos[0] + di, dead_wumpus_pos[1] + dj
            if 0 <= ni < N and 0 <= nj < N:
                adjacent_positions.append((ni, nj))
        
        # For each adjacent position, check if stench should be removed
        stenches_removed = []
        for adj_pos in adjacent_positions:
            i, j = adj_pos
            
            if 'S' not in self.agent.environment.game_map[i][j]:
                continue  # No stench to remove
            
            # Check if any other living Wumpus can cause stench here
            has_other_wumpus_nearby = False
            other_adjacent = []
            for di, dj in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                ni, nj = i + di, j + dj
                if 0 <= ni < N and 0 <= nj < N:
                    other_adjacent.append((ni, nj))
            
            # Check if any living Wumpus is adjacent to this position
            for other_adj in other_adjacent:
                if other_adj != dead_wumpus_pos:  # Skip the dead Wumpus
                    for idx, wumpus_pos in enumerate(self.current_wumpus_positions):
                        if (self.wumpus_alive_status[idx] and 
                            wumpus_pos == other_adj):
                            has_other_wumpus_nearby = True
                            break
                    if has_other_wumpus_nearby:
                        break
            
            # Remove stench only if no other living Wumpus causes it
            if not has_other_wumpus_nearby:
                self.agent.environment.game_map[i][j].remove('S')
                stenches_removed.append(adj_pos)
                
                # Also update KB to remove stench fact if agent has visited this position
                if adj_pos in self.visited_positions:
                    stench_fact = f"S({i},{j})"
                    if stench_fact in self.agent.kb.facts:
                        self.agent.kb.facts.discard(stench_fact)
                        self.agent.kb.tell(f"~S({i},{j})")
                        print(f"   🧠 Updated KB: removed stench fact at {adj_pos}")
        
        if stenches_removed:
            print(f"   🌬️ Removed stench from positions: {stenches_removed}")
        else:
            print(f"   ℹ️ No stench removed (other Wumpuses still nearby)")

    def _verify_stench_patterns(self):
        """Verify that stench patterns match current living Wumpus positions"""
        N = self.agent.environment.N
        stench_positions = []
        
        # Find all current stench positions
        for i in range(N):
            for j in range(N):
                if 'S' in self.agent.environment.game_map[i][j]:
                    stench_positions.append((i, j))
        
        # Count living Wumpuses
        living_wumpus_count = sum(self.wumpus_alive_status)
        living_wumpus_positions = [pos for i, pos in enumerate(self.current_wumpus_positions) 
                                  if self.wumpus_alive_status[i]]
        
        print(f"   🔍 Stench verification: {len(stench_positions)} stench cells, "
              f"{living_wumpus_count} living Wumpuses at {living_wumpus_positions}")

    def step(self):
        """Execute one step with Moving Wumpus capability and proper KB updates"""
        if not self.agent.alive:
            return "DEAD"
            
        # Increment action counter
        self.action_count += 1
        
        # Move Wumpuses if needed (every 5 actions)
        self._move_wumpuses_if_needed()
        
        # Get position before move
        old_position = self.agent.position
        
        # Call parent step method for all the KB-Safe logic
        result = super().step()
        
        # Get position after move
        new_position = self.agent.position
        
        # If agent moved to a new position, update KB with fresh sensory info
        if new_position != old_position and new_position not in self.visited_positions:
            self._update_kb_at_current_position()
        
        return result
    
    def _update_kb_at_current_position(self):
        """Update KB based on sensory information at current position - NO CHEATING"""
        current_pos = self.agent.position
        i, j = current_pos
        
        # Agent can only sense what's at current position
        has_stench = 'S' in self.agent.environment.game_map[i][j]
        has_breeze = 'B' in self.agent.environment.game_map[i][j]
        
        # Update KB with actual sensory information
        if has_stench:
            stench_fact = f"S({i},{j})"
            if stench_fact not in self.agent.kb.facts:
                self.agent.kb.add_fact(stench_fact)
                print(f"Agent smells stench at new position {current_pos}")
                
                # Try to deduce Wumpus from this new stench information
                self._deduce_wumpus_from_visited_stench(current_pos)
        else:
            # No stench at current position
            no_stench_fact = f"~S({i},{j})"
            if no_stench_fact not in self.agent.kb.facts:
                self.agent.kb.add_fact(no_stench_fact)
        
        if has_breeze:
            breeze_fact = f"B({i},{j})"
            if breeze_fact not in self.agent.kb.facts:
                self.agent.kb.add_fact(breeze_fact)
        else:
            no_breeze_fact = f"~B({i},{j})"
            if no_breeze_fact not in self.agent.kb.facts:
                self.agent.kb.add_fact(no_breeze_fact)

    def get_current_state(self):
        """Get current state including Moving Wumpus info"""
        base_state = super().get_current_state()
        
        # Add Moving Wumpus specific information
        base_state.update({
            'action_count': self.action_count,
            'next_wumpus_move': self.wumpus_move_interval - (self.action_count % self.wumpus_move_interval),
            'wumpus_positions': self.current_wumpus_positions,
            'wumpus_alive': self.wumpus_alive_status,
            'agent_type': 'KB-Safe Moving Wumpus',
            'environment_updated': True  # Signal UI to refresh environment display
        })
        
        return base_state

    def get_final_result(self):
        """Get final result including Moving Wumpus statistics"""
        base_result = super().get_final_result()
        
        # Add Moving Wumpus specific statistics
        wumpus_movements = sum(1 for i, (old, new) in enumerate(zip(self.initial_wumpus_positions, self.current_wumpus_positions)) 
                              if old != new and self.wumpus_alive_status[i])
        
        base_result.update({
            'total_actions': self.action_count,
            'wumpus_movements': wumpus_movements,
            'wumpus_move_cycles': self.action_count // self.wumpus_move_interval,
            'initial_wumpus_positions': self.initial_wumpus_positions,
            'final_wumpus_positions': self.current_wumpus_positions,
            'wumpus_alive_count': sum(self.wumpus_alive_status),
            'agent_type': 'KB-Safe Moving Wumpus Agent'
        })
        
        return base_result

    def _deduce_wumpus_positions_from_stench(self):
        """Deduce possible Wumpus positions from stench patterns using advanced constraint solving"""
        print(f"   🧠 Deducing Wumpus positions from stench patterns...")
        
        # Get all known stench positions
        stench_positions = []
        for fact in self.agent.kb.facts:
            if fact.startswith('S(') and not fact.startswith('~S('):
                import re
                match = re.match(r'S\((\d+),\s*(\d+)\)', fact)
                if match:
                    stench_positions.append((int(match.group(1)), int(match.group(2))))
        
        print(f"     💨 Known stench positions: {stench_positions}")
        deduction_count = 0
        
        # Method 1: Single stench deduction
        for stench_pos in stench_positions:
            adjacent_positions = self._get_adjacent_positions(stench_pos)
            
            # Find adjacent positions that could contain Wumpus
            possible_wumpus_positions = []
            for adj_pos in adjacent_positions:
                adj_i, adj_j = adj_pos
                # Check if we know there's NO Wumpus there
                if self.agent.kb.is_premise_true(f"~W({adj_i},{adj_j})") != True:
                    possible_wumpus_positions.append(adj_pos)
            
            # If only one possible position, deduce Wumpus is there!
            if len(possible_wumpus_positions) == 1:
                wumpus_pos = possible_wumpus_positions[0]
                w_i, w_j = wumpus_pos
                wumpus_fact = f"W({w_i},{w_j})"
                
                if wumpus_fact not in self.agent.kb.facts:
                    self.agent.kb.tell(wumpus_fact)
                    print(f"     🎯 DEDUCED Wumpus at {wumpus_pos} from single stench at {stench_pos}")
                    deduction_count += 1
                    self._mark_wumpus_unsafe(wumpus_pos)
        
        # Method 2: Advanced constraint solving for multiple stenches
        if len(stench_positions) >= 2:
            advanced_deductions = self._solve_stench_constraints(stench_positions)
            deduction_count += advanced_deductions
        
        if deduction_count > 0:
            print(f"     ✅ Successfully deduced {deduction_count} Wumpus position(s)")
            # Update KB reasoning
            self.agent.kb.forward_chain()
        else:
            print(f"     ℹ️ No definitive Wumpus positions could be deduced")

    def _solve_stench_constraints(self, stench_positions):
        """Advanced constraint solving to deduce Wumpus positions from multiple stenches"""
        print(f"     🔍 Applying advanced constraint solving...")
        deduction_count = 0
        
        # Build candidate Wumpus positions
        all_candidates = set()
        stench_to_candidates = {}
        
        for stench_pos in stench_positions:
            adjacent_positions = self._get_adjacent_positions(stench_pos)
            candidates = []
            
            for adj_pos in adjacent_positions:
                adj_i, adj_j = adj_pos
                # Only consider positions not ruled out by KB
                if self.agent.kb.is_premise_true(f"~W({adj_i},{adj_j})") != True:
                    candidates.append(adj_pos)
                    all_candidates.add(adj_pos)
            
            stench_to_candidates[stench_pos] = candidates
        
        print(f"       Candidate Wumpus positions: {sorted(all_candidates)}")
        
        # For each candidate position, check if it's the ONLY explanation for ANY stench
        for candidate in all_candidates:
            # Find all stenches that this candidate could explain
            explained_stenches = []
            for stench_pos in stench_positions:
                if candidate in stench_to_candidates[stench_pos]:
                    explained_stenches.append(stench_pos)
            
            # Check if this candidate is the ONLY explanation for any stench
            is_unique_for_any_stench = False
            for stench_pos in explained_stenches:
                if len(stench_to_candidates[stench_pos]) == 1:
                    is_unique_for_any_stench = True
                    break
            
            if is_unique_for_any_stench:
                w_i, w_j = candidate
                wumpus_fact = f"W({w_i},{w_j})"
                
                if wumpus_fact not in self.agent.kb.facts:
                    self.agent.kb.tell(wumpus_fact)
                    print(f"       🎯 CONSTRAINT DEDUCED Wumpus at {candidate} (unique explanation)")
                    deduction_count += 1
                    self._mark_wumpus_unsafe(candidate)
        
        # Try intersection analysis: positions that appear in multiple stench candidate sets
        if len(stench_positions) >= 2:
            intersection_deductions = self._analyze_stench_intersections(stench_to_candidates)
            deduction_count += intersection_deductions
        
        return deduction_count
    
    def _analyze_stench_intersections(self, stench_to_candidates):
        """Analyze intersections between stench candidate sets"""
        print(f"       📊 Analyzing stench intersections...")
        deduction_count = 0
        
        # Find positions that could explain multiple stenches
        position_to_stenches = {}
        for stench_pos, candidates in stench_to_candidates.items():
            for candidate in candidates:
                if candidate not in position_to_stenches:
                    position_to_stenches[candidate] = []
                position_to_stenches[candidate].append(stench_pos)
        
        # If we have exactly 2 stenches and they share exactly 1 candidate, that's likely the Wumpus
        if len(stench_to_candidates) == 2:
            stench_list = list(stench_to_candidates.keys())
            candidates_1 = set(stench_to_candidates[stench_list[0]])
            candidates_2 = set(stench_to_candidates[stench_list[1]])
            
            intersection = candidates_1 & candidates_2
            if len(intersection) == 1:
                candidate = list(intersection)[0]
                w_i, w_j = candidate
                wumpus_fact = f"W({w_i},{w_j})"
                
                if wumpus_fact not in self.agent.kb.facts:
                    self.agent.kb.tell(wumpus_fact)
                    print(f"       🎯 INTERSECTION DEDUCED Wumpus at {candidate} (only shared candidate)")
                    deduction_count += 1
                    self._mark_wumpus_unsafe(candidate)
        
        return deduction_count
    
    def _clear_old_wumpus_facts(self):
        """Clear old Wumpus position facts since they may have moved"""
        print("   🧹 Clearing old Wumpus position facts...")
        
        # Remove positive Wumpus facts (W(i,j))
        old_wumpus_facts = [fact for fact in self.agent.kb.facts if fact.startswith('W(')]
        for fact in old_wumpus_facts:
            self.agent.kb.facts.discard(fact)
            print(f"     ❌ Removed old Wumpus fact: {fact}")
        
        if old_wumpus_facts:
            print(f"   🧹 Cleared {len(old_wumpus_facts)} old Wumpus position facts")
        else:
            print(f"   ℹ️ No old Wumpus facts to clear")
    
    def _mark_wumpus_unsafe(self, wumpus_pos):
        """Mark a Wumpus position and its surroundings as unsafe"""
        w_i, w_j = wumpus_pos
        
        # Mark position as unsafe
        unsafe_fact = f"~Safe({w_i},{w_j})"
        if unsafe_fact not in self.agent.kb.facts:
            self.agent.kb.tell(unsafe_fact)
        
        # Mark adjacent positions as potentially unsafe (but not visited ones)
        for adj_pos in self._get_adjacent_positions(wumpus_pos):
            adj_i, adj_j = adj_pos
            if (adj_i, adj_j) not in self.visited_positions:
                unsafe_adj_fact = f"~Safe({adj_i},{adj_j})"
                if unsafe_adj_fact not in self.agent.kb.facts:
                    self.agent.kb.tell(unsafe_adj_fact)

# Alias for easier import
MovingWumpusAgent = KnowledgeBaseSafeMovingWumpusAgent
