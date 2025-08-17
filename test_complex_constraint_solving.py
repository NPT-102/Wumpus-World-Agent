#!/usr/bin/env python3
# test_complex_constraint_solving.py

"""
Test advanced constraint solving for complex stench patterns
"""

import sys
import os
from itertools import combinations
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def analyze_stench_constraint_problem():
    """Analyze the constraint solving problem we're facing"""
    print("🧮 Analyzing Stench Constraint Problem")
    print("=" * 50)
    
    # Data from last run
    stench_positions = [(2, 1), (3, 0), (3, 2), (3, 3), (4, 1), (4, 2), (4, 4)]
    actual_wumpus = [(3, 1), (4, 3)]
    
    print(f"Stench positions: {stench_positions}")
    print(f"Actual Wumpus positions: {actual_wumpus}")
    
    # For each stench, find possible Wumpus positions
    def get_adjacent(pos):
        i, j = pos
        return [(i+di, j+dj) for di, dj in [(-1,0), (1,0), (0,-1), (0,1)] 
                if 0 <= i+di < 5 and 0 <= j+dj < 5]
    
    print(f"\nConstraint analysis:")
    stench_to_candidates = {}
    all_candidates = set()
    
    for stench in stench_positions:
        candidates = get_adjacent(stench)
        stench_to_candidates[stench] = candidates
        all_candidates.update(candidates)
        print(f"  Stench at {stench} -> possible Wumpus at: {candidates}")
    
    print(f"\nAll candidate positions: {sorted(all_candidates)}")
    print(f"Actual Wumpus positions: {actual_wumpus}")
    
    # Try brute force: test all combinations of 2 positions
    print(f"\nTrying all combinations of 2 Wumpus positions...")
    valid_combinations = []
    
    for combo in combinations(all_candidates, 2):
        wumpus1, wumpus2 = combo
        
        # Check if this combination explains all stenches
        explained_stenches = set()
        
        for stench in stench_positions:
            stench_explained = False
            # Check if either Wumpus could cause this stench
            for wumpus in [wumpus1, wumpus2]:
                if wumpus in get_adjacent(stench):
                    stench_explained = True
                    break
            
            if stench_explained:
                explained_stenches.add(stench)
        
        # If all stenches are explained, this is a valid combination
        if len(explained_stenches) == len(stench_positions):
            valid_combinations.append(combo)
    
    print(f"Valid combinations found: {len(valid_combinations)}")
    for i, combo in enumerate(valid_combinations[:10]):  # Show first 10
        is_correct = set(combo) == set(actual_wumpus)
        marker = "✅ CORRECT" if is_correct else ""
        print(f"  {i+1}. {combo} {marker}")
    
    if len(valid_combinations) > 10:
        print(f"  ... and {len(valid_combinations) - 10} more")
    
    # Check if actual positions are in valid combinations
    actual_in_valid = tuple(actual_wumpus) in valid_combinations or tuple(reversed(actual_wumpus)) in valid_combinations
    print(f"\nActual Wumpus positions in valid combinations: {'✅ Yes' if actual_in_valid else '❌ No'}")

if __name__ == "__main__":
    analyze_stench_constraint_problem()
