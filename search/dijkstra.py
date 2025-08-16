import heapq
from agent.agent import Agent2, Env

def agent_state(agent: Agent2):
    return (agent.position, agent.direction, agent.gold_obtain, agent.arrow_hit)

def dijkstra(map, agent: Agent2):
    env = Env(map)

    q = [(0, agent)]
    total_cost = {agent_state(agent): 0}
    parent = {agent_state(agent): None}
    node_map = {agent_state(agent): agent}  # lưu lại object

    while q:
        cost, node = heapq.heappop(q)
        node.perceive(env.get_percept(node.position))
        state = agent_state(node)

        if (node.position == (0, 0)) and (node.gold_obtain is True):
            # build path of nodes
            path = []
            curr_state = state
            while curr_state:
                path.append(node_map[curr_state])
                curr_state = parent[curr_state]
            return path[::-1]

        if (not node.alive) or (total_cost[state] < cost):
            continue

        neighbors = []
        neighbors.append((1, node.turn_left()))
        neighbors.append((1, node.turn_right()))

        new_node = node.move_forward()
        if new_node.position != node.position:
            if node.kb.is_premise_true(f"Safe{new_node.position}"):
                neighbors.append((1, new_node))
            else:
                # Check if the new position has stench - lower penalty for exploration
                ni, nj = new_node.position
                if 0 <= ni < len(map) and 0 <= nj < len(map[0]) and 'S' in map[ni][nj]:
                    neighbors.append((50, new_node))  # Lower penalty for stench cells
                else:
                    neighbors.append((501, new_node))  # High penalty for other unsafe moves

        grab_node = node.grab_gold()
        if grab_node.gold_obtain:
            neighbors.append((0, grab_node))

        for weight, neighbor in neighbors:
            neighbor_state = agent_state(neighbor)
            new_cost = cost + weight
            if neighbor_state not in total_cost or total_cost[neighbor_state] > new_cost:
                total_cost[neighbor_state] = new_cost
                parent[neighbor_state] = state
                node_map[neighbor_state] = neighbor  # lưu node object
                heapq.heappush(q, (new_cost, neighbor))
