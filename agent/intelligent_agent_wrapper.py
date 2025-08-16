"""
Wrapper for Intelligent Agent to work with step-by-step UI
"""

from agent.intelligent_agent import IntelligentAgent

class IntelligentAgentWrapper:
    def __init__(self, base_agent, max_risk_threshold=0.3):
        self.intelligent_agent = IntelligentAgent(base_agent, max_risk_threshold)
        self.action_count = 0
        
    def step(self):
        """Execute one step and track action count"""
        result, message = self.intelligent_agent.step()
        if result:  # Only increment if action was taken
            self.action_count += 1
        return result, message
    
    def get_current_state(self):
        """Get current state for UI display"""
        state = self.intelligent_agent.get_current_state()
        state['action_count'] = self.action_count
        return state
    
    def get_final_result(self):
        """Get final game result"""
        result = self.intelligent_agent.get_final_result()
        result['actions'] = self.action_count
        return result
