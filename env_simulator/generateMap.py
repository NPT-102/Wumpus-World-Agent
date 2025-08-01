import numpy as np

GOLD = 1

class WumpusWorldGenerator:
  def __init__(self, N=8, wumpus=2, pits_probability=0.2):
    self.N = N
    self.wumpus = wumpus
    self.pits_probability = pits_probability
    self.map = [[None for _ in range(N)] for _ in range(N)]
    
  def generate_map(self):
    # place gold
    gold_position = (np.random.randint(0, self.N), np.random.randint(0, self.N))
    self.map[gold_position[0]][gold_position[1]] = GOLD
    