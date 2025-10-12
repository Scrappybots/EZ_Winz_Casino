"""
Test Suite for NeoBank & Chrome Slots
Run with: pytest test_suite.py
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

import pytest
from app import app, db, init_database
from models import User, Transaction, APIKey, generate_account_number
from auth import hash_password, verify_password
from transactions import create_transaction

@pytest.fixture
def client():
    """Create test client"""
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    
    with app.test_client() as client:
        with app.app_context():
            init_database()
        yield client

@pytest.fixture
def auth_headers(client):
    """Create authenticated user and return headers"""
    # Register user
    response = client.post('/api/v1/auth/register', json={
        'character_name': 'TestUser',
        'password': 'testpass123',
        'faction': 'Runners'
    })
    assert response.status_code == 201
    
    # Login
    response = client.post('/api/v1/auth/login', json={
        'character_name': 'TestUser',
        'password': 'testpass123'
    })
    assert response.status_code == 200
    data = response.get_json()
    token = data['access_token']
    
    return {'Authorization': f'Bearer {token}'}


class TestAuthentication:
    def test_registration(self, client):
        """Test user registration"""
        response = client.post('/api/v1/auth/register', json={
            'character_name': 'Alice',
            'password': 'password123',
            'faction': 'CorpSec'
        })
        assert response.status_code == 201
        data = response.get_json()
        assert 'user' in data
        assert data['user']['character_name'] == 'Alice'
        assert 'account_number' in data['user']
        assert data['user']['account_number'].startswith('NC-')
    
    def test_duplicate_registration(self, client):
        """Test duplicate username prevention"""
        client.post('/api/v1/auth/register', json={
            'character_name': 'Bob',
            'password': 'password123'
        })
        response = client.post('/api/v1/auth/register', json={
            'character_name': 'Bob',
            'password': 'password456'
        })
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data
    
    def test_login(self, client):
        """Test user login"""
        client.post('/api/v1/auth/register', json={
            'character_name': 'Charlie',
            'password': 'password123'
        })
        response = client.post('/api/v1/auth/login', json={
            'character_name': 'Charlie',
            'password': 'password123'
        })
        assert response.status_code == 200
        data = response.get_json()
        assert 'access_token' in data
        assert 'user' in data
    
    def test_invalid_login(self, client):
        """Test login with wrong password"""
        client.post('/api/v1/auth/register', json={
            'character_name': 'Dave',
            'password': 'password123'
        })
        response = client.post('/api/v1/auth/login', json={
            'character_name': 'Dave',
            'password': 'wrongpassword'
        })
        assert response.status_code == 401
        data = response.get_json()
        assert 'error' in data


class TestBanking:
    def test_get_account(self, client, auth_headers):
        """Test getting account information"""
        response = client.get('/api/v1/account', headers=auth_headers)
        assert response.status_code == 200
        data = response.get_json()
        assert 'account' in data
        assert data['account']['character_name'] == 'TestUser'
    
    def test_transfer_success(self, client, auth_headers):
        """Test successful transfer"""
        # Create recipient
        client.post('/api/v1/auth/register', json={
            'character_name': 'Recipient',
            'password': 'password123'
        })
        
        # Get sender account
        response = client.get('/api/v1/account', headers=auth_headers)
        sender_data = response.get_json()
        
        # Get recipient account
        response = client.post('/api/v1/auth/login', json={
            'character_name': 'Recipient',
            'password': 'password123'
        })
        recipient_token = response.get_json()['access_token']
        response = client.get('/api/v1/account', 
                              headers={'Authorization': f'Bearer {recipient_token}'})
        recipient_data = response.get_json()
        recipient_account = recipient_data['account']['account_number']
        
        # Give sender some money (using system account)
        with app.app_context():
            sender = User.query.filter_by(
                character_name='TestUser'
            ).first()
            sender.balance = 1000.0
            db.session.commit()
        
        # Perform transfer
        response = client.post('/api/v1/transactions', 
                               headers=auth_headers,
                               json={
                                   'to_account': recipient_account,
                                   'amount': 100.0,
                                   'memo': 'Test payment'
                               })
        assert response.status_code == 201
        data = response.get_json()
        assert data['transaction']['amount'] == 100.0
        assert data['new_balance'] == 900.0
    
    def test_transfer_insufficient_funds(self, client, auth_headers):
        """Test transfer with insufficient funds"""
        # Create recipient
        client.post('/api/v1/auth/register', json={
            'character_name': 'Recipient2',
            'password': 'password123'
        })
        
        response = client.post('/api/v1/auth/login', json={
            'character_name': 'Recipient2',
            'password': 'password123'
        })
        recipient_token = response.get_json()['access_token']
        response = client.get('/api/v1/account',
                              headers={'Authorization': f'Bearer {recipient_token}'})
        recipient_account = response.get_json()['account']['account_number']
        
        # Try to transfer more than balance
        response = client.post('/api/v1/transactions',
                               headers=auth_headers,
                               json={
                                   'to_account': recipient_account,
                                   'amount': 1000000.0,
                                   'memo': 'Impossible payment'
                               })
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data
    
    def test_get_transactions(self, client, auth_headers):
        """Test getting transaction history"""
        response = client.get('/api/v1/account/transactions',
                              headers=auth_headers)
        assert response.status_code == 200
        data = response.get_json()
        assert 'transactions' in data
        assert isinstance(data['transactions'], list)


class TestCasino:
    def test_glitch_grid_spin(self, client, auth_headers):
        """Test Glitch Grid slot machine"""
        # Give player some money
        with app.app_context():
            player = User.query.filter_by(character_name='TestUser').first()
            player.balance = 1000.0
            db.session.commit()
        
        response = client.post('/api/v1/casino/glitch-grid/spin',
                               headers=auth_headers,
                               json={'bet_amount': 10.0})
        assert response.status_code == 200
        data = response.get_json()
        assert 'reels' in data
        assert len(data['reels']) == 3
        assert 'win_amount' in data
        assert 'balance' in data
    
    def test_starlight_smuggler_spin(self, client, auth_headers):
        """Test Starlight Smuggler slot machine"""
        # Give player some money
        with app.app_context():
            player = User.query.filter_by(character_name='TestUser').first()
            player.balance = 1000.0
            db.session.commit()
        
        response = client.post('/api/v1/casino/starlight-smuggler/spin',
                               headers=auth_headers,
                               json={'bet_amount': 5.0})
        assert response.status_code == 200
        data = response.get_json()
        assert 'grid' in data
        assert len(data['grid']) == 3
        assert len(data['grid'][0]) == 5
        assert 'win_amount' in data
    
    def test_spin_insufficient_funds(self, client, auth_headers):
        """Test spinning with insufficient funds"""
        response = client.post('/api/v1/casino/glitch-grid/spin',
                               headers=auth_headers,
                               json={'bet_amount': 1000000.0})
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data


class TestModels:
    def test_account_number_generation(self):
        """Test unique account number generation"""
        with app.app_context():
            account1 = generate_account_number()
            account2 = generate_account_number()
            
            assert account1.startswith('NC-')
            assert account2.startswith('NC-')
            assert account1 != account2
            assert len(account1) == 13  # NC-XXXX-XXXX
    
    def test_password_hashing(self):
        """Test password hashing and verification"""
        password = 'mySecurePassword123'
        hashed = hash_password(password)
        
        assert hashed != password
        assert verify_password(password, hashed) == True
        assert verify_password('wrongPassword', hashed) == False


class TestHealth:
    def test_health_endpoint(self, client):
        """Test health check endpoint"""
        response = client.get('/health')
        assert response.status_code == 200
        data = response.get_json()
        assert data['status'] == 'healthy'
        assert data['service'] == 'neobank'


if __name__ == '__main__':
    print("🧪 Running NeoBank Test Suite...")
    print("="*50)
    pytest.main([__file__, '-v', '--tb=short'])
