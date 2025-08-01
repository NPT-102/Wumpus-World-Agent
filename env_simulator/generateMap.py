import numpy as np

class WumpusWorldGenerator:
  def __init__(self, N=8, wumpus=2, pits_probability=0.2):
    self.N = N
    self.wumpus = wumpus
    self.pits_probability = pits_probability
    self.map = [[None for _ in range(N)] for _ in range(N)]
    
  def generate_map(self):
    # place gold
    gold_position = (np.random.randint(0, self.N), np.random.randint(0, self.N))
    self.map[gold_position[0]][gold_position[1]] = 'G'
  
    # place wumpus
    wumpus = self.wumpus
    for _ in range(wumpus):
      while True:
        wumpus_position = (np.random.randint(0, self.N), np.random.randint(0, self.N))
        if self.map[wumpus_position[0]][wumpus_position[1]] is None:
          if wumpus_position != gold_position:
            if wumpus_position != (0, 0) and wumpus_position != (0, 1) and wumpus_position != (1, 0):
              self.map[wumpus_position[0]][wumpus_position[1]] = 'W'
              break