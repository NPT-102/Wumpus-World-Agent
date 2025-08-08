import tkinter as tk
from PIL import Image, ImageTk


class Display(tk.Frame):
    def __init__(self, parent, with_random, moving_wumpus):
        super().__init__(parent)
        self.with_random = with_random
        self.moving_wumpus = moving_wumpus
        if self.with_random:
            pass
            # color all cells with gray
        else:
            pass
            # color safe cells with green, dangerous cells with red
    
    def next(self):
        if self.with_random:
            pass
        else:
            if self.moving_wumpus:
                pass
            else:
                pass
                # visited cells will still be marked as safe