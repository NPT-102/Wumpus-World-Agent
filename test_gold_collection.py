from env_simulator.generateMap import WumpusWorldGenerator, print_map
from env_simulator.environment import WumpusEnvironment
from env_simulator.kb import KnowledgeBase
from agent.agent import Agent
from agent.kb_safe_agent import KnowledgeBaseSafeAgent

def test_kb_agent_with_gold():
    """Test KB-Safe Agent with gold collection and safe return"""
    
    print("=== TESTING KB-SAFE AGENT WITH GOLD COLLECTION ===\n")
    
    # Generate smaller map for focused testing
    generator = WumpusWorldGenerator(N=6)
    game_map, wumpus_position, pit_positions = generator.generate_map()
    
    # Convert to list format
    if isinstance(wumpus_position, tuple):
        wumpus_position = [wumpus_position]
    
    print("Generated 6x6 Map:")
    print_map(game_map)
    print(f"Wumpus at: {wumpus_position}")
    print(f"Pits at: {pit_positions}")
    
    # Create environment and agent
    environment = WumpusEnvironment(game_map, wumpus_position, pit_positions)
    base_agent = Agent(environment=environment, N=6)
    kb_agent = KnowledgeBaseSafeAgent(base_agent, max_risk_threshold=1.0)
    
    print(f"\nStarting KB-Safe Agent exploration...")
    step_count = 0
    max_steps = 200
    
    gold_found = False
    returned_home = False
    
    while step_count < max_steps:
        success, message = kb_agent.step()
        step_count += 1
        
        print(f"Step {step_count}: {message}")
        
        # Check if gold was found
        if "Grabbed gold" in message:
            gold_found = True
            print("✅ GOLD COLLECTED!")
        
        # Check if returned home successfully
        if "Successfully returned home" in message:
            returned_home = True
            print("🏠 MISSION ACCOMPLISHED!")
        
        if not success:
            print("Agent stopped!")
            break
        
        if not base_agent.alive:
            print("💀 Agent died!")
            break
    
    # Final analysis
    final_result = kb_agent.get_final_result()
    
    print(f"\n=== FINAL RESULTS ===")
    print(f"Steps taken: {step_count}")
    print(f"Final position: {final_result['final_position']}")
    print(f"Score: {final_result['score']}")
    print(f"Gold obtained: {final_result['gold']}")
    print(f"Agent alive: {final_result['alive']}")
    print(f"Positions explored: {len(kb_agent.visited_positions)}")
    
    print(f"\n=== MISSION STATUS ===")
    print(f"🏆 Gold found and collected: {'✅ YES' if gold_found else '❌ NO'}")
    print(f"🏠 Safely returned home: {'✅ YES' if returned_home else '❌ NO'}")
    print(f"🛡️ Agent survived: {'✅ YES' if final_result['alive'] else '❌ NO'}")
    
    mission_success = gold_found and returned_home and final_result['alive']
    print(f"\n{'🎉 MISSION SUCCESS!' if mission_success else '⚠️ Mission incomplete'}")
    
    if mission_success:
        print(f"Perfect KB-Safe exploration: Found gold, collected it, and returned home safely!")
        print(f"Final score: {final_result['score']}")
    else:
        if not final_result['alive']:
            print("Agent died - safety logic needs improvement")
        elif not gold_found:
            print("Gold not found - exploration range may be limited")
        elif not returned_home:
            print("Could not return home safely - pathfinding needs improvement")
    
    # Show exploration coverage
    total_cells = 6 * 6
    exploration_percentage = (len(kb_agent.visited_positions) / total_cells) * 100
    print(f"\nExploration coverage: {exploration_percentage:.1f}% ({len(kb_agent.visited_positions)}/{total_cells} cells)")
    print(f"Visited positions: {sorted(list(kb_agent.visited_positions))}")

if __name__ == "__main__":
    test_kb_agent_with_gold()
