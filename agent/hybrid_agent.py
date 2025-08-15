# agent/hybrid_agent.py
from agent.agent import Agent, Agent2, DIRECTION as ADIR, MOVE as AMOVE
from search.dijkstra import dijkstra
# KB có thể không cần import ở đây, để lại cũng không sao
# from env_simulator.kb import KnowledgeBase as KB

def _rotate_once_towards(agent: Agent, target_dir: str):
    """
    Xoay đúng 1 bước (trái hoặc phải) để tiến gần tới target_dir.
    Dựa trên ADIR trong agent.py:
        "E":0, "S":1, "W":2, "N":3 (và ngược lại)
    """
    cur_idx = ADIR[agent.direction]
    des_idx = ADIR[target_dir]
    if cur_idx == des_idx:
        return False  # không cần xoay

    # nếu quay phải 1 bước tới được desired
    if (cur_idx + 1) % 4 == des_idx:
        agent.turn_right()
        return True
    # nếu quay trái 1 bước tới được desired
    if (cur_idx - 1) % 4 == des_idx:
        agent.turn_left()
        return True

    # chênh 180 độ -> xoay phải (1 bước), vòng lặp ngoài sẽ gọi lại nếu cần
    agent.turn_right()
    return True


def _dir_from_delta(di: int, dj: int) -> str | None:
    """
    Tìm hướng (E/W/N/S) sao cho MOVE[hướng] == (di, dj)
    MOVE lấy từ agent.py: {"E":(0,1), "W":(0,-1), "S":(-1,0), "N":(1,0)}
    """
    for d, vec in AMOVE.items():
        if vec == (di, dj):
            return d
    return None


def hybrid_agent_action(agent: Agent, game_map: list[list[list]]):
    """
    Tác nhân lai:
      - Agent (thật) cảm nhận môi trường và cập nhật KB nội bộ.
      - Agent2 + dijkstra() lập kế hoạch đến đích (có vàng và quay về (0,0)),
        trong đó path có thể gồm các bước xoay hoặc tiến một ô.
      - Agent thật thực hiện đúng từng bước trong path: xoay hoặc đi lên ô kế.
    """
    N = len(game_map)
    visited = set()

    while True:
        if not agent.alive:
            print("Agent died! Game Over.")
            break

        # 1) Cảm nhận & cập nhật KB
        agent.perceive()
        visited.add(agent.position)

        # 2) Nếu có vàng ở đây -> nhặt
        if agent.grab_gold():
            print(f"Grabbed gold at {agent.position}!")

        # 3) Nếu đã có vàng và đang ở (0,0) -> thoát
        if agent.gold_obtain and agent.position == (0, 0):
            agent.escape()
            print("Escaped successfully!")
            break

        # 4) Dùng Agent2 + dijkstra() để lập kế hoạch trọn hành trình
        plan_agent = Agent2(
            position=agent.position,
            direction=agent.direction,
            alive=agent.alive,
            arrow_hit=agent.arrow_hit,
            gold_obtain=agent.gold_obtain,
            N=N,
            kb=agent.kb  # chia sẻ KB hiện tại
        )

        path_states = dijkstra(game_map, plan_agent)
        if not path_states or len(path_states) < 2:
            print("No path found or already at goal.")
            break

        # 5) Lấy bước tiếp theo (so với trạng thái hiện tại)
        next_state = path_states[1]

        # 5.a) Nếu bước tiếp theo CHỈ xoay hướng (không đổi ô)
        if next_state.position == agent.position:
            # Quay đúng theo hướng của next_state (một bước)
            target_dir = next_state.direction
            if target_dir != agent.direction:
                _rotate_once_towards(agent, target_dir)
            else:
                # Có thể path đang mô phỏng hành động 'grab' (cost 0). Thực hiện idempotent.
                agent.grab_gold()
            # xong một bước -> quay lại vòng lặp để cảm nhận & lập kế hoạch tiếp
            continue

        # 5.b) Nếu bước tiếp theo là DI CHUYỂN sang ô kề
        cur_i, cur_j = agent.position
        nxt_i, nxt_j = next_state.position
        di, dj = (nxt_i - cur_i, nxt_j - cur_j)

        desired_dir = _dir_from_delta(di, dj)
        if desired_dir is None:
            # Không phải ô kề (không hợp lệ) -> bỏ cuộc để tránh treo
            print("[ERROR] Next step is not an adjacent move; aborting to avoid lock.")
            break

        # Xoay (tối đa 4 lần) cho đến khi đúng hướng rồi đi tới
        spins = 0
        while agent.direction != desired_dir and spins < 4:
            _rotate_once_towards(agent, desired_dir)
            spins += 1

        if agent.direction == desired_dir:
            agent.move_forward()
        else:
            print("[ERROR] Could not align direction to move; aborting to avoid lock.")
            break

    return {
        "final_position": agent.position,
        "score": agent.score,
        "gold": agent.gold_obtain,
        "alive": agent.alive,
    }
