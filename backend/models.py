"""
Database models for NeoBank & Chrome Slots
"""
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import secrets
import string

db = SQLAlchemy()

def generate_account_number():
    """Generate a unique account number in NC-XXXX-XXXX format"""
    chars = string.ascii_uppercase + string.digits
    while True:
        part1 = ''.join(secrets.choice(chars) for _ in range(4))
        part2 = ''.join(secrets.choice(chars) for _ in range(4))
        account_num = f"NC-{part1}-{part2}"
        # Check if already exists
        if not User.query.filter_by(account_number=account_num).first():
            return account_num

def generate_api_key():
    """Generate a secure API key"""
    return secrets.token_urlsafe(32)


class User(db.Model):
    """User account model"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    character_name = db.Column(db.String(100), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    account_number = db.Column(db.String(20), unique=True, nullable=False, index=True)
    faction = db.Column(db.String(50), nullable=True)
    balance = db.Column(db.Float, default=1000.0, nullable=False)  # New users start with $1000
    is_admin = db.Column(db.Boolean, default=False)
    profile_picture = db.Column(db.String(255), nullable=True)  # URL or emoji for profile picture
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    sent_transactions = db.relationship('Transaction', 
                                       foreign_keys='Transaction.from_account_id',
                                       backref='sender',
                                       lazy='dynamic')
    received_transactions = db.relationship('Transaction',
                                           foreign_keys='Transaction.to_account_id',
                                           backref='receiver',
                                           lazy='dynamic')
    
    def to_dict(self, include_balance=True):
        data = {
            'character_name': self.character_name,
            'account_number': self.account_number,
            'faction': self.faction,
            'created_at': self.created_at.isoformat(),
            'is_admin': self.is_admin,
            'profile_picture': self.profile_picture
        }
        if include_balance:
            data['balance'] = round(self.balance, 2)
        return data


class Transaction(db.Model):
    """Transaction records"""
    __tablename__ = 'transactions'
    
    id = db.Column(db.Integer, primary_key=True)
    from_account_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    to_account_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    amount = db.Column(db.Float, nullable=False)
    memo = db.Column(db.String(140), nullable=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    transaction_type = db.Column(db.String(20), default='transfer')  # transfer, casino_bet, casino_win, admin_adjustment
    
    def to_dict(self):
        return {
            'id': self.id,
            'from_account': self.sender.account_number,
            'from_name': self.sender.character_name,
            'to_account': self.receiver.account_number,
            'to_name': self.receiver.character_name,
            'amount': round(self.amount, 2),
            'memo': self.memo,
            'timestamp': self.timestamp.isoformat(),
            'type': self.transaction_type
        }


class APIKey(db.Model):
    """API keys for external system integration"""
    __tablename__ = 'api_keys'
    
    id = db.Column(db.Integer, primary_key=True)
    key_value = db.Column(db.String(100), unique=True, nullable=False, index=True)
    description = db.Column(db.String(200), nullable=True)
    created_by_user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_used = db.Column(db.DateTime, nullable=True)
    
    created_by = db.relationship('User', backref='created_api_keys')
    
    def to_dict(self):
        return {
            'id': self.id,
            'key_value': self.key_value,
            'description': self.description,
            'created_by': self.created_by.character_name,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat(),
            'last_used': self.last_used.isoformat() if self.last_used else None
        }


class AuditLog(db.Model):
    """Audit log for admin actions"""
    __tablename__ = 'audit_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    admin_user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    action = db.Column(db.String(50), nullable=False)
    target_user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    details = db.Column(db.Text, nullable=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    
    admin = db.relationship('User', foreign_keys=[admin_user_id], backref='admin_actions')
    target = db.relationship('User', foreign_keys=[target_user_id], backref='targeted_by_admin')
    
    def to_dict(self):
        return {
            'id': self.id,
            'admin': self.admin.character_name,
            'action': self.action,
            'target': self.target.character_name if self.target else None,
            'details': self.details,
            'timestamp': self.timestamp.isoformat()
        }


class CasinoConfig(db.Model):
    """Casino configuration and controls"""
    __tablename__ = 'casino_config'
    
    id = db.Column(db.Integer, primary_key=True)
    game_name = db.Column(db.String(50), unique=True, nullable=False)
    is_enabled = db.Column(db.Boolean, default=True)
    payout_percentage = db.Column(db.Float, default=102.0)  # 102% RTP (generous default)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'game_name': self.game_name,
            'is_enabled': self.is_enabled,
            'payout_percentage': self.payout_percentage,
            'updated_at': self.updated_at.isoformat()
        }
