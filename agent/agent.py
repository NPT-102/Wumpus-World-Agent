from env_simulator.kb import KnowledgeBase as KB
from env_simulator.environment import WumpusEnvironment
from env_simulator.risk_calculator import RiskCalculator

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

	def __init__(self, environment: WumpusEnvironment, N=8):
		self.kb = KB(N=N)
		self.N = N
		self.environment = environment  # No direct map access - only through environment interface
		self.risk_calculator = RiskCalculator(N)
		
		# Initialize starting position as safe
		i, j = self.position
		self.kb.add_fact(
			f"~B({i}, {j})", 
			f"~S({i}, {j})",
			f"~W({i}, {j})",
			f"~P({i}, {j})",
			f"Safe({i}, {j})"
		)
		self.kb.forward_chain()
		
		# Initial perception
		self.perceive()

	def perceive(self):
		"""Perceive environment through official interface only"""
		i, j = self.position
		percepts = self.environment.get_percept(self.position)
		
		# Handle death scenarios
		if "Death_Wumpus" in percepts or "Death_Pit" in percepts:
			self.alive = False
			self.score += SCORE["die"]
			if "Death_Wumpus" in percepts:
				print(f"Agent killed by Wumpus at {self.position}!")
			if "Death_Pit" in percepts:
				print(f"Agent fell into pit at {self.position}!")
			return
		
		# Process normal percepts
		if "Stench" in percepts:
			self.kb.add_fact(f"S({i}, {j})")
		else:
			self.kb.add_fact(f"~S({i}, {j})")

		if "Breeze" in percepts:
			self.kb.add_fact(f"B({i}, {j})")
		else:
			self.kb.add_fact(f"~B({i}, {j})")
		
		if "Glitter" in percepts:
			self.kb.add_fact(f"G({i}, {j})")
		else:
			self.kb.add_fact(f"~G({i}, {j})")
		
		# Update risk calculator
		self.risk_calculator.update_perception(self.position, percepts)
		
		# Mark current position as safe (agent didn't die)
		self.kb.add_fact(f"~P({i}, {j})")
		self.kb.add_fact(f"~W({i}, {j})")
		self.kb.add_fact(f"Safe({i}, {j})")
		
		self.kb.forward_chain()


	def move_forward(self):
		if not self.alive:
			return None

		move = MOVE[self.direction]
		i, j = (self.position[0] + move[0], self.position[1] + move[1])
		print(f"Agent is trying to move {self.direction} to {(i, j)}.")
		self.score += SCORE["move"]
		
		if not self.environment.is_valid_position((i, j)):
			print("Agent cannot move out of bounds.")
			return False
		
		# Move to the position first
		self.position = (i, j)
		
		# Then perceive what happened
		self.perceive()
		
		# Return whether agent survived the move
		return self.alive


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

		# Use environment interface to grab gold
		if self.environment.grab_gold(self.position):
			self.gold_obtain = True
			self.score += SCORE["grab"]
			print(f"Grabbed gold at {self.position}!")
			return True
		return False

	def shoot(self):
		if not self.alive:
			return None
		
		if self.arrow_hit != 0:
			print("No arrows left!")
			return False

		self.score += SCORE["shoot"]
		
		# Use environment interface to shoot
		hit_any = self.environment.shoot_arrow(self.position, self.direction)
		
		if hit_any:
			self.arrow_hit = 1
			# Update knowledge base - remove wumpus facts in shooting line
			mi, mj = MOVE[self.direction]
			i, j = self.position
			i += mi
			j += mj
			while (0 <= i < self.N) and (0 <= j < self.N):
				self.kb.add_fact(f"~W({i}, {j})")
				# Remove stench around shot location
				for di, dj in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
					ni, nj = i + di, j + dj
					if (0 <= ni < self.N) and (0 <= nj < self.N):
						self.kb.add_fact(f"~S({ni}, {nj})")
				i += mi
				j += mj
			
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
	
	def get_safe_moves(self):
		"""Get list of adjacent moves with low risk"""
		moves = []
		current_i, current_j = self.position
		
		for direction, (di, dj) in MOVE.items():
			next_pos = (current_i + di, current_j + dj)
			
			if self.environment.is_valid_position(next_pos):
				risk = self.risk_calculator.calculate_total_risk(next_pos)
				moves.append((next_pos, direction, risk))
		
		# Sort by risk (lowest first)
		moves.sort(key=lambda x: x[2])
		return moves
	
	def get_safest_move(self):
		"""Get the safest adjacent move"""
		safe_moves = self.get_safe_moves()
		if safe_moves:
			return safe_moves[0]  # Return (position, direction, risk) tuple
		return None
	
	def plan_path_to_goal(self, goal_position=None):
		"""Plan a path to goal or explore safely"""
		if goal_position is None:
			# Find exploration targets
			candidates = self.risk_calculator.get_exploration_candidates(self.position)
			if candidates:
				goal_position = candidates[0]  # Choose safest exploration target
		
		if goal_position:
			# Simple pathfinding toward goal
			current_i, current_j = self.position
			goal_i, goal_j = goal_position
			
			# Choose direction that reduces distance to goal
			best_move = None
			best_distance = float('inf')
			
			for direction, (di, dj) in MOVE.items():
				next_pos = (current_i + di, current_j + dj)
				if self.environment.is_valid_position(next_pos):
					distance = abs(goal_i - next_pos[0]) + abs(goal_j - next_pos[1])
					risk = self.risk_calculator.calculate_total_risk(next_pos)
					
					# Prefer moves that get closer to goal with acceptable risk
					if distance < best_distance and risk < 0.5:  # Risk threshold
						best_distance = distance
						best_move = (next_pos, direction, risk)
			
			return best_move
		
		return None
	
	def die(self):
		self.score += SCORE["die"]
		self.alive = False


# Agent for Search algorithm
class Agent2:
	def __init__(self, position=(0, 0), direction="E", alive=True, arrow_hit=0, gold_obtain=False, N=8, kb=None, risk_calculator=None):
		self.position = position
		self.direction = direction
		self.alive = alive
		self.arrow_hit = arrow_hit
		self.gold_obtain = gold_obtain
		self.N = N
		
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
		
		if risk_calculator is None:
			self.risk_calculator = RiskCalculator(N)
		else:
			self.risk_calculator = risk_calculator

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
			N=self.N,
			kb=deepcopy(self.kb),
			risk_calculator=deepcopy(self.risk_calculator)
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
		"""Return list of possible Wumpus positions in agent's facing direction"""
		mi, mj = MOVE[self.direction]
		i, j = self.position
		cells = []
		i += mi
		j += mj
		while 0 <= i < self.N and 0 <= j < self.N:
			if self.risk_calculator.calculate_wumpus_probability((i, j)) > 0.3:  # Threshold for shooting
				cells.append((i, j))
			i += mi
			j += mj
		return cells


	
class Env:
	def __init__(self, environment: WumpusEnvironment):
		self.environment = environment

	def get_percept(self, pos):
		"""Get percepts at position through environment interface"""
		return self.environment.get_percept(pos)