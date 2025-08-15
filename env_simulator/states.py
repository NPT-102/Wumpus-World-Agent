class States:
    def __init__(self, is_random=False, actual_map=None):
        self.is_random = is_random
        self.states = []

    def add(self, agent, action):
        if (self.is_random):
            self.states.append(agent.map, action)
        else:
            pass

    def get_states(self):
        return self.states