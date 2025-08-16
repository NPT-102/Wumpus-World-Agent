from env_simulator.kb import KnowledgeBase as KB

DIRECTION = {
	"E": 0, "S": 1, "W": 2, "N": 3,
	0: "E", 1: "S", 2: "W", 3: "N",
}

MOVE = {
	"E": (0, 1), 	# East
	"W": (0, -1),	# West
	"S": (1, 0),	# South
	"N": (-1, 0),  	# North
}

SCORE = {
		"move": -1,
		"turn": -1,
		"grab": 10,
		"shoot": -10,
		"die": -1000,
		"esc": 1000,
		"esc!": 0
	}

class Agent:
	score = 0
	alive = True
	arrow_hit = 0 # -1:Missed, 0:Did not shoot, 1:Hit
	gold_obtain = False
	position = (0, 0)
	direction = "E" #East

	def __init__(self, environment_map: list[list[list]], N=8):
		self.kb = KB(N=N)
		self.N = N
		# Store reference to environment for sensing only - agent cannot directly access this
		self._environment_map = environment_map
		i, j = self.position
		self.kb.add_fact(
			f"~B({i}, {j})", 
			f"~S({i}, {j})",
			f"~W({i}, {j})",
			f"~P({i}, {j})",
			f"Safe({i}, {j})"
		)
		self.kb.forward_chain()

	def perceive(self):
		i, j = self.position
		# Get percepts from environment - agent only knows what it senses at current position
		pos = self._environment_map[i][j]

		if "B" in pos:
			self.kb.add_fact(f"B({i}, {j})")
		else:
			self.kb.add_fact(f"~B({i}, {j})")
			# If no breeze -> adjacent cells don't have pits
			for di, dj in [(0,1), (0,-1), (1,0), (-1,0)]:
				ni, nj = i + di, j + dj
				if 0 <= ni < self.N and 0 <= nj < self.N:
					self.kb.add_fact(f"~P({ni}, {nj})")

		if "S" in pos:
			self.kb.add_fact(f"S({i}, {j})")
		else:
			self.kb.add_fact(f"~S({i}, {j})")
			# If no stench -> adjacent cells don't have Wumpus
			for di, dj in [(0,1), (0,-1), (1,0), (-1,0)]:
				ni, nj = i + di, j + dj
				if 0 <= ni < self.N and 0 <= nj < self.N:
					self.kb.add_fact(f"~W({ni}, {nj})")

		self.kb.forward_chain()


	def move_forward(self):
		if not self.alive:
			return None

		move = MOVE[self.direction]
		i, j = (self.position[0] + move[0], self.position[1] + move[1])
		print(f"Agent is trying to move {self.direction} to {i, j}.")
		self.score += SCORE["move"]
		
		if (0 <= i < self.N) and (0 <= j < self.N):
			# Move to the position first
			self.position = (i, j)
			
			# Then check what happens based on what's actually there
			if ("W" in self._environment_map[i][j]) or ("P" in self._environment_map[i][j]):
				if "W" in self._environment_map[i][j]:
					print("Agent encountered a Wumpus and died.")
				if "P" in self._environment_map[i][j]:
					print("Agent fell into a pit and died.")
				self.die()
				return False
			else:
				# Safe move - update knowledge and perceive
				self.perceive()
				return True
		else:
			print("Agent cannot move out of bounds.")
		return False


	def turn_left(self):
		if not self.alive:
			return None

		self.score += SCORE["turn"]
		self.direction = DIRECTION[(DIRECTION[self.direction] - 1) % 4]
		return True

	def turn_right(self):
		if not self.alive:
			return None
		
		self.score += SCORE["turn"]
		self.direction = DIRECTION[(DIRECTION[self.direction] + 1) % 4]
		return True

	def grab_gold(self):
		if not self.alive:
			return None

		i, j = self.position
		pos = self._environment_map[i][j]

		if "G" in pos:
			self.gold_obtain = True
			self.score += SCORE["grab"]
			return True
		return False

	def shoot(self):
		if not self.alive:
			return None
		
		if self.arrow_hit != 0:
			print("No arrows left!")
			return False

		self.score += SCORE["shoot"]
		mi, mj = MOVE[self.direction]
		i, j = self.position
		hit_any = False

		i += mi
		j += mj
		while (0 <= i < self.N) and (0 <= j < self.N):
			if "W" in self._environment_map[i][j]:
				self._environment_map[i][j].remove("W")
				hit_any = True
				print(f"Scream! Wumpus at {(i,j)} is dead.")

				# Remove Stench around dead Wumpus
				for di, dj in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
					ni, nj = i + di, j + dj
					if (0 <= ni < self.N) and (0 <= nj < self.N):
						if "S" in self._environment_map[ni][nj]:
							self._environment_map[ni][nj].remove("S")
				
				# Update KB: Wumpus dead, surrounding cells no longer have stench
				self.kb.add_fact(f"~W({i}, {j})")
				for ni, nj in self.kb.get_adjacent_cells(i, j):
					self.kb.add_fact(f"~S({ni}, {nj})")

			i += mi
			j += mj

		if hit_any:
			self.arrow_hit = 1
			self.kb.forward_chain()
			return True
		else:
			self.arrow_hit = -1
			print("Arrow missed!")
			return False

	def escape(self):
		if not self.alive:
			return None

		if self.position == (0, 0):
			if self.gold_obtain == True:
				self.score += SCORE["esc"]
			else:
				self.score += SCORE["esc!"]

			return True
		return False
	
	def die(self):
		self.score += SCORE["die"]
		self.alive = False


# Agent for Search algorithm
class Agent2:
	def __init__ (self, position=(0, 0), direction="E", alive=True, arrow_hit=0, gold_obtain=False, N=8, kb=None):
		self.position = position
		self.direction = direction
		self.alive = alive
		self.arrow_hit = arrow_hit
		self.gold_obtain = gold_obtain

		if kb is None:	
			self.kb = KB(N)
			i, j = self.position
			self.kb.add_fact(
				f"~B({i}, {j})", 
				f"~S({i}, {j})",
				f"~W({i}, {j})",
				f"~P({i}, {j})",
				f"Safe({i}, {j})"
			)
			self.kb.forward_chain()
		else:
			self.kb = kb

	def __hash__(self):
		return hash((
			self.position,
			self.direction,
			self.alive,
			self.arrow_hit,
			self.gold_obtain
			# frozenset(self.kb.facts)
		))
	
	def __eq__ (self, other):
		return (
			isinstance(other, Agent2) and
			self.position == other.position and
			self.direction == other.direction and
			self.alive == other.alive and
			self.arrow_hit == other.arrow_hit and
			self.gold_obtain == other.gold_obtain
			# frozenset(self.kb.facts) == frozenset(other.kb.facts)
		)
	
	def __lt__(self, other):
		return (self.position, self.direction) < (other.position, other.direction)

	def __repr__(self):
		return f"(pos{self.position},direction={self.direction},gold={self.gold_obtain},arrow={self.arrow_hit})"
	
	def clone(self):
		from copy import deepcopy
		return Agent2(
			position=self.position,
			direction=self.direction,
			alive=self.alive,
			arrow_hit=self.arrow_hit,
			gold_obtain=self.gold_obtain,
			N=self.kb.N,
			kb=deepcopy(self.kb)
		)
	
	def perceive(self, percepts):
		if f"Deadly{self.position}" in percepts:
			self.alive = False
			return
		
		for percept in percepts:
			self.kb.add_fact(percept)

		self.kb.forward_chain()

	def turn_left(self):
		agent = self.clone()
		agent.direction = DIRECTION[(DIRECTION[agent.direction] - 1) % 4]
		return agent
	
	def turn_right(self):
		agent = self.clone()
		agent.direction = DIRECTION[(DIRECTION[agent.direction] + 1) % 4]
		return agent

	def move_forward(self):
		agent = self.clone()

		di, dj = MOVE[agent.direction]
		i, j = (agent.position[0] + di, agent.position[1] + dj)

		if (0 <= i < agent.kb.N) and (0 <= j < agent.kb.N):
			agent.position = (i, j)
		
		return agent

	def grab_gold(self):
		agent = self.clone()
		if agent.kb.is_premise_true(f"G{agent.position}"):
			agent.gold_obtain = True
		return agent
	
	def possible_wumpus_in_line(self):
		"""Trả về danh sách ô khả năng có Wumpus theo hướng agent"""
		mi, mj = MOVE[self.direction]
		i, j = self.position
		cells = []
		i += mi
		j += mj
		while 0 <= i < self.kb.N and 0 <= j < self.kb.N:
			if self.kb.is_possible_wumpus(i, j):
				cells.append((i, j))
			i += mi
			j += mj
		return cells


	
class Env:
	def __init__(self, environment_map):
		self._environment_map = environment_map

	def get_percept(self, pos):
		percepts = []
		i, j = pos
		square = self._environment_map[i][j]

		if ("W" in square) or ("P" in square):
			return [f"Deadly{pos}"]

		if "G" in square:
			percepts.append(f"G{pos}")

		if "B" in square:
			percepts.append(f"B{pos}")
		else:
			percepts.append(f"~B{pos}")

		if "S" in square:
			percepts.append(f"S{pos}")
		else:
			percepts.append(f"~S{pos}")
		
		return percepts