"""
Quick demonstration script showing the key differences between agent types
"""
print("=== WUMPUS WORLD AGENT TYPES COMPARISON ===\n")

print("1. RANDOM AGENT:")
print("   - Acts randomly: move, turn, shoot, or grab")
print("   - Does NOT use knowledge base or pathfinding")
print("   - Fixed map (Wumpus doesn't move)")
print("   - Likely to die quickly due to random actions")
print("   - Good for baseline comparison\n")

print("2. HYBRID AGENT:")
print("   - Uses knowledge base and Dijkstra pathfinding")
print("   - Intelligently shoots Wumpus when beneficial")
print("   - Fixed map (Wumpus doesn't move)")
print("   - Avoids known dangers, seeks optimal path")
print("   - Best performance on static maps\n")

print("3. DYNAMIC AGENT:")
print("   - Uses knowledge base and Dijkstra pathfinding")  
print("   - Handles moving Wumpus (every 5 actions)")
print("   - Updates knowledge when Wumpus moves")
print("   - More complex reasoning for dynamic threats")
print("   - Realistic simulation with moving threats\n")

print("Key Features Available in UI:")
print("• Custom map sizes (4x4 to 10x10)")
print("• Step-by-step visualization") 
print("• Play/Pause/Stop/Reset controls")
print("• Speed adjustment")
print("• Real-time statistics display")
print("• Agent status and path tracking\n")

print("To run the UI: python wumpus_ui.py")
print("To test all agents: python test_agent_types.py")
