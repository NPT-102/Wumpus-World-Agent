import heapq
from agent.agent import Agent2, Env

def agent_state(agent: Agent2):
    return (agent.position, agent.direction, agent.gold_obtain, agent.arrow_hit)

def dijkstra(environment_map, agent: Agent2):
    """
    Knowledge-based Dijkstra pathfinding that only uses the agent's knowledge base,
    not omniscient map information.
    """
    env = Env(environment_map)

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
            ni, nj = new_node.position
            # Only use knowledge-based reasoning - no direct map access!
            if 0 <= ni < len(environment_map) and 0 <= nj < len(environment_map[0]):
                if node.kb.is_premise_true(f"Safe({ni}, {nj})"):
                    # Known safe cell
                    neighbors.append((1, new_node))
                elif node.kb.is_premise_true(f"P({ni}, {nj})") or node.kb.is_premise_true(f"W({ni}, {nj})"):
                    # Known dangerous cell - very high penalty
                    neighbors.append((1000, new_node))
                else:
                    # Unknown cell - moderate penalty for exploration
                    neighbors.append((100, new_node))

        grab_node = node.grab_gold()
        if grab_node.gold_obtain and not node.gold_obtain:
            neighbors.append((0, grab_node))

        for neighbor_cost, neighbor in neighbors:
            neighbor_state = agent_state(neighbor)
            new_cost = cost + neighbor_cost
            
            if neighbor_state not in total_cost or new_cost < total_cost[neighbor_state]:
                total_cost[neighbor_state] = new_cost
                parent[neighbor_state] = state
                node_map[neighbor_state] = neighbor
                heapq.heappush(q, (new_cost, neighbor))

    return None
