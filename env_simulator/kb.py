class KnowledgeBase:
  def __init__(self, N=8):
    self.facts = set()
    self.rules = []
    self.N = N
    self.stench_cells = [[False]*N for _ in range(N)]
    self.dangerous = []
    self.initialize_rules()
  
  def perceive_stench(self, i, j, stench_present: bool):
      """
      Cập nhật thông tin Stench ở ô (i,j) dựa trên perception của agent.
      """
      self.stench_cells[i][j] = stench_present
      if stench_present:
          self.add_fact(f"S({i},{j})")
      else:
          self.add_fact(f"~S({i},{j})")
      self.forward_chain()

  def perceive(self):
    percept = self.sense()  # ví dụ ['S', 'B', ...]
    i, j = self.position
    self.kb.perceive_stench(i, j, 'S' in percept)


  def initialize_rules(self):
    for i in range(0, self.N):
      for j in range(0, self.N):
        adj_cells = self.get_adjacent_cells(i, j)
        
        # breeze implies at least one adjacent pit
        if adj_cells:
          pit_symbols = [f'P({adj[0]}, {adj[1]})' for adj in adj_cells]
          self.rules.append((f'B({i}, {j})', 'DISJUNCTION', pit_symbols))

        # no breeze implies no pits in adjacent cells
        for adj in adj_cells:
          self.rules.append((f'~B({i}, {j})', 'IMPLIES', [f'~P({adj[0]}, {adj[1]})']))

        # stench implies at least one wumpus
        if adj_cells:
          wumpus_symbols = [f'W({adj[0]}, {adj[1]})' for adj in adj_cells]
          self.rules.append((f'S({i}, {j})', 'DISJUNCTION', wumpus_symbols))

        # no stench implies no wumpus in adjacent cells
        for adj in adj_cells:
          self.rules.append((f'~S({i}, {j})', 'IMPLIES', [f'~W({adj[0]}, {adj[1]})']))
          
        # pit implies adjacent breeze
        for adj in adj_cells:
          self.rules.append((f'P({i}, {j})', 'IMPLIES', [f'B({adj[0]}, {adj[1]})']))

        # wumpus implies adjacent stench
        for adj in adj_cells:
          self.rules.append((f'W({i}, {j})', 'IMPLIES', [f'S({adj[0]}, {adj[1]})']))

        # no pit and no wumpus implies safe
        self.rules.append((f'~P({i}, {j}) AND ~W({i}, {j})', 'IMPLIES', [f'Safe({i}, {j})']))

  def get_adjacent_cells(self, i, j):
    adj = []
    for di, dj in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
      ni, nj = i + di, j + dj
      if 0 <= ni < self.N and 0 <= nj < self.N:
        adj.append((ni, nj))
    return adj

  def add_fact(self, *symbols):
    for symbol in symbols:
      if symbol not in self.facts:
        self.facts.add(symbol)

  def forward_chain(self):
    new_facts = True
    while new_facts:
      new_facts = False
      for premise, rule_type, conclusions in self.rules:
        if rule_type == 'DISJUNCTION':
          if self.is_premise_true(premise):
            possible = [c for c in conclusions if self.is_premise_true(c) is not False]
            
            if len(possible) == 1:
              if possible[0] not in self.facts:
                self.facts.add(possible[0])
                new_facts = True
        elif rule_type == 'IMPLIES':
            if 'AND' in premise:
              p1, p2 = premise.split(' AND ')
              premise_satisfied = self.is_premise_true(p1) is True and self.is_premise_true(p2) is True
            else:
              premise_satisfied = self.is_premise_true(premise) is True

            if premise_satisfied:
              for conclusion in conclusions:
                if conclusion not in self.facts:
                  self.facts.add(conclusion)
                  new_facts = True
    self.update_dangerous()
    
  # check if a premise is in facts or not
  def is_premise_true(self, premise):
    if premise.startswith('~'):
      symbol = premise[1:]
      if symbol in self.facts:
        return False
      elif f'~{symbol}' in self.facts:
        return True
      else:
        return None
    else:
      if premise in self.facts:
        return True
      elif f'~{premise}' in self.facts:
        return False
      else:
        return None  
  
  def update_dangerous(self):
    self.dangerous.clear()
    for i in range(self.N):
        for j in range(self.N):
            # Skip if known safe
            if self.is_safe(i, j):
                continue

            # If fact says Wumpus or Pit => dangerous
            if f"W({i},{j})" in self.facts or f"P({i},{j})" in self.facts:
                self.dangerous.append((i, j))
            # If possible Wumpus => dangerous
            elif self.is_possible_wumpus(i, j):
                self.dangerous.append((i, j))
            # If we don’t know about pits => also dangerous
            elif self.is_premise_true(f"P({i},{j})") is None:
                self.dangerous.append((i, j))

  def get_dangerous_cells(self):
      self.update_dangerous()
      return self.dangerous    
  
  def current_facts(self):
    return self.facts

  def print_facts(self):
    for fact in self.facts:
      print(fact)

  def remove_wumpus(self, i, j):
    self.add_fact(f"~W({i}, {j})")
    for ni, nj in self.get_adjacent_cells(i, j):
        self.add_fact(f"~S({ni}, {nj})")
    self.forward_chain()

  def is_possible_wumpus(self, i, j):
    if f"W({i}, {j})" in self.facts:
        return True      # chắc chắn có Wumpus
    if f"~W({i}, {j})" in self.facts:
        return False     # chắc chắn không có Wumpus
    
    # Nếu chưa biết, dự đoán khả năng từ Stench xung quanh
    adj = self.get_adjacent_cells(i, j)
    for ni, nj in adj:
        if f"S({ni}, {nj})" in self.facts:  # Fixed spacing to match fact format
            return True  # có Stench gần => khả năng Wumpus
    return False
  
  def is_safe(self, i, j):
    # coi ô safe nếu chắc chắn không có Wumpus hoặc Pit
    return self.is_premise_true(f"~W({i},{j})") and self.is_premise_true(f"~P({i},{j})")
  
  def is_stench(self, i, j):
    if 0 <= i < self.N and 0 <= j < self.N:
        return self.stench_cells[i][j]
    return False