import tkinter as tk
from tkinter import ttk
import threading
import time
from PIL import Image, ImageTk
from env_simulator.generateMap import WumpusWorldGenerator, print_map
from agent.agent import Agent
from stepwise_agent import StepByStepHybridAgent

class WumpusWorldUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Wumpus World Agent Visualization")
        self.root.geometry("1200x800")
        
        # Game state
        self.game_map = None
        self.wumpus_positions = None
        self.pit_positions = None
        self.agent = None
        self.step_agent = None
        self.current_step = 0
        self.is_playing = False
        self.is_stopped = True
        self.game_thread = None
        self.game_finished = False
        
        # UI settings
        self.grid_size = 4
        self.cell_size = 80
        
        # Create UI components
        self.create_widgets()
        self.load_images()
        self.setup_game()
        
    def create_widgets(self):
        # Main frame
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Control panel
        control_frame = ttk.Frame(main_frame)
        control_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Game controls
        self.play_button = ttk.Button(control_frame, text="▶ Play", command=self.play_game)
        self.play_button.pack(side=tk.LEFT, padx=(0, 5))
        
        self.pause_button = ttk.Button(control_frame, text="⏸ Pause", command=self.pause_game)
        self.pause_button.pack(side=tk.LEFT, padx=(0, 5))
        
        self.stop_button = ttk.Button(control_frame, text="⏹ Stop", command=self.stop_game)
        self.stop_button.pack(side=tk.LEFT, padx=(0, 5))
        
        self.reset_button = ttk.Button(control_frame, text="🔄 Reset", command=self.reset_game)
        self.reset_button.pack(side=tk.LEFT, padx=(0, 10))
        
        # Step controls
        self.step_button = ttk.Button(control_frame, text="➡ Step", command=self.step_forward)
        self.step_button.pack(side=tk.LEFT, padx=(0, 5))
        
        # Speed control
        ttk.Label(control_frame, text="Speed:").pack(side=tk.LEFT, padx=(10, 5))
        self.speed_var = tk.StringVar(value="1.0")
        self.speed_scale = ttk.Scale(control_frame, from_=0.1, to=3.0, variable=self.speed_var, orient=tk.HORIZONTAL, length=100)
        self.speed_scale.pack(side=tk.LEFT, padx=(0, 10))
        
        # Status
        self.status_var = tk.StringVar(value="Ready to start")
        self.status_label = ttk.Label(control_frame, textvariable=self.status_var)
        self.status_label.pack(side=tk.RIGHT)
        
        # Main content area
        content_frame = ttk.Frame(main_frame)
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Game canvas
        self.canvas = tk.Canvas(content_frame, 
                               width=(self.grid_size + 1) * self.cell_size, 
                               height=(self.grid_size + 1) * self.cell_size,
                               bg='white', relief=tk.SUNKEN, borderwidth=2)
        self.canvas.pack(side=tk.LEFT, padx=(0, 10))
        
        # Info panel
        info_frame = ttk.Frame(content_frame)
        info_frame.pack(fill=tk.BOTH, expand=True)
        
        # Agent stats
        stats_frame = ttk.LabelFrame(info_frame, text="Agent Status", padding=10)
        stats_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.stats_text = tk.Text(stats_frame, height=8, width=50)
        self.stats_text.pack(fill=tk.BOTH, expand=True)
        
        # Game log
        log_frame = ttk.LabelFrame(info_frame, text="Game Log", padding=10)
        log_frame.pack(fill=tk.BOTH, expand=True)
        
        self.log_text = tk.Text(log_frame, width=50)
        log_scrollbar = ttk.Scrollbar(log_frame, orient=tk.VERTICAL, command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=log_scrollbar.set)
        
        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        log_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
    def load_images(self):
        """Load game images"""
        try:
            self.images = {
                "S": ImageTk.PhotoImage(Image.open("visualization/assets/stench.png").resize((40, 40))),
                "B": ImageTk.PhotoImage(Image.open("visualization/assets/breeze.png").resize((40, 40))),
                "W": ImageTk.PhotoImage(Image.open("visualization/assets/wumpus.png").resize((50, 50))),
                "P": ImageTk.PhotoImage(Image.open("visualization/assets/pit.png").resize((50, 50))),
                "G": ImageTk.PhotoImage(Image.open("visualization/assets/treasure.png").resize((40, 40))),
            }
        except Exception as e:
            print(f"Could not load images: {e}")
            self.images = {}
    
    def setup_game(self):
        """Initialize a new game"""
        generator = WumpusWorldGenerator(N=4)
        self.game_map, self.wumpus_positions, self.pit_positions = generator.generate_map()
        
        # Convert single wumpus to list if needed
        if isinstance(self.wumpus_positions, tuple):
            self.wumpus_positions = [self.wumpus_positions]
        
        self.agent = Agent(map=self.game_map, N=4)
        self.step_agent = StepByStepHybridAgent(self.agent, self.game_map, self.wumpus_positions, self.pit_positions)
        self.current_step = 0
        self.game_finished = False
        
        self.add_log("Game initialized")
        self.add_log(f"Wumpus positions: {self.wumpus_positions}")
        self.add_log(f"Pit positions: {self.pit_positions}")
        
        self.draw_game_state()
        self.update_stats()
        
    def draw_game_state(self):
        """Draw the current game state"""
        self.canvas.delete("all")
        
        # Get current state from step agent
        if self.step_agent:
            state = self.step_agent.get_current_state()
            current_map = state['map']
            visited = set(state['visited'])
        else:
            current_map = self.game_map
            visited = set()
        
        # Draw grid
        for row in range(self.grid_size):
            for col in range(self.grid_size):
                x1 = col * self.cell_size + self.cell_size
                y1 = row * self.cell_size
                x2 = x1 + self.cell_size
                y2 = y1 + self.cell_size
                
                # Cell background color
                if (row, col) in visited:
                    color = 'lightgreen'
                elif (row, col) == self.agent.position:
                    color = 'lightblue'
                else:
                    color = 'lightgray'
                
                self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline='black', width=2)
                
                # Draw cell contents
                cell_contents = current_map[row][col]
                self.draw_cell_contents(row, col, cell_contents)
        
        # Draw coordinates
        for i in range(self.grid_size):
            self.canvas.create_text(self.cell_size//2, i*self.cell_size+self.cell_size//2, 
                                  text=f'{self.grid_size - i - 1}', font=('Arial', 12, 'bold'))
            self.canvas.create_text((i+1)*self.cell_size+self.cell_size//2, 
                                  self.cell_size*self.grid_size+self.cell_size//2, 
                                  text=f'{i}', font=('Arial', 12, 'bold'))
        
        # Draw agent
        self.draw_agent(self.agent.position[0], self.agent.position[1], self.agent.direction)
        
    def draw_cell_contents(self, row, col, contents):
        """Draw contents of a specific cell"""
        x = col * self.cell_size + self.cell_size + self.cell_size//2
        y = row * self.cell_size + self.cell_size//2
        
        # Draw each item in the cell
        y_offset = -15
        for item in contents:
            if item == 'A':  # Skip agent marker
                continue
            elif item in self.images:
                self.canvas.create_image(x, y + y_offset, image=self.images[item])
                y_offset += 20
            else:
                # Draw text for items without images
                self.canvas.create_text(x, y + y_offset, text=item, font=('Arial', 10, 'bold'))
                y_offset += 15
    
    def draw_agent(self, row, col, direction):
        """Draw the agent at specified position"""
        x = col * self.cell_size + self.cell_size + self.cell_size//2
        y = row * self.cell_size + self.cell_size//2
        
        # Draw agent circle
        self.canvas.create_oval(x-20, y-20, x+20, y+20, fill='blue', outline='darkblue', width=3)
        
        # Draw direction arrow
        if direction == "N":
            self.canvas.create_line(x, y, x, y-15, arrow=tk.LAST, width=3, fill='white', arrowshape=(10, 12, 3))
        elif direction == "S":
            self.canvas.create_line(x, y, x, y+15, arrow=tk.LAST, width=3, fill='white', arrowshape=(10, 12, 3))
        elif direction == "E":
            self.canvas.create_line(x, y, x+15, y, arrow=tk.LAST, width=3, fill='white', arrowshape=(10, 12, 3))
        elif direction == "W":
            self.canvas.create_line(x, y, x-15, y, arrow=tk.LAST, width=3, fill='white', arrowshape=(10, 12, 3))
    
    def play_game(self):
        """Start or resume the game"""
        if not self.is_playing and not self.game_finished:
            self.is_playing = True
            self.is_stopped = False
            self.play_button.config(state='disabled')
            self.pause_button.config(state='normal')
            self.stop_button.config(state='normal')
            
            if self.game_thread is None or not self.game_thread.is_alive():
                self.game_thread = threading.Thread(target=self.run_game_loop, daemon=True)
                self.game_thread.start()
    
    def pause_game(self):
        """Pause the game"""
        self.is_playing = False
        self.play_button.config(state='normal')
        self.pause_button.config(state='disabled')
        self.status_var.set("Paused")
    
    def stop_game(self):
        """Stop the game"""
        self.is_playing = False
        self.is_stopped = True
        self.play_button.config(state='normal')
        self.pause_button.config(state='disabled')
        self.stop_button.config(state='disabled')
        self.status_var.set("Stopped")
    
    def reset_game(self):
        """Reset the game to initial state"""
        self.stop_game()
        time.sleep(0.1)  # Give thread time to stop
        self.setup_game()
        self.status_var.set("Reset complete")
        self.play_button.config(state='normal')
        self.stop_button.config(state='normal')
    
    def step_forward(self):
        """Execute one step of the game manually"""
        if not self.game_finished and not self.is_playing:
            self.execute_step()
    
    def run_game_loop(self):
        """Run the game logic in a separate thread"""
        try:
            while not self.is_stopped and not self.game_finished:
                if self.is_playing:
                    self.execute_step()
                    
                    # Control game speed
                    speed = float(self.speed_var.get())
                    delay = max(0.1, 1.0 / speed)
                    time.sleep(delay)
                else:
                    time.sleep(0.1)  # Wait while paused
                    
        except Exception as e:
            error_msg = str(e)
            self.root.after(0, lambda: self.status_var.set(f"Error: {error_msg}"))
            self.root.after(0, lambda: self.add_log(f"Error: {error_msg}"))
        finally:
            self.root.after(0, self.game_ended)
    
    def execute_step(self):
        """Execute one step of the game"""
        if self.step_agent and not self.game_finished:
            can_continue, message = self.step_agent.step()
            
            # Update display on main thread
            self.root.after(0, self.update_display, message)
            
            if not can_continue:
                self.game_finished = True
                final_result = self.step_agent.get_final_result()
                self.root.after(0, self.show_final_result, final_result)
    
    def update_display(self, message):
        """Update the display with current game state"""
        self.draw_game_state()
        self.update_stats()
        self.add_log(message)
        
        if self.step_agent:
            state = self.step_agent.get_current_state()
            self.status_var.set(f"Step {self.step_agent.action_count} - {state['state']} - Score: {state['score']}")
    
    def update_stats(self):
        """Update the stats panel"""
        if self.step_agent:
            state = self.step_agent.get_current_state()
            
            stats = f"""Position: {state['position']}
Direction: {state['direction']}
Score: {state['score']}
Alive: {state['alive']}
Has Gold: {state['gold']}
Arrow Status: {'Not shot' if state['arrow'] == 0 else 'Hit' if state['arrow'] == 1 else 'Missed'}
Actions: {state['action_count']}
Current State: {state['state']}
Visited Cells: {len(state['visited'])}
Living Wumpuses: {sum(state['wumpus_alive'])}"""
            
            self.stats_text.delete(1.0, tk.END)
            self.stats_text.insert(1.0, stats)
    
    def show_final_result(self, result):
        """Show final game result"""
        self.add_log("=" * 40)
        self.add_log("GAME FINISHED!")
        self.add_log(f"Final Position: {result['final_position']}")
        self.add_log(f"Final Score: {result['score']}")
        self.add_log(f"Gold Obtained: {result['gold']}")
        self.add_log(f"Agent Alive: {result['alive']}")
        self.add_log(f"Total Actions: {result['actions']}")
        
        if result['gold'] and result['alive'] and result['final_position'] == (0, 0):
            self.add_log("🎉 SUCCESS: Agent returned home with gold!")
            self.status_var.set(f"SUCCESS! Score: {result['score']}")
        elif result['gold'] and result['alive']:
            self.add_log("⚠️ PARTIAL SUCCESS: Has gold but not home")
            self.status_var.set(f"Partial Success - Score: {result['score']}")
        else:
            self.add_log("❌ FAILED: Agent did not succeed")
            self.status_var.set(f"Failed - Score: {result['score']}")
    
    def game_ended(self):
        """Handle game end"""
        self.is_playing = False
        self.play_button.config(state='disabled' if self.game_finished else 'normal')
        self.pause_button.config(state='disabled')
    
    def add_log(self, message):
        """Add message to log panel"""
        self.log_text.insert(tk.END, f"{message}\n")
        self.log_text.see(tk.END)
    
    def run(self):
        """Start the UI"""
        self.root.mainloop()

if __name__ == "__main__":
    app = WumpusWorldUI()
    app.run()
