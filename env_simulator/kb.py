class KnowledgeBase:
  def __init__(self, N=8, wumpus=2):
    self.facts = set()
    self.rules = []
    self.N = N
    self.wumpus = wumpus
    self.stench_cells = [[False]*N for _ in range(N)]
    self.dangerous = []
    self.initialize_rules()

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
        normalized_symbol = self._normalize_fact_format(symbol)
        if normalized_symbol not in self.facts:
          self.facts.add(normalized_symbol)

  def _normalize_fact_format(self, fact):
    import re
    pattern = r'(\w+)\((\d+),\s*(\d+)\)'
    match = re.match(pattern, fact)
    if match:
      predicate, x, y = match.groups()
      return f"{predicate}({x}, {y})"
    return fact

  def forward_chain(self):
    new_facts = True
    iteration = 0
    while new_facts and iteration < 50:
      new_facts = False
      iteration += 1
      
      for premise, rule_type, conclusions in self.rules:
        if rule_type == 'DISJUNCTION':
          if self.is_premise_true(premise):
            possible = [c for c in conclusions if self.is_premise_true(c) is not False]
            
            if len(possible) == 1:
              wumpus_fact = possible[0]
              if wumpus_fact.startswith('W(') and not self._can_add_wumpus():
                continue
                
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
      
      if self._check_all_wumpus_found():
        new_facts = True 
    
    self.update_dangerous()

  def _can_add_wumpus(self):
    known_wumpus_count = 0
    for i in range(self.N):
      for j in range(self.N):
        if f"W({i}, {j})" in self.facts:
          known_wumpus_count += 1
    return known_wumpus_count < self.wumpus

  def _check_all_wumpus_found(self):
    known_wumpus = []
    for i in range(self.N):
      for j in range(self.N):
        if f"W({i}, {j})" in self.facts:
          known_wumpus.append((i, j))
    
    if len(known_wumpus) >= self.wumpus:
      facts_added = False
      for i in range(self.N):
        for j in range(self.N):
          if (i, j) not in known_wumpus:
            if f"~W({i}, {j})" not in self.facts:
              self.facts.add(f"~W({i}, {j})")
              facts_added = True
      return facts_added
    
    return False              
    
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
        if self.is_safe(i, j):
          continue

        if f"W({i}, {j})" in self.facts or f"P({i}, {j})" in self.facts:
          self.dangerous.append((i, j))
        elif self.is_possible_wumpus(i, j): 
          self.dangerous.append((i, j))
        elif self.is_premise_true(f"P({i}, {j})") is None:
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
    self.forward_chain()

  def is_possible_wumpus(self, i, j):
    if f"W({i}, {j})" in self.facts:
        return True 
    if f"~W({i}, {j})" in self.facts:
        return False 
    
    adj = self.get_adjacent_cells(i, j)
    for ni, nj in adj:
        if f"S({ni}, {nj})" in self.facts: 
            return True 
    return False
  
  def is_safe(self, i, j):
    return self.is_premise_true(f"~W({i}, {j})") and self.is_premise_true(f"~P({i}, {j})")

  def is_stench(self, i, j):
    if 0 <= i < self.N and 0 <= j < self.N:
        return self.stench_cells[i][j]
    return False