#!/usr/bin/env python3
"""
Create a custom scenario to test enhanced Wumpus hunting with UI display
"""

from agent.kb_safe_agent import KnowledgeBaseSafeAgent
from env_simulator.generateMap import WumpusWorldGenerator 
from env_simulator.environment import WumpusEnvironment
from agent.agent import Agent
import time

def create_hunting_scenario():
    """Create a scenario where agent will need to hunt Wumpus"""
    
    print("=== CREATING ENHANCED HUNTING SCENARIO ===")
    
    # Generate a 4x4 map
    generator = WumpusWorldGenerator(4)
    game_map, wumpus_positions, pit_positions = generator.generate_map()
    
    print(f"Generated Map:")
    print(f"  Wumpus at: {wumpus_positions}")
    print(f"  Pits at: {pit_positions}")
    
    # Create environment and agent
    environment = WumpusEnvironment(game_map, wumpus_positions, pit_positions)
    agent = Agent(environment)
    kb_agent = KnowledgeBaseSafeAgent(agent)
    
    print(f"\nStarting Enhanced Hunting Test...")
    print(f"Agent position: {agent.position}")
    print(f"Agent has arrow: {agent.arrow_hit == 0}")
    
    # Run some steps to gather knowledge
    max_steps = 30
    step_count = 0
    
    while not agent.is_dead() and step_count < max_steps:
        step_count += 1
        
        # Take a step
        success, message = kb_agent.step()
        
        print(f"Step {step_count}: {message}")
        
        if not success or "Final score" in message:
            break
            
        # Check if we found any Wumpus in KB
        wumpus_facts = [f for f in agent.kb.facts if f.startswith('W(') and not f.startswith('~W(')]
        dead_wumpus_facts = [f for f in agent.kb.facts if f.startswith('~W(')]
        
        if wumpus_facts:
            print(f"  💀 Known Wumpus: {wumpus_facts}")
        if dead_wumpus_facts:
            print(f"  ⚰️  Dead Wumpus: {dead_wumpus_facts}")
            
        # Show KB facts periodically
        if step_count % 5 == 0:
            all_facts = sorted(list(agent.kb.facts))
            print(f"  📚 KB Facts ({len(all_facts)}): {all_facts[:10]}...")
        
        time.sleep(0.1)  # Small delay for readability
    
    print(f"\n=== SCENARIO COMPLETE ===")
    print(f"Final position: {agent.position}")
    print(f"Score: {agent.score}")
    print(f"Gold obtained: {agent.gold_obtain}")
    print(f"Agent alive: {not agent.is_dead()}")
    print(f"Steps taken: {step_count}")
    
    # Show final KB state
    all_facts = sorted(list(agent.kb.facts))
    wumpus_facts = [f for f in all_facts if 'W(' in f]
    dead_wumpus_facts = [f for f in all_facts if f.startswith('~W(')]
    
    print(f"\nFinal KB Wumpus State:")
    print(f"  Wumpus facts: {wumpus_facts}")
    print(f"  Dead Wumpus facts: {dead_wumpus_facts}")
    
    # Test UI display logic with final facts
    print(f"\n=== UI DISPLAY TEST ===")
    for fact in wumpus_facts:
        if fact.startswith('W(') and not fact.startswith('~W('):
            # Extract position
            import re
            match = re.search(r'W\((\d+),\s*(\d+)\)', fact)
            if match:
                pos = (int(match.group(1)), int(match.group(2)))
                dead_fact = f"~W({pos[0]},{pos[1]})"
                should_show = dead_fact not in all_facts
                status = "SHOW" if should_show else "HIDE"
                print(f"  Wumpus at {pos}: {status} ({dead_fact} {'not ' if should_show else ''}in KB)")

if __name__ == "__main__":
    create_hunting_scenario()
