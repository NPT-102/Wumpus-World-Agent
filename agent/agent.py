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

class Agent:
	tscore = 0
	gold_obtain = False
	position = (0, 0)
	direction = "E" #East
	action = {
		"move": -1,
		"lturn": -1,
		"rturn": -1,
		"grab": 10,
		"shoot": -10,
		"die": -1000,
		"esc": 1000,
		"esc!": 0
	}

	def __init__(self, N=4):
		self.kb = KB(N=N)
		self.kb.add_fact("~B(0, 0)", "~S(0, 0)")
		self.kb.forward_chain()

	def move_forward(self):
		move = MOVE[self.direction]
		position = (position(0) + move(0), position(1) + move(1))

	def turn_left(self):
		self.direction = DIRECTION[(DIRECTION[self.direction] - 1) % 4]

	def turn_right(self):
		self.direction = DIRECTION[(DIRECTION[self.direction] + 1) % 4]

	def shoot(self):
		pass