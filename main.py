from env_simulator.generateMap import WumpusWorldGenerator, print_map
from env_simulator.kb import KnowledgeBase

def main():
  kb = KnowledgeBase(N=4)
  kb.add_fact('~P(0, 0)')
  kb.add_fact('~W(0, 0)')
  kb.add_fact('~S(0, 0)')
  kb.add_fact('~B(0, 0)')

  kb.add_fact('B(0, 1)')
  kb.add_fact('~S(0, 1)')
  kb.forward_chain()
    
  kb.add_fact('S(1, 0)')
  kb.add_fact('~B(1, 0)')
  
  kb.forward_chain() 
  kb.print_knowledge()
  
if __name__ == "__main__":
  main()