"""
Test anti-cheat functionality - Make sure UI only shows information agent actually knows
"""
import sys
from agent.intelligent_agent_dynamic import IntelligentAgentDynamic
from stepwise_agent import StepByStepHybridAgent 
from agent.agent import Agent

def test_anticheat():
    print("=== TESTING ANTI-CHEAT FUNCTIONALITY ===")
    
    # Create agent starting at (0,0)
    agent = Agent(start_position=(0, 0))
    intelligent_agent = IntelligentAgentDynamic(agent)
    step_agent = StepByStepHybridAgent(intelligent_agent)
    
    print(f"Agent started at: {agent.position}")
    print(f"Agent visited: {step_agent.get_current_state()['visited']}")
    print()
    
    # Take one step
    print("=== TAKING ONE STEP ===")
    success, message = step_agent.step()
    print(f"Step result: {success}, {message}")
    
    current_state = step_agent.get_current_state()
    print(f"Agent position: {current_state['position']}")
    print(f"Agent visited: {current_state['visited']}")
    print(f"Agent perceptions: {agent.perception}")
    print()
    
    # Check what agent should know vs what's in the map
    print("=== ANTI-CHEAT VERIFICATION ===")
    game_map = agent.environment.map
    visited = set(current_state['visited'])
    
    print("What agent SHOULD know (visited positions only):")
    for pos in visited:
        row, col = pos
        cell_content = game_map[row][col]
        print(f"  Position {pos}: {cell_content}")
    
    print("\nWhat agent SHOULD NOT see (unvisited positions):")
    for row in range(agent.environment.grid_size):
        for col in range(agent.environment.grid_size):
            if (row, col) not in visited and (row, col) != agent.position:
                cell_content = game_map[row][col]
                if 'S' in cell_content or 'B' in cell_content or 'W' in cell_content or 'P' in cell_content:
                    print(f"  Position ({row}, {col}): {cell_content} <- MUST NOT BE SHOWN IN UI")
    
    print("\n=== CONCLUSION ===")
    print("✅ UI should ONLY show S/B for positions in visited list")
    print("❌ UI must NOT show any S/B/W/P for unvisited positions")
    print(f"✅ Visited positions: {list(visited)}")
    print(f"🔍 Current position: {current_state['position']} (can see glitter if gold present)")
    
if __name__ == "__main__":
    test_anticheat()
