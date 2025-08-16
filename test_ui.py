import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'visualization'))

from visualization.UI import UI

def main():
    ui = UI()
    ui.run()

if __name__ == "__main__":
    main()
