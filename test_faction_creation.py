"""
Test script for new Faction Creation feature
"""
import requests

BASE_URL = "http://localhost:8080/api"

def test_faction_creation():
    """Test creating a new faction"""
    print("=" * 60)
    print("TESTING FACTION CREATION")
    print("=" * 60)
    
    # Login as admin
    print("\n1. Logging in as admin...")
    response = requests.post(f"{BASE_URL}/v1/auth/login", json={
        "character_name": "admin",
        "password": "neotropolis2025"
    })
    
    if response.status_code != 200:
        print(f"✗ Login failed: {response.text}")
        return
    
    data = response.json()
    token = data['access_token']
    print(f"✓ Login successful!")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test creating a new faction
    print("\n2. Creating new faction 'Neo Syndicate'...")
    response = requests.post(f"{BASE_URL}/admin/factions/create",
        headers=headers,
        json={
            "name": "Neo Syndicate",
            "description": "Elite cybernetic operatives specializing in corporate espionage"
        }
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"✓ Faction created: {data}")
    else:
        print(f"✗ Faction creation failed: {response.text}")
    
    # Test creating another faction without description
    print("\n3. Creating new faction 'Void Runners' (no description)...")
    response = requests.post(f"{BASE_URL}/admin/factions/create",
        headers=headers,
        json={
            "name": "Void Runners"
        }
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"✓ Faction created: {data}")
    else:
        print(f"✗ Faction creation failed: {response.text}")
    
    # Test creating duplicate faction (should fail)
    print("\n4. Attempting to create duplicate 'Neo Syndicate' (should fail)...")
    response = requests.post(f"{BASE_URL}/admin/factions/create",
        headers=headers,
        json={
            "name": "Neo Syndicate",
            "description": "This should fail"
        }
    )
    
    if response.status_code == 400:
        print(f"✓ Duplicate correctly rejected: {response.json()}")
    else:
        print(f"✗ Unexpected response: {response.status_code} - {response.text}")
    
    # List all factions to verify
    print("\n5. Listing all factions to verify...")
    response = requests.get(f"{BASE_URL}/admin/factions/list", headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        print(f"✓ Found {len(data['factions'])} factions:")
        for faction in data['factions']:
            print(f"   - {faction['faction']}: {faction['user_count']} users, ¤{faction['total_balance']}")
    else:
        print(f"✗ Failed to list factions: {response.text}")
    
    print("\n" + "=" * 60)
    print("✅ FACTION CREATION TEST COMPLETED")
    print("=" * 60)
    print("\nNext steps:")
    print("1. Open http://localhost:8080 in your browser")
    print("2. Login as admin/neotropolis2025")
    print("3. Go to Admin tab")
    print("4. Scroll to 'CREATE NEW FACTION' section")
    print("5. Enter a faction name and optional description")
    print("6. Click 'CREATE FACTION' button\n")

if __name__ == "__main__":
    try:
        test_faction_creation()
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
