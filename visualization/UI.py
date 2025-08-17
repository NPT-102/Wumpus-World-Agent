import tkinter as tk
from tkinter import ttk
import threading
import time
from PIL import Image, ImageTk
from env_simulator.generateMap import WumpusWorldGenerator
from env_simulator.environment import WumpusEnvironment
from agent.agent import Agent
from agent.kb_safe_agent import KnowledgeBaseSafeAgent
from agent.kb_safe_moving_wumpus_agent import KnowledgeBaseSafeMovingWumpusAgent
from agent.random_agent import RandomAgent
import re
import json
import os

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
        
        self.available_maps = self.load_random_maps()
        
        # Initially hide testcase controls if Random is selected
        self.update_control_visibility()
        
    def load_random_maps(self):
        """Load list of available random maps from all_maps_index.json (60 maps)"""
        try:
            with open('all_maps_index.json', 'r') as f:
                maps_info = json.load(f)
            
            available_maps = {}
            for map_info in maps_info:
                if os.path.exists(map_info['filename']):
                    map_name = f"Map {map_info['id']:02d}: {map_info['size']}x{map_info['size']} ({map_info['wumpuses']}W, {map_info['pits']}P)"
                    available_maps[map_name] = map_info['filename']
            
            if not available_maps:
                print("⚠️ No random maps found, using default")
                available_maps = {"Default 8x8": "default_map.json"}
            
            print(f"📋 Loaded {len(available_maps)} random maps with 20% pit probability")
            return available_maps
            
        except FileNotFoundError:
            print("⚠️ all_maps_index.json not found, please run generate_60_maps.py first")
            return {"Default 8x8": "default_map.json"}
        except Exception as e:
            print(f"❌ Error loading maps index: {e}")
            return {"Default 8x8": "default_map.json"}
    
    def load_map_from_json(self, filename):
        """Load map data from JSON file"""
        try:
            filepath = os.path.join("testcases", "map", filename)
            with open(filepath, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"❌ Error loading map from {filename}: {e}")
            return None
    
    def update_control_visibility(self):
        """Update the visibility of controls based on map type selection"""
        map_type = self.map_type_var.get()
        
        if map_type == "Random":
            # Show random controls, hide testcase controls
            self.random_frame.pack(side=tk.LEFT)
            self.testcase_frame.pack_forget()
        else:  # Testcase
            # Hide random controls, show testcase controls
            self.random_frame.pack_forget()
            self.testcase_frame.pack(side=tk.LEFT)
        
    def create_widgets(self):
        # Main frame
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Control panel
        control_frame = ttk.Frame(main_frame)
        control_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Map type selector
        ttk.Label(control_frame, text="Map Type:").pack(side=tk.LEFT, padx=(0, 5))
        self.map_type_var = tk.StringVar(value="Random")
        self.map_type_combo = ttk.Combobox(control_frame, textvariable=self.map_type_var, 
                                          values=["Random", "Testcase"], width=10, state="readonly")
        self.map_type_combo.pack(side=tk.LEFT, padx=(0, 15))
        self.map_type_combo.bind('<<ComboboxSelected>>', self.on_map_type_change)
        
        # Random map controls frame
        self.random_frame = ttk.Frame(control_frame)
        self.random_frame.pack(side=tk.LEFT)
        
        ttk.Label(self.random_frame, text="Map Size:").pack(side=tk.LEFT, padx=(0, 5))
        self.size_var = tk.StringVar(value="8")
        self.size_combo = ttk.Combobox(self.random_frame, textvariable=self.size_var, values=["8", "9", "10"], width=5, state="readonly")
        self.size_combo.pack(side=tk.LEFT, padx=(0, 15))
        self.size_combo.bind('<<ComboboxSelected>>', self.on_size_change)
        
        # Number of Wumpus input
        ttk.Label(self.random_frame, text="Wumpus Count:").pack(side=tk.LEFT, padx=(0, 5))
        self.wumpus_count_var = tk.StringVar(value="2")
        self.wumpus_count_entry = ttk.Entry(self.random_frame, textvariable=self.wumpus_count_var, width=5)
        self.wumpus_count_entry.pack(side=tk.LEFT, padx=(0, 15))
        
        # Pit probability input
        ttk.Label(self.random_frame, text="Pit Probability:").pack(side=tk.LEFT, padx=(0, 5))
        self.pit_prob_var = tk.StringVar(value="0.2")
        self.pit_prob_entry = ttk.Entry(self.random_frame, textvariable=self.pit_prob_var, width=5)
        self.pit_prob_entry.pack(side=tk.LEFT, padx=(0, 15))
        
        # Testcase controls frame
        self.testcase_frame = ttk.Frame(control_frame)
        self.testcase_frame.pack(side=tk.LEFT)
        
        ttk.Label(self.testcase_frame, text="Test Map:").pack(side=tk.LEFT, padx=(0, 5))
        self.testcase_var = tk.StringVar(value="Map 8x8_07")
        self.testcase_combo = ttk.Combobox(self.testcase_frame, textvariable=self.testcase_var, 
                                          values=["Map 8x8_07", "Map 10x10_01", "Map 12x12_16"], 
                                          width=12, state="readonly")
        self.testcase_combo.pack(side=tk.LEFT, padx=(0, 15))
        self.testcase_combo.bind('<<ComboboxSelected>>', self.on_testcase_change)
        
        # Agent type selector (in main control frame)
        ttk.Label(control_frame, text="Agent Type:").pack(side=tk.LEFT, padx=(0, 5))
        self.agent_var = tk.StringVar(value="Random")
        self.agent_combo = ttk.Combobox(control_frame, textvariable=self.agent_var, 
                                       values=["Random", "Hybrid", "Moving Wumpus"], width=25, state="readonly")
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
        
    def load_images(self):
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
        map_type = self.map_type_var.get()
        
        if map_type == "Testcase":
            # Load testcase map
            testcase_name = self.testcase_var.get()
            filename_map = {
                "Map 8x8_07": "map_8x8_07.json",
                "Map 10x10_01": "map_10x10_01.json", 
                "Map 12x12_16": "map_12x12_16.json"
            }
            
            filename = filename_map.get(testcase_name, "map_8x8_07.json")
            map_data = self.load_map_from_json(filename)
            
            if map_data is None:
                print(f"❌ Failed to load testcase map {filename}, falling back to random generation")
                self.setup_random_game()
                return
            
            # Extract data from JSON
            self.grid_size = map_data['size']
            self.game_map = map_data['map']
            self.wumpus_positions = [tuple(pos) for pos in map_data['wumpus_positions']]
            self.pit_positions = [tuple(pos) for pos in map_data['pit_positions']]
            
            # Update canvas size
            self.canvas.config(
                width=(self.grid_size + 1) * self.cell_size, 
                height=(self.grid_size + 1) * self.cell_size
            )
            
            # Create environment with loaded data
            self.environment = WumpusEnvironment(self.game_map, self.wumpus_positions, self.pit_positions)
            
        else:
            # Random map generation
            self.setup_random_game()
        
        # Create agent (common for both types)
        self.agent = Agent(environment=self.environment, N=self.grid_size)
        
        agent_type = self.agent_var.get()
        if agent_type == "Random":
            self.step_agent = RandomAgent(self.agent)
        elif agent_type == "Hybrid":
            self.step_agent = KnowledgeBaseSafeAgent(self.agent, max_risk_threshold=1.0)
        elif agent_type == "Moving Wumpus":
            self.step_agent = KnowledgeBaseSafeMovingWumpusAgent(self.agent, 'dijkstra')
        else:
            self.step_agent = RandomAgent(self.agent)
        
        self.current_step = 0
        self.game_finished = False
        
        self.draw_game_state()
        self.update_stats()
    
    def setup_random_game(self):
        """Setup a randomly generated game"""
        self.grid_size = int(self.size_var.get())
        
        try:
            wumpus_count = int(self.wumpus_count_var.get())
            wumpus_count = max(1, min(wumpus_count, self.grid_size // 2))
        except ValueError:
            wumpus_count = 2  
            self.wumpus_count_var.set("2")
        
        try:
            pit_probability = float(self.pit_prob_var.get())
            pit_probability = max(0.0, min(pit_probability, 1.0)) 
        except ValueError:
            pit_probability = 0.2
            self.pit_prob_var.set("0.2")
        
        # Update canvas size
        self.canvas.config(
            width=(self.grid_size + 1) * self.cell_size, 
            height=(self.grid_size + 1) * self.cell_size
        )
        
        generator = WumpusWorldGenerator(N=self.grid_size, wumpus=wumpus_count, pits_probability=pit_probability)
        self.game_map, self.wumpus_positions, self.pit_positions = generator.generate_map()
        
        if isinstance(self.wumpus_positions, tuple):
            self.wumpus_positions = [self.wumpus_positions]
        
        self.environment = WumpusEnvironment(self.game_map, self.wumpus_positions, self.pit_positions)
        
    def draw_game_state(self):
        self.canvas.delete("all")
        
        if self.step_agent:
            state = self.step_agent.get_current_state()
            
            if hasattr(self.step_agent, 'current_wumpus_positions'):
                current_map = self.agent.environment.game_map
            else:
                current_map = self.game_map
                
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

                cell_contents = current_map[row][col]
                visible_contents = []
                
                if (row, col) in visited or (row, col) == self.agent.position:
                    if 'G' in cell_contents and self.agent.position == (row, col) and not self.agent.gold_obtain:
                        visible_contents.append('G')
                    
                    if (row, col) in visited:
                        if 'B' in cell_contents:
                            visible_contents.append('B')
                        # Only show stench if there's actually a living Wumpus causing it
                        if 'S' in cell_contents and self._is_stench_valid(row, col):
                            visible_contents.append('S')
                
                if hasattr(self.step_agent, 'current_wumpus_positions') and (row, col) in visited:
                    if 'W' in cell_contents:
                        wumpus_pos = (row, col)
                        if wumpus_pos in self.step_agent.current_wumpus_positions:
                            wumpus_idx = self.step_agent.current_wumpus_positions.index(wumpus_pos)
                            if not self.step_agent.wumpus_alive_status[wumpus_idx]:
                                visible_contents.append('W_DEAD')

                if visible_contents:
                    self.draw_cell_contents(flipped_row, col, visible_contents)

        for i in range(self.grid_size):
            self.canvas.create_text(
            self.cell_size // 2,
            (self.grid_size - i - 1) * self.cell_size + self.cell_size // 2,
            text=f'{i}',
            font=('Arial', 12, 'bold')
            )
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

        if hasattr(self.agent, 'kb') and hasattr(self.agent.kb, 'current_facts'):
            facts = self.agent.kb.current_facts()
            if self.step_agent:
                state = self.step_agent.get_current_state()
                visited = set(state.get('visited', []))
            else:
                visited = set()
            
            positive_facts = []
            negative_facts = []
            
            for fact in facts:
                if fact.startswith('~'):
                    negative_facts.append(fact)
                else:
                    positive_facts.append(fact)
            
            for fact in positive_facts:
                fact_pos = self.fact_position(fact)
                if fact_pos:
                    fact_row, fact_col = fact_pos
                    flipped_row = self.grid_size - fact_row - 1
                    symbol = self.get_symbol(fact)
                    
                    if symbol == 'S':
                        if (fact_row, fact_col) in visited and self._is_stench_valid(fact_row, fact_col):
                            self.draw_positive_fact(flipped_row, fact_col, 'S')
                    elif symbol == 'B':
                        if (fact_row, fact_col) in visited:
                            self.draw_positive_fact(flipped_row, fact_col, 'B')
                    elif symbol == 'W':  
                        dead_wumpus_fact = f"~W({fact_row},{fact_col})"
                        if dead_wumpus_fact not in facts:
                            self.draw_positive_fact(flipped_row, fact_col, 'W')
                    elif symbol == 'P':
                        self.draw_positive_fact(flipped_row, fact_col, 'P')
                    elif symbol == 'G':  
                        if (fact_row, fact_col) in visited and not self.agent.gold_obtain:
                            self.draw_positive_fact(flipped_row, fact_col, 'G')
                            
            self.update_kb_facts_display(positive_facts)

        flipped_row = self.grid_size - agent_row - 1
        self.draw_agent(flipped_row, agent_col, agent_dir)
        
    def _is_stench_valid(self, row, col):
        """Check if stench at (row, col) is caused by a living Wumpus"""
        # Check adjacent cells for living Wumpuses
        for di, dj in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            adj_row, adj_col = row + di, col + dj
            
            if 0 <= adj_row < self.grid_size and 0 <= adj_col < self.grid_size:
                # Check if there's a Wumpus at adjacent position
                if hasattr(self.step_agent, 'current_wumpus_positions'):
                    # For Moving Wumpus agent, check the tracked positions and alive status
                    for idx, wumpus_pos in enumerate(self.step_agent.current_wumpus_positions):
                        if (wumpus_pos == (adj_row, adj_col) and 
                            self.step_agent.wumpus_alive_status[idx]):
                            return True
                else:
                    # For regular agents, check the map directly
                    if 'W' in self.agent.environment.game_map[adj_row][adj_col]:
                        return True
        
        return False
        
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
    
    def draw_positive_fact(self, row, col, symbol):
        """Draw a positive fact with images when available, fallback to shapes"""
        x = col * self.cell_size + self.cell_size + self.cell_size//2
        y = row * self.cell_size + self.cell_size//2

        if symbol == 'W':
                self.canvas.create_image(x, y, image=self.images['W'])
        elif symbol == 'P':
                self.canvas.create_image(x, y, image=self.images['P'])
        elif symbol == 'S':
                self.canvas.create_image(x-17, y+2, image=self.images['S'])
        elif symbol == 'B':
                self.canvas.create_image(x+17, y+2, image=self.images['B'])
        elif symbol == 'G':
                self.canvas.create_image(x, y+23, image=self.images['G'])
    
    def update_kb_facts_display(self, positive_facts):
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

    def draw_cell_contents(self, row, col, contents):
        """Draw contents of a specific cell"""
        x = col * self.cell_size + self.cell_size + self.cell_size//2
        y = row * self.cell_size + self.cell_size//2
        
        if not contents:
            return
        
        y_offset = -15
        for item in contents:
            if item == 'A': 
                continue
            elif item == 'W_DEAD':  
                if 'W' in self.images:
                    self.canvas.create_image(x, y + y_offset, image=self.images['W'])
                    self.canvas.create_line(x-20, y-20+y_offset, x+20, y+20+y_offset, 
                                          fill='red', width=4)
                    self.canvas.create_line(x-20, y+20+y_offset, x+20, y-20+y_offset, 
                                          fill='red', width=4)
                else:
                    self.canvas.create_text(x, y + y_offset, text="W†", 
                                          font=('Arial', 12, 'bold'), fill='gray')
                y_offset += 30
            elif item in self.images:
                self.canvas.create_image(x, y + y_offset, image=self.images[item])
                y_offset += 20
            else:
                self.canvas.create_text(x, y + y_offset, text=item, font=('Arial', 10, 'bold'))
                y_offset += 15
    
    def draw_agent(self, row, col, direction):
        """Draw the agent at specified position"""
        x = col * self.cell_size + self.cell_size + self.cell_size//2
        y = row * self.cell_size + self.cell_size//2
        
        self.canvas.create_oval(x-20, y-20, x+20, y+20, fill='blue', outline='darkblue', width=3)
        
        draw_direction = direction
        if direction == "N":
            draw_direction = "S"
        elif direction == "S":
            draw_direction = "N"
        
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
    
    def stop_game(self):
        """Stop the game"""
        self.is_playing = False
        self.is_stopped = True
        self.play_button.config(state='normal')
        self.pause_button.config(state='disabled')
        self.stop_button.config(state='disabled')
    
    def reset_game(self):
        """Reset the game to initial state"""
        self.stop_game()
        time.sleep(0.1)
        
        self.game_finished = False
        self.current_step = 0
        
        self.setup_game()
        self.play_button.config(state='normal')
        self.stop_button.config(state='normal')
        self.reset_button.config(state='normal')
    
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
                    
                    speed = float(self.speed_var.get())
                    delay = max(0.1, 1.0 / speed)
                    time.sleep(delay)
                else:
                    time.sleep(0.1)  
                    
        except Exception as e:
            error_msg = str(e)
        finally:
            self.root.after(0, self.game_ended)
    
    def execute_step(self):
        """Execute one step of the game"""
        if self.step_agent and not self.game_finished:
            can_continue, message = self.step_agent.step()
            
            # Update display on main thread
            self.root.after(0, self.draw_game_state)
            self.root.after(0, self.update_stats)
            
            if not can_continue:
                self.game_finished = True
                self.is_playing = False  # Stop the game loop immediately
                final_result = self.step_agent.get_final_result()
                self.root.after(0, self.show_final_result, final_result)
    
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

            # KB-Safe agent always uses Dijkstra pathfinding
            pathfinding_info = ""
            if hasattr(self.step_agent, 'pathfinding_algorithm'):
                pathfinding_info = f"\nPathfinding: {self.step_agent.pathfinding_algorithm.upper()}"

            # Moving Wumpus specific info
            moving_wumpus_info = ""
            if hasattr(self.step_agent, 'current_wumpus_positions'):
                living_count = sum(self.step_agent.wumpus_alive_status)
                total_count = len(self.step_agent.wumpus_alive_status)
                next_move = state.get('next_wumpus_move', 0)
                action_count = state.get('action_count', 0)
                
                moving_wumpus_info = f"""
Wumpus Status: {living_count}/{total_count} alive
Next Wumpus Move: {next_move} actions
Total Actions: {action_count}"""

            stats = f"""Agent Type: {self.agent_var.get()}{pathfinding_info}{moving_wumpus_info}
Position: {state['position']}
Direction: {draw_direction}
Score: {state['score']}
Alive: {state['alive']}
Percepts: {', '.join(percepts)}
Has Gold: {state['gold']}
Arrow Status: {'Not shot' if state['arrow'] == 0 else 'Hit' if state['arrow'] == 1 else 'Missed'}
Current State: {state.get('state', 'exploring')}
Current Strategy: {state.get('current_strategy', 'N/A')}
Risk at Position: {risk_info}
Risk Threshold: {state.get('risk_threshold', 'N/A')}"""
            
            self.stats_text.delete(1.0, tk.END)
            self.stats_text.insert(1.0, stats)
    
    def show_final_result(self, result):
        """Show final game result as a message box"""

        import tkinter.messagebox as msgbox

        if result['gold'] and result['alive']:
            msg = f"SUCCESS! Score: {result['score']}"
        elif result['gold'] and not result['alive']:    
            msg = f"Partial Success - Score: {result['score']}"
        else:
            msg = f"Failed - Score: {result['score']}"

        msgbox.showinfo("Game Result", msg)

    def game_ended(self):
        """Handle game end"""
        self.is_playing = False
        self.is_stopped = True
        self.play_button.config(state='disabled' if self.game_finished else 'normal')
        self.pause_button.config(state='disabled')
        self.stop_button.config(state='disabled')
        self.reset_button.config(state='normal')  # Always allow reset
        
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
    
    def on_map_type_change(self, event):
        """Handle map type change"""
        if not self.is_playing:  # Only allow map type change when not playing
            self.update_control_visibility()
            self.reset_game()
        else:
            # Revert to previous selection if game is running
            pass
    
    def on_testcase_change(self, event):
        """Handle testcase map change"""
        if not self.is_playing:  # Only allow testcase change when not playing
            self.reset_game()
    
    def run(self):
        """Start the UI"""
        self.root.mainloop()