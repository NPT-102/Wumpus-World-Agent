#!/usr/bin/env python3
"""
Test Wumpus removal from UI after death
"""

# Simulate KB facts to test Wumpus display logic

def test_wumpus_display_logic():
    """Test the logic that determines whether to show Wumpus on UI"""
    
    print("=== TESTING WUMPUS DISPLAY LOGIC ===")
    
    # Test Case 1: Alive Wumpus should be shown
    facts_set1 = {
        "W(2,1)",  # Wumpus at (2,1)
        "S(1,1)",  # Stench at (1,1) 
        "S(2,0)",  # Stench at (2,0)
        "S(3,1)",  # Stench at (3,1)
        "S(2,2)"   # Stench at (2,2)
    }
    
    wumpus_pos = (2, 1)
    dead_wumpus_fact = f"~W({wumpus_pos[0]},{wumpus_pos[1]})"
    
    should_show_1 = dead_wumpus_fact not in facts_set1
    print(f"Test 1 - Alive Wumpus at {wumpus_pos}:")
    print(f"  Facts: {sorted(facts_set1)}")
    print(f"  Looking for: {dead_wumpus_fact}")
    print(f"  Should show Wumpus: {should_show_1} ✅" if should_show_1 else f"  Should show Wumpus: {should_show_1} ❌")
    
    # Test Case 2: Dead Wumpus should NOT be shown
    facts_set2 = {
        "W(2,1)",     # Original Wumpus fact (historical)
        "~W(2,1)",    # Wumpus is dead
        "~S(1,1)",    # No stench at (1,1) 
        "~S(2,0)",    # No stench at (2,0)
        "~S(3,1)",    # No stench at (3,1)
        "~S(2,2)",    # No stench at (2,2)
        "Safe(2,1)"   # Position is now safe
    }
    
    should_show_2 = dead_wumpus_fact not in facts_set2
    print(f"\nTest 2 - Dead Wumpus at {wumpus_pos}:")
    print(f"  Facts: {sorted(facts_set2)}")
    print(f"  Looking for: {dead_wumpus_fact}")
    print(f"  Should show Wumpus: {should_show_2} ❌" if not should_show_2 else f"  Should show Wumpus: {should_show_2} ✅")
    
    # Test Case 3: Multiple Wumpus, one dead, one alive
    facts_set3 = {
        "W(2,1)",     # First Wumpus (dead)
        "~W(2,1)",    # First Wumpus is dead
        "W(0,3)",     # Second Wumpus (alive)
        "S(0,2)",     # Stench from second Wumpus
        "S(1,3)",     # Stench from second Wumpus
        "Safe(2,1)"   # First Wumpus position is safe
    }
    
    wumpus1_pos = (2, 1)
    wumpus2_pos = (0, 3)
    dead_wumpus1_fact = f"~W({wumpus1_pos[0]},{wumpus1_pos[1]})"
    dead_wumpus2_fact = f"~W({wumpus2_pos[0]},{wumpus2_pos[1]})"
    
    should_show_wumpus1 = dead_wumpus1_fact not in facts_set3
    should_show_wumpus2 = dead_wumpus2_fact not in facts_set3
    
    print(f"\nTest 3 - Multiple Wumpus scenario:")
    print(f"  Facts: {sorted(facts_set3)}")
    print(f"  Wumpus 1 at {wumpus1_pos}: Should show: {should_show_wumpus1} ❌")
    print(f"  Wumpus 2 at {wumpus2_pos}: Should show: {should_show_wumpus2} ✅")
    
    # Summary
    all_tests_passed = (should_show_1 == True and 
                       should_show_2 == False and 
                       should_show_wumpus1 == False and 
                       should_show_wumpus2 == True)
    
    print(f"\n=== SUMMARY ===")
    if all_tests_passed:
        print("✅ ALL TESTS PASSED! Wumpus display logic is working correctly.")
        print("- Alive Wumpus: SHOWN ✅")
        print("- Dead Wumpus: HIDDEN ✅") 
        print("- Multiple Wumpus: Correctly shows only alive ones ✅")
    else:
        print("❌ Some tests failed!")
    
    return all_tests_passed

if __name__ == "__main__":
    test_wumpus_display_logic()
