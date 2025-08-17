import tkinter as tk
from tkinter import ttk
import threading
import time
from PIL import Image, ImageTk
from env_simulator.generateMap import WumpusWorldGenerator, print_map
from env_simulator.environment import WumpusEnvironment
from agent.agent import Agent
from agent.intelligent_agent_wrapper import IntelligentAgentWrapper
from agent.intelligent_agent_dynamic import IntelligentAgentDynamic
from agent.random_agent import RandomAgent
from agent.hybrid_agent import HybridAgent
from agent.hybrid_agent_action_dynamic import HybridAgentDynamic
import re

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
        self.grid_size = 8  # This will be updated from combo box
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
        
        ttk.Label(control_frame, text="Map Size:").pack(side=tk.LEFT, padx=(0, 5))
        self.size_var = tk.StringVar(value="8")
        self.size_combo = ttk.Combobox(control_frame, textvariable=self.size_var, values=["8", "9", "10"], width=5, state="readonly")
        self.size_combo.pack(side=tk.LEFT, padx=(0, 15))
        self.size_combo.bind('<<ComboboxSelected>>', self.on_size_change)
        
        # Agent type selector
        ttk.Label(control_frame, text="Agent Type:").pack(side=tk.LEFT, padx=(0, 5))
        self.agent_var = tk.StringVar(value="Random")
        self.agent_combo = ttk.Combobox(control_frame, textvariable=self.agent_var, 
                                       values=["Random", "Hybrid", "Hybrid Dynamic", "Intelligent", "Intelligent Dynamic"], width=18, state="readonly")
        self.agent_combo.pack(side=tk.LEFT, padx=(0, 15))
        self.agent_combo.bind('<<ComboboxSelected>>', self.on_agent_change)
        
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
        
        self.stats_text = tk.Text(stats_frame, height=12, width=50)
        self.stats_text.pack(fill=tk.BOTH, expand=True)
        
        # Knowledge Base Facts panel
        kb_frame = ttk.LabelFrame(info_frame, text="Knowledge Base Facts", padding=10)
        kb_frame.pack(fill=tk.BOTH, expand=True, pady=(10, 0))
        
        # Create tabs for different fact types
        self.kb_notebook = ttk.Notebook(kb_frame)
        self.kb_notebook.pack(fill=tk.BOTH, expand=True)
        
        # Positive facts tab
        positive_frame = ttk.Frame(self.kb_notebook)
        self.kb_notebook.add(positive_frame, text="Positive Facts")
        
        self.positive_facts_text = tk.Text(positive_frame, height=8, width=50)
        positive_scrollbar = ttk.Scrollbar(positive_frame, orient="vertical", command=self.positive_facts_text.yview)
        self.positive_facts_text.configure(yscrollcommand=positive_scrollbar.set)
        self.positive_facts_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        positive_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Negative facts tab
        negative_frame = ttk.Frame(self.kb_notebook)
        self.kb_notebook.add(negative_frame, text="Negative Facts")
        
        self.negative_facts_text = tk.Text(negative_frame, height=8, width=50)
        negative_scrollbar = ttk.Scrollbar(negative_frame, orient="vertical", command=self.negative_facts_text.yview)
        self.negative_facts_text.configure(yscrollcommand=negative_scrollbar.set)
        self.negative_facts_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        negative_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # All facts tab
        all_frame = ttk.Frame(self.kb_notebook)
        self.kb_notebook.add(all_frame, text="All Facts")
        
        self.all_facts_text = tk.Text(all_frame, height=8, width=50)
        all_scrollbar = ttk.Scrollbar(all_frame, orient="vertical", command=self.all_facts_text.yview)
        self.all_facts_text.configure(yscrollcommand=all_scrollbar.set)
        self.all_facts_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        all_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
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
        # Get selected grid size
        self.grid_size = int(self.size_var.get())
        
        # Update canvas size
        self.canvas.config(
            width=(self.grid_size + 1) * self.cell_size, 
            height=(self.grid_size + 1) * self.cell_size
        )
        
        generator = WumpusWorldGenerator(N=self.grid_size)
        self.game_map, self.wumpus_positions, self.pit_positions = generator.generate_map()
        
        # Convert single wumpus to list if needed
        if isinstance(self.wumpus_positions, tuple):
            self.wumpus_positions = [self.wumpus_positions]
        
        # Create environment interface - no direct map access for agents
        self.environment = WumpusEnvironment(self.game_map, self.wumpus_positions, self.pit_positions)
        
        # Create base agent with environment interface
        self.agent = Agent(environment=self.environment, N=self.grid_size)
        
        # Create appropriate agent wrapper based on selection
        agent_type = self.agent_var.get()
        if agent_type == "Random":
            self.step_agent = RandomAgent(self.agent)
        elif agent_type == "Hybrid":
            self.step_agent = HybridAgent(self.agent)
        elif agent_type == "Hybrid Dynamic":
            self.step_agent = HybridAgentDynamic(self.agent)
        elif agent_type == "Intelligent":
            self.step_agent = IntelligentAgentWrapper(self.agent, max_risk_threshold=0.3)
        elif agent_type == "Intelligent Dynamic":
            self.step_agent = IntelligentAgentDynamic(self.agent, max_risk_threshold=0.3)
        else:
            # Default to random agent
            self.step_agent = RandomAgent(self.agent)
        
        self.current_step = 0
        self.game_finished = False
        
        self.draw_game_state()
        self.update_stats()
        
    def draw_game_state(self):
        """Draw the current game state"""
        self.canvas.delete("all")
        
        # Get current state from step agent
        if self.step_agent:
            state = self.step_agent.get_current_state()
            current_map = self.game_map  # Use original map for display
            visited = set(state.get('visited', []))
        else:
            current_map = self.game_map
            visited = set()
        
        # Draw grid
        for row in range(self.grid_size):
            for col in range(self.grid_size):
                # Flip the row index to match (0,0) at bottom-left
                flipped_row = self.grid_size - row - 1
                x1 = col * self.cell_size + self.cell_size
                y1 = flipped_row * self.cell_size
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

                # Draw cell contents - ONLY show what agent knows (anti-cheat)
                cell_contents = current_map[row][col]
                visible_contents = []
                
                # Only show contents if agent has been to this position OR it's current position
                if (row, col) in visited or (row, col) == self.agent.position:
                    # Show gold only if agent is currently at the position (can see glitter)
                    if 'G' in cell_contents and self.agent.position == (row, col):
                        visible_contents.append('G')
                    
                    # Show breeze/stench only if agent has been there (experienced it)
                    if (row, col) in visited:
                        if 'B' in cell_contents:
                            visible_contents.append('B')
                        if 'S' in cell_contents:
                            visible_contents.append('S')
                
                # Draw visible contents only
                if visible_contents:
                    self.draw_cell_contents(flipped_row, col, visible_contents)

        # Draw coordinates
        for i in range(self.grid_size):
            # Y axis (row labels)
            self.canvas.create_text(
            self.cell_size // 2,
            (self.grid_size - i - 1) * self.cell_size + self.cell_size // 2,
            text=f'{i}',
            font=('Arial', 12, 'bold')
            )
            # X axis (col labels)
            self.canvas.create_text(
            (i + 1) * self.cell_size + self.cell_size // 2,
            self.cell_size * self.grid_size + self.cell_size // 2,
            text=f'{i}',
            font=('Arial', 12, 'bold')
            )
        
        # Draw agent
        if self.step_agent:
            state = self.step_agent.get_current_state()
            agent_row, agent_col = state['position']
            agent_dir = state['direction']
        else:
            agent_row, agent_col = self.agent.position
            agent_dir = self.agent.direction

        # Draw knowledge-based facts only for visited positions (no cheating by showing unknown info)
        if hasattr(self.agent, 'kb') and hasattr(self.agent.kb, 'current_facts'):
            facts = self.agent.kb.current_facts()
            if self.step_agent:
                state = self.step_agent.get_current_state()
                visited = set(state.get('visited', []))
            else:
                visited = set()
            
            # Separate positive and negative facts
            positive_facts = []
            negative_facts = []
            
            for fact in facts:
                if fact.startswith('~'):
                    negative_facts.append(fact)
                else:
                    positive_facts.append(fact)
            
            # Draw positive facts on the map with better visualization
            for fact in positive_facts:
                fact_pos = self.fact_position(fact)
                if fact_pos:
                    fact_row, fact_col = fact_pos
                    flipped_row = self.grid_size - fact_row - 1
                    symbol = self.get_symbol(fact)
                    
                    # Draw different types of positive facts
                    if symbol == 'S':
                        if (fact_row, fact_col) in visited:
                            self.draw_positive_fact(flipped_row, fact_col, 'S', 'red')
                    elif symbol == 'B': 
                        if (fact_row, fact_col) in visited:
                            self.draw_positive_fact(flipped_row, fact_col, 'B', 'cyan')
                    elif symbol == 'W':  
                        self.draw_positive_fact(flipped_row, fact_col, 'W', 'darkred')
                    elif symbol == 'P':  
                        self.draw_positive_fact(flipped_row, fact_col, 'P', 'brown')
                    elif symbol == 'G':  
                        if (fact_row, fact_col) in visited:
                            self.draw_positive_fact(flipped_row, fact_col, 'G', 'gold')
                            
            # Update KB facts display
            self.update_kb_facts_display(positive_facts, negative_facts, facts)

        # Flip the row index to match the canvas coordinates
        flipped_row = self.grid_size - agent_row - 1
        self.draw_agent(flipped_row, agent_col, agent_dir)
        
    def fact_position(self, fact):
        if not fact.startswith('~'):
            match = re.match(r'.*\((\d+),\s*(\d+)\)', fact)
            if match:
                return int(match.group(1)), int(match.group(2))
        return None
        
    def get_symbol(self, fact):
        if not fact.startswith('~'):
            match = re.match(r'(P|W|B|S|G|Safe)\((\d+),\s*(\d+)\)', fact)
            if match:
                return match.group(1)
        return None
    
    def draw_positive_fact(self, row, col, symbol, color):
        """Draw a positive fact with images when available, fallback to shapes"""
        x = col * self.cell_size + self.cell_size + self.cell_size//2
        y = row * self.cell_size + self.cell_size//2
        
        if symbol == 'SAFE':
            # Draw safe indicator as a small green circle with checkmark
            self.canvas.create_oval(x+15, y+20, x+31, y+36, fill=color, outline='darkgreen', width=2)
            self.canvas.create_text(x+23, y+28, text="✓", font=('Arial', 8, 'bold'), fill='white')
        elif symbol == 'W':
                self.canvas.create_image(x, y, image=self.images['W'])
        elif symbol == 'P':
                self.canvas.create_image(x, y, image=self.images['P'])
        elif symbol == 'S':
                self.canvas.create_image(x-17, y+2, image=self.images['S'])
        elif symbol == 'B':
                self.canvas.create_image(x+17, y+2, image=self.images['B'])
        elif symbol == 'G':
                self.canvas.create_image(x, y+23, image=self.images['G'])
    
    def update_kb_facts_display(self, positive_facts, negative_facts, all_facts):
        """Update the knowledge base facts display panels"""
        # Update positive facts
        self.positive_facts_text.delete(1.0, tk.END)
        positive_facts_sorted = sorted(positive_facts)
        
        # Add summary header
        stench_count = len([f for f in positive_facts if f.startswith('S(')])
        breeze_count = len([f for f in positive_facts if f.startswith('B(')])
        wumpus_count = len([f for f in positive_facts if f.startswith('W(')])
        pit_count = len([f for f in positive_facts if f.startswith('P(')])
        safe_count = len([f for f in positive_facts if f.startswith('Safe(')])
        gold_count = len([f for f in positive_facts if f.startswith('G(')])
        
        summary = f"Total positive facts: {len(positive_facts)}\n"
        summary += f"Stenches: {stench_count}, Breezes: {breeze_count}\n"
        summary += f"Known Wumpus: {wumpus_count}, Known Pits: {pit_count}\n"
        summary += f"Safe cells: {safe_count}, Gold: {gold_count}\n"
        summary += "-" * 40 + "\n"
        
        self.positive_facts_text.insert(tk.END, summary, "summary")
        
        for i, fact in enumerate(positive_facts_sorted, 1):
            fact_type = ""
            if fact.startswith('S('):
                fact_type = "stench"
            elif fact.startswith('B('):
                fact_type = "breeze"
            elif fact.startswith('W('):
                fact_type = "wumpus"
            elif fact.startswith('P('):
                fact_type = "pit"
            elif fact.startswith('Safe('):
                fact_type = "safe"
            elif fact.startswith('G('):
                fact_type = "gold"
                
            self.positive_facts_text.insert(tk.END, f"{i:2d}. {fact}\n", fact_type)
        
        # Configure text colors for positive facts
        self.positive_facts_text.tag_config("summary", foreground="blue", font=('Arial', 9, 'bold'))
        self.positive_facts_text.tag_config("stench", foreground="red")
        self.positive_facts_text.tag_config("breeze", foreground="cyan")
        self.positive_facts_text.tag_config("wumpus", foreground="darkred", font=('Arial', 9, 'bold'))
        self.positive_facts_text.tag_config("pit", foreground="brown", font=('Arial', 9, 'bold'))
        self.positive_facts_text.tag_config("safe", foreground="green")
        self.positive_facts_text.tag_config("gold", foreground="orange", font=('Arial', 9, 'bold'))
        
        # Update negative facts
        self.negative_facts_text.delete(1.0, tk.END)
        negative_facts_sorted = sorted(negative_facts)
        
        # Add summary header for negative facts
        neg_summary = f"Total negative facts: {len(negative_facts)}\n"
        neg_summary += "-" * 40 + "\n"
        self.negative_facts_text.insert(tk.END, neg_summary, "summary")
        
        for i, fact in enumerate(negative_facts_sorted, 1):
            self.negative_facts_text.insert(tk.END, f"{i:2d}. {fact}\n", "negative")
        
        self.negative_facts_text.tag_config("summary", foreground="blue", font=('Arial', 9, 'bold'))
        self.negative_facts_text.tag_config("negative", foreground="darkred")
        
        # Update all facts
        self.all_facts_text.delete(1.0, tk.END)
        all_facts_sorted = sorted(all_facts)
        
        # Add summary for all facts
        all_summary = f"Total facts: {len(all_facts)} (Positive: {len(positive_facts)}, Negative: {len(negative_facts)})\n"
        all_summary += "-" * 50 + "\n"
        self.all_facts_text.insert(tk.END, all_summary, "summary")
        
        for i, fact in enumerate(all_facts_sorted, 1):
            if fact.startswith('~'):
                color_tag = "negative"
            else:
                color_tag = "positive"
            
            self.all_facts_text.insert(tk.END, f"{i:2d}. {fact}\n", color_tag)
        
        # Configure text colors
        self.all_facts_text.tag_config("summary", foreground="blue", font=('Arial', 9, 'bold'))
        self.all_facts_text.tag_config("positive", foreground="darkgreen")
        self.all_facts_text.tag_config("negative", foreground="darkred")

    def draw_cell_contents(self, row, col, contents):
        """Draw contents of a specific cell"""
        x = col * self.cell_size + self.cell_size + self.cell_size//2
        y = row * self.cell_size + self.cell_size//2
        
        if not contents:
            return
        
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
        
        # Adjust direction for flipped y-axis
        draw_direction = direction
        if direction == "N":
            draw_direction = "S"
        elif direction == "S":
            draw_direction = "N"
        
        # Draw direction arrow
        if draw_direction == "N":
            self.canvas.create_line(x, y, x, y-15, arrow=tk.LAST, width=3, fill='white', arrowshape=(10, 12, 3))
        elif draw_direction == "S":
            self.canvas.create_line(x, y, x, y+15, arrow=tk.LAST, width=3, fill='white', arrowshape=(10, 12, 3))
        elif draw_direction == "E":
            self.canvas.create_line(x, y, x+15, y, arrow=tk.LAST, width=3, fill='white', arrowshape=(10, 12, 3))
        elif draw_direction == "W":
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
        
        if self.step_agent:
            state = self.step_agent.get_current_state()
            action_count = getattr(self.step_agent, 'action_count', state.get('step', 0))
            self.status_var.set(f"Step {action_count} - {state['state']} - Score: {state['score']}")
    
    def update_stats(self):
        """Update the stats panel"""
        if self.step_agent:
            state = self.step_agent.get_current_state()
            row, col = state['position']

            # Get percepts at the current cell through environment interface
            percepts = []
            if hasattr(self.agent, 'environment'):
                env_percepts = self.agent.environment.get_percept((row, col))
                for percept in env_percepts:
                    if percept == "Stench":
                        percepts.append("Stench")
                    elif percept == "Breeze":
                        percepts.append("Breeze")
                    elif percept == "Glitter":
                        percepts.append("Glitter")
            if not percepts:
                percepts = ["None"]
            
            # Get risk information
            risk_info = "N/A"
            if hasattr(self.agent, 'risk_calculator'):
                risk = self.agent.risk_calculator.calculate_total_risk(state['position'])
                risk_info = f"{risk:.3f}"

            draw_direction = state['direction']
            if draw_direction == "N":
                draw_direction = "S"
            elif draw_direction == "S":
                draw_direction = "N"

            stats = f"""Agent Type: {self.agent_var.get()}
Position: {state['position']}
Direction: {draw_direction}
Score: {state['score']}
Alive: {state['alive']}
Has Gold: {state['gold']}
Arrow Status: {'Not shot' if state['arrow'] == 0 else 'Hit' if state['arrow'] == 1 else 'Missed'}
Current State: {state.get('state', 'exploring')}
Risk at Position: {risk_info}
Risk Threshold: {state.get('risk_threshold', 'N/A')}
Returning Home: {state.get('returning_home', False)}
Percepts: {', '.join(percepts)}"""
            
            self.stats_text.delete(1.0, tk.END)
            self.stats_text.insert(1.0, stats)
    
    def show_final_result(self, result):
        """Show final game result as a message box"""

        import tkinter.messagebox as msgbox

        if result['gold'] and result['alive'] and result['final_position'] == (0, 0):
            msg = f"SUCCESS! Score: {result['score']}"
        elif result['gold'] and result['alive']:
            msg = f"Partial Success - Score: {result['score']}"
        else:
            msg = f"Failed - Score: {result['score']}"

        self.status_var.set(msg)
        msgbox.showinfo("Game Result", msg)
    
    def game_ended(self):
        """Handle game end"""
        self.is_playing = False
        self.play_button.config(state='disabled' if self.game_finished else 'normal')
        self.pause_button.config(state='disabled')
        
    def on_size_change(self, event):
        """Handle map size change"""
        if not self.is_playing:  # Only allow size change when not playing
            self.reset_game()
        else:
            # Revert to previous size if game is running
            self.size_var.set(str(self.grid_size))
    
    def on_agent_change(self, event):
        """Handle agent type change"""
        if not self.is_playing:  # Only allow agent change when not playing
            self.reset_game()
    
    def run(self):
        """Start the UI"""
        self.root.mainloop()

if __name__ == "__main__":
    app = WumpusWorldUI()
    app.run()
