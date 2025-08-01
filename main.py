from env_simulator.generateMap import WumpusWorldGenerator, print_map

def main():
  gen_map = WumpusWorldGenerator()
  print("Generating Wumpus World Map...")
  map = gen_map.generate_map()
  print_map(map)
  
if __name__ == "__main__":
  main()