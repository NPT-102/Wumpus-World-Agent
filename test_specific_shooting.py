#!/usr/bin/env python3
"""Test the specific shooting scenario that failed."""

from env_simulator.generateMap import print_map
from agent.agent import Agent
from agent.hybrid_agent_action_dynamic import hybrid_agent_action_dynamic

def test_specific_shooting_scenario():
    """Test the exact scenario that failed with improved shooting logic."""
    print("Testing specific shooting scenario...")
    print("Original problem: Agent at (3,1) should shoot towards Wumpuses at (1,1) and (2,0)")
    
    # Recreate the exact scenario:
    # . S P B
    # S W BS B  <- Wumpus at (1,1)
    # W S . P   <- Wumpus at (2,0)  
    # S . G.P   <- Agent goes to (3,1)
    
    game_map = [
        [[], ['S'], ['P'], ['B']],           # . S P B
        [['S'], ['W'], ['B','S'], ['B']],    # S W BS B
        [['W'], ['S'], [], ['P']],           # W S . P
        [['S'], [], ['G'], ['P']]            # S . G P
    ]
    
    wumpus_positions = [(1,1), (2,0)]
    pit_positions = [(0,2), (2,3), (3,3)]
    
    print("Test Map - Specific Shooting Scenario:")
    print_map(game_map)
    print(f"Wumpus positions: {wumpus_positions}")
    print(f"Pit positions: {pit_positions}")
    print()
    print("Expected behavior:")
    print("- Agent should reach stench cell (3,1)")
    print("- From (3,1): North direction hits (2,1)->(1,1)->(0,1), can hit Wumpus at (1,1)")
    print("- From (3,1): West direction hits (3,0)->(2,0)->(1,0), can hit Wumpus at (2,0)")
    print("- Agent should choose the direction with better stench pattern analysis")
    print()
    
    agent = Agent(map=game_map, N=4)
    result = hybrid_agent_action_dynamic(agent, game_map, wumpus_positions, pit_positions)
    
    print(f"\nFinal Result: {result}")
    print(f"Arrow status: {agent.arrow_hit} (0=not shot, 1=hit, -1=missed)")
    
    return result, agent

if __name__ == "__main__":
    result, agent = test_specific_shooting_scenario()
    
    print("\n" + "="*50)
    print("ANALYSIS:")
    if result['alive'] and result['gold']:
        print("✅ SUCCESS: Agent survived and got gold!")
    elif result['alive'] and not result['gold']:
        if result['score'] > -50:
            print("⚠️ PARTIAL SUCCESS: Agent survived but didn't get gold")
        else:
            print("❌ FAILED: Agent survived but poor score")
    else:
        print("💀 FAILED: Agent died")
    
    print(f"Final score: {result['score']}")
    arrow_status = agent.arrow_hit if hasattr(agent, 'arrow_hit') else result.get('arrow_hit', 0)
    print(f"Arrow result: {'Hit' if arrow_status == 1 else 'Missed' if arrow_status == -1 else 'Not used'}")
