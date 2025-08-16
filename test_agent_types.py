"""
Test script to verify different agent types work correctly
"""
from env_simulator.generateMap import WumpusWorldGenerator
from agent.agent import Agent
from agent_wrapper import RandomAgentWrapper, HybridAgentWrapper, DynamicAgentWrapper

def test_agent_type(agent_type, map_size=4, max_steps=50):
    """Test a specific agent type"""
    print(f"\n{'='*50}")
    print(f"Testing {agent_type} Agent on {map_size}x{map_size} map")
    print(f"{'='*50}")
    
    # Generate map
    generator = WumpusWorldGenerator(N=map_size)
    game_map, wumpus_positions, pit_positions = generator.generate_map()
    
    # Convert single wumpus to list if needed
    if isinstance(wumpus_positions, tuple):
        wumpus_positions = [wumpus_positions]
    
    print(f"Wumpus positions: {wumpus_positions}")
    print(f"Pit positions: {pit_positions}")
    
    # Create agent
    agent = Agent(map=game_map, N=map_size)
    
    # Create appropriate wrapper
    if agent_type == "Random":
        step_agent = RandomAgentWrapper(agent, game_map, wumpus_positions, pit_positions)
    elif agent_type == "Hybrid":
        step_agent = HybridAgentWrapper(agent, game_map, wumpus_positions, pit_positions)
    elif agent_type == "Dynamic":
        step_agent = DynamicAgentWrapper(agent, game_map, wumpus_positions, pit_positions)
    else:
        print(f"Unknown agent type: {agent_type}")
        return
    
    # Run simulation
    step_count = 0
    print("\nStarting simulation...")
    
    while step_count < max_steps:
        step_count += 1
        
        try:
            can_continue, message = step_agent.step()
            state = step_agent.get_current_state()
            
            print(f"Step {step_count}: {message}")
            print(f"  Position: {state['position']}, Direction: {state['direction']}, Score: {state['score']}")
            
            if not can_continue:
                print(f"Game ended: {message}")
                break
                
        except Exception as e:
            print(f"Error in step {step_count}: {e}")
            break
    
    # Final results
    final_result = step_agent.get_final_result()
    print(f"\nFinal Results for {agent_type} Agent:")
    print(f"  Final Position: {final_result['final_position']}")
    print(f"  Score: {final_result['score']}")
    print(f"  Has Gold: {final_result['gold']}")
    print(f"  Alive: {final_result['alive']}")
    print(f"  Total Actions: {final_result['actions']}")
    
    return final_result

def main():
    """Test all agent types"""
    agent_types = ["Random", "Hybrid", "Dynamic"]
    results = {}
    
    for agent_type in agent_types:
        try:
            result = test_agent_type(agent_type, map_size=4, max_steps=100)
            results[agent_type] = result
        except Exception as e:
            print(f"Failed to test {agent_type} agent: {e}")
            results[agent_type] = None
    
    # Summary
    print(f"\n{'='*60}")
    print("SUMMARY OF ALL AGENT TYPES")
    print(f"{'='*60}")
    
    for agent_type, result in results.items():
        if result:
            status = "WON" if result['gold'] and result['final_position'] == (0, 0) else "ALIVE" if result['alive'] else "DIED"
            print(f"{agent_type:8} | Score: {result['score']:4} | Actions: {result['actions']:3} | Status: {status}")
        else:
            print(f"{agent_type:8} | FAILED TO RUN")

if __name__ == "__main__":
    main()
