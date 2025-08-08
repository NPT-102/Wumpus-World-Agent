# import generateMap
# import kb

# directions = ['N', 'E', 'S', 'W']

# class Environment:
#     def __init__(self, N=8, wumpus=2, pits_probability=0.2):
#         self.N = N
#         self.wumpus = wumpus
#         self.pits_probability = pits_probability
#         self.map_generator = generateMap.WumpusWorldGenerator(N, wumpus, pits_probability)
#         self.map = self.map_generator.generate_map()
#         self.agent = None

#     def set_agent(self, agent):
#         self.agent = agent

#     def reset(self):
#         self.map = self.map_generator.generate_map()
#         if self.agent:
#             self.agent.map = self.map
#             self.agent.position = (0, 0)
#             self.agent.direction = 'E'
#             self.agent.kb.reset()
#             self.agent.perceive()

#     def update(self):
#         if self.agent:
#             self.agent.perceive()
#             if not self.agent.alive:
#                 print("Agent has died. Resetting environment.")
#                 self.reset()
#             else:
#                 new_wumpus_position = kb.update_wumpus_position(self.agent, self.map, self.agent.wumpus_position, self.map_generator.pit_positions)
#                 if new_wumpus_position != self.agent.wumpus_position:
#                     print(f"Wumpus moved to {new_wumpus_position}")
#                     self.agent.wumpus_position = new_wumpus_position