# API Key Behavior and Document Store Access

## Overview

This application allows users to provide their own Gemini API keys for RAG (Retrieval-Augmented Generation) functionality. Understanding how API keys interact with document stores is crucial for managing your knowledge base.

## How It Works

### One Store Per User Per API Key

Each user's document store is **tied to the API key used to create it**. This is a limitation of the Gemini File Search API, not our application.

```
User ID: 12345 + API Key A → Document Store A (contains docs uploaded with Key A)
User ID: 12345 + API Key B → Document Store B (contains docs uploaded with Key B)
```

### What Happens When You Switch API Keys

**Scenario: You upload documents with API Key A, then switch to API Key B**

1. ✅ Your old documents remain in Gemini (Store A)
2. ⚠️ **You lose access to those documents** (API Key B cannot access Store A)
3. ✅ A new empty store (Store B) is created automatically
4. ⚠️ You'll need to re-upload your documents to Store B

**Scenario: You switch back to API Key A later**

1. ⚠️ A **new** empty store is created (not the original Store A)
2. ⚠️ Original documents are still inaccessible
3. 💡 This is because the original store was marked inactive when you switched away

## API Key Identifier

In the Store Info section, you'll see an **API Key Identifier** (e.g., `a1b2c3d4`). This is the first 8 characters of your API key's hash.

**Use this to:**
- ✅ Verify which API key owns your current store
- ✅ Identify if you're using a different API key than before
- ✅ Troubleshoot permission errors

**Example:**
```json
{
  "api_key_identifier": "a1b2c3d4",
  "document_count": 5,
  "total_size_bytes": 1048576
}
```

If you see a different identifier after changing API keys, you're now using a different store.

## Best Practices

### ✅ DO: Stick with One API Key

**Recommended: Choose one API key and use it consistently**

- Keep your API key saved securely (password manager, environment variable)
- Don't switch between multiple API keys
- Your documents will remain accessible as long as you use the same key

### ✅ DO: Export Important Documents

Before switching API keys:
1. Download/backup any critical documents
2. Export important data from your knowledge base
3. Plan to re-upload to the new store

### ❌ DON'T: Frequently Switch API Keys

**Each switch means:**
- Loss of access to previous documents
- Need to re-upload everything
- Potential confusion about which store is active

## Permission Errors

### "403 PERMISSION_DENIED" Error

**Error message:**
```
You do not have permission to access the file search store
user-xxx-st-xxx or it may not exist.
```

**Cause:** You're trying to access a store created with a different API key.

**Solution:**
1. Check your current API key identifier in Store Info
2. Verify you're using the intended API key
3. If you switched keys, you'll need to re-upload your documents

## Technical Details

### How Stores Are Created

```python
# When you upload your first document
1. System checks: "Does this user have an active store?"
2. If yes: "Was it created with the current API key?"
   - If API keys match → Use existing store ✅
   - If API keys don't match → Mark old store inactive, create new store ⚠️
3. If no: Create new store ✅
```

### Why This Design?

**Gemini API Limitation:**
- File Search Stores are scoped to API keys at the Google Cloud level
- No cross-key access is supported
- This ensures security and billing isolation

**Our Implementation:**
- One active store per user (at any given time)
- Automatic store creation when API key changes
- Old stores marked inactive (not deleted) for audit purposes

## Alternatives

If you want **consistent access without API key concerns**, consider:

### Option 1: Server-Side API Key (Recommended for Production)

Ask your administrator to configure a server-side Gemini API key:
- All users share one API key (managed by server)
- No user-provided keys needed
- Consistent access for all users
- No data loss when users change settings

### Option 2: Google Cloud Service Account (Enterprise)

For enterprise deployments:
- Use Google Cloud service accounts
- Implement granular permission controls
- Share stores across multiple keys via IAM policies

## Summary

| Scenario | Result |
|----------|--------|
| First upload with API Key A | ✅ Store A created |
| Upload more docs with API Key A | ✅ Added to Store A |
| Switch to API Key B | ⚠️ Store A inactive, Store B created (empty) |
| Upload docs with API Key B | ✅ Added to Store B |
| Switch back to API Key A | ⚠️ Store B inactive, Store C created (empty) |
| Original documents | ❌ Still in Store A but inaccessible |

**Bottom line: Stick with one API key for consistent access to your documents.**

## Questions?

- **Q: Can I recover documents from an inactive store?**
  A: No, not through the application. The store is still in Gemini but inaccessible without the original API key.

- **Q: What if I lost my API key?**
  A: You'll need to re-upload your documents with a new API key.

- **Q: Can I merge multiple stores?**
  A: No, this isn't supported by the Gemini File Search API.

- **Q: How much does this cost?**
  A: Each API key has its own quota and billing. Creating multiple stores doesn't incur extra costs, but you're paying for document indexing in each store separately.

---

**Last Updated:** December 2025
**Related Documentation:**
- [Gemini File Search API](https://ai.google.dev/gemini-api/docs/file-search)
- [Document Upload Guide](./DOCUMENT_UPLOAD.md)
