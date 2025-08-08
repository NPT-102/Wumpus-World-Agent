import tkinter as tk

class Selector(tk.Frame):
    def __init__(self, parent=None, on_start=None):
        super().__init__(parent)
        self.parent = parent
        self.on_start = on_start
        self.create_widget()

    def create_widget(self):
        size_var = tk.StringVar()
        random_agent = tk.IntVar()
        moving_wumpus = tk.IntVar()
        size_label = tk.Label(self, text='Grid size: ')
        size_entry = tk.Entry(self, textvariable=size_var)
        random_agent_check = tk.Checkbutton(self, text='Random Agent', variable=random_agent, onvalue=1, offvalue=0)
        moving_wumpus_check = tk.Checkbutton(self, text='Moving Wumpus', variable=moving_wumpus, onvalue=1, offvalue=0)

        start_button = tk.Button(self, text='START', command=lambda: self.on_start(size_var.get(), random_agent.get(), moving_wumpus.get()))

        size_label.pack(side='left')
        size_entry.pack(side='left', padx=(10, 0))
        random_agent_check.pack(side='left', padx=(10, 0))
        moving_wumpus_check.pack(side='left', padx=(10, 0))
        start_button.pack(side='right')