# wumpus_agent_fc.py
from __future__ import annotations
from dataclasses import dataclass
from typing import List, Tuple, Set
import heapq

# -----------------------
# Environment primitives
# -----------------------
Pos = Tuple[int, int]

@dataclass
class Percept:
    stench: bool
    breeze: bool
    glitter: bool
    bump: bool
    scream: bool

class WumpusWorld:
    def __init__(self, size: int = 4, pits: Set[Pos] = None,
                 wumpus: Pos = (2, 0), gold: Pos = (3, 3)):
        self.n = size
        self.wumpus = wumpus
        self.gold = gold
        self.pits = pits if pits is not None else {(1, 3), (2, 2)}
        self.agent_pos = (0, 0)
        self.agent_alive = True
        self.gold_picked = False
        self.wumpus_alive = True  # <— key for stench and scream

    def in_bounds(self, p: Pos) -> bool:
        x, y = p
        return 0 <= x < self.n and 0 <= y < self.n

    def neighbors4(self, p: Pos) -> List[Pos]:
        x, y = p
        cands = [(x+1,y), (x-1,y), (x,y+1), (x,y-1)]
        return [q for q in cands if self.in_bounds(q)]

    def _local_percept(self) -> Tuple[bool, bool, bool]:
        """Compute stench/breeze/glitter based on current world state (no scream/bump)."""
        p = self.agent_pos
        adj = self.neighbors4(p)
        stench = self.wumpus_alive and any(q == self.wumpus for q in adj)
        breeze = any(q in self.pits for q in adj)
        glitter = (p == self.gold) and not self.gold_picked
        return stench, breeze, glitter

    def step(self, action: str) -> Percept:
        """
        Actions:
         - Moves: 'Up','Down','Left','Right'
         - Special: 'Grab','Climb'
         - Shooting: 'ShootUp','ShootDown','ShootLeft','ShootRight'
        """
        scream = False
        bump = False

        if action in ("Up","Down","Left","Right"):
            x, y = self.agent_pos
            nxt = {
                "Up": (x,y+1), "Down": (x,y-1),
                "Left": (x-1,y), "Right": (x+1,y)
            }[action]
            if self.in_bounds(nxt):
                self.agent_pos = nxt
                # death check
                if nxt in self.pits or (self.wumpus_alive and nxt == self.wumpus):
                    self.agent_alive = False
            else:
                bump = True

        elif action in ("ShootUp","ShootDown","ShootLeft","ShootRight"):
            # Minimal model: the arrow targets the *adjacent* square in that direction.
            ax, ay = self.agent_pos
            target = {
                "ShootUp":    (ax, ay+1),
                "ShootDown":  (ax, ay-1),
                "ShootLeft":  (ax-1, ay),
                "ShootRight": (ax+1, ay),
            }[action]
            if self.in_bounds(target) and self.wumpus_alive and target == self.wumpus:
                self.wumpus_alive = False
                scream = True
            # Agent does not move when shooting.

        elif action == "Grab":
            if self.agent_pos == self.gold and not self.gold_picked:
                self.gold_picked = True

        elif action == "Climb":
            # Nothing to change in the world; controller will stop when desired.
            pass

        # Build percept after the action
        stench, breeze, glitter = self._local_percept()
        return Percept(stench, breeze, glitter, bump, scream)

# -----------------------
# A* route planning
# -----------------------
def astar_route(start: Pos, goals: Set[Pos], allowed: Set[Pos]) -> List[str]:
    def neighbors(p: Pos):
        x,y = p
        for q, a in [((x+1,y),"Right"),((x-1,y),"Left"),
                     ((x,y+1),"Up"),((x,y-1),"Down")]:
            if q in allowed:
                yield q, a

    if not goals: return []

    def h(p: Pos) -> int:
        return min(abs(p[0]-g[0])+abs(p[1]-g[1]) for g in goals)

    frontier = [(h(start),0,start,[])]
    best_g = {start:0}
    while frontier:
        f,g,node,path = heapq.heappop(frontier)
        if node in goals:
            return path
        for nxt,act in neighbors(node):
            ng = g+1
            if ng < best_g.get(nxt,1e9):
                best_g[nxt]=ng
                heapq.heappush(frontier,(ng+h(nxt),ng,nxt,path+[act]))
    return []

def apply_move(p: Pos, action: str) -> Pos:
    x,y = p
    return {
        "Up":(x,y+1),"Down":(x,y-1),
        "Left":(x-1,y),"Right":(x+1,y)
    }.get(action,p)

# -----------------------
# Forward chaining KB
# -----------------------
class ForwardChainingKB:
    def __init__(self):
        self.facts = set()
        self.rules = []

    def tell(self, fact):
        """Add fact if not already known, and re-run inference"""
        if fact not in self.facts:
            self.facts.add(fact)
            self.infer()

    def ask(self, fact):
        return fact in self.facts

    def infer(self):
        """Forward chaining: apply all Horn rules (if you add any)."""
        new_inferred = True
        while new_inferred:
            new_inferred = False
            for conds, concl in self.rules:
                if all(c in self.facts for c in conds) and concl not in self.facts:
                    self.facts.add(concl)
                    new_inferred = True

    def add_rule(self, conditions, conclusion):
        self.rules.append((conditions, conclusion))

# -----------------------
# Helpers
# -----------------------
def neighbors(pos: Pos, n: int=4) -> List[Pos]:
    x, y = pos
    cands = [(x+1,y),(x-1,y),(x,y+1),(x,y-1)]
    return [(a,b) for a,b in cands if 0<=a<n and 0<=b<n]

def parse_pos(fact: str) -> Pos:
    # Extract tuple from fact like Safe(1,2)
    inside = fact[fact.find("(")+1: fact.find(")")]
    x,y = inside.split(",")
    return int(x), int(y)

# -----------------------
# Update KB from percepts
# -----------------------
def update_kb_from_percept(kb: ForwardChainingKB, pos: Pos, percept: Percept, n=4):
    x,y = pos
    kb.tell(f"Visited({x},{y})")
    kb.tell(f"Safe({x},{y})")

    if not percept.breeze:
        for nx,ny in neighbors(pos,n):
            kb.tell(f"PFree({nx},{ny})")
            kb.tell(f"Safe({nx},{ny})")

    if not percept.stench or kb.ask("WumpusDead"):
        # If no stench OR Wumpus is dead, neighbors are Wumpus-free.
        for nx,ny in neighbors(pos,n):
            kb.tell(f"WFree({nx},{ny})")
            kb.tell(f"Safe({nx},{ny})")
    else:
        # Stench and Wumpus not dead: mark neighbors as possible Wumpus unless already free.
        for nx,ny in neighbors(pos,n):
            if f"WFree({nx},{ny})" not in kb.facts:
                kb.tell(f"WumpusPossible({nx},{ny})")

# -----------------------
# Hybrid Agent with FC KB + shooting
# -----------------------
class HybridWumpusAgentFC:
    def __init__(self, n=4):
        self.t=0
        self.plan=[]
        self.kb=ForwardChainingKB()
        self.current=(0,0)
        self.have_gold=False
        self.arrow=True     # only one arrow
        self.n=n
        self.kb.tell("Safe(0,0)")

    def next_action(self, percept: Percept) -> str:
        # 1) Update KB from percept
        update_kb_from_percept(self.kb, self.current, percept, self.n)

        # 2) If we heard a scream last step, Wumpus is dead => world is Wumpus-free
        if percept.scream and not self.kb.ask("WumpusDead"):
            self.kb.tell("WumpusDead")
            for x in range(self.n):
                for y in range(self.n):
                    self.kb.tell(f"WFree({x},{y})")
                    self.kb.tell(f"Safe({x},{y})")

        safe_cells={parse_pos(f) for f in self.kb.facts if f.startswith("Safe")}
        visited={parse_pos(f) for f in self.kb.facts if f.startswith("Visited")}
        unvisited=safe_cells-visited

        # 3) If glitter: grab and plan to climb out
        if percept.glitter and not self.have_gold:
            self.have_gold=True
            route=astar_route(self.current,{(0,0)},safe_cells)
            self.plan=["Grab"]+route+["Climb"]

        # 4) Shoot only when absolutely necessary: exactly one adjacent Wumpus candidate
        if self.arrow and not self.kb.ask("WumpusDead"):
            shoot_action = self._maybe_shoot(percept)
            if shoot_action is not None:
                self.arrow = False
                return shoot_action

        # 5) Exploration plan (safe → unvisited)
        if not self.plan and unvisited:
            route=astar_route(self.current,unvisited,safe_cells)
            self.plan=route

        # 6) Escape fallback
        if not self.plan and self.current!=(0,0):
            self.plan=astar_route(self.current,{(0,0)},safe_cells)
        if not self.plan and self.current==(0,0) and self.have_gold:
            self.plan=["Climb"]

        # 7) Execute next action
        action=self.plan.pop(0) if self.plan else "Climb"
        self.current=apply_move(self.current,action)
        self.t+=1
        return action

    # --- Shooting helpers ---
    def _maybe_shoot(self, percept: Percept):
        """Return Shoot{Dir} if exactly one adjacent square can host the Wumpus; else None."""
        if not percept.stench:
            return None
        # Consider only current neighbors
        neighs = neighbors(self.current, self.n)
        suspects = []
        for nx, ny in neighs:
            if f"WFree({nx},{ny})" in self.kb.facts:
                continue
            if f"WumpusPossible({nx},{ny})" in self.kb.facts:
                suspects.append((nx,ny))
        if len(suspects) != 1:
            return None
        tx, ty = suspects[0]
        x, y = self.current
        if tx == x+1 and ty == y: return "ShootRight"
        if tx == x-1 and ty == y: return "ShootLeft"
        if ty == y+1 and tx == x: return "ShootUp"
        if ty == y-1 and tx == x: return "ShootDown"
        return None

# -----------------------
# Demo run
# -----------------------
def run_demo():
    env=WumpusWorld(size=4,pits={(1,3),(2,2)},wumpus=(2,0),gold=(3,3))
    agent=HybridWumpusAgentFC(n=env.n)

    print("=== Forward Chaining Wumpus World Demo (with Shooting) ===")
    print(f"Gold at {env.gold}, Wumpus at {env.wumpus}, pits at {env.pits}\n")

    steps=0
    while steps<100 and env.agent_alive:
        percept=env._local_percept()  # peek before action (for logging)
        percept = Percept(*percept, bump=False, scream=False)
        action=agent.next_action(percept)
        percept2=env.step(action)
        print(f"t={agent.t:02d}, pos={env.agent_pos}, action={action}, "
              f"pre-percept=(stench={percept.stench}, breeze={percept.breeze}, glitter={percept.glitter}) "
              f"post-percept=(stench={percept2.stench}, breeze={percept2.breeze}, glitter={percept2.glitter}, scream={percept2.scream}), "
              f"gold={'Y' if env.gold_picked else 'N'}")
        if action=="Climb" and env.agent_pos==(0,0):
            print("\nAgent climbed out.")
            break
        steps+=1

    print("\n=== Result ===")
    print("Alive:",env.agent_alive)
    print("Gold picked:",env.gold_picked)

if __name__=="__main__":
    run_demo()