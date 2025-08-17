"""
Environment interface for Wumpus World - provides only perception-based information
No direct map access allowed for agents
"""

class WumpusEnvironment:
    def __init__(self, game_map, wumpus_positions, pit_positions):
        self.game_map = game_map
        self.wumpus_positions = wumpus_positions
        self.pit_positions = pit_positions
        self.N = len(game_map)
        self.gold_collected = False
        
    def get_percept(self, position):
        """Get percepts at given position - this is the ONLY way agents can sense environment"""
        i, j = position
        
        if not (0 <= i < self.N and 0 <= j < self.N):
            return ["OutOfBounds"]
        
        cell_contents = self.game_map[i][j]
        percepts = []
        
        # Check for deadly elements first
        if "W" in cell_contents or "P" in cell_contents:
            if "W" in cell_contents:
                percepts.append("Death_Wumpus")
            if "P" in cell_contents:
                percepts.append("Death_Pit")
            return percepts
        
        # Normal percepts
        if "S" in cell_contents:
            percepts.append("Stench")
        else:
            percepts.append("NoStench")
            
        if "B" in cell_contents:
            percepts.append("Breeze")
        else:
            percepts.append("NoBreeze")
            
        if "G" in cell_contents and not self.gold_collected:
            percepts.append("Glitter")
        else:
            percepts.append("NoGlitter")
            
        return percepts
    
    def get_wumpus_count(self):
        """Get the total number of wumpus in the world"""
        return len(self.wumpus_positions)
    
    def grab_gold(self, position):
        """Try to grab gold at position"""
        i, j = position
        if "G" in self.game_map[i][j] and not self.gold_collected:
            self.game_map[i][j].remove("G")
            self.gold_collected = True
            return True
        return False
    
    def shoot_arrow(self, position, direction):
        """Shoot arrow from position in given direction"""
        from agent.agent import MOVE
        
        mi, mj = MOVE[direction]
        i, j = position
        hit_any = False
        
        i += mi
        j += mj
        while (0 <= i < self.N) and (0 <= j < self.N):
            if "W" in self.game_map[i][j]:
                self.game_map[i][j].remove("W")
                hit_any = True
                print(f"Scream! Wumpus at {(i,j)} is dead.")
                
                # Remove Stench around dead Wumpus more carefully
                self._remove_stench_around_dead_wumpus(i, j)
                
                # Update wumpus positions
                if (i, j) in self.wumpus_positions:
                    self.wumpus_positions.remove((i, j))
                break
                
            i += mi
            j += mj
            
        return hit_any
    
    def _remove_stench_around_dead_wumpus(self, dead_wumpus_row, dead_wumpus_col):
        """Remove stench around dead Wumpus, but only if no other living Wumpus causes it"""
        adjacent_positions = []
        for di, dj in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            ni, nj = dead_wumpus_row + di, dead_wumpus_col + dj
            if (0 <= ni < self.N) and (0 <= nj < self.N):
                adjacent_positions.append((ni, nj))
        
        for adj_pos in adjacent_positions:
            ni, nj = adj_pos
            if "S" in self.game_map[ni][nj]:
                # Check if any other living Wumpus can cause stench at this position
                has_other_wumpus_causing_stench = False
                
                # Check all positions adjacent to this stench position
                for di2, dj2 in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                    check_i, check_j = ni + di2, nj + dj2
                    if (0 <= check_i < self.N) and (0 <= check_j < self.N):
                        # Skip the dead Wumpus position
                        if (check_i, check_j) == (dead_wumpus_row, dead_wumpus_col):
                            continue
                        # If there's another Wumpus here, it can cause the stench
                        if "W" in self.game_map[check_i][check_j]:
                            has_other_wumpus_causing_stench = True
                            break
                
                # Remove stench only if no other Wumpus causes it
                if not has_other_wumpus_causing_stench:
                    self.game_map[ni][nj].remove("S")
                    print(f"Removed stench at {(ni, nj)} - no more Wumpus nearby")
    
    def is_valid_position(self, position):
        """Check if position is within bounds"""
        i, j = position
        return 0 <= i < self.N and 0 <= j < self.N
    
    def move_wumpus(self):
        """Move Wumpuses to random adjacent positions (for dynamic agent)"""
        import random
        
        new_wumpus_positions = []
        
        for wumpus_pos in self.wumpus_positions:
            i, j = wumpus_pos
            
            # Remove current stench
            for di, dj in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                ni, nj = i + di, j + dj
                if self.is_valid_position((ni, nj)) and "S" in self.game_map[ni][nj]:
                    self.game_map[ni][nj].remove("S")
            
            # Remove Wumpus from current position
            if "W" in self.game_map[i][j]:
                self.game_map[i][j].remove("W")
            
            # Find valid adjacent positions
            adjacent_positions = []
            for di, dj in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                ni, nj = i + di, j + dj
                if (self.is_valid_position((ni, nj)) and 
                    "P" not in self.game_map[ni][nj]):  # Don't move into pits
                    adjacent_positions.append((ni, nj))
            
            # If no valid adjacent positions, stay in place
            if not adjacent_positions:
                new_pos = (i, j)
            else:
                # Move to random adjacent position
                new_pos = random.choice(adjacent_positions)
            
            new_wumpus_positions.append(new_pos)
            
            # Add Wumpus to new position
            ni, nj = new_pos
            if "W" not in self.game_map[ni][nj]:
                self.game_map[ni][nj].append("W")
            
            # Add stench around new position
            for di, dj in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                si, sj = ni + di, nj + dj
                if self.is_valid_position((si, sj)) and "S" not in self.game_map[si][sj]:
                    self.game_map[si][sj].append("S")
        
        # Update wumpus positions
        self.wumpus_positions = new_wumpus_positions
        return new_wumpus_positions
