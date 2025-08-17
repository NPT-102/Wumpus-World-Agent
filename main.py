from env_simulator.generateMap import WumpusWorldGenerator, print_map
from env_simulator.environment import WumpusEnvironment
from env_simulator.kb import KnowledgeBase
from agent.agent import Agent
from agent.intelligent_agent import IntelligentAgent
from agent.intelligent_agent_dynamic import IntelligentAgentDynamic
from agent.safe_first_intelligent_agent import SafeFirstIntelligentAgent
from agent.simple_safe_agent import SafeFirstIntelligentAgent as SimpleSafeAgent
from agent.kb_safe_agent import KnowledgeBaseSafeAgent
from agent.random_agent import RandomAgent
from agent.hybrid_agent import HybridAgent
from agent.hybrid_agent_action_dynamic import HybridAgentDynamic
import sys

def test_agent(agent_type, game_map, wumpus_position, pit_positions, max_steps=200):
    """Test a specific agent type"""
    print(f"\n=== Testing {agent_type} Agent ===")
    
    # Create environment interface (no direct map access for agents)
    environment = WumpusEnvironment(game_map, wumpus_position, pit_positions)
    
    # Create base agent with environment interface
    base_agent = Agent(environment=environment, N=4)
    
    # Create the appropriate agent wrapper
    if agent_type == "Random":
        agent = RandomAgent(base_agent)
    elif agent_type == "Hybrid":
        agent = HybridAgent(base_agent)
    elif agent_type == "Hybrid Dynamic":
        agent = HybridAgentDynamic(base_agent)
    elif agent_type == "Intelligent":
        agent = IntelligentAgent(base_agent, max_risk_threshold=0.3)
    elif agent_type == "Intelligent Dynamic":
        agent = IntelligentAgentDynamic(base_agent, max_risk_threshold=0.3)
    elif agent_type == "Safe-First Intelligent":
        agent = KnowledgeBaseSafeAgent(base_agent, max_risk_threshold=1.0)  # Not used
    elif agent_type == "KB-Safe":
        agent = KnowledgeBaseSafeAgent(base_agent, max_risk_threshold=1.0)  # Pure KB agent
    else:
        raise ValueError(f"Unknown agent type: {agent_type}")
    
    print(f"Starting {agent_type.lower()} agent...")
    step_count = 0
    
    while step_count < max_steps:
        success, message = agent.step()
        step_count += 1
        
        print(f"Step {step_count}: {message}")
        
        if not success:
            print("Game ended!")
            break
        
        if not base_agent.alive:
            print("Agent died!")
            break
    
    # Print final results
    final_result = agent.get_final_result()
    print(f"\n{agent_type} Agent Final Results:")
    print(f"Position: {final_result['final_position']}")
    print(f"Score: {final_result['score']}")
    print(f"Gold obtained: {final_result['gold']}")
    print(f"Alive: {final_result['alive']}")
    print(f"Steps taken: {step_count}")
    
    return final_result

def main():
    # Generate a 4x4 map as requested
    generator = WumpusWorldGenerator(N=4)
    game_map, wumpus_position, pit_positions = generator.generate_map()
    
    # Convert single wumpus to list if needed
    if isinstance(wumpus_position, tuple):
        wumpus_position = [wumpus_position]
    elif isinstance(wumpus_position, list):
        wumpus_position = list(wumpus_position)
    else:
        raise ValueError("wumpus_position is invalid")

    print("Generated 4x4 Game Map:")
    print_map(game_map)
    print(f"Wumpus at: {wumpus_position}")
    print(f"Pits at: {pit_positions}")
    
    # Check command line argument for agent type
    if len(sys.argv) > 1:
        agent_type = sys.argv[1].title()
        if agent_type in ["Random", "Hybrid", "Intelligent"]:
            test_agent(agent_type, game_map, wumpus_position, pit_positions)
        elif agent_type in ["Dynamic", "Hybrid-Dynamic"]:
            test_agent("Hybrid Dynamic", game_map, wumpus_position, pit_positions)
        elif agent_type in ["Intelligent-Dynamic", "Int-Dynamic"]:
            test_agent("Intelligent Dynamic", game_map, wumpus_position, pit_positions)
        elif agent_type in ["Safe-First", "Safe-First-Intelligent", "SafeFirst"]:
            test_agent("Safe-First Intelligent", game_map, wumpus_position, pit_positions)
        elif agent_type in ["KB-Safe", "KBSafe", "Knowledge-Base"]:
            test_agent("KB-Safe", game_map, wumpus_position, pit_positions)
        else:
            print(f"Unknown agent type: {agent_type}")
            print("Available types: random, hybrid, dynamic, intelligent, intelligent-dynamic, safe-first")
    else:
        # Test all agent types if no argument provided
        agent_types = ["Random", "Hybrid", "Hybrid Dynamic", "Intelligent", "Intelligent Dynamic", "Safe-First Intelligent", "KB-Safe"]
        results = {}
        
        for agent_type in agent_types:
            try:
                result = test_agent(agent_type, game_map, wumpus_position, pit_positions)
                results[agent_type] = result
            except Exception as e:
                print(f"Error testing {agent_type} agent: {e}")
                results[agent_type] = None
        
        # Summary comparison
        print("\n=== AGENT COMPARISON SUMMARY ===")
        print(f"{'Agent Type':<15} {'Score':<8} {'Gold':<6} {'Alive':<6} {'Position'}")
        print("-" * 50)
        
        for agent_type, result in results.items():
            if result:
                score = result['score']
                gold = "Yes" if result['gold'] else "No"
                alive = "Yes" if result['alive'] else "No"
                pos = result['final_position']
                print(f"{agent_type:<15} {score:<8} {gold:<6} {alive:<6} {pos}")
            else:
                print(f"{agent_type:<15} {'ERROR':<8} {'--':<6} {'--':<6} {'--'}")

if __name__ == "__main__":
    main()