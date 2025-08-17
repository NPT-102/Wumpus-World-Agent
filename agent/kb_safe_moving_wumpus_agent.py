# agent/kb_safe_moving_wumpus_agent.py
from agent.kb_safe_agent import KnowledgeBaseSafeAgent
from module.moving_Wumpus import update_wumpus_position
from search.kb_pathfinding import kb_safe_dijkstra

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
        
        # We can't know exactly where Wumpuses moved, but we can:
        # 1. Keep our safe/unsafe classifications for positions we've visited
        # 2. Be more cautious about previously "safe" positions near old Wumpus locations
        # 3. Update our understanding based on new stench patterns we encounter
        
        # Mark areas near previous Wumpus positions as potentially unsafe
        for i, old_pos in enumerate(self.initial_wumpus_positions):
            if self.wumpus_alive_status[i]:  # Only if this Wumpus is still alive
                # Adjacent positions to old Wumpus location might now be safe or unsafe
                for di, dj in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                    adj_pos = (old_pos[0] + di, old_pos[1] + dj)
                    
                    if (0 <= adj_pos[0] < self.agent.environment.N and 
                        0 <= adj_pos[1] < self.agent.environment.N and
                        adj_pos not in self.visited_positions):
                        
                        # Remove strong assumptions about these positions
                        fact_key = f"safe_{adj_pos[0]}_{adj_pos[1]}"
                        if fact_key in self.agent.kb.facts:
                            del self.agent.kb.facts[fact_key]
                            
        print(f"   ✅ KB updated - being more cautious about {len(self.initial_wumpus_positions)} Wumpus areas")

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
            if not has_other_wumpus_nearby and 'S' in self.agent.environment.game_map[i][j]:
                self.agent.environment.game_map[i][j].remove('S')
                stenches_removed.append(adj_pos)
        
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
        """Execute one step with Moving Wumpus capability"""
        if not self.agent.alive:
            return "DEAD"
            
        # Increment action counter
        self.action_count += 1
        
        # Move Wumpuses if needed (every 5 actions)
        self._move_wumpuses_if_needed()
        
        # Call parent step method for all the KB-Safe logic
        result = super().step()
        
        return result

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

# Alias for easier import
MovingWumpusAgent = KnowledgeBaseSafeMovingWumpusAgent
