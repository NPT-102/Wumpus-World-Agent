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
        if knowledge is None:
            i, j = agent.position
            self.actions.append(i, j, agent.direction, result)
            self.pits.append(pit)
            self.wumpuses.append(wumpus)
            self.knowledge.append['']
        else:
            pass