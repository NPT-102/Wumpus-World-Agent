import heapq
from agent.agent import Agent2, Env

def dijkstra(map, agent: Agent2):
	env = Env(map)

	q = [(0, agent)]
	total_cost = {agent: 0}
	parent = {agent: None}

	while q:
		cost, node = heapq.heappop(q)
		node.perceive(env.get_percept(node.position))

		if (node.position == (0, 0)) and (node.gold_obtain is True):
			path = []
			curr = node
			while curr:
				path.append(curr)
				curr = parent[curr]
			return path[::-1]

		if (not node.alive) or (total_cost[node] < cost):
			continue

		# Retrieve adjacent node
		neighbors = []

		neighbors.append((1, node.turn_left()))
		neighbors.append((1, node.turn_right()))

		new_node = node.move_forward()
		if new_node.position != node.position:
			if node.kb.is_premise_true(f"Safe{new_node.position}"):
				neighbors.append((1 + 0, new_node))
			else:
				neighbors.append((1 + 500, new_node))

		grab_node = node.grab_gold()
		if grab_node.gold_obtain is True:
			neighbors.append((0, grab_node))

		for weight, neighbor in neighbors:
			new_cost = weight + cost
			if neighbor not in total_cost or total_cost[neighbor] > new_cost:
				total_cost[neighbor] = new_cost
				parent[neighbor] = node
				heapq.heappush(q, (new_cost, neighbor))
