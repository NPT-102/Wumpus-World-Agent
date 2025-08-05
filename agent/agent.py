from env_simulator.kb import KnowledgeBase as KB

DIRECTION = {
	"E": 0, "S": 1, "W": 2, "N": 3,
	0: "E", 1: "S", 2: "W", 3: "N",
}

MOVE = {
	"E": (0, 1), 	# East
	"W": (0, -1),	# West
	"S": (-1, 0),	# South
	"N": (1, 0),  	# North
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

	def __init__(self, map: list[list[list]], N=8):
		self.kb = KB(N=N)
		self.N = N
		self.map = map
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
		pos = self.map[i, j]
		if "B" in pos:
			self.kb.add_fact(f"B({i}, {j})")
		else:
			self.kb.add_fact(f"~B({i}, {j})")

		if "S" in pos:
			self.kb.add_fact(f"S({i}, {j})")
		else:
			self.kb.add_fact(f"~S({i}, {j})")

		self.kb.forward_chain()

	def move_forward(self):
		if not self.alive:
			return None

		move = MOVE[self.direction]
		i, j = (self.position[0] + move[0], self.position[1] + move[1])
		self.score += SCORE["move"]
		if (0 <= i < self.N) and (0 <= j < self.N):
			if ("W" not in self.map[i][j]) and ("P" not in self.map[i][j]):
				self.position = (i, j)
				self.perceive()
				return True
			else:
				self.die()
		
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
		pos = self.map[i, j]

		if "G" in pos:
			self.gold_obtain = True
			self.score += SCORE["grab"]
			return True
		return False

	def shoot(self):
		if not self.alive:
			return None
		
		self.score += SCORE["shoot"]
		mi, mj = MOVE[self.direction]
		i, j = self.position
		while (0 <= i < self.N) and (0 <= j < self.N):
			if "W" in self.map[i][j]:
				# TODO
				self.map[i][j].remove("W")
				for di, dj in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
					ni, nj = i + di, j + dj
					if (0 <= ni < self.N) and (0 <= nj < self.N):
						if "S" in self.map[ni][nj]:
							self.map[ni][nj].remove("S")

				self.arrow_hit = 1
				return True

			i += mi
			j += mj

		self.arrow_hit = -1
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