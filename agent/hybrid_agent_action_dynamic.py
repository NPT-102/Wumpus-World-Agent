from agent.agent import Agent, Agent2, MOVE, DIRECTION
from search.dijkstra import dijkstra
from env_simulator.kb import KnowledgeBase as KB
from module.moving_Wumpus import update_wumpus_position
from copy import deepcopy

SCORE = {
    "move": -1,
    "shoot": -10,
    "grab": 1000,
    "die": -1000,
    "escape": 0
}

def rotate_towards(agent: Agent, desired_dir: str):
    turns_done = 0
    dir_list = list(DIRECTION.keys())[:4]
    while agent.direction != desired_dir and turns_done < 4:
        cur_idx = dir_list.index(agent.direction)
        des_idx = dir_list.index(desired_dir)
        if (cur_idx + 1) % 4 == des_idx:
            agent.turn_right()
        else:
            agent.turn_left()
        turns_done += 1
    return turns_done

def direction_from_delta(di, dj):
    for d, (mi, mj) in MOVE.items():
        if (di, dj) == (mi, mj):
            return d
    return None

def hybrid_agent_action_dynamic(agent: Agent, game_map, wumpus_positions, pit_positions):
    N = len(game_map)
    visited = set()
    kb = agent.kb if hasattr(agent, 'kb') else KB(N=N)
    action_counter = 0

    # Quản lý trạng thái sống/chết của Wumpus
    wumpus_alive = [True]*len(wumpus_positions)

    def increment_counter(count=1):
        nonlocal action_counter, wumpus_positions
        action_counter += count
        while action_counter >= 5:
            wumpus_positions = update_wumpus_position(agent, game_map, wumpus_positions, pit_positions, wumpus_alive)
            action_counter -= 5

    while True:
        if not agent.alive:
            break

        agent.perceive()
        visited.add(agent.position)

        if agent.grab_gold():
            increment_counter()

        if agent.gold_obtain and agent.position == (0, 0):
            agent.escape()
            increment_counter()
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

        if agent.arrow_hit == 0:
            mi, mj = MOVE[agent.direction]
            i, j = agent.position
            in_sight_wumpus = []

            i += mi
            j += mj
            while 0 <= i < N and 0 <= j < N:
                for idx, w_pos in enumerate(wumpus_positions):
                    if (i, j) == w_pos and wumpus_alive[idx]:
                        in_sight_wumpus.append((idx, w_pos))
                        break
                i += mi
                j += mj

            if in_sight_wumpus:
                idx, w_pos = in_sight_wumpus[0]
                temp_map = deepcopy(game_map)
                if "W" in temp_map[w_pos[0]][w_pos[1]]:
                    temp_map[w_pos[0]][w_pos[1]].remove("W")

                path_with_detour = dijkstra(temp_map, plan_agent)
                path_direct = dijkstra(game_map, plan_agent)

                shoot_wumpus = False
                if path_with_detour and path_direct:
                    detour_cost = (len(path_with_detour) - len(path_direct)) * SCORE["move"]
                    if detour_cost >= SCORE["shoot"]:
                        shoot_wumpus = True
                else:
                    shoot_wumpus = True

                if shoot_wumpus:
                    agent.shoot()
                    wumpus_alive[idx] = False
                    wumpus_positions[idx] = w_pos  # giữ vị trí để update vẫn nhận biết là dead
                    continue

        path_states = dijkstra(game_map, plan_agent)
        if not path_states or len(path_states) < 2:
            break

        next_state = path_states[1]

        if next_state.position == agent.position:
            turns = rotate_towards(agent, next_state.direction)
            increment_counter(turns)
        else:
            di = next_state.position[0] - agent.position[0]
            dj = next_state.position[1] - agent.position[1]
            desired_dir = direction_from_delta(di, dj)
            if desired_dir is None:
                break
            turns = rotate_towards(agent, desired_dir)
            increment_counter(turns)
            agent.move_forward()
            increment_counter()

    return {
        "final_position": agent.position,
        "score": agent.score,
        "gold": agent.gold_obtain,
        "alive": agent.alive
    }
