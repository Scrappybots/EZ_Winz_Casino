# Admin Features Documentation

## Overview
This document describes the administrative features available in the NEOTROPOLIS 2025 banking and casino system.

## New Features Implemented

### 1. New User Starting Balance: $1000

**Description**: All newly registered users automatically receive ¤1,000 as a welcome bonus to start using the banking and casino services.

**Implementation Details**:
- Default balance set in User model: `balance = db.Column(db.Float, default=1000.0)`
- Applied during user registration in `register_user()` function
- Allows new users to immediately:
  - Send transfers to other accounts
  - Play casino games
  - Experience the full platform without manual funding

**Example**:
```python
# New user registration
user = User(
    character_name="newplayer",
    password_hash=hash_password("password"),
    account_number=generate_account_number(),
    faction="Runners",
    balance=1000.0  # Welcome bonus!
)
```

---

### 2. Grant/Revoke Admin Status

**Description**: Superadmins can promote regular users to admin status or demote existing admins through the admin control panel.

**Features**:
- ✅ Toggle admin privileges with one click
- ✅ Visual confirmation dialogs before changes
- ✅ Admin badge displayed for users with admin status
- ✅ Audit logging of all admin status changes
- ✅ Protection: Admins cannot modify their own admin status

**Access**: 
Admin Control Panel → User Lookup → Search for user → Click "MAKE ADMIN" or "REVOKE ADMIN"

**API Endpoint**:
```
POST /api/admin/users/{account_number}/toggle-admin
Authorization: Bearer <admin_token>
```

**Response Example**:
```json
{
    "message": "Admin status granted",
    "user": {
        "account_number": "NC-1234-ABCD",
        "character_name": "newadmin",
        "is_admin": true,
        "balance": 1000.0
    }
}
```

**Security Features**:
1. Requires existing admin authentication (JWT token)
2. Prevents self-modification (cannot revoke own admin)
3. Full audit trail in `audit_logs` table
4. Confirmation dialog before action

**Audit Log Entry**:
```
Action: TOGGLE_ADMIN
Details: "Admin status granted to newadmin"
Timestamp: 2025-10-12 02:22:45
Admin User ID: 3 (admin account)
Target User ID: 5 (newadmin account)
```

---

## Admin Panel UI Improvements

### User Card Display
Each user in search results now shows:
- **Character Name** (bold)
- **Account Number** (gray text)
- **Admin Badge** (colorful gradient badge if user is admin)
- **Current Balance**
- **Action Buttons**:
  - "ADJUST BALANCE" (blue) - Modify user's account balance
  - "MAKE ADMIN" (green) - Grant admin privileges
  - "REVOKE ADMIN" (yellow/orange) - Remove admin privileges

### Visual Indicators
- **Admin Badge**: Cyan-magenta gradient badge showing "ADMIN" status
- **Button Colors**:
  - 🟢 Green = "MAKE ADMIN" (positive action)
  - 🟡 Orange = "REVOKE ADMIN" (warning action)
  - 🔵 Blue = "ADJUST BALANCE" (neutral action)

---

## Usage Examples

### Example 1: Creating a New User
```bash
# User registers through frontend
POST /api/v1/auth/register
{
    "character_name": "runner_zero",
    "password": "securepass123",
    "faction": "Runners"
}

# Response includes starting balance
{
    "user": {
        "account_number": "NC-R0Z3-7X9K",
        "character_name": "runner_zero",
        "balance": 1000.0,  # ← Automatic $1000 welcome bonus
        "is_admin": false
    }
}
```

### Example 2: Promoting User to Admin
1. Admin logs into http://localhost:8080
2. Clicks **⚙️ ADMIN** tab
3. Searches for user "runner_zero"
4. Clicks **MAKE ADMIN** button (green)
5. Confirms action in dialog
6. User now has admin privileges and can access admin panel

### Example 3: Revoking Admin Access
1. Admin searches for user with admin status
2. User card shows colorful "ADMIN" badge
3. Clicks **REVOKE ADMIN** button (orange)
4. Confirms action
5. Admin status removed, user returns to normal privileges

---

## Database Schema Updates

### Users Table
```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    character_name VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    account_number VARCHAR(20) UNIQUE NOT NULL,
    faction VARCHAR(50),
    balance FLOAT DEFAULT 1000.0,  -- Changed from 0.0 to 1000.0
    is_admin BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW()
);
```

### Audit Logs Table
New action type:
- `TOGGLE_ADMIN` - Records all admin status changes

---

## Security Considerations

### Admin Status Management
1. **Authentication Required**: Only existing admins can grant/revoke admin status
2. **Self-Protection**: Admins cannot accidentally remove their own admin privileges
3. **Audit Trail**: All admin privilege changes are logged with:
   - Who made the change (admin user ID)
   - Who was affected (target user ID)
   - What happened (granted/revoked)
   - When it happened (timestamp)
   - Detailed message

### Starting Balance
- $1000 is generous enough for testing but not excessive
- Prevents abuse scenarios where users create multiple accounts for free money
- Can be adjusted in code if needed:
  - Increase for more generous welcome bonus
  - Decrease for more conservative approach
  - Set to 0 for "earn your way" gameplay

---

## Testing Checklist

### New User Registration
- [x] New users receive exactly $1000 starting balance
- [x] Balance is immediately available for transactions
- [x] Balance is correctly stored in database
- [x] Balance displays correctly in UI

### Admin Status Toggle
- [x] Admin can grant admin status to regular users
- [x] Admin can revoke admin status from other admins
- [x] Admin cannot modify own admin status
- [x] UI shows admin badge for admin users
- [x] Confirmation dialogs appear before changes
- [x] Success/error messages display correctly
- [x] Audit logs record all changes
- [x] API endpoint requires authentication
- [x] Changes persist after page reload

---

## Future Enhancements

### Potential Improvements
1. **Tiered Admin Levels**: Super Admin, Moderator, Support
2. **Temporary Admin**: Time-limited admin access
3. **Permission Granularity**: Specific admin capabilities (casino only, users only, etc.)
4. **Admin Activity Dashboard**: Visual analytics of admin actions
5. **Bulk User Management**: Grant/revoke admin for multiple users
6. **Welcome Bonus Customization**: UI to configure starting balance
7. **Referral Bonuses**: Extra credits for inviting friends

---

## API Reference

### Toggle Admin Status
**Endpoint**: `POST /api/admin/users/{account_number}/toggle-admin`

**Headers**:
```
Authorization: Bearer <jwt_token>
Content-Type: application/json
```

**Path Parameters**:
- `account_number` (string): User's account number (e.g., "NC-1234-ABCD")

**Response 200 OK**:
```json
{
    "message": "Admin status granted",
    "user": {
        "account_number": "NC-1234-ABCD",
        "character_name": "username",
        "is_admin": true,
        "balance": 1000.0,
        "faction": "Runners",
        "created_at": "2025-10-12T02:22:33.471908"
    }
}
```

**Error 403 Forbidden** (trying to modify own status):
```json
{
    "error": "Cannot modify your own admin status"
}
```

**Error 404 Not Found** (user doesn't exist):
```json
{
    "error": "User not found"
}
```

---

## Changelog

### Version 1.2.0 (2025-10-11)
- ✅ Added $1000 starting balance for new users
- ✅ Implemented toggle admin status feature
- ✅ Added admin badge UI indicator
- ✅ Created audit logging for admin changes
- ✅ Updated admin panel with new action buttons
- ✅ Added confirmation dialogs for admin actions
- ✅ Implemented security checks (self-protection)

### Version 1.1.0 (Previous)
- Casino odds configuration panel
- JWT authentication fix
- PostgreSQL migration
- Admin panel foundation

---

## Support

For issues or questions:
1. Check audit logs for admin action history
2. Review PostgreSQL database for user records
3. Check application logs for errors
4. Verify JWT token is valid for admin operations

**Database Query Examples**:
```sql
-- View all admin users
SELECT character_name, account_number, is_admin, balance 
FROM users WHERE is_admin = true;

-- View recent admin status changes
SELECT * FROM audit_logs 
WHERE action = 'TOGGLE_ADMIN' 
ORDER BY timestamp DESC LIMIT 10;

-- Count users by admin status
SELECT is_admin, COUNT(*) 
FROM users GROUP BY is_admin;
```
