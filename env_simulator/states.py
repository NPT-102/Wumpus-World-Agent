import re

class States:
    def __init__(self, pit, wumpus, is_random=False):
        self.actions = []
        self.pits = [pit]
        self.wumpuses = [wumpus]
        if is_random:
            self.knowledge = ['']
        else:
            self.knowledge = []

    def add(self, agent, result, pit, wumpus, knowledge=None):
        def kb_to_grid_string(kb, N):
            #  "$" = Safe, "!" = Deadly, "-" = unknown
            grid = ["-"] * (N * N)
            
            for s in kb:
                match = re.match(r"Safe\((\d+),\s*(\d+)\)", s)
                if match:
                    i, j = int(match.group(1)), int(match.group(2))
                    grid[i * N + j] = "$"
                    continue
                match = re.match(r"Deadly\((\d+),\s*(\d+)\)", s)
                if match:
                    i, j = int(match.group(1)), int(match.group(2))
                    grid[i * N + j] = "!"
            
            return "".join(grid)
        i, j = agent.position
        self.actions.append(i, j, agent.direction, result)
        self.pits.append(pit)
        self.wumpuses.append(wumpus)
        if knowledge is None:
            self.knowledge.append['']
        else:
            self.knowledge.append[kb_to_grid_string(knowledge)]