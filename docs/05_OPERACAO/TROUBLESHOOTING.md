# 🔧 Troubleshooting Guide - IgnisBot

**Last Updated:** 2025-11-07

---

## Common Issues

### Bot Not Responding

**Symptoms:**
- Commands don't respond
- Bot appears offline
- No error messages

**Solutions:**
1. Check if bot is running: `python ignis_main.py`
2. Check logs: `logs/ignisbot.log`
3. Verify Discord token in `.env`
4. Check bot permissions in Discord server
5. Use `/health` command to check system status

---

### Database Connection Errors

**Symptoms:**
- `RuntimeError: DB pool not initialized`
- `Connection refused` errors
- Timeout errors

**Solutions:**
1. Verify database credentials in `.env`:
   ```
   DB_HOST=localhost
   DB_USER=ignis_user
   DB_PASSWORD=your_password
   DB_NAME=ignis
   ```
2. Check if MySQL is running
3. Verify database exists: `CREATE DATABASE ignis;`
4. Check firewall settings
5. Verify connection pool settings:
   ```
   DB_POOL_MIN=2
   DB_POOL_MAX=10
   ```

---

### Cache Issues

**Symptoms:**
- Stale data displayed
- Cache hit rate very low
- Memory usage high

**Solutions:**
1. Clear cache: Use `/cache_stats` command
2. Check cache TTL: Default is 30 seconds
3. Monitor cache stats: `utils/cache.get_cache_stats()`
4. Disable cache warming if memory is an issue

---

### Command Sync Issues

**Symptoms:**
- Commands not appearing in Discord
- "Command not found" errors
- Commands take long to sync

**Solutions:**
1. Wait 1-2 minutes after bot restart (global sync delay)
2. Check bot permissions: `applications.commands` scope required
3. Verify guild ID in `.env`
4. Check logs for sync errors
5. Manually sync: Use `/sync` command (if available)

---

### Integration Errors (Bloxlink/Roblox)

**Symptoms:**
- "User not found" errors
- API timeout errors
- Circuit breaker open

**Solutions:**
1. Check Bloxlink API key in `.env`
2. Verify user is verified with Bloxlink
3. Check circuit breaker status: Use `/health` command
4. Wait for circuit breaker recovery (60 seconds default)
5. Check Roblox API status

---

### Permission Errors

**Symptoms:**
- "You cannot use this command here"
- "Missing permissions" errors

**Solutions:**
1. Check channel restrictions:
   - `/add`, `/remove`, `/vc_log`, `/induction` → Staff channel only
   - `/userinfo` → Userinfo channel only
2. Verify user has required permissions:
   - Admin commands require `manage_messages` or `administrator`
3. Check command channel ID in `.env`

---

### Performance Issues

**Symptoms:**
- Slow command responses
- High database load
- Memory usage high

**Solutions:**
1. Check cache hit rate: Use `/cache_stats`
2. Optimize database: Run `scripts/optimize_database.py`
3. Increase connection pool: `DB_POOL_MAX=20`
4. Monitor with `/health` command
5. Check for slow queries in logs

---

## Debug Commands

### `/health`
Check bot health and system status.

### `/cache_stats`
View cache statistics and performance.

### `/help`
View all available commands and channel restrictions.

---

## Log Analysis

### Check Recent Errors
```bash
grep -i error logs/ignisbot.log | tail -20
```

### Check Cache Issues
```bash
grep -i cache logs/ignisbot.log | tail -20
```

### Check Database Issues
```bash
grep -i "database\|db\|mysql" logs/ignisbot.log | tail -20
```

---

## Getting Help

1. Check logs: `logs/ignisbot.log`
2. Use `/health` command
3. Review this troubleshooting guide
4. Check GitHub issues
5. Contact support

---

**For more information, see the main README.md**

