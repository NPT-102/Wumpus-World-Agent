# agent/hybrid_agent_action_dynamic.py
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
    """Quay Agent về hướng desired_dir."""
    turn_count = 0
    dir_list = list(DIRECTION.keys())[:4]  # ["E","S","W","N"]
    print(f"[ROTATE] Current direction: {agent.direction}, Desired: {desired_dir}")
    while agent.direction != desired_dir and turn_count < 4:
        cur_idx = dir_list.index(agent.direction)
        des_idx = dir_list.index(desired_dir)
        if (cur_idx + 1) % 4 == des_idx:
            agent.turn_right()
            print(f"[ROTATE] Turned right → Now facing {agent.direction}")
        else:
            agent.turn_left()
            print(f"[ROTATE] Turned left → Now facing {agent.direction}")
        turn_count += 1

def direction_from_delta(di, dj):
    """Xác định hướng từ delta (di, dj)."""
    for d, (mi, mj) in MOVE.items():
        if (di, dj) == (mi, mj):
            return d
    return None

def hybrid_agent_action_dynamic(agent: Agent, game_map, wumpus_positions, pit_positions):
    N = len(game_map)
    visited = set()
    kb = agent.kb if hasattr(agent, 'kb') else KB(N=N)
    action_counter = 0  # Đếm số hành động thực tế

    while True:
        if not agent.alive:
            print("Agent died! Game Over.")
            break

        # 1. Cảm nhận
        agent.perceive()
        visited.add(agent.position)

        # 2. Nhặt vàng nếu có
        if agent.grab_gold():
            print(f"Grabbed gold at {agent.position}!")
            action_counter += 1
            print(f"[DEBUG] Action counter: {action_counter} (grab gold)")

        # 3. Nếu có vàng và ở (0,0) → về đích
        if agent.gold_obtain and agent.position == (0, 0):
            agent.escape()
            print("Escaped successfully!")
            break

        # 4. Lập kế hoạch tạm thời
        plan_agent = Agent2(
            position=agent.position,
            direction=agent.direction,
            alive=agent.alive,
            arrow_hit=agent.arrow_hit,
            gold_obtain=agent.gold_obtain,
            N=N,
            kb=deepcopy(agent.kb)
        )

        # 5. Kiểm tra Wumpus trong tầm bắn
        if agent.arrow_hit == 0:
            mi, mj = MOVE[agent.direction]
            i, j = agent.position
            in_sight_wumpus = []

            i += mi
            j += mj
            while (0 <= i < N) and (0 <= j < N):
                for w_pos in wumpus_positions:
                    if (i, j) == w_pos:
                        in_sight_wumpus.append(w_pos)
                        break
                i += mi
                j += mj

            if in_sight_wumpus:
                wumpus_pos = in_sight_wumpus[0]

                temp_map = deepcopy(game_map)
                if "W" in temp_map[wumpus_pos[0]][wumpus_pos[1]]:
                    temp_map[wumpus_pos[0]][wumpus_pos[1]].remove("W")

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
                    print(f"Shooting Wumpus at {wumpus_pos}")
                    agent.shoot()
                    action_counter += 1
                    print(f"[DEBUG] Action counter: {action_counter} (shoot)")
                    wumpus_positions = [w for w in wumpus_positions if w != wumpus_pos]
                    if action_counter >= 5:
                        print(f"[DEBUG] 5 actions reached → Wumpus moves")
                        wumpus_positions = update_wumpus_position(agent, game_map, wumpus_positions, pit_positions)
                        action_counter = 0
                    continue

        # 6. Tìm đường đi tiếp
        path_states = dijkstra(game_map, plan_agent)
        if not path_states or len(path_states) < 2:
            print("No path found or already at goal.")
            break

        next_state = path_states[1]

        # Nếu chỉ xoay hướng
        if next_state.position == agent.position:
            rotate_towards(agent, next_state.direction)
            action_counter += 1
            print(f"[DEBUG] Action counter: {action_counter} (rotate)")
        else:
            # Xoay tới hướng trước khi đi
            rotate_towards(agent, direction_from_delta(next_state.position[0]-agent.position[0],
                                                       next_state.position[1]-agent.position[1]))
            action_counter += 1
            print(f"[DEBUG] Action counter: {action_counter} (rotate)")

            # Di chuyển 1 ô
            agent.move_forward()
            action_counter += 1
            print(f"[DEBUG] Action counter: {action_counter} (move)")

        # 7. Kiểm tra nếu đủ 5 hành động → Wumpus di chuyển
        if action_counter >= 5:
            print(f"[DEBUG] 5 actions reached → Wumpus moves")
            wumpus_positions = update_wumpus_position(agent, game_map, wumpus_positions, pit_positions)
            action_counter = 0

    return {
        "final_position": agent.position,
        "score": agent.score,
        "gold": agent.gold_obtain,
        "alive": agent.alive
    }
