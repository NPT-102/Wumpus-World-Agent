import tkinter as tk
from PIL import Image, ImageTk


class Display(tk.Frame):
    def __init__(self, parent, with_random, moving_wumpus, grid_size, cell_size):
        super().__init__(parent)
        self.with_random = with_random
        self.moving_wumpus = moving_wumpus
        self.grid = grid_size
        self.cell = cell_size
        self.canvas = tk.Canvas(parent, width=(self.grid+1)*self.cell, height=(self.grid+1)*self.cell)
        self.canvas.pack()
        self.set_initial_background()
    
    def coordinate_converter():
        pass
    
    def set_initial_background(self):
        for row in range(self.grid):
            for col in range(self.grid):
                x = row * self.cell + self.cell
                y = col * self.cell
                self.canvas.create_rectangle(x, y, x+self.cell, y+self.cell, fill='gray', outline='white')
        for i in range(self.grid):
            self.canvas.create_text(self.cell//2, i*self.cell+self.cell//2, text=f'{self.grid - i - 1}')
            self.canvas.create_text((i+1)*self.cell+self.cell//2, self.cell*self.grid+self.cell//2, text=f'{i}')

    def next(self):
        if self.with_random:
            pass
        else:
            if self.moving_wumpus:
                pass
            else:
                pass
                # visited cells will still be marked as safe