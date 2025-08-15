from .agent import Agent
import random

def random_agent_action(agent: Agent, gam_map: list[list[int]]):
    """
    Randomly selects an action for the agent.
    """
    actions = ["move", "shoot", "grab", "climb"]
    action = random.choice(actions)
    if not agent.alive:
        print("Agent is no longer alive.")
        return None

    if action == "move":
        choice_direction = random.choice(["left", "right", "forward"])
        if choice_direction == "left":
            agent.turn_left()
        elif choice_direction == "right":
            agent.turn_right()
        else:
            print("Agent cannot move forward.")
    elif action == "shoot":
        if agent.shoot():
            print("Agent shot an arrow.")
        else:
            print("Agent missed the shot.")
    elif action == "grab":
        if agent.grab_gold():
            print("Agent grabbed gold.")
        else:
            print("No gold to grab.")
    elif action == "climb":
        if agent.escape():
            print("Agent successfully escaped the cave.")
        else:
            print("Agent cannot climb out of the cave.")

    return action

def is_valid_move(gam_map, position):
    x, y = position
    return (0 <= x < len(gam_map) and 
            0 <= y < len(gam_map[0]) and 
            not gam_map[x][y])  # Ensure the cell is not a wall or obstacle

def random_agent(gam_map, wumpus_position, pit_positions, states):
    """
    Main function to run the random agent.
    """
    agent_instance = Agent(gam_map, N = len(gam_map))
    while agent_instance.alive:
        if not agent_instance.alive:
            print("Agent is no longer alive.")
            break
        action = random_agent_action(agent_instance, gam_map)
        states.add(agent_instance, action)
        if action == "climb" and agent_instance.position == (0, 0) and not agent_instance.gold_obtain:
            print("Agent has escaped without gold.")
            break
        elif action == "climb" and agent_instance.position == (0, 0) and agent_instance.gold_obtain:
            print("Agent has escaped with gold.")
            break
        print(f"Agent's current position: {agent_instance.position}, Score: {agent_instance.score}")
    return agent_instance.score, states