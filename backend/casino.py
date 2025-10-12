"""
Casino game logic - Server-side slot machine engines
"""
import random
from .models import db, User, CasinoConfig
from .transactions import create_transaction


# Slot Machine 1: Glitch Grid (3-Reel Classic)
GLITCH_GRID_SYMBOLS = ['💀', '01', '🔌', '㊙️', '🏢']  # Skull, Binary, Jack, Kanji, Wild
GLITCH_GRID_WILD = '🏢'

GLITCH_GRID_PAYOUTS = {
    ('🏢', '🏢', '🏢'): 100,  # Three wilds - jackpot
    ('💀', '💀', '💀'): 50,
    ('01', '01', '01'): 30,
    ('🔌', '🔌', '🔌'): 20,
    ('㊙️', '㊙️', '㊙️'): 40,
    # Two wilds + any
    ('🏢', '🏢', None): 10,
    # Two of a kind
    ('💀', '💀', None): 5,
    ('01', '01', None): 3,
    ('🔌', '🔌', None): 2,
    ('㊙️', '㊙️', None): 4,
}


# Slot Machine 2: Starlight Smuggler (5-Reel, 3-Row, Multi-line)
STARLIGHT_SYMBOLS = ['🚀', '🗺️', '🔫', '💎', '🌀', '⭐']  # Freighter, Map, Blaster, Gem, Wormhole, Star
STARLIGHT_SCATTER = '🌀'

# Paylines for 5-reel, 3-row grid (9 paylines)
STARLIGHT_PAYLINES = [
    [(0, 0), (0, 1), (0, 2), (0, 3), (0, 4)],  # Top row
    [(1, 0), (1, 1), (1, 2), (1, 3), (1, 4)],  # Middle row
    [(2, 0), (2, 1), (2, 2), (2, 3), (2, 4)],  # Bottom row
    [(0, 0), (1, 1), (2, 2), (1, 3), (0, 4)],  # V shape
    [(2, 0), (1, 1), (0, 2), (1, 3), (2, 4)],  # Inverse V
    [(0, 0), (0, 1), (1, 2), (2, 3), (2, 4)],  # Diagonal down
    [(2, 0), (2, 1), (1, 2), (0, 3), (0, 4)],  # Diagonal up
    [(1, 0), (0, 1), (0, 2), (0, 3), (1, 4)],  # W shape top
    [(1, 0), (2, 1), (2, 2), (2, 3), (1, 4)],  # W shape bottom
]

STARLIGHT_PAYOUTS = {
    ('🚀', 5): 200,
    ('🚀', 4): 50,
    ('🚀', 3): 15,
    ('🗺️', 5): 150,
    ('🗺️', 4): 40,
    ('🗺️', 3): 12,
    ('🔫', 5): 100,
    ('🔫', 4): 30,
    ('🔫', 3): 10,
    ('💎', 5): 250,
    ('💎', 4): 75,
    ('💎', 3): 20,
    ('⭐', 5): 80,
    ('⭐', 4): 25,
    ('⭐', 3): 8,
}


def get_casino_house_account():
    """Get the casino house account"""
    house = User.query.filter_by(account_number='NC-CASA-0000').first()
    if not house:
        raise Exception("Casino house account not found")
    return house


def get_game_config(game_name):
    """Get casino game configuration"""
    config = CasinoConfig.query.filter_by(game_name=game_name).first()
    if not config:
        # Create default config with generous payout
        config = CasinoConfig(game_name=game_name, is_enabled=True, payout_percentage=102.0)
        db.session.add(config)
        db.session.commit()
    return config


def spin_glitch_grid(player_account, bet_amount):
    """
    Spin the Glitch Grid slot machine
    
    Args:
        player_account: Account number or User object
        bet_amount: Amount to bet
    
    Returns:
        dict with spin results
    """
    try:
        # Get player
        if isinstance(player_account, str):
            player = User.query.filter_by(account_number=player_account).first()
        else:
            player = player_account
        
        if not player:
            return {'error': 'Player not found'}
        
        # Check game is enabled
        config = get_game_config('glitch_grid')
        if not config.is_enabled:
            return {'error': 'Game is currently disabled'}
        
        # Process bet
        house = get_casino_house_account()
        transaction, error = create_transaction(
            player, house, bet_amount,
            memo="Glitch Grid bet",
            transaction_type='casino_bet'
        )
        
        if error:
            return {'error': error}
        
        # Generate random spin
        reels = [
            random.choice(GLITCH_GRID_SYMBOLS),
            random.choice(GLITCH_GRID_SYMBOLS),
            random.choice(GLITCH_GRID_SYMBOLS)
        ]
        
        # Calculate winnings
        win_multiplier = calculate_glitch_grid_win(reels)
        
        # Adjust for payout percentage (house edge)
        payout_factor = config.payout_percentage / 100.0
        win_multiplier = int(win_multiplier * payout_factor)
        
        win_amount = bet_amount * win_multiplier
        
        # Process winnings if any
        if win_amount > 0:
            win_transaction, error = create_transaction(
                house, player, win_amount,
                memo=f"Glitch Grid win ({win_multiplier}x)",
                transaction_type='casino_win'
            )
            if error:
                return {'error': f'Failed to process winnings: {error}'}
        
        return {
            'reels': reels,
            'bet': bet_amount,
            'win_multiplier': win_multiplier,
            'win_amount': win_amount,
            'balance': player.balance
        }
        
    except Exception as e:
        return {'error': str(e)}


def calculate_glitch_grid_win(reels):
    """Calculate win multiplier for Glitch Grid"""
    # Check for exact matches
    if tuple(reels) in GLITCH_GRID_PAYOUTS:
        return GLITCH_GRID_PAYOUTS[tuple(reels)]
    
    # Check for wild substitutions
    if reels[0] == reels[1] == GLITCH_GRID_WILD:
        return GLITCH_GRID_PAYOUTS.get(('🏢', '🏢', None), 0)
    
    # Check for two of a kind
    if reels[0] == reels[1]:
        return GLITCH_GRID_PAYOUTS.get((reels[0], reels[0], None), 0)
    
    return 0


def spin_starlight_smuggler(player_account, bet_amount):
    """
    Spin the Starlight Smuggler slot machine
    
    Args:
        player_account: Account number or User object
        bet_amount: Amount to bet (per payline)
    
    Returns:
        dict with spin results
    """
    try:
        # Get player
        if isinstance(player_account, str):
            player = User.query.filter_by(account_number=player_account).first()
        else:
            player = player_account
        
        if not player:
            return {'error': 'Player not found'}
        
        # Check game is enabled
        config = get_game_config('starlight_smuggler')
        if not config.is_enabled:
            return {'error': 'Game is currently disabled'}
        
        # Total bet is per payline * number of paylines
        total_bet = bet_amount * len(STARLIGHT_PAYLINES)
        
        # Process bet
        house = get_casino_house_account()
        transaction, error = create_transaction(
            player, house, total_bet,
            memo="Starlight Smuggler bet",
            transaction_type='casino_bet'
        )
        
        if error:
            return {'error': error}
        
        # Generate 5x3 grid
        grid = [
            [random.choice(STARLIGHT_SYMBOLS) for _ in range(5)],
            [random.choice(STARLIGHT_SYMBOLS) for _ in range(5)],
            [random.choice(STARLIGHT_SYMBOLS) for _ in range(5)]
        ]
        
        # Check for scatter bonus
        scatter_count = sum(row.count(STARLIGHT_SCATTER) for row in grid)
        bonus_spins = 5 if scatter_count >= 3 else 0
        
        # Calculate winnings across all paylines
        total_win_multiplier = 0
        winning_lines = []
        
        for line_idx, payline in enumerate(STARLIGHT_PAYLINES):
            symbols = [grid[row][col] for row, col in payline]
            multiplier = calculate_starlight_win(symbols)
            if multiplier > 0:
                total_win_multiplier += multiplier
                winning_lines.append(line_idx)
        
        # Adjust for payout percentage
        payout_factor = config.payout_percentage / 100.0
        total_win_multiplier = int(total_win_multiplier * payout_factor)
        
        win_amount = bet_amount * total_win_multiplier
        
        # Process winnings
        if win_amount > 0:
            win_transaction, error = create_transaction(
                house, player, win_amount,
                memo=f"Starlight Smuggler win ({total_win_multiplier}x)",
                transaction_type='casino_win'
            )
            if error:
                return {'error': f'Failed to process winnings: {error}'}
        
        return {
            'grid': grid,
            'bet_per_line': bet_amount,
            'total_bet': total_bet,
            'win_multiplier': total_win_multiplier,
            'win_amount': win_amount,
            'winning_lines': winning_lines,
            'scatter_count': scatter_count,
            'bonus_spins': bonus_spins,
            'balance': player.balance
        }
        
    except Exception as e:
        return {'error': str(e)}


def calculate_starlight_win(symbols):
    """Calculate win multiplier for a payline"""
    # Count consecutive matching symbols from left
    if not symbols:
        return 0
    
    first = symbols[0]
    count = 1
    
    for symbol in symbols[1:]:
        if symbol == first:
            count += 1
        else:
            break
    
    # Check payout table
    key = (first, count)
    return STARLIGHT_PAYOUTS.get(key, 0)
