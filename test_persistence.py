import tools
import os
import csv

def test_csv_persistence():
    print("Testing CSV persistence in tools.py...")
    
    # Ensure fresh start
    if os.path.exists(tools.DB_FILE):
        os.remove(tools.DB_FILE)
    
    # 1. Test booking
    res = tools.make_reservation("2026-03-01", "19:00", 4, "Persistence User")
    assert "Successfully booked" in res
    assert os.path.exists(tools.DB_FILE)
    print("✓ make_reservation & CSV creation passed")
    
    # 2. Test reading from CSV (simulate system restart)
    # We'll just call check_availability which loads from file
    res = tools.check_availability("2026-03-01", "19:00", 76) # Total 80, 4 taken
    assert "available" in res.lower()
    
    res = tools.check_availability("2026-03-01", "19:00", 77) # Should be over limit
    assert "fully booked" in res.lower()
    print("✓ persistence & capacity check passed")
    
    # 3. Verify CSV content structure
    with open(tools.DB_FILE, 'r') as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        assert len(rows) == 1
        assert rows[0]['name'] == "Persistence User"
        assert rows[0]['party_size'] == "4"
    print("✓ CSV record content verified")

if __name__ == "__main__":
    try:
        test_csv_persistence()
        print("\nAll persistence tests passed successfully!")
    except AssertionError as e:
        print(f"\nTest failed: {e}")
    except Exception as e:
        print(f"\nAn error occurred: {e}")
