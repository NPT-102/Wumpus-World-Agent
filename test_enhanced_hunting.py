#!/usr/bin/env python3
"""
Test enhanced Wumpus hunting strategy
"""

from agent.kb_safe_agent import SafeFirstIntelligentAgent
from env_simulator.generateMap import WumpusWorldGenerator
from agent.agent import Agent

def test_enhanced_hunting():
    """Test enhanced Wumpus hunting strategy"""
    print("=== TESTING ENHANCED WUMPUS HUNTING STRATEGY ===")
    
    # Create a custom map where we know Wumpus positions  
    generator = WumpusWorldGenerator(4)
    game_map = generator.create_map_single_gold()
    game_map.wumpus_position = [(2, 1)]  # Single Wumpus at (2,1)
    game_map.pit_positions = [(1, 2)]    # Single pit at (1,2)  
    game_map.gold_position = (3, 3)      # Gold far away
    
    print(f"Test Map:")
    print(f"  Wumpus at: {game_map.wumpus_position}")
    print(f"  Pits at: {game_map.pit_positions}")
    print(f"  Gold at: {game_map.gold_position}")
    
    # Create Safe-First agent
    agent = Agent(game_map)
    safe_agent = SafeFirstIntelligentAgent(agent)
    
    step_count = 0
    max_steps = 50
    
    print("\n=== AGENT EXPLORATION LOG ===")
    
    while not agent.is_dead() and step_count < max_steps:
        step_count += 1
        
        # Run one step
        success, message = safe_agent.step()
        
        print(f"Step {step_count}: {message}")
        
        if not success or "Final score" in message:
            break
            
        # Check if agent found and grabbed gold
        if agent.gold_obtain and agent.position == (0, 0):
            print(f"\n🏆 SUCCESS! Agent completed mission with gold!")
            break
    
    print(f"\n=== FINAL RESULTS ===")
    print(f"Steps taken: {step_count}")
    print(f"Final position: {agent.position}")
    print(f"Score: {agent.score}")
    print(f"Gold obtained: {agent.gold_obtain}")
    print(f"Agent alive: {not agent.is_dead()}")
    print(f"Arrow used: {agent.arrow_hit > 0}")
    
    # Check if enhanced hunting was used
    if hasattr(safe_agent, 'visited_positions'):
        print(f"Positions explored: {len(safe_agent.visited_positions)}")
        print(f"Visited positions: {sorted(list(safe_agent.visited_positions))}")
    
    return agent.gold_obtain and not agent.is_dead() and agent.position == (0, 0)

if __name__ == "__main__":
    success = test_enhanced_hunting()
    if success:
        print("\n✅ ENHANCED WUMPUS HUNTING STRATEGY TEST PASSED!")
    else:
        print("\n❌ Test failed - agent did not complete mission successfully")
