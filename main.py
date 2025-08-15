from env_simulator.generateMap import WumpusWorldGenerator, print_map
from env_simulator.kb import KnowledgeBase
from agent.random_agent import random_agent
from search.dijkstra import dijkstra
from agent.agent import  Agent
from agent.hybrid_agent import hybrid_agent_action

# def main():
#   kb = KnowledgeBase(N=4)
#   kb.add_fact('~P(0, 0)')
#   kb.add_fact('~W(0, 0)')
#   kb.add_fact('~S(0, 0)')
#   kb.add_fact('~B(0, 0)')
#   kb.forward_chain()
#   kb.print_knowledge()
# def main():
#     generator = WumpusWorldGenerator(N=4)
#     gam_map, wumpus_position, pit_positions = generator.generate_map()
#     
#     print("Generated Game Map:")
#     print_map(gam_map)
#     
#     score = random_agent(gam_map, wumpus_position, pit_positions)
#     print(f"Final Score: {score}")
  
def main():
  generator = WumpusWorldGenerator(N=4)
  gam_map, wumpus_position, pit_positions = generator.generate_map()
  
  print("Generated Game Map:")
  print_map(gam_map)

  # agent = Agent2(N=4)
  # path = dijkstra(gam_map, agent)
  # if path is not None:
  #   for x in path:
  #     print(x)

  agent = Agent(map=gam_map, N=4)
  result = hybrid_agent_action(agent, gam_map)
  print("Final result:", result)

if __name__ == "__main__":
  main()