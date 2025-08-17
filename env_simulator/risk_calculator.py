"""
Risk Calculator for Wumpus World - calculates probability of danger in each cell
"""
class RiskCalculator:
    def __init__(self, N):
        self.N = N
        self.visited = set()
        self.safe_cells = set()
        self.dangerous_cells = set()
        self.stench_cells = set()
        self.breeze_cells = set()
        self.no_stench_cells = set()
        self.no_breeze_cells = set()
        
    def update_perception(self, position, percepts):
        """Update risk calculations based on new perceptions"""
        self.visited.add(position)
        
        if "Stench" in percepts:
            self.stench_cells.add(position)
        else:
            self.no_stench_cells.add(position)
            
        if "Breeze" in percepts:
            self.breeze_cells.add(position)
        else:
            self.no_breeze_cells.add(position)
            
        # Mark current position as safe (agent didn't die)
        self.safe_cells.add(position)
    
    def calculate_wumpus_probability(self, position):
        """Calculate probability of Wumpus at given position"""
        if position in self.visited or position in self.safe_cells:
            return 0.0
            
        if position in self.dangerous_cells:
            return 1.0
            
        i, j = position
        if not (0 <= i < self.N and 0 <= j < self.N):
            return 1.0  # Out of bounds = dangerous
            
        # Base probability (assume uniform distribution of remaining Wumpuses)
        unvisited_cells = []
        for x in range(self.N):
            for y in range(self.N):
                if (x, y) not in self.visited and (x, y) not in self.safe_cells:
                    unvisited_cells.append((x, y))
        
        if not unvisited_cells:
            return 0.0
            
        base_prob = 1.0 / len(unvisited_cells)  # Assume 1 Wumpus remaining on average
        
        # Adjust based on stench evidence
        stench_evidence = 0
        no_stench_evidence = 0
        
        adjacent_cells = self.get_adjacent_cells(position)
        for adj_cell in adjacent_cells:
            if adj_cell in self.stench_cells:
                stench_evidence += 1
            elif adj_cell in self.no_stench_cells:
                no_stench_evidence += 1
        
        # Bayesian update
        if stench_evidence > 0:
            # Higher probability if adjacent to stench
            prob_multiplier = 1 + (stench_evidence * 2)
            base_prob *= prob_multiplier
        
        if no_stench_evidence > 0:
            # Lower probability if adjacent to no-stench cells
            prob_divisor = 1 + (no_stench_evidence * 0.5)
            base_prob /= prob_divisor
        
        return min(1.0, base_prob)
    
    def calculate_pit_probability(self, position):
        """Calculate probability of pit at given position"""
        if position in self.visited or position in self.safe_cells:
            return 0.0
            
        if position in self.dangerous_cells:
            return 1.0
            
        i, j = position
        if not (0 <= i < self.N and 0 <= j < self.N):
            return 1.0  # Out of bounds = dangerous
            
        # Base pit probability (typically 0.2 in Wumpus World)
        base_prob = 0.2
        
        # Adjust based on breeze evidence
        breeze_evidence = 0
        no_breeze_evidence = 0
        
        adjacent_cells = self.get_adjacent_cells(position)
        for adj_cell in adjacent_cells:
            if adj_cell in self.breeze_cells:
                breeze_evidence += 1
            elif adj_cell in self.no_breeze_cells:
                no_breeze_evidence += 1
        
        # Bayesian update
        if breeze_evidence > 0:
            # Higher probability if adjacent to breeze
            prob_multiplier = 1 + (breeze_evidence * 3)
            base_prob *= prob_multiplier
        
        if no_breeze_evidence > 0:
            # Lower probability if adjacent to no-breeze cells
            prob_divisor = 1 + (no_breeze_evidence * 2)
            base_prob /= prob_divisor
        
        return min(1.0, base_prob)
    
    def calculate_total_risk(self, position):
        """Calculate total risk (death probability) at given position"""
        wumpus_prob = self.calculate_wumpus_probability(position)
        pit_prob = self.calculate_pit_probability(position)
        
        # Probability of survival = (1 - wumpus_prob) * (1 - pit_prob)
        # Probability of death = 1 - survival_prob
        survival_prob = (1 - wumpus_prob) * (1 - pit_prob)
        risk = 1 - survival_prob
        
        return risk
    
    def get_adjacent_cells(self, position):
        """Get adjacent cells to given position"""
        i, j = position
        adjacent = []
        for di, dj in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            ni, nj = i + di, j + dj
            if 0 <= ni < self.N and 0 <= nj < self.N:
                adjacent.append((ni, nj))
        return adjacent
    
    def find_safest_move(self, current_position, possible_moves):
        """Find the safest move among possible options"""
        if not possible_moves:
            return None
            
        move_risks = []
        for move in possible_moves:
            risk = self.calculate_total_risk(move)
            move_risks.append((move, risk))
        
        # Sort by risk (lowest first)
        move_risks.sort(key=lambda x: x[1])
        
        return move_risks[0][0]  # Return safest move
    
    def get_exploration_candidates(self, current_position, max_distance=3):
        """Get candidate cells for exploration, sorted by risk"""
        candidates = []
        
        for i in range(self.N):
            for j in range(self.N):
                if (i, j) not in self.visited and (i, j) not in self.safe_cells:
                    # Calculate Manhattan distance
                    distance = abs(i - current_position[0]) + abs(j - current_position[1])
                    if distance <= max_distance:
                        risk = self.calculate_total_risk((i, j))
                        candidates.append(((i, j), risk, distance))
        
        # Sort by risk first, then by distance
        candidates.sort(key=lambda x: (x[1], x[2]))
        
        return [pos for pos, risk, dist in candidates]
