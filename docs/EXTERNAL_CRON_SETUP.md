# External Cron Service Setup Guide
## Solution 2: Reliable 30-Minute Auto-Update

### Problem
GitHub Actions cron schedule (`*/30 * * * *`) experiences delays during high load periods:
- Expected: Run every 30 minutes
- Actual: Can delay 1-7 hours
- Example: Last run 05:16, next expected 05:46, actual run 12:18 (7-hour gap)

### Solution: cron-job.org External Service

**Why External Cron?**
- ✅ Reliable execution (99.9% uptime)
- ✅ Independent of GitHub Actions queue
- ✅ Guaranteed 30-minute intervals
- ✅ Free tier: Up to 50 jobs
- ✅ Email notifications on failure

---

## Step-by-Step Setup Instructions

### Step 1: Create GitHub Personal Access Token (PAT)

1. Go to GitHub Settings: https://github.com/settings/tokens
2. Click **"Generate new token"** → **"Generate new token (classic)"**
3. Set token name: `cron-job-org-qip-dashboard`
4. Set expiration: **90 days** (or longer)
5. Select scopes:
   - ✅ **`actions`** (full access to GitHub Actions workflows)
6. Click **"Generate token"**
7. **CRITICAL**: Copy token immediately (only shown once)
   - Format: `ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`
8. Save token securely (password manager recommended)

---

### Step 2: Register on cron-job.org

1. Visit: https://cron-job.org/en/
2. Click **"Sign up"** (free account)
3. Verify email address
4. Login to dashboard

---

### Step 3: Create Cron Job

1. Click **"Create cronjob"** button

2. **Basic Settings**:
   - **Title**: `QIP Dashboard Auto-Update (GitHub Actions Trigger)`
   - **Address**:
     ```
     https://api.github.com/repos/moonkaicuzui/qip-dashboard/actions/workflows/auto-update-enhanced.yml/dispatches
     ```

3. **Schedule**:
   - Select **"Every 30 minutes"**
   - Alternative: Custom expression `*/30 * * * *`

4. **Advanced Settings** (click to expand):
   - **Request method**: `POST`
   - **Request body**:
     ```json
     {"ref": "main"}
     ```
   - **Headers** (click "Add header"):
     ```
     Header 1:
       Name: Authorization
       Value: Bearer YOUR_GITHUB_PAT_TOKEN_HERE

     Header 2:
       Name: Accept
       Value: application/vnd.github+json

     Header 3:
       Name: X-GitHub-Api-Version
       Value: 2022-11-28

     Header 4:
       Name: Content-Type
       Value: application/json
     ```

   **IMPORTANT**: Replace `YOUR_GITHUB_PAT_TOKEN_HERE` with your actual PAT from Step 1

5. **Notification Settings**:
   - ✅ Enable **"On failure"** email notifications
   - ✅ Enable **"On success"** (first few times for verification)

6. **Save Configuration**:
   - Click **"Create cronjob"**
   - Job will start running immediately

---

### Step 4: Verification

**Immediate Verification** (within 2 minutes):
1. Go to cron-job.org dashboard
2. Check job status: Should show ✅ **"Success"** with HTTP 204 response
3. Go to GitHub Actions: https://github.com/moonkaicuzui/qip-dashboard/actions
4. Verify new workflow run appeared (triggered by API)

**30-Minute Verification**:
1. Wait 30 minutes
2. Check cron-job.org execution log (should run again)
3. Verify GitHub Actions shows 2nd execution
4. Dashboard should update with latest data

**Dashboard Verification**:
1. Open: https://moonkaicuzui.github.io/qip-dashboard/selector.html
2. Check **"마지막 업데이트"** timestamp
3. Should update every 30 minutes (±2 minutes tolerance)

---

## Expected Results

### Before (GitHub Actions Cron Only)
```
04:34 - Auto-update ✅
05:16 - Auto-update ✅
... 7 hours of silence ...
12:18 - Auto-update ✅ (should have run at 05:46, 06:16, 06:46...)
```

### After (External Cron + GitHub Actions)
```
04:34 - Auto-update ✅
05:04 - Auto-update ✅ (cron-job.org)
05:34 - Auto-update ✅ (cron-job.org)
06:04 - Auto-update ✅ (cron-job.org)
... continues reliably every 30 minutes ...
```

---

## Troubleshooting

### Issue: HTTP 401 Unauthorized
**Cause**: Invalid or expired GitHub PAT
**Fix**:
1. Regenerate PAT in GitHub Settings
2. Update cron-job.org header with new token

### Issue: HTTP 404 Not Found
**Cause**: Incorrect workflow file name or repository path
**Fix**: Verify URL:
```
https://api.github.com/repos/moonkaicuzui/qip-dashboard/actions/workflows/auto-update-enhanced.yml/dispatches
```

### Issue: HTTP 204 but no workflow run
**Cause**: Workflow file has `workflow_dispatch` trigger disabled
**Fix**: Verify `.github/workflows/auto-update-enhanced.yml` contains:
```yaml
on:
  schedule:
    - cron: '*/30 * * * *'
  workflow_dispatch:  # ← Must be present
```

### Issue: Execution time exceeds 10 minutes
**Cause**: Google Drive download or calculation timeout
**Fix**:
1. Check GitHub Actions logs for specific failure
2. Increase timeout in workflow file
3. Consider breaking into smaller steps

---

## Security Considerations

1. **PAT Security**:
   - Never commit PAT to git
   - Never share PAT publicly
   - Rotate PAT every 90 days
   - Use minimum required scopes (only `actions`)

2. **Audit Log**:
   - GitHub Settings → Security log → Search "workflow dispatch"
   - Verify all triggers are from cron-job.org IP

3. **Rate Limits**:
   - GitHub API: 5,000 requests/hour (PAT)
   - 30-minute interval = 48 requests/day = well within limit

---

## Cost Analysis

### cron-job.org Free Tier
- Jobs: Up to 50 (we use 1)
- Execution frequency: Every minute minimum (we use 30 minutes)
- Retention: 30 days of logs
- Support: Community forum

### Total Cost: **$0.00 USD/month** ✅

---

## Alternative Solutions Considered

### Option A: GitHub Actions Cron Only ❌
- **Pros**: Built-in, no external dependency
- **Cons**: Unreliable (7-hour delays observed)
- **Status**: Current system, insufficient

### Option B: AWS EventBridge ⚠️
- **Pros**: Highly reliable (99.99% SLA)
- **Cons**: Requires AWS account, overkill for simple cron
- **Cost**: $0.00 (free tier: 1M events/month)

### Option C: cron-job.org ✅ **RECOMMENDED**
- **Pros**: Free, reliable, simple setup, no AWS complexity
- **Cons**: External dependency
- **Status**: Best balance of reliability and simplicity

---

## Maintenance

### Monthly Tasks
- [ ] Verify cron-job.org execution log (check for failures)
- [ ] Review GitHub Actions execution times
- [ ] Update CLAUDE.md if any changes

### Quarterly Tasks
- [ ] Rotate GitHub PAT (if 90-day expiration)
- [ ] Review cron-job.org notification emails
- [ ] Test manual trigger button on selector.html

### Annual Tasks
- [ ] Review external service alternatives
- [ ] Audit GitHub Actions usage costs (should be $0)

---

## Documentation References

- GitHub API Documentation: https://docs.github.com/en/rest/actions/workflows
- cron-job.org Documentation: https://cron-job.org/en/documentation/
- Workflow Dispatch API: https://docs.github.com/en/rest/actions/workflows#create-a-workflow-dispatch-event

---

**Last Updated**: 2025-11-25
**Status**: Solution 2 - Ready for implementation
**Estimated Setup Time**: 15 minutes
