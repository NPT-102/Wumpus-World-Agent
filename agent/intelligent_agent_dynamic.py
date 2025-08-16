"""
Intelligent Agent Dynamic for Wumpus World - advanced AI with Wumpus movement every 5 actions
"""
from agent.intelligent_agent import IntelligentAgent

class IntelligentAgentDynamic(IntelligentAgent):
    def __init__(self, base_agent, max_risk_threshold=0.3):
        super().__init__(base_agent, max_risk_threshold)
        self.wumpus_move_counter = 0
        self.wumpus_move_interval = 5
        self.agent_type_name = 'Intelligent Dynamic'
        
    def step(self):
        """Execute one intelligent step with dynamic Wumpus movement"""
        if not self.agent.alive:
            return False, "Game Over"
        
        # Check if Wumpus should move (every 5 actions)
        if self.wumpus_move_counter >= self.wumpus_move_interval:
            self._trigger_wumpus_movement()
            self.wumpus_move_counter = 0
            
            # Check if agent got eaten by moved Wumpus
            if self._check_wumpus_danger():
                self.agent.alive = False
                self.agent.score -= 1000
                return False, f"Agent was eaten by moving Wumpus at {self.agent.position}!"
        
        # Execute normal intelligent step
        continue_game, message = super().step()
        
        # Increment movement counter for Wumpus
        self.wumpus_move_counter += 1
        
        return continue_game, message
    
    def _trigger_wumpus_movement(self):
        """Trigger Wumpus movement in environment"""
        # Call environment method to move Wumpus
        if hasattr(self.agent.environment, 'move_wumpus'):
            self.agent.environment.move_wumpus()
            
            # Update our risk calculations since Wumpus moved
            self._update_knowledge_after_wumpus_move()
        
        print(f"Wumpus moved after {self.wumpus_move_interval} actions!")
    
    def _update_knowledge_after_wumpus_move(self):
        """Update agent's knowledge after Wumpus movement"""
        # Wumpus movement makes our stench-based risk calculations potentially outdated
        # Clear the risk calculator cache to force recalculation with new percepts
        if hasattr(self, 'risk_calculator'):
            # Force risk recalculation on next step
            self.risk_calculator = self.agent.environment.get_risk_calculator()
        
        # Update our exploration strategy to be more adaptive
        # Positions we thought were dangerous due to stench might now be safe
        # Will be updated through normal perception on next moves
    
    def _check_wumpus_danger(self):
        """Check if agent is in immediate danger from Wumpus"""
        # Environment will handle Wumpus encounters directly
        # This is just a placeholder for additional safety checks
        return False
    
    def _choose_next_action(self, safe_moves, risky_moves):
        """Choose next action with dynamic Wumpus consideration"""
        # If Wumpus is about to move, be more conservative
        if self.wumpus_move_counter >= self.wumpus_move_interval - 1:
            # Prefer staying in known safe areas when Wumpus about to move
            current_pos = self.agent.position
            
            # Check if we can stay in a previously visited safe position
            for move_type, position, direction, risk in safe_moves:
                if position in self.visited_positions:
                    return move_type, position, direction, risk, f"Staying safe before Wumpus move - {move_type} to {position}"
            
            # If no previously visited safe moves, be extra cautious with risk
            ultra_safe_moves = [(mt, pos, d, r) for mt, pos, d, r in safe_moves if r < self.risk_threshold * 0.5]
            if ultra_safe_moves:
                return self._select_best_move(ultra_safe_moves, "ultra-safe before Wumpus move")
        
        # Use parent class logic for normal situations
        return super()._choose_next_action(safe_moves, risky_moves)
    
    def _explore_intelligently(self):
        """Intelligent exploration with dynamic Wumpus adaptation"""
        # Get current state
        current_pos = self.agent.position
        percepts = self.agent.environment.get_percept(current_pos)
        
        # If Wumpus recently moved, be more careful about stench interpretation
        recent_wumpus_move = self.wumpus_move_counter <= 2
        
        # Use parent exploration but adjust risk tolerance
        if recent_wumpus_move:
            # Temporarily reduce risk tolerance after Wumpus movement
            original_threshold = self.risk_threshold
            self.risk_threshold *= 0.7  # Be more conservative
            
            result = super()._explore_intelligently()
            
            # Restore original threshold
            self.risk_threshold = original_threshold
            return result
        else:
            return super()._explore_intelligently()
    
    def get_current_state(self):
        """Get current state for UI display"""
        state = super().get_current_state()
        state['agent_type'] = self.agent_type_name
        state['wumpus_move_counter'] = self.wumpus_move_counter
        state['wumpus_move_interval'] = self.wumpus_move_interval
        state['wumpus_moves_in'] = self.wumpus_move_interval - self.wumpus_move_counter
        return state
