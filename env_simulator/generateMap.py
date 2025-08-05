import numpy as np

class WumpusWorldGenerator:
  def __init__(self, N=8, wumpus=2, pits_probability=0.2):
    self.N = N
    self.wumpus = wumpus
    self.pits_probability = pits_probability
    self.map = [[[] for _ in range(N)] for _ in range(N)]
    self.protected_cells = [(0, 0), (0, 1), (1, 0)]
    
  def generate_map(self):
    # place gold
    gold_position = (np.random.randint(0, self.N), np.random.randint(0, self.N))
    self.map[gold_position[0]][gold_position[1]].append('G')
  
    # place wumpus
    wumpus = self.wumpus
    for _ in range(wumpus):
      while True:
        wumpus_position = (np.random.randint(0, self.N), np.random.randint(0, self.N))
        if self.map[wumpus_position[0]][wumpus_position[1]] == []:
          if wumpus_position != gold_position:
            if wumpus_position not in self.protected_cells:
              self.map[wumpus_position[0]][wumpus_position[1]].append('W')
              self.adjacent_cells(wumpus_position[0], wumpus_position[1], 'S')
              break
    
    # place pits and breeze
    for i in range(self.N):
      for j in range(self.N):
        if self.map[i][j] != gold_position and (i, j) != wumpus_position and np.random.rand() < self.pits_probability:
          if (i, j) not in self.protected_cells:
            if not any(item in self.map[i][j] for item in ['W', 'P', 'G', 'S']):
              if 'B' in self.map[i][j]:
                self.map[i][j].remove('B')
              
              self.map[i][j].append('P')
              self.adjacent_cells(i, j, 'B')

    return self.map

  def adjacent_cells(self, i, j, char):
    for di, dj in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
      ni, nj = i + di, j + dj
      if 0 <= ni < self.N and 0 <= nj < self.N:
          if char not in self.map[ni][nj]:
              if char == 'B' and 'P' in self.map[ni][nj]:
                continue
              else: self.map[ni][nj].append(char)
  
def print_map(map):
  for row in map:
    print(' '.join([''.join(cell) if cell else '.' for cell in row]))