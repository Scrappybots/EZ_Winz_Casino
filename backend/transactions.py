"""
Transaction engine - Atomic, secure transaction processing
"""
from .models import db, User, Transaction
from sqlalchemy.exc import SQLAlchemyError


def create_transaction(from_account, to_account, amount, memo=None, transaction_type='transfer'):
    """
    Create an atomic transaction between two accounts
    
    Args:
        from_account: Account number (string) or User object
        to_account: Account number (string) or User object
        amount: Transaction amount (float)
        memo: Optional memo (string, max 140 chars)
        transaction_type: Type of transaction (string)
    
    Returns:
        (transaction, error) tuple
    """
    try:
        # Validate amount
        if amount <= 0:
            return None, "Amount must be positive"
        
        # Get user objects if account numbers provided
        if isinstance(from_account, str):
            sender = User.query.filter_by(account_number=from_account).first()
            if not sender:
                return None, f"Sender account {from_account} not found"
        else:
            sender = from_account
        
        if isinstance(to_account, str):
            receiver = User.query.filter_by(account_number=to_account).first()
            if not receiver:
                return None, f"Receiver account {to_account} not found"
        else:
            receiver = to_account
        
        # Validate sender has sufficient funds
        if sender.balance < amount:
            return None, "Insufficient funds"
        
        # Validate memo length
        if memo and len(memo) > 140:
            return None, "Memo exceeds 140 characters"
        
        # Begin atomic transaction
        sender.balance -= amount
        receiver.balance += amount
        
        # Create transaction record
        transaction = Transaction(
            from_account_id=sender.id,
            to_account_id=receiver.id,
            amount=amount,
            memo=memo,
            transaction_type=transaction_type
        )
        
        db.session.add(transaction)
        db.session.commit()
        
        return transaction, None
        
    except SQLAlchemyError as e:
        db.session.rollback()
        return None, f"Database error: {str(e)}"
    except Exception as e:
        db.session.rollback()
        return None, f"Transaction failed: {str(e)}"


def get_user_transactions(user, limit=None, offset=0):
    """Get transaction history for a user"""
    # Get all transactions where user is sender or receiver
    sent = user.sent_transactions
    received = user.received_transactions
    
    # Combine and sort by timestamp
    all_transactions = sent.union(received).order_by(Transaction.timestamp.desc())
    
    if limit:
        all_transactions = all_transactions.limit(limit).offset(offset)
    
    return all_transactions.all()


def get_recent_transactions(user, limit=10):
    """Get the most recent transactions for a user"""
    return get_user_transactions(user, limit=limit)


def search_transactions(user, query, limit=50):
    """Search user's transactions by memo or account number"""
    sent = user.sent_transactions.filter(
        db.or_(
            Transaction.memo.ilike(f'%{query}%'),
            User.account_number.ilike(f'%{query}%')
        )
    )
    received = user.received_transactions.filter(
        db.or_(
            Transaction.memo.ilike(f'%{query}%'),
            User.account_number.ilike(f'%{query}%')
        )
    )
    
    all_transactions = sent.union(received).order_by(Transaction.timestamp.desc()).limit(limit)
    return all_transactions.all()


def get_all_transactions(limit=100, offset=0):
    """Get all transactions (for admin panel)"""
    return Transaction.query.order_by(Transaction.timestamp.desc()).limit(limit).offset(offset).all()


def adjust_account_balance(admin_user, target_account, amount, reason):
    """
    Admin function to manually adjust an account balance
    Creates an audit trail
    """
    from .models import AuditLog
    
    try:
        # Get target user
        if isinstance(target_account, str):
            target = User.query.filter_by(account_number=target_account).first()
            if not target:
                return None, f"Account {target_account} not found"
        else:
            target = target_account
        
        # Determine transaction direction
        if amount > 0:
            # Credit - money comes from system account
            system_account = User.query.filter_by(account_number='NC-SYST-EM00').first()
            if not system_account:
                return None, "System account not found"
            
            transaction, error = create_transaction(
                system_account,
                target,
                amount,
                memo=f"Admin credit by {admin_user.character_name}: {reason}",
                transaction_type='admin_adjustment'
            )
        else:
            # Debit - money goes to system account
            system_account = User.query.filter_by(account_number='NC-SYST-EM00').first()
            if not system_account:
                return None, "System account not found"
            
            transaction, error = create_transaction(
                target,
                system_account,
                abs(amount),
                memo=f"Admin debit by {admin_user.character_name}: {reason}",
                transaction_type='admin_adjustment'
            )
        
        if error:
            return None, error
        
        # Create audit log entry
        audit = AuditLog(
            admin_user_id=admin_user.id,
            action='BALANCE_ADJUSTMENT',
            target_user_id=target.id,
            details=f"Amount: {amount}, Reason: {reason}"
        )
        db.session.add(audit)
        db.session.commit()
        
        return transaction, None
        
    except Exception as e:
        db.session.rollback()
        return None, f"Failed to adjust balance: {str(e)}"
