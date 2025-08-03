class KnowledgeBase:
  def __init__(self, N=4):
    self.facts = set()
    self.rules = []
    self.N = N
    self.initialize_rules()

  def initialize_rules(self):
    for i in range(0, self.N):
      for j in range(0, self.N):
        # Get adjacent cells
        adj_cells = self.get_adjacent_cells(i, j)
        
        # Rule: Breeze implies at least one adjacent pit
        if adj_cells:
          pit_symbols = [f'P({adj[0]}, {adj[1]})' for adj in adj_cells]
          self.rules.append((f'B({i}, {j})', 'DISJUNCTION', pit_symbols))

        # Rule: No breeze implies no pits in adjacent cells
        for adj in adj_cells:
          self.rules.append((f'~B({i}, {j})', 'IMPLIES', [f'~P({adj[0]}, {adj[1]})']))

        # Rule: Stench implies at least one adjacent Wumpus
        if adj_cells:
          wumpus_symbols = [f'W({adj[0]}, {adj[1]})' for adj in adj_cells]
          self.rules.append((f'S({i}, {j})', 'DISJUNCTION', wumpus_symbols))

        # Rule: No stench implies no Wumpus in adjacent cells
        for adj in adj_cells:
          self.rules.append((f'~S({i}, {j})', 'IMPLIES', [f'~W({adj[0]}, {adj[1]})']))

        # Rule: No pit and no Wumpus implies safe
        self.rules.append((f'~P({i}, {j}) AND ~W({i}, {j})', 'IMPLIES', [f'Safe({i}, {j})']))

  def get_adjacent_cells(self, i, j):
    adj = []
    for di, dj in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
      ni, nj = i + di, j + dj
      if 0 <= ni < self.N and 0 <= nj < self.N:
        adj.append((ni, nj))
    return adj

  def add_fact(self, symbol):
    self.facts.add(symbol)

  def forward_chain(self):
    new_facts = True
    while new_facts:
      new_facts = False
      for premise, rule_type, conclusions in self.rules:
        if rule_type == 'DISJUNCTION':
          if premise in self.facts:
            continue
        elif rule_type == 'IMPLIES':
            if 'AND' in premise:
              p1, p2 = premise.split(' AND ')
              premise_satisfied = self.is_premise_true(p1) and self.is_premise_true(p2)
            else:
              premise_satisfied = self.is_premise_true(premise)

            if premise_satisfied:
              for conclusion in conclusions:
                if conclusion not in self.facts:
                  self.facts.add(conclusion)
                  new_facts = True

  def is_premise_true(self, premise):
    return premise in self.facts or (premise.startswith('~') and premise[1:] not in self.facts)
    
  def query_safe(self, i, j):
    return f'Safe({i}, {j})' in self.facts

  def print_knowledge(self):
    print("Current facts in KB:")
    for fact in sorted(self.facts):
        print(fact)