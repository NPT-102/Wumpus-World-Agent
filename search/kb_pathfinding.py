"""
A* and improved Dijkstra pathfinding for KB-Safe Agent
"""
import heapq
from typing import List, Tuple, Optional, Set
import math

class PathNode:
    """Node for pathfinding with KB-safe information"""
    def __init__(self, position: Tuple[int, int], g_cost: float = 0, h_cost: float = 0, parent=None):
        self.position = position
        self.g_cost = g_cost  # Cost from start
        self.h_cost = h_cost  # Heuristic cost to goal
        self.f_cost = g_cost + h_cost  # Total cost
        self.parent = parent
    
    def __lt__(self, other):
        return self.f_cost < other.f_cost
    
    def __eq__(self, other):
        return self.position == other.position
    
    def __hash__(self):
        return hash(self.position)

def manhattan_distance(pos1: Tuple[int, int], pos2: Tuple[int, int]) -> float:
    """Calculate Manhattan distance between two positions"""
    return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])

def euclidean_distance(pos1: Tuple[int, int], pos2: Tuple[int, int]) -> float:
    """Calculate Euclidean distance between two positions"""
    return math.sqrt((pos1[0] - pos2[0])**2 + (pos1[1] - pos2[1])**2)

def get_neighbors(position: Tuple[int, int], grid_size: int) -> List[Tuple[int, int]]:
    """Get valid neighboring positions within grid bounds"""
    x, y = position
    neighbors = []
    
    for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
        nx, ny = x + dx, y + dy
        if 0 <= nx < grid_size and 0 <= ny < grid_size:
            neighbors.append((nx, ny))
    
    return neighbors

def kb_safe_astar(start: Tuple[int, int], 
                  goal: Tuple[int, int], 
                  kb_safe_positions: Set[Tuple[int, int]], 
                  visited_positions: Set[Tuple[int, int]], 
                  grid_size: int,
                  heuristic_func=manhattan_distance) -> Optional[List[Tuple[int, int]]]:
    """
    A* pathfinding using only KB-confirmed safe positions
    
    Args:
        start: Starting position
        goal: Target position  
        kb_safe_positions: Set of KB-confirmed safe positions
        visited_positions: Set of already visited positions
        grid_size: Size of the grid (N x N)
        heuristic_func: Heuristic function to use
    
    Returns:
        List of positions from start to goal, or None if no path exists
    """
    
    if start not in kb_safe_positions or goal not in kb_safe_positions:
        return None
    
    open_set = []
    closed_set = set()
    
    start_node = PathNode(start, 0, heuristic_func(start, goal))
    heapq.heappush(open_set, start_node)
    
    # Keep track of nodes for path reconstruction
    all_nodes = {start: start_node}
    
    while open_set:
        current = heapq.heappop(open_set)
        
        if current.position == goal:
            # Reconstruct path
            path = []
            node = current
            while node:
                path.append(node.position)
                node = node.parent
            return path[::-1]
        
        closed_set.add(current.position)
        
        for neighbor_pos in get_neighbors(current.position, grid_size):
            if neighbor_pos in closed_set:
                continue
            
            # Only consider KB-safe positions
            if neighbor_pos not in kb_safe_positions:
                continue
            
            # Calculate costs
            g_cost = current.g_cost + 1  # Each move costs 1
            
            # Bonus for visiting new positions vs revisiting old ones
            if neighbor_pos not in visited_positions:
                g_cost += 0.1  # Small penalty for unvisited (exploration vs exploitation)
            
            h_cost = heuristic_func(neighbor_pos, goal)
            
            # Check if we've seen this neighbor before
            if neighbor_pos in all_nodes:
                existing_node = all_nodes[neighbor_pos]
                if g_cost < existing_node.g_cost:
                    # Update existing node with better path
                    existing_node.g_cost = g_cost
                    existing_node.h_cost = h_cost
                    existing_node.f_cost = g_cost + h_cost
                    existing_node.parent = current
                    heapq.heappush(open_set, existing_node)
            else:
                # Create new node
                neighbor_node = PathNode(neighbor_pos, g_cost, h_cost, current)
                all_nodes[neighbor_pos] = neighbor_node
                heapq.heappush(open_set, neighbor_node)
    
    return None  # No path found

def kb_safe_dijkstra(start: Tuple[int, int], 
                     goal: Tuple[int, int], 
                     kb_safe_positions: Set[Tuple[int, int]], 
                     visited_positions: Set[Tuple[int, int]], 
                     grid_size: int) -> Optional[List[Tuple[int, int]]]:
    """
    Dijkstra pathfinding using only KB-confirmed safe positions
    
    Args:
        start: Starting position
        goal: Target position
        kb_safe_positions: Set of KB-confirmed safe positions
        visited_positions: Set of already visited positions  
        grid_size: Size of the grid (N x N)
    
    Returns:
        List of positions from start to goal, or None if no path exists
    """
    
    if start not in kb_safe_positions or goal not in kb_safe_positions:
        return None
    
    # Priority queue: (cost, position)
    pq = [(0, start)]
    distances = {start: 0}
    previous = {start: None}
    visited = set()
    
    while pq:
        current_cost, current_pos = heapq.heappop(pq)
        
        if current_pos in visited:
            continue
            
        visited.add(current_pos)
        
        if current_pos == goal:
            # Reconstruct path
            path = []
            pos = goal
            while pos is not None:
                path.append(pos)
                pos = previous[pos]
            return path[::-1]
        
        for neighbor_pos in get_neighbors(current_pos, grid_size):
            if neighbor_pos in visited or neighbor_pos not in kb_safe_positions:
                continue
            
            # Calculate cost to neighbor
            cost = 1  # Base cost
            
            # Add small penalty for unvisited positions to encourage exploration of new areas
            if neighbor_pos not in visited_positions:
                cost += 0.1
            
            new_cost = current_cost + cost
            
            if neighbor_pos not in distances or new_cost < distances[neighbor_pos]:
                distances[neighbor_pos] = new_cost
                previous[neighbor_pos] = current_pos
                heapq.heappush(pq, (new_cost, neighbor_pos))
    
    return None  # No path found

def find_best_kb_safe_path(start: Tuple[int, int], 
                           targets: List[Tuple[int, int]], 
                           kb_safe_positions: Set[Tuple[int, int]], 
                           visited_positions: Set[Tuple[int, int]], 
                           grid_size: int,
                           use_astar: bool = True) -> Optional[Tuple[Tuple[int, int], List[Tuple[int, int]]]]:
    """
    Find the best path to any of the target positions
    
    Args:
        start: Starting position
        targets: List of potential target positions
        kb_safe_positions: Set of KB-confirmed safe positions
        visited_positions: Set of already visited positions
        grid_size: Size of the grid
        use_astar: Whether to use A* (True) or Dijkstra (False)
    
    Returns:
        Tuple of (best_target, path_to_target) or None if no path exists
    """
    
    best_path = None
    best_target = None
    shortest_cost = float('inf')
    
    pathfind_func = kb_safe_astar if use_astar else kb_safe_dijkstra
    
    for target in targets:
        if use_astar:
            path = pathfind_func(start, target, kb_safe_positions, visited_positions, grid_size)
        else:
            path = pathfind_func(start, target, kb_safe_positions, visited_positions, grid_size)
        
        if path:
            path_cost = len(path)
            
            # Prioritize unvisited targets
            if target not in visited_positions:
                path_cost -= 0.5
            
            if path_cost < shortest_cost:
                shortest_cost = path_cost
                best_path = path
                best_target = target
    
    return (best_target, best_path) if best_path else None
