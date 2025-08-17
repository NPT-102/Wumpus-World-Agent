from env_simulator.generateMap import WumpusWorldGenerator, print_map
from env_simulator.environment import WumpusEnvironment
from env_simulator.kb import KnowledgeBase
from agent.agent import Agent
from agent.kb_safe_agent import KnowledgeBaseSafeAgent

def analyze_kb_safe_exploration():
    """Phân tích xem KB-Safe Agent có đi hết tất cả các ô safe mà KB phát hiện được không"""
    
    print("=== PHÂN TÍCH KB-SAFE AGENT - ĐI HẾT CÁC Ô SAFE ===\n")
    
    total_tests = 5
    successful_complete_explorations = 0
    
    for test_num in range(1, total_tests + 1):
        print(f"=== Test {test_num} ===")
        
        # Generate map
        generator = WumpusWorldGenerator(N=6)  # Smaller map for detailed analysis
        game_map, wumpus_position, pit_positions = generator.generate_map()
        
        # Convert to list format
        if isinstance(wumpus_position, tuple):
            wumpus_position = [wumpus_position]
        
        print(f"Map {test_num}:")
        print_map(game_map)
        print(f"Wumpus: {wumpus_position}, Pits: {pit_positions}")
        
        # Create environment and agent
        environment = WumpusEnvironment(game_map, wumpus_position, pit_positions)
        base_agent = Agent(environment=environment, N=6)
        kb_agent = KnowledgeBaseSafeAgent(base_agent, max_risk_threshold=1.0)
        
        # Run agent with reasonable step limit
        step_count = 0
        max_steps = 100
        
        while step_count < max_steps:
            success, message = kb_agent.step()
            step_count += 1
            
            if not success:
                break
            
            if not base_agent.alive:
                break
        
        # Analyze results
        final_result = kb_agent.get_final_result()
        
        print(f"\n--- Kết quả Test {test_num} ---")
        print(f"Steps: {step_count}, Score: {final_result['score']}, Alive: {final_result['alive']}")
        print(f"Vị trí cuối: {final_result['final_position']}")
        print(f"Số ô đã thăm: {len(kb_agent.visited_positions)}")
        print(f"Các ô đã thăm: {sorted(list(kb_agent.visited_positions))}")
        
        # Get all KB-safe positions that were discovered
        all_kb_safe = kb_agent._get_all_kb_safe_positions()
        visited = kb_agent.visited_positions
        unvisited_kb_safe = [pos for pos in all_kb_safe if pos not in visited]
        
        print(f"Tổng số ô KB-safe: {len(all_kb_safe)}")
        print(f"Ô KB-safe đã thăm: {len([pos for pos in all_kb_safe if pos in visited])}")
        print(f"Ô KB-safe chưa thăm: {len(unvisited_kb_safe)}")
        
        if unvisited_kb_safe:
            print(f"Các ô KB-safe chưa thăm: {unvisited_kb_safe}")
            # Check if these unvisited positions are reachable
            for pos in unvisited_kb_safe:
                target, path = kb_agent._find_path_to_kb_safe_positions()
                if target == pos and path:
                    print(f"  {pos} CÓ THỂ ĐẾN ĐƯỢC qua path: {path}")
                else:
                    print(f"  {pos} KHÔNG THỂ ĐẾN ĐƯỢC")
        else:
            print("✅ ĐÃ THĂM HẾT TẤT CẢ Ô KB-SAFE!")
            successful_complete_explorations += 1
        
        # Calculate exploration efficiency
        total_cells = 6 * 6
        exploration_percentage = (len(visited) / total_cells) * 100
        kb_safe_completion = (len([pos for pos in all_kb_safe if pos in visited]) / len(all_kb_safe)) * 100 if all_kb_safe else 0
        
        print(f"Tỷ lệ khám phá tổng: {exploration_percentage:.1f}%")
        print(f"Tỷ lệ hoàn thành ô KB-safe: {kb_safe_completion:.1f}%")
        print("-" * 60)
    
    print(f"\n=== KẾT QUẢ TỔNG KẾT ===")
    print(f"Số test hoàn thành 100% ô KB-safe: {successful_complete_explorations}/{total_tests}")
    print(f"Tỷ lệ thành công: {(successful_complete_explorations/total_tests)*100:.1f}%")
    
    if successful_complete_explorations == total_tests:
        print("🎉 KB-SAFE AGENT ĐÃ ĐI HẾT TẤT CẢ Ô SAFE TRONG TẤT CẢ TEST!")
    elif successful_complete_explorations > total_tests * 0.8:
        print("✅ KB-Safe Agent hoạt động tốt, đi hết hầu hết các ô safe")
    else:
        print("⚠️ KB-Safe Agent cần cải thiện để đi hết tất cả ô safe")

if __name__ == "__main__":
    analyze_kb_safe_exploration()
