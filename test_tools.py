import tools
import os

def test_tools():
    print("Testing tools.py...")
    
    # Test availability
    res = tools.check_availability("2026-03-01", "19:00", 4)
    assert "available" in res.lower()
    print("✓ check_availability passed")
    
    # Test booking
    res = tools.make_reservation("2026-03-01", "19:00", 4, "John Doe")
    assert "Successfully booked" in res
    print("✓ make_reservation passed")
    
    # Test availability after booking
    # Total capacity 80, booked 4, remaining 76.
    # Try booking 77.
    res = tools.check_availability("2026-03-01", "19:00", 77)
    assert "fully booked" in res.lower()
    print("✓ capacity check passed")
    
    # Test order status
    res = tools.get_order_status("BV123")
    assert "being prepared" in res
    print("✓ get_order_status (valid) passed")
    
    res = tools.get_order_status("UNKNOWN")
    assert "not found" in res
    print("✓ get_order_status (invalid) passed")
    
    # Test menu info
    res = tools.get_menu_info()
    assert "Appetizers" in res
    assert "Main Courses" in res
    print("✓ get_menu_info passed")

if __name__ == "__main__":
    try:
        test_tools()
        print("\nAll tool tests passed successfully!")
    except AssertionError as e:
        print(f"\nTest failed: {e}")
    except Exception as e:
        print(f"\nAn error occurred: {e}")
