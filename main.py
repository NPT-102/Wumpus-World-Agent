from env_simulator.generateMap import WumpusWorldGenerator, print_map
from env_simulator.kb import KnowledgeBase
from agent.random_agent import random_agent

# def main():
#   kb = KnowledgeBase(N=4)
#   kb.add_fact('~P(0, 0)')
#   kb.add_fact('~W(0, 0)')
#   kb.add_fact('~S(0, 0)')
#   kb.add_fact('~B(0, 0)')

#   kb.add_fact('B(0, 1)')
#   kb.add_fact('~S(0, 1)')
#   kb.forward_chain()
    
#   kb.add_fact('S(1, 0)')
#   kb.add_fact('~B(1, 0)')
  
#   kb.forward_chain() 
#   kb.print_knowledge()
def main():
    generator = WumpusWorldGenerator(N=4)
    gam_map, wumpus_position, pit_positions = generator.generate_map()
    
    print("Generated Game Map:")
    print_map(gam_map)
    
    score = random_agent(gam_map, wumpus_position, pit_positions)
    print(f"Final Score: {score}")
  
if __name__ == "__main__":
  main()