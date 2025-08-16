# Wumpus World Agent - Anti-Cheat Version

## 🎯 Overview
This is a completely refactored version of the Wumpus World Agent that eliminates all cheating behaviors and implements intelligent risk-based decision making. The agent now operates with realistic limitations and uses probability calculations to navigate safely.

## 🚫 Cheats Removed

### 1. **Direct Environment Access**
- **Before**: Agents could directly access `environment_map` to see all cells
- **After**: Agents only receive information through `WumpusEnvironment` interface via perception

### 2. **Omniscient Map Knowledge** 
- **Before**: Agents knew exact positions of Wumpuses, pits, and gold
- **After**: Agents must discover world through exploration and sensory input

### 3. **Perfect Wumpus Movement**
- **Before**: Wumpuses had perfect knowledge of all obstacles when moving
- **After**: Wumpuses move with limited local knowledge, can only sense nearby dangers

### 4. **Auto-Knowledge Updates**
- **Before**: Knowledge base automatically removed stench when Wumpus died
- **After**: Agent must perceive environmental changes through normal perception

### 5. **UI Information Leakage**
- **Before**: UI showed all agent knowledge including unvisited cells
- **After**: UI only shows information agent has actually perceived

## 🧠 New Intelligent Features

### Risk Calculator
- **Wumpus Probability**: Bayesian inference based on stench evidence
- **Pit Probability**: Statistical calculation based on breeze patterns  
- **Total Risk**: Combined death probability for any cell
- **Safe Path Finding**: Prioritizes low-risk routes

### Smart Decision Making
- **Safe Exploration**: Prefers known safe areas with high information value
- **Risk-Based Movement**: When no safe moves exist, chooses lowest risk option
- **Loop Detection**: Identifies and breaks free from oscillating behavior
- **Calculated Shooting**: Only shoots when probability of hitting Wumpus is high
- **Dynamic Thresholds**: Adjusts risk tolerance based on desperation level

### Exploration Strategy
- **Information Value**: Prioritizes cells that reveal most unknown areas
- **Center Bias**: Assumes gold more likely in center regions
- **Visited Memory**: Strongly avoids revisiting explored areas
- **Progressive Risk**: Takes higher calculated risks when stuck

## 📁 File Structure

### Core System
- `env_simulator/environment.py` - Clean environment interface (no cheating)
- `env_simulator/risk_calculator.py` - Probability-based risk assessment
- `agent/agent.py` - Fixed agent with no direct map access
- `agent/intelligent_agent.py` - New smart agent with risk-based logic

### Algorithms
- `search/dijkstra.py` - Risk-aware pathfinding instead of omniscient
- `module/moving_Wumpus.py` - Fair Wumpus movement with limited knowledge

### UI
- `wumpus_ui.py` - Updated to show only legitimate information
- `agent/intelligent_agent_wrapper.py` - UI integration wrapper

## 🎮 Usage

### Command Line
```bash
python main.py
```

### Graphical Interface
```bash
python wumpus_ui.py
```

### Key Controls
- **Play/Pause**: Control game execution
- **Step**: Execute one action at a time  
- **Reset**: Generate new random world
- **Speed**: Adjust game speed

## 🔍 Agent Behavior

### Risk Calculation Process
1. **Perceive Environment**: Get stench/breeze at current position
2. **Update Probabilities**: Use Bayesian inference for adjacent cells
3. **Calculate Risks**: Compute death probability for all moves
4. **Choose Action**: Select safest move with highest exploration value

### Decision Priority
1. **Grab Gold**: If glitter detected at current position
2. **Return Home**: If gold obtained, path back to (0,0)
3. **Safe Exploration**: Move to low-risk unexplored areas
4. **Intelligent Shooting**: Fire arrow if high Wumpus probability
5. **Calculated Risk**: Take minimal risk move when no safe options
6. **Loop Breaking**: Detect and escape oscillating behavior

### Risk Thresholds
- **Safe Movement**: Risk ≤ 0.3 (30% death chance)
- **Emergency Movement**: Risk ≤ 0.7 (70% death chance) 
- **Desperate Movement**: Risk ≤ 0.9 (90% death chance)
- **Shooting Threshold**: Wumpus probability ≥ 0.5 (50% hit chance)

## 📊 Performance Metrics

The agent now demonstrates realistic performance with:
- **No Cheating**: All decisions based on legitimate perception
- **Smart Risk Assessment**: Probability-based danger evaluation
- **Adaptive Behavior**: Adjusts strategy based on situation
- **Loop Avoidance**: Breaks free from unproductive patterns
- **Calculated Exploration**: Balances risk vs information gain

## 🔧 Technical Implementation

### Environment Interface
```python
# Clean perception - no direct map access
percepts = environment.get_percept(position)
```

### Risk Assessment  
```python
# Calculate danger probability
wumpus_risk = calculate_wumpus_probability(position)
pit_risk = calculate_pit_probability(position)
total_risk = 1 - (1 - wumpus_risk) * (1 - pit_risk)
```

### Decision Making
```python
# Choose safest move with highest exploration value
best_move = max(moves, key=lambda m: exploration_value(m) / (1 + risk(m)))
```

This implementation provides a fair, challenging, and intelligent Wumpus World experience without any cheating behaviors.
