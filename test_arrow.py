"""
Simple test to check arrow availability
"""

def test_arrow_status():
    print("Testing arrow status logic...")
    
    # Simulate arrow_hit values
    arrow_values = [0, 1, -1]
    
    for arrow_hit in arrow_values:
        print(f"\narrow_hit = {arrow_hit}")
        print(f"arrow_hit != 0: {arrow_hit != 0}")
        print(f"arrow_hit > 0: {arrow_hit > 0}")
        
        # Current logic: arrow_hit != 0
        has_no_arrow_current = arrow_hit != 0
        print(f"Has no arrow (current logic): {has_no_arrow_current}")
        
        # Correct logic: arrow_hit != 0 means no arrow available  
        # arrow_hit = 0: still has arrow
        # arrow_hit = 1: hit something, no arrow left
        # arrow_hit = -1: missed, no arrow left

if __name__ == "__main__":
    test_arrow_status()
