# agent/hybrid_agent_action_dynamic.py
from agent.agent import Agent, Agent2, MOVE, DIRECTION
from search.dijkstra import dijkstra
from env_simulator.kb import KnowledgeBase as KB
from module.moving_Wumpus import update_wumpus_position

def rotate_towards(agent: Agent, desired_dir: str):
    """Quay Agent về hướng desired_dir."""
    turn_count = 0
    dir_list = list(DIRECTION.keys())[:4]  # ["E","S","W","N"]
    while agent.direction != desired_dir and turn_count < 4:
        cur_idx = dir_list.index(agent.direction)
        des_idx = dir_list.index(desired_dir)
        if (cur_idx + 1) % 4 == des_idx:
            agent.turn_right()
        else:
            agent.turn_left()
        turn_count += 1

def direction_from_delta(di, dj):
    """Xác định hướng từ delta (di, dj)."""
    for d, (mi, mj) in MOVE.items():
        if (di, dj) == (mi, mj):
            return d
    return None

def wumpus_in_sight(agent: Agent, game_map):
    """Kiểm tra có Wumpus trong tầm bắn hay không."""
    mi, mj = MOVE[agent.direction]
    i, j = agent.position
    N = len(game_map)
    i += mi
    j += mj
    while (0 <= i < N) and (0 <= j < N):
        if "W" in game_map[i][j]:
            return (i, j)  # Vị trí Wumpus
        i += mi
        j += mj
    return None

def hybrid_agent_action_dynamic(agent: Agent, game_map, wumpus_position, pit_positions):
    N = len(game_map)
    visited = set()
    kb = agent.kb if hasattr(agent, 'kb') else KB(N=N)

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

        # 3. Nếu có vàng và ở (0,0) → về đích
        if agent.gold_obtain and agent.position == (0, 0):
            agent.escape()
            print("Escaped successfully!")
            break

        # 4. Quyết định bắn Wumpus nếu có trong tầm và còn đạn
        if agent.arrow_hit == 0:
            wumpus_pos = wumpus_in_sight(agent, game_map)
            if wumpus_pos:
                print(f"Wumpus spotted at {wumpus_pos}, shooting!")
                agent.shoot()
                # Sau khi bắn, Wumpus di chuyển (nếu còn)
                wumpus_position = update_wumpus_position(agent, game_map, wumpus_position, pit_positions)
                continue  # Lập kế hoạch lại vì bản đồ thay đổi

        # 5. Lập kế hoạch tới mục tiêu
        plan_agent = Agent2(
            position=agent.position,
            direction=agent.direction,
            alive=agent.alive,
            arrow_hit=agent.arrow_hit,
            gold_obtain=agent.gold_obtain,
            N=N,
            kb=agent.kb
        )
        path_states = dijkstra(game_map, plan_agent)

        if not path_states or len(path_states) < 2:
            print("No path found or already at goal.")
            break

        # 6. Bước tiếp theo
        next_state = path_states[1]

        if next_state.position == agent.position:
            # Nếu bước này chỉ xoay
            rotate_towards(agent, next_state.direction)
            wumpus_position = update_wumpus_position(agent, game_map, wumpus_position, pit_positions)
            continue

        # Nếu bước này là di chuyển
        di = next_state.position[0] - agent.position[0]
        dj = next_state.position[1] - agent.position[1]
        desired_dir = direction_from_delta(di, dj)

        if desired_dir is None:
            print(f"[ERROR] Invalid move from {agent.position} to {next_state.position}")
            break

        rotate_towards(agent, desired_dir)
        agent.move_forward()

        # Sau khi di chuyển, Wumpus di chuyển
        wumpus_position = update_wumpus_position(agent, game_map, wumpus_position, pit_positions)

    return {
        "final_position": agent.position,
        "score": agent.score,
        "gold": agent.gold_obtain,
        "alive": agent.alive
    }
