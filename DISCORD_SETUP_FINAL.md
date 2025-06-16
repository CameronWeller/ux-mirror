# Discord Integration Setup - Final Steps

## Your Discord Webhook
Your webhook URL is configured and tested:
```
https://discord.com/api/webhooks/1384291487876907129/y6_yUFUsJU0QvvYsJjz25IbAz2gKql96exUSEMTjEGXn6q4arRlulpQ132-E5p-Y5E32
```

## 1. Add Webhook to GitHub Secrets

### Via GitHub CLI (Recommended)
```bash
# Run this command in your repository directory
gh secret set DISCORD_WEBHOOK --body "https://discord.com/api/webhooks/1384291487876907129/y6_yUFUsJU0QvvYsJjz25IbAz2gKql96exUSEMTjEGXn6q4arRlulpQ132-E5p-Y5E32"
```

### Via GitHub Web Interface
1. Go to: https://github.com/CameronWeller/ux-mirror/settings/secrets/actions
2. Click "New repository secret"
3. Name: `DISCORD_WEBHOOK`
4. Value: `https://discord.com/api/webhooks/1384291487876907129/y6_yUFUsJU0QvvYsJjz25IbAz2gKql96exUSEMTjEGXn6q4arRlulpQ132-E5p-Y5E32`
5. Click "Add secret"

## 2. Update Discord Invite Link

Create a permanent invite link:
1. In Discord, right-click on your server name
2. Click "Invite People"
3. Click "Edit invite link"
4. Set to "Never expire"
5. Copy the invite link

Then update your README.md:
```bash
# Replace YOUR_INVITE with your actual Discord invite code
sed -i 's/YOUR_INVITE/YOUR_ACTUAL_CODE/g' README.md
```

## 3. Test the Integration

### Test GitHub Actions
```bash
# Make a small change and push
echo "# Test" >> test.md
git add test.md
git commit -m "Test Discord integration"
git push
```

### Expected Discord Notifications
- 📤 Push notifications when code is pushed
- 📦 Pull request notifications (opened/closed/merged)
- 🐛 Issue notifications (opened/closed)
- 🎉 Release notifications
- ✅/❌ Build status from CI/CD

## 4. Discord Server Quick Setup

If you haven't created the server yet:

1. **Create Server**
   - Click + in Discord
   - "Create My Own"
   - "For a club or community"
   - Server name: "UX Mirror Community"

2. **Quick Channel Setup**
   ```
   Delete default channels, then create:
   - #welcome
   - #announcements (where webhook posts)
   - #general
   - #development
   - #help
   ```

3. **Set Webhook Channel**
   - Right-click #announcements
   - Edit Channel → Integrations
   - Webhooks → Your webhook should appear here

## 5. Community Launch Checklist

- [x] GitHub repository created and pushed
- [x] Discord webhook tested and working
- [ ] Discord server created with channels
- [ ] GitHub secret added (DISCORD_WEBHOOK)
- [ ] Discord invite link updated in README
- [ ] First push to test integration
- [ ] Launch announcement sent

## 6. Next Actions

1. **Commit and Push Current Changes**
   ```bash
   git add .
   git commit -m "Add Discord integration and documentation"
   git push
   ```

2. **Create Discord Server** (if not done)
   - Use the structure from discord-setup.md

3. **Send Launch Announcement**
   ```bash
   python discord-webhook-test.py
   # Choose option 2 for launch announcement
   ```

4. **Start Outreach**
   - Use templates from NEXT_STEPS.md
   - Post on Reddit/HackerNews
   - Reach out to GitHub projects

## Troubleshooting

### Webhook Not Working?
- Check the webhook URL is correct
- Ensure the channel still exists
- Verify webhook hasn't been deleted in Discord

### No GitHub Notifications?
- Check GitHub secret is set correctly
- Verify workflow files are in `.github/workflows/`
- Check Actions tab for any errors

### Need Help?
- Discord webhook docs: https://discord.com/developers/docs/resources/webhook
- GitHub Actions docs: https://docs.github.com/en/actions

---

Your UX Mirror project is ready to launch! 🚀 