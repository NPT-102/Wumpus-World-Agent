# agent/hybrid_agent.py
from agent.agent import Agent, Agent2, DIRECTION as ADIR, MOVE as AMOVE, SCORE
from search.dijkstra import dijkstra
from copy import deepcopy

def _rotate_once_towards(agent: Agent, target_dir: str):
    cur_idx = ADIR[agent.direction]
    des_idx = ADIR[target_dir]
    if cur_idx == des_idx:
        return False
    if (cur_idx + 1) % 4 == des_idx:
        agent.turn_right()
        return True
    if (cur_idx - 1) % 4 == des_idx:
        agent.turn_left()
        return True
    agent.turn_right()
    return True

def _dir_from_delta(di: int, dj: int) -> str | None:
    for d, vec in AMOVE.items():
        if vec == (di, dj):
            return d
    return None

def calculate_path_cost(path_states):
    """Tính chi phí điểm của path (−1 mỗi bước đi hoặc quay, grab = 0)."""
    if not path_states:
        return float("inf")
    cost = 0
    for idx in range(1, len(path_states)):
        prev = path_states[idx - 1]
        cur = path_states[idx]
        if cur.position != prev.position:
            cost += abs(SCORE["move"])  # di chuyển
        elif cur.direction != prev.direction:
            cost += abs(SCORE["turn"])  # xoay
    return cost

def hybrid_agent_action(agent: Agent, game_map: list[list[list]]):
    N = len(game_map)
    visited = set()

    while True:
        if not agent.alive:
            print("Agent died! Game Over.")
            break

        agent.perceive()
        visited.add(agent.position)

        if agent.grab_gold():
            print(f"Grabbed gold at {agent.position}!")

        if agent.gold_obtain and agent.position == (0, 0):
            agent.escape()
            print("Escaped successfully!")
            break

        plan_agent = Agent2(
            position=agent.position,
            direction=agent.direction,
            alive=agent.alive,
            arrow_hit=agent.arrow_hit,
            gold_obtain=agent.gold_obtain,
            N=N,
            kb=deepcopy(agent.kb)
        )

        # Kiểm tra bắn Wumpus nếu có lợi
        if agent.arrow_hit == 0:
            mi, mj = AMOVE[agent.direction]
            i, j = agent.position
            in_sight_wumpus = []
            i += mi
            j += mj
            while (0 <= i < N) and (0 <= j < N):
                if "W" in game_map[i][j]:
                    in_sight_wumpus.append((i, j))
                i += mi
                j += mj

            if in_sight_wumpus:
                path_with_wumpus = dijkstra(game_map, plan_agent)
                game_map_no_wumpus = deepcopy(game_map)
                for wpos in in_sight_wumpus:
                    if "W" in game_map_no_wumpus[wpos[0]][wpos[1]]:
                        game_map_no_wumpus[wpos[0]][wpos[1]].remove("W")
                path_no_wumpus = dijkstra(game_map_no_wumpus, plan_agent)

                cost_with = calculate_path_cost(path_with_wumpus)
                cost_no = calculate_path_cost(path_no_wumpus) + abs(SCORE["shoot"])

                if cost_no < cost_with:
                    print(f"Detour cost {cost_with} > Shooting cost {cost_no} → Shooting Wumpus at {in_sight_wumpus}")
                    agent.shoot()
                    continue

        path_states = dijkstra(game_map, plan_agent)
        if not path_states or len(path_states) < 2:
            print("No path found or already at goal.")
            break

        next_state = path_states[1]

        if next_state.position == agent.position:
            target_dir = next_state.direction
            if target_dir != agent.direction:
                _rotate_once_towards(agent, target_dir)
            else:
                agent.grab_gold()
            continue

        cur_i, cur_j = agent.position
        nxt_i, nxt_j = next_state.position
        di, dj = (nxt_i - cur_i, nxt_j - cur_j)
        desired_dir = _dir_from_delta(di, dj)

        if desired_dir is None:
            print("[ERROR] Next step is not an adjacent move; aborting.")
            break

        spins = 0
        while agent.direction != desired_dir and spins < 4:
            _rotate_once_towards(agent, desired_dir)
            spins += 1

        if agent.direction == desired_dir:
            agent.move_forward()
        else:
            print("[ERROR] Could not align direction; aborting.")
            break

    return {
        "final_position": agent.position,
        "score": agent.score,
        "gold": agent.gold_obtain,
        "alive": agent.alive,
    }
