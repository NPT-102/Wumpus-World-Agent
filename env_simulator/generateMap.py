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
        wumpus_positions = []
        for _ in range(self.wumpus):
            while True:
                pos = (np.random.randint(0, self.N), np.random.randint(0, self.N))
                if self.map[pos[0]][pos[1]] == [] and pos != gold_position and pos not in self.protected_cells:
                    self.map[pos[0]][pos[1]].append('W')
                    self.adjacent_cells(pos[0], pos[1], 'S')
                    wumpus_positions.append(pos)
                    break

        # place pits and breeze
        for i in range(self.N):
            for j in range(self.N):
                if (i,j) != gold_position and (i,j) not in wumpus_positions and (i,j) not in self.protected_cells:
                    if np.random.rand() < self.pits_probability:
                        if not any(item in self.map[i][j] for item in ['W', 'P', 'G', 'S']):
                            if 'B' in self.map[i][j]:
                                self.map[i][j].remove('B')
                            self.map[i][j].append('P')
                            self.adjacent_cells(i, j, 'B')

        # trả về map, tất cả vị trí Wumpus và vị trí pits
        pit_positions = [(i,j) for i in range(self.N) for j in range(self.N) if 'P' in self.map[i][j]]
        return self.map, wumpus_positions, pit_positions

    def adjacent_cells(self, i, j, char):
        for di, dj in [(0,1), (1,0), (0,-1), (-1,0)]:
            ni, nj = i + di, j + dj
            if 0 <= ni < self.N and 0 <= nj < self.N:
                if char not in self.map[ni][nj]:
                    # bỏ qua gió nếu đã có hố
                    if char == 'B' and 'P' in self.map[ni][nj]:
                        continue
                    self.map[ni][nj].append(char)

def print_map(map):
    for row in map:
        print(' '.join([''.join(cell) if cell else '.' for cell in row]))
