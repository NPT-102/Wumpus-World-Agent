import tkinter as tk
from tkinter import ttk

from selector import Selector
from display import Display

class UI:
    def __init__(self, N=8, actual_map=None):
        self.window = tk.Tk()
        self.window.title("Wumpus World")
        self.N = N
        self.map = actual_map
        self.random_agent = False
        self.moving_wumpus = False
        self.displays = []
        self.auto_timer = None

        # Get screen height
        self.window.update_idletasks()
        self.window.attributes('-fullscreen', True)
        self.window.state('iconic')
        geometry = self.window.winfo_geometry()
        self.window.state('normal')
        self.window.attributes('-fullscreen', False)
        _, self.screen_height = map(int, geometry.split('+')[0].split('x'))

        # Create selector
        self.selector_frame = tk.Frame(self.window)
        self.selector_frame.pack(side='top', pady=10)
        self.selector = Selector(self.selector_frame, self.start)
        self.selector.pack()
        
        # Create main display frame
        self.main_frame = tk.Frame(self.window)
        self.main_frame.pack(side='top', expand=True, fill='both')
    
    def start(self, size_var, random_agent, moving_wumpus):
        try:
            self.N = int(size_var) if size_var else 8
        except ValueError:
            self.N = 8
        
        self.random_agent = bool(random_agent)
        self.moving_wumpus = bool(moving_wumpus)
        
        # Stop any existing timer
        if self.auto_timer:
            self.window.after_cancel(self.auto_timer)
        
        # Clear previous displays
        for widget in self.main_frame.winfo_children():
            widget.destroy()
        self.displays.clear()
        
        self.create_displays()
        
        self.auto_advance()
    
    def auto_advance(self):
        if self.displays:
            for display in self.displays:
                self.next_step_for_display(display)
            
            self.auto_timer = self.window.after(1000, self.auto_advance)
    
    def create_displays(self):
        if self.random_agent:
            self.create_dual_displays()
        else:
            self.create_single_display()
    
    def create_single_display(self):
        display_frame = tk.Frame(self.main_frame)
        display_frame.pack(side='left', expand=True, fill='both')
        
        title = tk.Label(display_frame, text="Wumpus World Agent")
        title.pack(pady=5)
        
        # Call agent to get states
        # here
        cell_size = self.screen_height // 5 * 3 // (self.N + 1)
        display = Display(display_frame, self.N, cell_size, states=None)  # Replace None with actual states
        self.displays.append(display)
    
    def create_dual_displays(self):
        # Left display frame
        left_frame = tk.Frame(self.main_frame)
        left_frame.pack(side='left', expand=True, fill='both', padx=5)
        
        # Left title
        left_title = tk.Label(left_frame, text="Hybrid Agent")
        left_title.pack(pady=5)
        
        # Left display
        cell_size = self.screen_height // 5 * 3 // (self.N + 1)
        # Call hybrid agent to get states
        # here
        left_display = Display(left_frame, self.N, cell_size, states=None)
        self.displays.append(left_display)
        
        # Separator
        separator = ttk.Separator(self.main_frame, orient='vertical')
        separator.pack(side='left', fill='y', padx=5)
        
        # Right display frame
        right_frame = tk.Frame(self.main_frame)
        right_frame.pack(side='left', expand=True, fill='both', padx=5)
        
        # Right title
        right_title = tk.Label(right_frame, text="Random Agent")
        right_title.pack(pady=5)
        
        # Right display
        # Call random agent to get states
        # here
        right_display = Display(right_frame, self.N, cell_size, states=None)  # Replace None with actual states
        self.displays.append(right_display)
    
    def next_step_for_display(self, display):
        if display and hasattr(display, 'next'):
            try:
                display.next()
            except Exception as e:
                print(f"Error advancing display: {e}")
    
    def run(self):
        self.window.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.window.mainloop()
    
    def on_closing(self):
        if self.auto_timer:
            self.window.after_cancel(self.auto_timer)
        self.window.destroy()