"""
Test script for new Profile and Admin features
"""
import requests
import json

BASE_URL = "http://localhost:8080/api"

def test_profile_features():
    """Test user profile management features"""
    print("=" * 60)
    print("TESTING PROFILE FEATURES")
    print("=" * 60)
    
    # Login as admin
    print("\n1. Logging in as admin...")
    response = requests.post(f"{BASE_URL}/v1/auth/login", json={
        "character_name": "admin",
        "password": "admin123"
    })
    if response.status_code == 200:
        data = response.json()
        token = data['access_token']
        print(f"✓ Login successful! Token: {token[:20]}...")
    else:
        print(f"✗ Login failed: {response.text}")
        return None
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test profile update
    print("\n2. Updating profile (faction and profile picture)...")
    response = requests.put(f"{BASE_URL}/v1/account/profile", 
        headers=headers,
        json={
            "faction": "Technocrats",
            "profile_picture": "🤖"
        }
    )
    if response.status_code == 200:
        print(f"✓ Profile updated: {response.json()}")
    else:
        print(f"✗ Profile update failed: {response.text}")
    
    # Test password change
    print("\n3. Testing password change...")
    response = requests.put(f"{BASE_URL}/v1/account/password",
        headers=headers,
        json={
            "current_password": "admin123",
            "new_password": "admin123new"
        }
    )
    if response.status_code == 200:
        print(f"✓ Password changed: {response.json()}")
        
        # Change it back
        print("   Changing password back to original...")
        response = requests.put(f"{BASE_URL}/v1/account/password",
            headers=headers,
            json={
                "current_password": "admin123new",
                "new_password": "admin123"
            }
        )
        if response.status_code == 200:
            print("   ✓ Password restored")
    else:
        print(f"✗ Password change failed: {response.text}")
    
    return token

def test_faction_features(token):
    """Test admin faction management features"""
    print("\n" + "=" * 60)
    print("TESTING FACTION FEATURES")
    print("=" * 60)
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test faction list
    print("\n1. Fetching faction list...")
    response = requests.get(f"{BASE_URL}/admin/factions/list", headers=headers)
    if response.status_code == 200:
        data = response.json()
        print(f"✓ Factions loaded: {len(data['factions'])} factions found")
        for faction in data['factions']:
            print(f"   - {faction['faction']}: {faction['user_count']} users, ¤{faction['total_balance']}")
    else:
        print(f"✗ Faction list failed: {response.text}")
    
    # Test adding credits to a faction
    print("\n2. Adding credits to Technocrats faction...")
    response = requests.post(f"{BASE_URL}/admin/factions/Technocrats/add-credits",
        headers=headers,
        json={
            "amount": 100.00,
            "reason": "Test bonus from automated test"
        }
    )
    if response.status_code == 200:
        data = response.json()
        print(f"✓ Credits added: {data['users_affected']} users received ¤100")
    else:
        print(f"✗ Add credits failed: {response.text}")

def test_export_feature(token):
    """Test CSV export feature"""
    print("\n" + "=" * 60)
    print("TESTING CSV EXPORT")
    print("=" * 60)
    
    headers = {"Authorization": f"Bearer {token}"}
    
    print("\n1. Requesting CSV export...")
    response = requests.get(f"{BASE_URL}/admin/users/export", headers=headers)
    if response.status_code == 200:
        csv_content = response.text
        lines = csv_content.strip().split('\n')
        print(f"✓ CSV export successful: {len(lines)} lines")
        print(f"   Header: {lines[0]}")
        print(f"   First record: {lines[1] if len(lines) > 1 else 'No data'}")
        
        # Save to file
        with open('test_export.csv', 'w') as f:
            f.write(csv_content)
        print("   ✓ Saved to test_export.csv")
    else:
        print(f"✗ CSV export failed: {response.text}")

def main():
    """Run all tests"""
    print("\n🧪 NeoBank Feature Test Suite")
    print("Testing Profile and Admin features\n")
    
    try:
        # Test profile features
        token = test_profile_features()
        
        if token:
            # Test faction features
            test_faction_features(token)
            
            # Test export feature
            test_export_feature(token)
            
            print("\n" + "=" * 60)
            print("✅ ALL TESTS COMPLETED")
            print("=" * 60)
            print("\nNext steps:")
            print("1. Open http://localhost:8080 in your browser")
            print("2. Login as admin/admin123")
            print("3. Navigate to Profile tab to test UI")
            print("4. Navigate to Admin tab to test faction management")
            print("5. Click 'Download CSV Export' to test export\n")
        
    except Exception as e:
        print(f"\n❌ Test suite failed with error: {e}")

if __name__ == "__main__":
    main()
