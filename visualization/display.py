import tkinter as tk
from PIL import Image, ImageTk

class Display(tk.Frame):
    def __init__(self, parent, grid_size, cell_size, states):
        super().__init__(parent)
        self.grid = grid_size
        self.cell = cell_size
        self.canvas = tk.Canvas(parent, width=(self.grid+1)*self.cell, height=(self.grid+1)*self.cell)
        self.canvas.pack()
        self.at_step = 0
        self.states = states
        self.visited = []
        self.carry_gold = False
        self.img = {
            "B": ImageTk.PhotoImage(Image.open("visualization/assets/breeze.png").resize((self.cell, self.cell))),
            "S": ImageTk.PhotoImage(Image.open("visualization/assets/stench.png").resize((self.cell, self.cell))),
            "W": ImageTk.PhotoImage(Image.open("visualization/assets/wumpus.png").resize((self.cell, self.cell))),
            "SB": ImageTk.PhotoImage(Image.open("visualization/assets/stenchbreeze.png").resize((self.cell, self.cell))),
            "P": ImageTk.PhotoImage(Image.open("visualization/assets/pit.png").resize((self.cell, self.cell))),
            "North": ImageTk.PhotoImage(Image.open("visualization/assets/front.png").resize((self.cell//2, self.cell//2))),
            "West": ImageTk.PhotoImage(Image.open("visualization/assets/left.png").resize((self.cell//2, self.cell//2))),
            "East": ImageTk.PhotoImage(Image.open("visualization/assets/right.png").resize((self.cell//2, self.cell//2))),
            "South": ImageTk.PhotoImage(Image.open("visualization/assets/back.png").resize((self.cell//2, self.cell//2))),
            "T": ImageTk.PhotoImage(Image.open("visualization/assets/treasure.png").resize((self.cell//3, self.cell//3))),
            "bomb": ImageTk.PhotoImage(Image.open("visualization/assets/bomb.png").resize((self.cell//5, self.cell//5))),
        }
        self.set_background()
    
    def coordinate_converter(self, i, j):
        return j * self.cell + self.cell, i * self.cell
    
    def set_background(self):
        for i in range(self.grid):
            self.canvas.create_text(self.cell//2, i*self.cell+self.cell//2, text=f'{self.grid - i - 1}')
            self.canvas.create_text((i+1)*self.cell+self.cell//2, self.cell*self.grid+self.cell//2, text=f'{i}')
        for row in range(self.grid):
            for col in range(self.grid):
                x, y = self.coordinate_converter(row, col)
                if self.states.knowledge[self.at_step][row*self.grid + col] == '-':
                    color = 'gray'
                elif self.states.knowledge[self.at_step][row*self.grid + col] == '$':
                    color = 'green'
                elif self.states.knowledge[self.at_step][row*self.grid + col] == '!':
                    color = 'red'
                self.canvas.create_rectangle(x, y, x + self.cell, y + self.cell, fill=color, outline='white')
    
    def put_objects(self):
        for i, j in self.states.pits[self.at_step]:
            x, y = self.coordinate_converter(i, j)
            self.canvas.create_image(x+self.cell//2, y+self.cell//2, self.img['P'])
        for i, j in self.states.wumpuses[self.at_step]:
            x, y = self.coordinate_converter(i, j)
            self.canvas.create_image(x+self.cell//2, y+self.cell//2, self.img['W'])
        
    def put_hints(self):
        for row in range(self.grid):
            for col in range(self.grid):
                if (row, col) in self.states.pits[self.at_step] or (row, col) in self.states.wumpuses[self.at_step]:
                    continue
                stench = self.is_nearby(row, col, self.states.wumpuses[self.at_step])
                breeze = self.is_nearby(row, col, self.states.pits[self.at_step])
                x, y = self.coordinate_converter(row, col)
                if stench and breeze:
                    self.canvas.create_image(x+self.cell//2, y+self.cell//2, self.img['SB'])
                elif stench:
                    self.canvas.create_image(x+self.cell//2, y+self.cell//2, self.img['S'])
                elif breeze:
                    self.canvas.create_image(x+self.cell//2, y+self.cell//2, self.img['B'])

    def is_nearby(self, i, j, object_pos):
        dir = [-1, 0, 1, 0, -1]
        for k in range(4):
            ni, nj = i + dir[k], j + dir[k + 1]
            if (ni, nj) in object_pos:
                return True
        return False
    
    def put_agent(self):
        i, j, direction, result = self.states.actions[self.at_step]
        if result == 'killed':
            pass
        elif result == 'missed':
            pass
        elif result == 'gold':
            pass
        elif result == 'escaped':
            pass
        elif result == 'die':
            pass
        x, y = self.coordinate_converter(i, j)

        if self.carry_gold:
            self.states.gold = (i, j)    
            self.canvas.create_image(x+self.cell//2, y+self.cell//3*2, self.img['T'])
        else:
            xg, yg = self.coordinate_converter(*self.states.gold)
            self.canvas.create_image(xg+self.cell//2, yg+self.cell//3*2, self.img['T'])


    def next(self):
        self.at_step += 1
        self.set_background()
        self.put_objects()
        self.put_hints()
        self.put_agent()