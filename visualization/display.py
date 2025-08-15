import tkinter as tk
from PIL import Image, ImageTk

class Display(tk.Frame):
    def __init__(self, parent, grid_size, cell_size, states):
        super().__init__(parent)
        self.grid = grid_size
        self.cell = cell_size
        self.canvas = tk.Canvas(parent, width=(self.grid+1)*self.cell, height=(self.grid+1)*self.cell)
        self.canvas.pack()
        self.set_initial_background()
        self.at_step = 0
        self.states = states
        self.img = {
            "B": ImageTk.PhotoImage(Image.open("assets/breeze.png")),
            "S": ImageTk.PhotoImage(Image.open("assets/stench.png")),
            "W": ImageTk.PhotoImage(Image.open("assets/wumpus.png")),
            "SB": ImageTk.PhotoImage(Image.open("assets/stenchbreeze.png")),
            "P": ImageTk.PhotoImage(Image.open("assets/pit.png")),
            "North": ImageTk.PhotoImage(Image.open("assets/front.png")),
            "West": ImageTk.PhotoImage(Image.open("assets/left.png")),
            "East": ImageTk.PhotoImage(Image.open("assets/right.png")),
            "South": ImageTk.PhotoImage(Image.open("assets/back.png")),
            "T": ImageTk.PhotoImage(Image.open("assets/treasure.png"))
        }
    
    def coordinate_converter(self, i, j):
        return j * self.cell + self.cell, i * self.cell
    
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
        self.at_step += 1
        map, action, dir = self.states[self.at_step] 
        for row in range(self.grid):
            for col in range(self.grid):
                content = map[row][col]
                x, y = self.coordinate_converter(row, col)
                if '+' in content:
                    self.canvas.create_rectangle(x, y, x+self.cell, y+self.cell, fill='green', outline='white')
                elif '-' in content:
                    self.canvas.create_rectangle(x, y, x+self.cell, y+self.cell, fill='red', outline='white')
                else:
                    self.canvas.create_rectangle(x, y, x+self.cell, y+self.cell, fill='gray', outline='white')
                
                if 'SB' in content:
                    self.canvas.create_image(x+self.cell//2, y+self.cell//2, self.img['SB'])
                elif 'S' in content:
                    self.canvas.create_image(x+self.cell//2, y+self.cell//2, self.img['S'])
                elif 'B' in content:
                    self.canvas.create_image(x+self.cell//2, y+self.cell//2, self.img['B'])

                if 'P' in content:
                    self.canvas.create_image(x+self.cell//2, y+self.cell//2, self.img['P'])
                if 'W' in content:
                    self.canvas.create_image(x+self.cell//2, y+self.cell//2, self.img['W'])
                if 'T' in content:
                    self.canvas.create_image(x+self.cell//2, y+self.cell//2, self.img['T'])
                if 'A' in content:
                    if dir == 'E':
                        self.canvas.create_image(x+self.cell//2, y+self.cell//2, self.img['East'])
                    elif dir == 'W':
                        self.canvas.create_image(x+self.cell//2, y+self.cell//2, self.img['West'])
                    elif dir == 'N':
                        self.canvas.create_image(x+self.cell//2, y+self.cell//2, self.img['North'])
                    elif dir == 'S':
                        self.canvas.create_image(x+self.cell//2, y+self.cell//2, self.img['South'])