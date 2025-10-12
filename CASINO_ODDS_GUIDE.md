# 🎰 Casino Odds Configuration Guide

## Overview
The EZ Winz Casino uses a configurable Return-To-Player (RTP) percentage system that allows admins to control how generous the slot machines are to players.

## Understanding RTP (Return To Player)

**RTP** is the percentage of all wagered money that a slot machine pays back to players over time.

### RTP Reference Guide:

| RTP Range | Category | Description | Visual Indicator |
|-----------|----------|-------------|------------------|
| 50-84% | 🔴 Very Tight | Much less than real casinos, house wins heavily | Red |
| 85-97% | 🟡 Standard Casino | Typical real-world casino range | Yellow |
| 98-104% | 🟢 Player Friendly | More generous than real casinos | Green |
| 105%+ | 💚 Very Generous | Players profit over time (house loses) | Cyan (pulsing) |

### Real Casino Comparisons:
- **Typical Las Vegas Slots**: 85-96% RTP
- **Best Real Casinos**: 96-98% RTP
- **Online Slots (good)**: 95-97% RTP
- **Penny Slots**: 85-90% RTP

## Default Configuration

**Current Default: 102% RTP** - Player Friendly

Since this is fictional money, the default is set to be more generous than real casinos. This gives players a slight edge while still maintaining exciting gameplay.

## Adjusting Odds via Admin Panel

### Accessing Casino Controls:
1. Log in as an admin user
2. Click the **⚙️ ADMIN** tab
3. Scroll to **CASINO ODDS CONFIGURATION**

### Available Controls:
- **Enable/Disable**: Toggle individual games on/off
- **RTP Slider**: Adjust from 50% to 150%
  - Real-time visual feedback shows category
  - Changes apply immediately

### Recommended Settings:

#### For Fun, Player-Friendly Gameplay:
- **Glitch Grid**: 100-105% RTP
- **Starlight Smuggler**: 100-105% RTP

#### For Balanced Gameplay (like real casinos):
- **Glitch Grid**: 94-96% RTP
- **Starlight Smuggler**: 94-96% RTP

#### To Slow Down Winners (tighter):
- **Glitch Grid**: 85-92% RTP
- **Starlight Smuggler**: 85-92% RTP

#### For Maximum Generosity (house loses):
- **Glitch Grid**: 110-120% RTP
- **Starlight Smuggler**: 110-120% RTP

## How It Works

The RTP percentage affects the casino's payout multiplier:
```
Actual Payout = Base Payout × (RTP / 100)
```

For example, with 102% RTP:
- A win that would normally pay 100¤ pays 102¤
- Over time, the casino pays out 102% of what players bet
- The house slowly loses money (intentionally, for fun!)

With 90% RTP:
- A win that would normally pay 100¤ pays 90¤
- Over time, the casino keeps 10% of all bets
- Players still win sometimes, but house has edge

## Monitoring & Adjustments

### When to Increase RTP:
- Players complaining about losing too much
- You want more exciting, frequent wins
- Economic stimulus needed in the game

### When to Decrease RTP:
- Players winning too much money
- Casino house balance depleting rapidly
- Need to create more challenging gameplay

## Technical Details

### Database:
```sql
SELECT game_name, payout_percentage 
FROM casino_config;
```

### API Endpoint:
```
PUT /api/admin/casino/config/{game_name}
Authorization: Bearer {admin_token}
Body: {
  "payout_percentage": 102.0,
  "is_enabled": true
}
```

### Files Modified:
- `backend/models.py` - CasinoConfig default RTP
- `backend/app.py` - init_database() default values
- `backend/casino.py` - get_game_config() defaults
- `frontend/index.html` - Admin UI controls
- `frontend/css/cyberpunk.css` - Visual indicators

## Current Games

### 1. Glitch Grid (3-Reel Classic)
- **Type**: Simple 3-reel slot
- **Symbols**: 💀 01 🔌 ㊙️ 🏢
- **Current RTP**: 102%
- **Jackpot**: 🏢🏢🏢 = 100x bet

### 2. Starlight Smuggler (5-Reel Multi-line)
- **Type**: Advanced 5-reel, 9-payline slot
- **Symbols**: 🚀 🗺️ 🔫 💎 🌀 ⭐
- **Current RTP**: 102%
- **Jackpot**: 💎💎💎💎💎 = 250x bet

## Tips for Admins

1. **Start Generous**: Begin with 102-105% RTP to build player confidence
2. **Monitor House Balance**: Check casino house account regularly
3. **Adjust Gradually**: Make small 1-2% changes rather than large swings
4. **Communicate Changes**: Let players know when you adjust odds
5. **Test Before Committing**: Try different percentages in test scenarios

## Emergency Reset

If you need to reset to defaults:
```sql
UPDATE casino_config 
SET payout_percentage = 102.0 
WHERE game_name IN ('glitch_grid', 'starlight_smuggler');
```

Or rebuild the container with `podman compose up --build -d`

---

**Remember**: This is fictional money for fun! Being generous with odds makes for more enjoyable gameplay than trying to maximize house profits. 🎮💰
