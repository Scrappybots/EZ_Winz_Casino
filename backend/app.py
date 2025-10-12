"""
Main Flask application for NeoBank & Chrome Slots
"""
import os
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from flask_jwt_extended import JWTManager, jwt_required
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from datetime import timedelta

from .models import db, User, Transaction
from .auth import register_user, login_user, get_current_user, api_key_required
from .transactions import create_transaction, get_recent_transactions, search_transactions
from .casino import spin_glitch_grid, spin_starlight_smuggler
from .admin import admin_bp

# Initialize Flask app
app = Flask(__name__, static_folder='../frontend', static_url_path='')

# Configuration
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'neotropolis-dev-key-change-in-production')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///neobank.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = app.config['SECRET_KEY']
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=int(os.environ.get('JWT_EXPIRY_HOURS', 24)))

# Initialize extensions
db.init_app(app)
CORS(app)
jwt = JWTManager(app)
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=[f"{os.environ.get('RATE_LIMIT_PER_MINUTE', 60)} per minute"]
)

# Register blueprints
app.register_blueprint(admin_bp)


# ============================================================================
# Authentication Routes
# ============================================================================

@app.route('/api/v1/auth/register', methods=['POST'])
@limiter.limit("5 per hour")
def api_register():
    """Register a new user"""
    data = request.get_json()
    
    character_name = data.get('character_name')
    password = data.get('password')
    faction = data.get('faction')
    
    if not character_name or not password:
        return jsonify({'error': 'Character name and password required'}), 400
    
    if len(password) < 6:
        return jsonify({'error': 'Password must be at least 6 characters'}), 400
    
    user, error = register_user(character_name, password, faction)
    
    if error:
        return jsonify({'error': error}), 400
    
    return jsonify({
        'message': 'Registration successful',
        'user': user.to_dict()
    }), 201


@app.route('/api/v1/auth/login', methods=['POST'])
@limiter.limit("10 per minute")
def api_login():
    """Login and get JWT token"""
    data = request.get_json()
    
    character_name = data.get('character_name')
    password = data.get('password')
    
    if not character_name or not password:
        return jsonify({'error': 'Character name and password required'}), 400
    
    result, error = login_user(character_name, password)
    
    if error:
        return jsonify({'error': error}), 401
    
    return jsonify(result)


# ============================================================================
# Account & Banking Routes
# ============================================================================

@app.route('/api/v1/account', methods=['GET'])
@jwt_required()
def get_account():
    """Get current user's account information"""
    user = get_current_user()
    return jsonify({'account': user.to_dict()})


@app.route('/api/v1/account/transactions', methods=['GET'])
@jwt_required()
def get_transactions():
    """Get user's transaction history"""
    user = get_current_user()
    limit = int(request.args.get('limit', 10))
    
    transactions = get_recent_transactions(user, limit=limit)
    
    return jsonify({
        'transactions': [t.to_dict() for t in transactions]
    })


@app.route('/api/v1/account/transactions/search', methods=['GET'])
@jwt_required()
def search_user_transactions():
    """Search user's transactions"""
    user = get_current_user()
    query = request.args.get('q', '')
    
    if not query:
        return jsonify({'error': 'Search query required'}), 400
    
    transactions = search_transactions(user, query)
    
    return jsonify({
        'transactions': [t.to_dict() for t in transactions],
        'query': query
    })


@app.route('/api/v1/transactions', methods=['POST'])
@jwt_required()
@limiter.limit("30 per minute")
def create_user_transaction():
    """Create a P2P transaction"""
    data = request.get_json()
    user = get_current_user()
    
    to_account = data.get('to_account')
    amount = data.get('amount')
    memo = data.get('memo')
    
    if not to_account or not amount:
        return jsonify({'error': 'Recipient account and amount required'}), 400
    
    try:
        amount = float(amount)
    except ValueError:
        return jsonify({'error': 'Invalid amount'}), 400
    
    transaction, error = create_transaction(
        user.account_number,
        to_account,
        amount,
        memo=memo
    )
    
    if error:
        return jsonify({'error': error}), 400
    
    return jsonify({
        'message': 'Transaction successful',
        'transaction': transaction.to_dict(),
        'new_balance': user.balance
    }), 201


# ============================================================================
# External API Routes (for integrations)
# ============================================================================

@app.route('/api/v1/external/transactions', methods=['POST'])
@api_key_required
@limiter.limit("100 per minute")
def external_transaction():
    """External API endpoint for creating transactions"""
    data = request.get_json()
    
    from_account = data.get('from_account')
    to_account = data.get('to_account')
    amount = data.get('amount')
    memo = data.get('memo')
    
    if not from_account or not to_account or not amount:
        return jsonify({'error': 'from_account, to_account, and amount required'}), 400
    
    try:
        amount = float(amount)
    except ValueError:
        return jsonify({'error': 'Invalid amount'}), 400
    
    transaction, error = create_transaction(from_account, to_account, amount, memo=memo)
    
    if error:
        return jsonify({'error': error}), 400
    
    return jsonify({
        'message': 'Transaction successful',
        'transaction': transaction.to_dict()
    }), 201


@app.route('/api/v1/external/account/<account_number>/balance', methods=['GET'])
@api_key_required
def external_check_balance(account_number):
    """External API endpoint for checking account balance"""
    user = User.query.filter_by(account_number=account_number).first()
    
    if not user:
        return jsonify({'error': 'Account not found'}), 404
    
    return jsonify({
        'account_number': user.account_number,
        'balance': round(user.balance, 2)
    })


# ============================================================================
# Casino Routes
# ============================================================================

@app.route('/api/v1/casino/glitch-grid/spin', methods=['POST'])
@jwt_required()
@limiter.limit("30 per minute")
def spin_glitch():
    """Spin the Glitch Grid slot machine"""
    data = request.get_json()
    bet_amount = data.get('bet_amount')
    
    if not bet_amount:
        return jsonify({'error': 'Bet amount required'}), 400
    
    try:
        bet_amount = float(bet_amount)
    except ValueError:
        return jsonify({'error': 'Invalid bet amount'}), 400
    
    if bet_amount <= 0:
        return jsonify({'error': 'Bet amount must be positive'}), 400
    
    user = get_current_user()
    result = spin_glitch_grid(user, bet_amount)
    
    if 'error' in result:
        return jsonify({'error': result['error']}), 400
    
    return jsonify(result)


@app.route('/api/v1/casino/starlight-smuggler/spin', methods=['POST'])
@jwt_required()
@limiter.limit("30 per minute")
def spin_starlight():
    """Spin the Starlight Smuggler slot machine"""
    data = request.get_json()
    bet_amount = data.get('bet_amount')
    
    if not bet_amount:
        return jsonify({'error': 'Bet amount required'}), 400
    
    try:
        bet_amount = float(bet_amount)
    except ValueError:
        return jsonify({'error': 'Invalid bet amount'}), 400
    
    if bet_amount <= 0:
        return jsonify({'error': 'Bet amount must be positive'}), 400
    
    user = get_current_user()
    result = spin_starlight_smuggler(user, bet_amount)
    
    if 'error' in result:
        return jsonify({'error': result['error']}), 400
    
    return jsonify(result)


# ============================================================================
# Frontend Routes
# ============================================================================

@app.route('/')
def index():
    """Serve main application"""
    return send_from_directory(app.static_folder, 'index.html')


@app.route('/<path:path>')
def serve_static(path):
    """Serve static files or return index.html for SPA routes"""
    import os
    file_path = os.path.join(app.static_folder, path)
    
    # If the file exists, serve it
    if os.path.isfile(file_path):
        return send_from_directory(app.static_folder, path)
    
    # Otherwise, return index.html for SPA routing (e.g., /admin, /casino)
    return send_from_directory(app.static_folder, 'index.html')


# ============================================================================
# Health Check
# ============================================================================

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'service': 'neobank'})


# ============================================================================
# Database initialization
# ============================================================================

def init_database():
    """Initialize database with system accounts"""
    with app.app_context():
        db.create_all()
        
        # Create system account if not exists
        system_account = User.query.filter_by(account_number='NC-SYST-EM00').first()
        if not system_account:
            from .auth import hash_password
            system_account = User(
                character_name='SYSTEM',
                password_hash=hash_password('system-no-login'),
                account_number='NC-SYST-EM00',
                balance=999999999.0,  # Unlimited funds
                is_admin=True
            )
            db.session.add(system_account)
        
        # Create casino house account if not exists
        house_account = User.query.filter_by(account_number='NC-CASA-0000').first()
        if not house_account:
            from .auth import hash_password
            house_account = User(
                character_name='CASINO HOUSE',
                password_hash=hash_password('house-no-login'),
                account_number='NC-CASA-0000',
                balance=100000.0,  # Starting casino bank
                is_admin=False
            )
            db.session.add(house_account)
        
        # Create default admin account if not exists
        admin_account = User.query.filter_by(character_name='admin').first()
        if not admin_account:
            from .auth import hash_password
            from .models import generate_account_number
            admin_account = User(
                character_name='admin',
                password_hash=hash_password('neotropolis2025'),
                account_number=generate_account_number(),
                balance=1000.0,
                is_admin=True
            )
            db.session.add(admin_account)
        
        # Initialize casino game configs with generous defaults
        from .models import CasinoConfig
        games = ['glitch_grid', 'starlight_smuggler']
        for game in games:
            if not CasinoConfig.query.filter_by(game_name=game).first():
                config = CasinoConfig(
                    game_name=game,
                    is_enabled=True,
                    payout_percentage=102.0  # Generous default: 102% RTP (player-friendly)
                )
                db.session.add(config)
        
        db.session.commit()
        print("✅ Database initialized successfully")


if __name__ == '__main__':
    init_database()
    app.run(host='0.0.0.0', port=5000, debug=os.environ.get('FLASK_DEBUG', 'False') == 'True')
