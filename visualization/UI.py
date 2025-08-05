import tkinter as tk

CELL_SIZE = 64
GRID_SIZE = 8

window = tk.Tk()
canvas = tk.Canvas(window, width=(GRID_SIZE + 1) *CELL_SIZE, height=(GRID_SIZE + 1)*CELL_SIZE)
canvas.pack()

for row in range(GRID_SIZE):
    for col in range(GRID_SIZE):
        x1 = col * CELL_SIZE + CELL_SIZE
        y1 = row * CELL_SIZE
        x2 = x1 + CELL_SIZE + CELL_SIZE
        y2 = y1 + CELL_SIZE

        color = 'lightgreen' if (row + col) % 2 == 0 else 'orange'
        canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline='')

for i in range(GRID_SIZE):
    xy = CELL_SIZE // 2
    yy = i * CELL_SIZE + CELL_SIZE // 2
    xx = (i + 1) * CELL_SIZE + CELL_SIZE // 2
    yx = CELL_SIZE * GRID_SIZE + CELL_SIZE // 2
    canvas.create_text(xy, yy, text=f'{GRID_SIZE - i - 1}')
    canvas.create_text(xx, yx, text=f'{i}')



window.mainloop()