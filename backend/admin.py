"""
Admin panel routes and functionality
"""
from flask import Blueprint, request, jsonify
from .models import db, User, APIKey, AuditLog, CasinoConfig, generate_api_key
from .auth import admin_required, get_current_user, hash_password
from .transactions import get_all_transactions, adjust_account_balance
from datetime import datetime

admin_bp = Blueprint('admin', __name__, url_prefix='/api/admin')


@admin_bp.route('/users/search', methods=['GET'])
@admin_required
def search_users():
    """Search for users by character name or account number"""
    query = request.args.get('q', '')
    
    if not query:
        return jsonify({'error': 'Search query required'}), 400
    
    users = User.query.filter(
        db.or_(
            User.character_name.ilike(f'%{query}%'),
            User.account_number.ilike(f'%{query}%')
        )
    ).limit(20).all()
    
    return jsonify({'users': [user.to_dict() for user in users]})


@admin_bp.route('/users/<account_number>', methods=['GET'])
@admin_required
def get_user_details(account_number):
    """Get detailed information about a user"""
    user = User.query.filter_by(account_number=account_number).first()
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    return jsonify({
        'user': user.to_dict(),
        'total_sent': user.sent_transactions.count(),
        'total_received': user.received_transactions.count()
    })


@admin_bp.route('/users/<account_number>/reset-password', methods=['POST'])
@admin_required
def reset_user_password(account_number):
    """Reset a user's password"""
    data = request.get_json()
    new_password = data.get('new_password')
    
    if not new_password or len(new_password) < 6:
        return jsonify({'error': 'Password must be at least 6 characters'}), 400
    
    user = User.query.filter_by(account_number=account_number).first()
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    # Reset password
    user.password_hash = hash_password(new_password)
    
    # Create audit log
    admin = get_current_user()
    audit = AuditLog(
        admin_user_id=admin.id,
        action='PASSWORD_RESET',
        target_user_id=user.id,
        details=f"Password reset for {user.character_name}"
    )
    
    db.session.add(audit)
    db.session.commit()
    
    return jsonify({'message': 'Password reset successfully'})


@admin_bp.route('/users/<account_number>/toggle-admin', methods=['POST'])
@admin_required
def toggle_admin_status(account_number):
    """Toggle admin status for a user"""
    user = User.query.filter_by(account_number=account_number).first()
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    # Prevent removing own admin access
    admin = get_current_user()
    if user.id == admin.id:
        return jsonify({'error': 'Cannot modify your own admin status'}), 403
    
    # Toggle admin status
    user.is_admin = not user.is_admin
    
    # Create audit log
    audit = AuditLog(
        admin_user_id=admin.id,
        action='TOGGLE_ADMIN',
        target_user_id=user.id,
        details=f"Admin status {'granted to' if user.is_admin else 'revoked from'} {user.character_name}"
    )
    
    db.session.add(audit)
    db.session.commit()
    
    return jsonify({
        'message': f"Admin status {'granted' if user.is_admin else 'revoked'}",
        'user': user.to_dict()
    })


@admin_bp.route('/users/<account_number>/adjust-balance', methods=['POST'])
@admin_required
def adjust_balance(account_number):
    """Manually adjust a user's balance"""
    data = request.get_json()
    amount = data.get('amount')
    reason = data.get('reason', 'Admin adjustment')
    
    if amount is None:
        return jsonify({'error': 'Amount required'}), 400
    
    try:
        amount = float(amount)
    except ValueError:
        return jsonify({'error': 'Invalid amount'}), 400
    
    if not reason:
        return jsonify({'error': 'Reason required'}), 400
    
    admin = get_current_user()
    transaction, error = adjust_account_balance(admin, account_number, amount, reason)
    
    if error:
        return jsonify({'error': error}), 400
    
    return jsonify({
        'message': 'Balance adjusted successfully',
        'transaction': transaction.to_dict()
    })


@admin_bp.route('/transactions', methods=['GET'])
@admin_required
def list_all_transactions():
    """Get global transaction log"""
    limit = int(request.args.get('limit', 100))
    offset = int(request.args.get('offset', 0))
    
    transactions = get_all_transactions(limit=limit, offset=offset)
    
    return jsonify({
        'transactions': [t.to_dict() for t in transactions],
        'limit': limit,
        'offset': offset
    })


@admin_bp.route('/api-keys', methods=['GET'])
@admin_required
def list_api_keys():
    """List all API keys"""
    keys = APIKey.query.all()
    return jsonify({'api_keys': [key.to_dict() for key in keys]})


@admin_bp.route('/api-keys', methods=['POST'])
@admin_required
def create_api_key():
    """Generate a new API key"""
    data = request.get_json()
    description = data.get('description', 'API Key')
    
    admin = get_current_user()
    
    api_key = APIKey(
        key_value=generate_api_key(),
        description=description,
        created_by_user_id=admin.id
    )
    
    db.session.add(api_key)
    
    # Create audit log
    audit = AuditLog(
        admin_user_id=admin.id,
        action='API_KEY_CREATED',
        details=f"Created API key: {description}"
    )
    db.session.add(audit)
    
    db.session.commit()
    
    return jsonify({
        'message': 'API key created',
        'api_key': api_key.to_dict()
    }), 201


@admin_bp.route('/api-keys/<int:key_id>', methods=['DELETE'])
@admin_required
def revoke_api_key(key_id):
    """Revoke an API key"""
    api_key = APIKey.query.get(key_id)
    
    if not api_key:
        return jsonify({'error': 'API key not found'}), 404
    
    api_key.is_active = False
    
    # Create audit log
    admin = get_current_user()
    audit = AuditLog(
        admin_user_id=admin.id,
        action='API_KEY_REVOKED',
        details=f"Revoked API key: {api_key.description}"
    )
    db.session.add(audit)
    
    db.session.commit()
    
    return jsonify({'message': 'API key revoked'})


@admin_bp.route('/casino/config', methods=['GET'])
@admin_required
def get_casino_config():
    """Get casino configuration"""
    configs = CasinoConfig.query.all()
    return jsonify({'games': [config.to_dict() for config in configs]})


@admin_bp.route('/casino/config/<game_name>', methods=['PUT'])
@admin_required
def update_casino_config(game_name):
    """Update casino game configuration"""
    data = request.get_json()
    
    config = CasinoConfig.query.filter_by(game_name=game_name).first()
    if not config:
        config = CasinoConfig(game_name=game_name)
        db.session.add(config)
    
    if 'is_enabled' in data:
        config.is_enabled = bool(data['is_enabled'])
    
    if 'payout_percentage' in data:
        payout = float(data['payout_percentage'])
        if 50 <= payout <= 99:
            config.payout_percentage = payout
        else:
            return jsonify({'error': 'Payout percentage must be between 50 and 99'}), 400
    
    # Create audit log
    admin = get_current_user()
    audit = AuditLog(
        admin_user_id=admin.id,
        action='CASINO_CONFIG_UPDATE',
        details=f"Updated {game_name}: enabled={config.is_enabled}, payout={config.payout_percentage}%"
    )
    db.session.add(audit)
    
    db.session.commit()
    
    return jsonify({
        'message': 'Casino configuration updated',
        'config': config.to_dict()
    })


@admin_bp.route('/audit-logs', methods=['GET'])
@admin_required
def get_audit_logs():
    """Get admin audit logs"""
    limit = int(request.args.get('limit', 50))
    offset = int(request.args.get('offset', 0))
    
    logs = AuditLog.query.order_by(AuditLog.timestamp.desc()).limit(limit).offset(offset).all()
    
    return jsonify({
        'logs': [log.to_dict() for log in logs],
        'limit': limit,
        'offset': offset
    })


@admin_bp.route('/factions/list', methods=['GET'])
@admin_required
def get_factions():
    """Get list of all factions with user counts"""
    from sqlalchemy import func
    
    factions = db.session.query(
        User.faction,
        func.count(User.id).label('user_count'),
        func.sum(User.balance).label('total_balance')
    ).group_by(User.faction).all()
    
    faction_list = []
    for faction, count, total_bal in factions:
        faction_list.append({
            'faction': faction if faction else 'None',
            'user_count': count,
            'total_balance': round(total_bal, 2) if total_bal else 0
        })
    
    return jsonify({'factions': faction_list})


@admin_bp.route('/factions/<faction>/add-credits', methods=['POST'])
@admin_required
def add_faction_credits(faction):
    """Add credits to all users in a faction"""
    data = request.get_json()
    amount = data.get('amount')
    reason = data.get('reason', 'Faction bonus')
    
    if not amount or amount <= 0:
        return jsonify({'error': 'Valid amount required'}), 400
    
    # Handle 'None' faction
    if faction.lower() == 'none':
        faction = None
    
    # Get all users in faction
    users = User.query.filter_by(faction=faction).all()
    
    if not users:
        return jsonify({'error': 'No users found in this faction'}), 404
    
    # Add credits to each user
    admin = get_current_user()
    affected_count = 0
    
    for user in users:
        # Skip system accounts
        if user.account_number.startswith('NC-SYST') or user.account_number.startswith('NC-CASA'):
            continue
        
        user.balance += amount
        affected_count += 1
    
    # Create audit log
    audit = AuditLog(
        admin_user_id=admin.id,
        action='FACTION_CREDITS',
        details=f"Added ¤{amount} to {affected_count} users in faction '{faction or 'None'}': {reason}"
    )
    db.session.add(audit)
    db.session.commit()
    
    return jsonify({
        'message': f'Added ¤{amount} to {affected_count} users',
        'affected_users': affected_count,
        'faction': faction or 'None'
    })


@admin_bp.route('/users/export', methods=['GET'])
@admin_required
def export_users_csv():
    """Export all users to CSV"""
    import csv
    from io import StringIO
    from flask import make_response
    
    # Get all users (excluding system accounts)
    users = User.query.filter(
        ~User.account_number.in_(['NC-SYST-EM00', 'NC-CASA-0000'])
    ).order_by(User.character_name).all()
    
    # Create CSV in memory
    output = StringIO()
    writer = csv.writer(output)
    
    # Write header
    writer.writerow([
        'Character Name',
        'Account Number',
        'Balance',
        'Faction',
        'Is Admin',
        'Created At'
    ])
    
    # Write user data
    for user in users:
        writer.writerow([
            user.character_name,
            user.account_number,
            f'{user.balance:.2f}',
            user.faction or 'None',
            'Yes' if user.is_admin else 'No',
            user.created_at.strftime('%Y-%m-%d %H:%M:%S')
        ])
    
    # Create response
    response = make_response(output.getvalue())
    response.headers['Content-Type'] = 'text/csv'
    response.headers['Content-Disposition'] = 'attachment; filename=neobank_users_export.csv'
    
    # Log export
    admin = get_current_user()
    audit = AuditLog(
        admin_user_id=admin.id,
        action='USER_EXPORT',
        details=f"Exported {len(users)} users to CSV"
    )
    db.session.add(audit)
    db.session.commit()
    
    return response
