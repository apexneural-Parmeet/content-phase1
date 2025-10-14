# .env to Credentials Migration

## Overview

Automatically load your existing `.env` credentials into the credential management system, making them active for all posts.

## How It Works

### Automatic Migration (First Visit)
1. **Visit** `/connections` page
2. **System checks** if any credentials are saved
3. **If no credentials found**, automatically loads from `.env`
4. **Success message** shows which platforms were loaded
5. **Credentials are now active** and used for all posts

### Manual Migration
1. **Click** "Load from .env" button in the header
2. **System imports** all credentials from `.env` file
3. **Overrides** any existing saved credentials
4. **Refreshes** connection status

## Supported Platforms

### Facebook
**Environment Variables:**
- `FACEBOOK_PAGE_ACCESS_TOKEN`
- `FACEBOOK_PAGE_ID`

### Instagram
**Environment Variables:**
- `INSTAGRAM_ACCESS_TOKEN`
- `INSTAGRAM_ACCOUNT_ID`

### Twitter/X
**Environment Variables:**
- `TWITTER_API_KEY`
- `TWITTER_API_SECRET`
- `TWITTER_ACCESS_TOKEN`
- `TWITTER_ACCESS_TOKEN_SECRET`
- `TWITTER_BEARER_TOKEN` (optional)

### Reddit
**Environment Variables:**
- `REDDIT_CLIENT_ID`
- `REDDIT_CLIENT_SECRET`
- `REDDIT_USERNAME`
- `REDDIT_PASSWORD`
- `REDDIT_USER_AGENT` (optional, defaults to "SocialHub Bot v1.0")

### Telegram
**Environment Variables:**
- `TELEGRAM_BOT_TOKEN`
- `TELEGRAM_CHANNEL_ID` (optional)

## API Endpoint

### POST `/api/credentials/migrate-from-env`

**Description:** Migrates all credentials from environment variables to credential storage.

**Response:**
```json
{
  "success": true,
  "message": "Migrated 3 platform(s) from environment variables",
  "migrated": ["facebook", "twitter", "reddit"],
  "skipped": ["instagram", "telegram"]
}
```

**Behavior:**
- Reads credentials from `.env` file (via environment variables)
- Saves to `user_credentials.json`
- Only migrates platforms with complete credentials
- Skips platforms with missing required fields

## User Experience

### Before Migration
```
Status: "Not Configured" (Red badge)
System: Using .env variables (if present)
Management: Edit .env file manually
```

### After Migration
```
Status: "Active & Connected" (Green badge)
System: Using saved credentials
Management: Edit via UI (view/edit mode)
Banner: "✅ Credentials Active - System is using saved credentials"
```

## Benefits

✅ **One-Time Setup** - Automatically loads existing credentials  
✅ **No Manual Entry** - Uses what you already have in `.env`  
✅ **Visual Management** - See and edit credentials in UI  
✅ **Backward Compatible** - Falls back to `.env` if needed  
✅ **Easy Updates** - Click "Edit Credentials" to update  
✅ **Clear Status** - Know exactly which platforms are active  

## Migration Flow

```
.env file
    ↓
[Visit /connections]
    ↓
Auto-check for credentials
    ↓
If none found → Load from .env
    ↓
Save to user_credentials.json
    ↓
✅ Credentials Active
    ↓
All posts use saved credentials
```

## Code Implementation

### Auto-Migration on Page Load
```javascript
useEffect(() => {
  fetchConnectionStatus()
  fetchAllCredentials()
  checkAndMigrateEnvCredentials() // Auto-migrate
}, [])

const checkAndMigrateEnvCredentials = async () => {
  // Check if any credentials exist
  const hasAnyCredentials = ...
  
  // If none, migrate from .env
  if (!hasAnyCredentials) {
    await fetch('/api/credentials/migrate-from-env', { method: 'POST' })
  }
}
```

### Manual Migration Button
```javascript
<button onClick={handleMigrateFromEnv}>
  Load from .env
</button>
```

### Backend Migration Logic
```python
@router.post("/api/credentials/migrate-from-env")
async def migrate_credentials_from_env():
    migrated = []
    
    # Facebook
    if settings.FACEBOOK_ACCESS_TOKEN and settings.FACEBOOK_PAGE_ID:
        update_platform_credentials("facebook", {
            "access_token": settings.FACEBOOK_ACCESS_TOKEN,
            "page_id": settings.FACEBOOK_PAGE_ID
        })
        migrated.append("facebook")
    
    # ... (repeat for other platforms)
    
    return {
        "success": True,
        "migrated": migrated
    }
```

## Priority Order

The system now uses credentials in this order:

1. **Saved credentials** (`user_credentials.json`) - **Highest priority**
2. **Environment variables** (`.env` file) - **Fallback**
3. **Error** - If neither exists

## Files Modified

- `app/routes/credentials.py` - Added migration endpoint
- `app/config.py` - Added FACEBOOK_PAGE_ID, TWITTER_BEARER_TOKEN, TELEGRAM_CHANNEL_ID
- `frontend/src/pages/ConnectionsPage.jsx` - Auto-migration + manual button
- `frontend/src/pages/ConnectionsPage.css` - Button styling

## Example Scenarios

### Scenario 1: New User with .env
```
1. User has credentials in .env
2. Visits /connections for first time
3. Sees: "Automatically loaded credentials from .env for: facebook, twitter"
4. All platforms show "Active & Connected"
5. Can now manage via UI
```

### Scenario 2: Existing User
```
1. User already has saved credentials
2. Visits /connections
3. No auto-migration (credentials already exist)
4. Can click "Load from .env" to re-import
```

### Scenario 3: No Credentials
```
1. User has no .env credentials
2. Visits /connections
3. No auto-migration (nothing to import)
4. Manually enters credentials via UI
```

## Testing

### Test Auto-Migration
1. Delete `user_credentials.json` if it exists
2. Ensure `.env` has credentials
3. Visit `/connections`
4. Should see success message
5. Platforms should show "Active & Connected"

### Test Manual Migration
1. Have credentials in `.env`
2. Click "Load from .env" button
3. Should see success message with platform names
4. Credentials should be active

### Verify API
```bash
curl -X POST http://localhost:8000/api/credentials/migrate-from-env
```

## Result

✅ Credentials from `.env` automatically loaded  
✅ All platforms configured and active  
✅ System uses saved credentials for all posts  
✅ Easy to update via UI  
✅ Clear visual feedback  

**No more manual credential entry - just load from .env and you're done!**

---

**Created**: October 14, 2025  
**Version**: 1.0.0  
**Status**: Production Ready

