# OAuth Error 400 Fix - "Missing required parameter: redirect_uri"

## Problem
You're getting "Error 400: invalid_request - Missing required parameter: redirect_uri" when trying to authenticate with Gmail.

## Root Cause
The OAuth flow wasn't properly configured with a redirect URI parameter.

## ✅ Solution Applied

I've fixed the code to properly handle the redirect URI. The issue was:

1. **Missing redirect_uri parameter** in the OAuth flow
2. **Incorrect flow configuration** for out-of-band authentication

## 🔧 What Was Fixed

### Updated Gmail Service
- Added explicit `flow.redirect_uri = 'urn:ietf:wg:oauth:2.0:oob'`
- Proper `access_type='offline'` and `prompt='consent'` parameters
- Simplified client configuration

### Google Cloud Console Requirements

**Important:** Make sure your OAuth client in Google Cloud Console is configured as:

1. **Application type:** Desktop application
2. **Authorized redirect URIs:** Should include `urn:ietf:wg:oauth:2.0:oob`

If you created it as "Web application", you need to either:
- Create a new "Desktop application" OAuth client, OR
- Add `urn:ietf:wg:oauth:2.0:oob` to authorized redirect URIs

## 🧪 Test the Fix

### Option 1: Quick Test
```bash
# Test OAuth configuration
python test_oauth.py
```

### Option 2: Full Authentication
```bash
# Clean up old tokens
rm -f token.json

# Test authentication
python auth_gmail.py
```

## 📋 Expected Flow Now

1. **Script generates proper OAuth URL** with redirect_uri parameter
2. **You open URL in browser** - should work without 400 error
3. **Complete Google authorization**
4. **Copy authorization code** from the success page
5. **Paste code in terminal** - token gets saved

## 🚨 If Still Getting Errors

### Check Your OAuth Client Type
```bash
# Go to: https://console.cloud.google.com/apis/credentials
# Find your OAuth client
# Check: Application type should be "Desktop application"
```

### Create New OAuth Client (if needed)
1. Go to Google Cloud Console → APIs & Services → Credentials
2. Click "Create Credentials" → "OAuth 2.0 Client ID"
3. Choose "Desktop application"
4. Name it "Gmail Verification Bot"
5. Copy the new Client ID and Secret to your .env file

## 🎯 The Fix Explained

**Before:** OAuth flow was missing the redirect_uri parameter
**After:** Explicitly set `flow.redirect_uri = 'urn:ietf:wg:oauth:2.0:oob'`

This tells Google to use "out-of-band" authentication, which shows the authorization code on a webpage for manual copying - perfect for server environments!
