# Profile and Admin Features Update

## Overview
This update adds three major features to the NeoBank & Chrome Slots application:
1. User Profile Management
2. Admin Faction Management
3. CSV User Export

## Features Implemented

### 1. User Profile Management

#### Backend (app.py)
- **Profile Update Endpoint** (`PUT /api/v1/account/profile`)
  - Updates user's faction and profile picture
  - Validates input data
  - Returns updated user information
  
- **Password Change Endpoint** (`PUT /api/v1/account/password`)
  - Requires current password verification
  - Validates new password strength (min 8 characters)
  - Rate limited to 5 attempts per hour
  - Hashes password with bcrypt

#### Database (models.py)
- Added `profile_picture` column to User model (String 255, nullable)
- Updated `to_dict()` method to include profile_picture field

#### Frontend
- **New Profile View** with:
  - Profile picture selector with 16 emoji options (😎, 🤖, 👾, 🦾, 💀, 🔥, ⚡, 💎, 🌟, 🎮, 🎯, 🚀, 🔫, 💊, 🌀, 👁️)
  - Interactive emoji grid with hover effects
  - Faction dropdown selector (None, CorpSec, Runners, Syndicate, Technocrats)
  - Password change form with validation
  - Account information display grid showing:
    - Character Name
    - Account Number
    - Current Balance
    - Member Since date

### 2. Admin Faction Management

#### Backend (admin.py)
- **List Factions Endpoint** (`GET /api/admin/factions/list`)
  - Returns all factions with statistics:
    - User count per faction
    - Total balance per faction
  - Uses SQLAlchemy aggregation (func.count, func.sum)

- **Add Faction Credits Endpoint** (`POST /api/admin/factions/<faction>/add-credits`)
  - Bulk adds credits to all users in a faction
  - Requires amount and reason
  - Creates audit log entry
  - Returns number of users affected

#### Frontend
- **Faction Management Panel** in Admin view:
  - Displays all factions with user counts and balances
  - "Refresh Factions" button
  - Individual "Add Credits" button for each faction
  - Modal dialog for credit distribution:
    - Amount input
    - Reason field
    - Confirm/Cancel buttons

### 3. CSV User Export

#### Backend (admin.py)
- **Export Users Endpoint** (`GET /api/admin/users/export`)
  - Generates CSV file with all user data
  - Columns: Character Name, Account Number, Balance, Faction, Is Admin, Created At
  - Uses in-memory StringIO for efficiency
  - Sets proper Content-Disposition header for download
  - Creates audit log entry

#### Frontend
- **Export Section** in Admin view:
  - Description text
  - Download button with icon (📥)
  - Triggers browser download automatically
  - Filename format: `users_export_YYYY-MM-DD.csv`

## API Endpoints

### User Endpoints
```
PUT /api/v1/account/profile
Body: { faction: string, profile_picture: string }
Returns: { message: string, user: object }

PUT /api/v1/account/password
Body: { current_password: string, new_password: string }
Returns: { message: string }
Rate Limit: 5 requests per hour
```

### Admin Endpoints
```
GET /api/admin/factions/list
Returns: { factions: [{ faction: string, user_count: int, total_balance: float }] }

POST /api/admin/factions/<faction>/add-credits
Body: { amount: float, reason: string }
Returns: { message: string, users_affected: int }

GET /api/admin/users/export
Returns: CSV file download
```

## Database Changes

### User Model (models.py)
```python
profile_picture = db.Column(db.String(255), nullable=True)
```

## Frontend JavaScript Functions

### Profile Management (app.js)
- `selectProfilePicture(emoji)` - Updates selected profile picture
- `updateProfile()` - Saves profile changes to backend
- `changePassword()` - Validates and updates password

### Faction Management (app.js)
- `loadFactions()` - Fetches faction statistics
- `openAddFactionCredits(faction)` - Opens modal for credit distribution
- `addFactionCredits()` - Submits bulk credit addition

### CSV Export (app.js)
- `exportUsersCSV()` - Triggers CSV download from backend

## CSS Styling (cyberpunk.css)

### New Classes Added
- `.profile-picture-display` - Container for profile picture section
- `.current-profile-pic` - Large display of current emoji (120px, glowing)
- `.emoji-grid` - 8-column grid for emoji selection
- `.emoji-option` - Individual emoji buttons with hover effects
- `.account-info-grid` - Responsive grid for account information
- `.info-item` - Individual info card with label/value
- `.faction-list` - Grid layout for faction cards
- `.faction-card` - Individual faction display with hover effects
- `.faction-header` - Faction name and stats container
- `.modal` - Full-screen modal backdrop with blur
- `.modal-content` - Modal dialog with slide-in animation
- `.button-group` - Flex container for action buttons

### Animations
- Emoji hover: scale(1.2) with glow
- Faction card hover: slide right with border glow
- Modal entrance: slide-in with fade

## Security Features

1. **Password Change**
   - Requires current password verification
   - Minimum 8 characters for new password
   - Rate limited to prevent brute force
   - Passwords hashed with bcrypt

2. **Admin Operations**
   - All faction/export endpoints require admin authentication
   - Audit logs created for bulk operations
   - JWT token required for all operations

3. **Data Validation**
   - Input sanitization on all endpoints
   - SQL injection prevention via SQLAlchemy ORM
   - XSS prevention via Vue.js escaping

## User Experience Improvements

1. **Profile Management**
   - Visual emoji selection (no typing needed)
   - Instant profile picture update
   - Clear password requirements
   - Confirmation matching for password change

2. **Admin Faction Tools**
   - Quick faction overview with statistics
   - Bulk operations for efficiency
   - Modal confirmation prevents accidents
   - Real-time feedback with toast notifications

3. **Data Export**
   - One-click CSV download
   - Automatic filename with date
   - No server file storage (in-memory generation)
   - Includes all relevant user data

## Testing Checklist

### Profile Features
- [ ] Select profile picture from emoji grid
- [ ] Update faction via dropdown
- [ ] Change password with valid current password
- [ ] Verify password validation (min 8 chars)
- [ ] Test password mismatch handling
- [ ] Check profile picture persists after logout/login

### Faction Management
- [ ] Load faction list shows all factions
- [ ] User counts accurate per faction
- [ ] Total balances calculated correctly
- [ ] Add credits updates all faction users
- [ ] Modal opens/closes properly
- [ ] Audit log created for bulk operations

### CSV Export
- [ ] Download button triggers file download
- [ ] CSV contains all expected columns
- [ ] Data matches database records
- [ ] Filename includes current date
- [ ] Audit log created for export

## Files Modified

### Backend
- `backend/models.py` - Added profile_picture column
- `backend/app.py` - Added profile and password endpoints
- `backend/admin.py` - Added faction and export endpoints

### Frontend
- `frontend/index.html` - Added Profile view, faction management UI, export button
- `frontend/js/app.js` - Added 7 new methods and data properties
- `frontend/css/cyberpunk.css` - Added ~150 lines of new styles

## Database Migration

To apply the new profile_picture column to existing database:

```sql
ALTER TABLE users ADD COLUMN profile_picture VARCHAR(255);
```

Or restart containers with fresh database (development only):
```bash
podman-compose down -v
podman-compose up -d
```

## Access Information

- **Application URL**: http://localhost:8080
- **Admin User**: admin / admin123
- **Database**: PostgreSQL on localhost:5432

## Next Steps

1. Test all features thoroughly
2. Add unit tests for new endpoints
3. Consider additional profile fields (bio, avatar upload)
4. Add faction leaderboard view
5. Implement more export formats (JSON, Excel)

## Notes

- Profile pictures are stored as emoji Unicode strings
- CSV export is in-memory (no server file storage)
- Faction operations create audit trail
- Password changes invalidate current session tokens (optional enhancement)
