import heapq
from agent.agent import Agent2

def agent_state(agent: Agent2):
    return (agent.position, agent.direction, agent.gold_obtain, agent.arrow_hit)

def dijkstra(environment_map, agent: Agent2):
    """
    Risk-based Dijkstra pathfinding that uses risk calculations instead of direct map access
    """
    q = [(0, agent)]
    total_cost = {agent_state(agent): 0}
    parent = {agent_state(agent): None}
    node_map = {agent_state(agent): agent}  # Store object references

    while q:
        cost, node = heapq.heappop(q)
        state = agent_state(node)

        # Goal check: reached (0,0) with gold
        if (node.position == (0, 0)) and (node.gold_obtain is True):
            # Build path of nodes
            path = []
            curr_state = state
            while curr_state:
                path.append(node_map[curr_state])
                curr_state = parent[curr_state]
            return path[::-1]

        if (not node.alive) or (total_cost[state] < cost):
            continue

        neighbors = []
        
        # Add rotation moves (always safe)
        neighbors.append((1, node.turn_left()))
        neighbors.append((1, node.turn_right()))

        # Add forward movement with risk-based costing
        new_node = node.move_forward()
        if new_node.position != node.position:
            ni, nj = new_node.position
            
            # Check bounds
            if 0 <= ni < node.N and 0 <= nj < node.N:
                # Use risk calculator instead of direct map access
                risk = node.risk_calculator.calculate_total_risk((ni, nj))
                
                if risk == 0.0:
                    # Known safe cell - low cost
                    neighbors.append((1, new_node))
                elif risk >= 0.9:
                    # Very dangerous - very high cost
                    neighbors.append((1000, new_node))
                elif risk >= 0.5:
                    # Moderately dangerous - high cost
                    neighbors.append((50, new_node))
                else:
                    # Low risk - moderate cost for exploration
                    move_cost = int(1 + risk * 20)  # 1-21 based on risk
                    neighbors.append((move_cost, new_node))

        # Add gold grabbing action
        grab_node = node.grab_gold()
        if grab_node.gold_obtain and not node.gold_obtain:
            neighbors.append((0, grab_node))  # Free action to grab gold

        # Process neighbors
        for neighbor_cost, neighbor in neighbors:
            neighbor_state = agent_state(neighbor)
            new_cost = cost + neighbor_cost
            
            if neighbor_state not in total_cost or new_cost < total_cost[neighbor_state]:
                total_cost[neighbor_state] = new_cost
                parent[neighbor_state] = state
                node_map[neighbor_state] = neighbor
                heapq.heappush(q, (new_cost, neighbor))

    return None
