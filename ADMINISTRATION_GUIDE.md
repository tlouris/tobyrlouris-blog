# Technology Innovations Blog - System Administration Guide

**Version:** 1.1
**Last Updated:** February 7, 2026
**System:** Ubuntu 24.04.2 LTS
**Server:** devserver (10.0.0.109)
**Database:** MariaDB 10.11 (MySQL-compatible)

---

## Table of Contents

1. [System Overview](#system-overview)
2. [Container Management](#container-management)
3. [Database Management](#database-management)
4. [Backup and Restore](#backup-and-restore)
5. [Security Management](#security-management)
6. [Monitoring and Health Checks](#monitoring-and-health-checks)
7. [Log Management](#log-management)
8. [System Updates](#system-updates)
9. [Troubleshooting](#troubleshooting)
10. [Emergency Procedures](#emergency-procedures)

---

## System Overview

### Architecture
The blog runs as a containerized application with three main components:

- **Nginx Container** (`tobyrlouris-nginx`) - Web server and reverse proxy
- **FastAPI Container** (`tobyrlouris-backend`) - Python backend API
- **MariaDB Container** (`tobyrlouris-mysql`) - Database server (MariaDB 10.11)

### Database: MariaDB vs MySQL

**Important:** This system uses **MariaDB 10.11**, not MySQL.

**Why MariaDB?**
- During deployment, MySQL 8.0 required CPU instruction set x86-64-v2
- Your server's CPU doesn't support x86-64-v2
- We switched to MariaDB 10.11 for better CPU compatibility
- MariaDB is a drop-in replacement for MySQL (100% compatible)

**What This Means:**
- ✅ All commands use `mysql` client (same as MySQL)
- ✅ All SQL syntax is identical to MySQL
- ✅ Tools like `mysqldump`, `mysqlcheck` work the same
- ✅ Binary compatible - can migrate databases between them
- ✅ Often faster and more efficient than MySQL
- ✅ Actively maintained by original MySQL creators

**In Practice:**
Everything in this guide works exactly as written. When you see "MySQL" in commands or container names, it refers to MariaDB. They're interchangeable for your purposes.

```bash
# Verify database version
sudo docker exec tobyrlouris-mysql mysql --version
# Output: mysql  Ver 15.1 Distrib 10.11.x-MariaDB...
```

### Key Locations
- **Project Directory:** `/opt/tobyrlouris-blog/`
- **Environment File:** `/opt/tobyrlouris-blog/.env` (contains passwords)
- **Backups:** `/var/backups/tobyrlouris-blog/`
- **Logs:** `/var/log/tobyrlouris-blog/`
- **Git Repository:** `/opt/tobyrlouris-blog/.git`

### Important Credentials
```bash
# View credentials (SSH to server)
cat /opt/tobyrlouris-blog/.env
```

**Database Passwords:**
- MariaDB Root: Stored in `.env` as `MYSQL_ROOT_PASSWORD`
- Application User: Stored in `.env` as `MYSQL_PASSWORD`

**Note:** Environment variables use "MYSQL" prefix for compatibility, but the actual database is MariaDB.

---

## Container Management

### Accessing the Server
```bash
# From your local machine
ssh devserver

# Or using IP
ssh ubuntu@10.0.0.109
```

### Viewing Container Status
```bash
# Check all containers
cd /opt/tobyrlouris-blog
sudo docker compose ps

# Detailed container information
sudo docker ps -a

# Check container health
sudo docker inspect tobyrlouris-mysql | grep -A 10 Health
```

### Starting Containers
```bash
# Start all containers
cd /opt/tobyrlouris-blog
sudo docker compose up -d

# Start specific container
sudo docker compose start nginx
sudo docker compose start backend
sudo docker compose start mysql
```

### Stopping Containers
```bash
# Stop all containers (graceful shutdown)
cd /opt/tobyrlouris-blog
sudo docker compose stop

# Stop specific container
sudo docker compose stop backend

# Force stop (use with caution)
sudo docker compose kill backend
```

### Restarting Containers
```bash
# Restart all containers
cd /opt/tobyrlouris-blog
sudo docker compose restart

# Restart specific container
sudo docker compose restart backend
sudo docker compose restart nginx
sudo docker compose restart mysql
```

### Viewing Container Logs
```bash
# View all container logs
cd /opt/tobyrlouris-blog
sudo docker compose logs

# View specific container logs
sudo docker logs tobyrlouris-backend
sudo docker logs tobyrlouris-mysql
sudo docker logs tobyrlouris-nginx

# Follow logs in real-time
sudo docker logs -f tobyrlouris-backend

# View last 100 lines
sudo docker logs --tail 100 tobyrlouris-backend

# View logs with timestamps
sudo docker logs -t tobyrlouris-backend
```

### Rebuilding Containers

**When to rebuild:**
- After code changes
- After updating dependencies
- After configuration changes

```bash
# Rebuild all containers
cd /opt/tobyrlouris-blog
sudo docker compose build

# Rebuild specific container
sudo docker compose build backend

# Rebuild and restart
sudo docker compose up -d --build

# Rebuild without cache (clean build)
sudo docker compose build --no-cache backend
```

### Accessing Container Shell
```bash
# Access backend container shell
sudo docker exec -it tobyrlouris-backend /bin/bash

# Access MySQL container shell
sudo docker exec -it tobyrlouris-mysql /bin/bash

# Access Nginx container shell
sudo docker exec -it tobyrlouris-nginx /bin/sh

# Execute single command in container
sudo docker exec tobyrlouris-backend ls -la /app
```

### Container Resource Usage
```bash
# View resource usage for all containers
sudo docker stats

# View specific container resources
sudo docker stats tobyrlouris-backend

# One-time snapshot
sudo docker stats --no-stream
```

---

## Database Management

**Database System:** MariaDB 10.11 (MySQL-compatible)
**Container Name:** `tobyrlouris-mysql`
**Client Commands:** Uses standard `mysql` command-line tools

All `mysql` commands in this section work with MariaDB. They are fully compatible.

### Accessing the Database

**Method 1: Using docker exec**
```bash
# Access MySQL shell
sudo docker exec -it tobyrlouris-mysql mysql -uroot -p

# Enter password from .env file when prompted
```

**Method 2: Direct command**
```bash
# Get password from .env first
PASSWORD=$(grep MYSQL_ROOT_PASSWORD /opt/tobyrlouris-blog/.env | cut -d'=' -f2)

# Access database
sudo docker exec -it tobyrlouris-mysql mysql -uroot -p"$PASSWORD" visitor_log
```

### Common Database Operations

**View all databases:**
```sql
SHOW DATABASES;
```

**Select the blog database:**
```sql
USE visitor_log;
```

**View all tables:**
```sql
SHOW TABLES;
```

**View table structure:**
```sql
DESCRIBE blog_posts;
DESCRIBE comments;
DESCRIBE contact_submissions;
DESCRIBE newsletter_subscribers;
DESCRIBE visitor_logs;
```

**Count records:**
```sql
SELECT COUNT(*) FROM blog_posts;
SELECT COUNT(*) FROM comments;
SELECT COUNT(*) FROM contact_submissions;
SELECT COUNT(*) FROM newsletter_subscribers;
```

**View recent entries:**
```sql
-- Recent blog posts
SELECT id, title, category, created_at FROM blog_posts ORDER BY created_at DESC LIMIT 10;

-- Recent comments
SELECT id, author, post_id, created_at, approved FROM comments ORDER BY created_at DESC LIMIT 20;

-- Recent contact submissions
SELECT id, name, email, topic, submitted_at FROM contact_submissions ORDER BY submitted_at DESC LIMIT 20;

-- Recent newsletter subscribers
SELECT id, email, subscribed_at, active FROM newsletter_subscribers ORDER BY subscribed_at DESC LIMIT 20;
```

### Database Backup (Manual)
```bash
# Run the automated backup script
sudo /usr/local/bin/backup-all.sh

# Or manual database backup
PASSWORD=$(grep MYSQL_ROOT_PASSWORD /opt/tobyrlouris-blog/.env | cut -d'=' -f2)
sudo docker exec tobyrlouris-mysql mysqldump -uroot -p"$PASSWORD" \
    --all-databases --single-transaction --quick --lock-tables=false \
    > ~/database_backup_$(date +%Y%m%d_%H%M%S).sql

# Compress the backup
gzip ~/database_backup_*.sql
```

### Database Restore
```bash
# Stop the backend to prevent new writes
cd /opt/tobyrlouris-blog
sudo docker compose stop backend

# Restore from backup
PASSWORD=$(grep MYSQL_ROOT_PASSWORD /opt/tobyrlouris-blog/.env | cut -d'=' -f2)
gunzip -c /var/backups/tobyrlouris-blog/database_YYYYMMDD_HHMMSS.sql.gz | \
    sudo docker exec -i tobyrlouris-mysql mysql -uroot -p"$PASSWORD"

# Restart backend
sudo docker compose start backend
```

### Database Maintenance
```bash
# Optimize all tables
PASSWORD=$(grep MYSQL_ROOT_PASSWORD /opt/tobyrlouris-blog/.env | cut -d'=' -f2)
sudo docker exec tobyrlouris-mysql mysqlcheck -uroot -p"$PASSWORD" --optimize --all-databases

# Check table integrity
sudo docker exec tobyrlouris-mysql mysqlcheck -uroot -p"$PASSWORD" --check --all-databases

# Repair tables if needed
sudo docker exec tobyrlouris-mysql mysqlcheck -uroot -p"$PASSWORD" --repair --all-databases
```

---

## Backup and Restore

### Automated Backups

**Backup Schedule:**
- Daily full backup: 2:00 AM
- Weekly full backup: Sundays at 3:00 AM
- Hourly health checks
- Retention: 7 days

**View Backup Cron Jobs:**
```bash
sudo crontab -l
```

**Backup Locations:**
```bash
# View all backups
ls -lh /var/backups/tobyrlouris-blog/

# Recent backups
ls -lht /var/backups/tobyrlouris-blog/ | head -20
```

### Manual Backup

**Full System Backup:**
```bash
# Run the backup script
sudo /usr/local/bin/backup-all.sh

# View backup log output
sudo tail -f /var/log/backup.log  # If script writes to log
```

**Backup Individual Components:**

**Database only:**
```bash
PASSWORD=$(grep MYSQL_ROOT_PASSWORD /opt/tobyrlouris-blog/.env | cut -d'=' -f2)
sudo docker exec tobyrlouris-mysql mysqldump -uroot -p"$PASSWORD" \
    visitor_log > ~/visitor_log_backup_$(date +%Y%m%d).sql
gzip ~/visitor_log_backup_*.sql
```

**Configuration files:**
```bash
cd /opt/tobyrlouris-blog
tar czf ~/config_backup_$(date +%Y%m%d).tar.gz \
    .env docker-compose.yml docker/ README.md
```

**Website files:**
```bash
cd /opt/tobyrlouris-blog
tar czf ~/frontend_backup_$(date +%Y%m%d).tar.gz frontend/
```

**Docker volumes:**
```bash
# Backup MySQL data volume
sudo docker run --rm \
    -v tobyrlouris-blog_mysql_data:/data \
    -v /var/backups/tobyrlouris-blog:/backup \
    alpine tar czf /backup/mysql_volume_$(date +%Y%m%d).tar.gz -C /data .
```

### Restore Procedures

**Restore Database from Backup:**
```bash
# 1. Stop backend to prevent writes
cd /opt/tobyrlouris-blog
sudo docker compose stop backend

# 2. Restore database
PASSWORD=$(grep MYSQL_ROOT_PASSWORD /opt/tobyrlouris-blog/.env | cut -d'=' -f2)
gunzip -c /var/backups/tobyrlouris-blog/database_YYYYMMDD_HHMMSS.sql.gz | \
    sudo docker exec -i tobyrlouris-mysql mysql -uroot -p"$PASSWORD"

# 3. Restart backend
sudo docker compose start backend

# 4. Verify
curl http://localhost/api/health
```

**Restore Configuration:**
```bash
# 1. Stop all containers
cd /opt/tobyrlouris-blog
sudo docker compose down

# 2. Extract backup
cd /opt/tobyrlouris-blog
tar xzf ~/config_backup_YYYYMMDD.tar.gz

# 3. Restart containers
sudo docker compose up -d
```

**Restore Docker Volume:**
```bash
# 1. Stop containers
cd /opt/tobyrlouris-blog
sudo docker compose down

# 2. Remove old volume (CAUTION!)
sudo docker volume rm tobyrlouris-blog_mysql_data

# 3. Restore volume
sudo docker run --rm \
    -v tobyrlouris-blog_mysql_data:/data \
    -v /var/backups/tobyrlouris-blog:/backup \
    alpine sh -c "cd /data && tar xzf /backup/mysql_volume_YYYYMMDD.tar.gz"

# 4. Restart containers
sudo docker compose up -d
```

### Off-Site Backup

**Manual off-site backup:**
```bash
# Copy backups to remote location
rsync -avz /var/backups/tobyrlouris-blog/ \
    user@backup-server:/backups/tobyrlouris-blog/

# Or create archive for download
cd /var/backups
tar czf tobyrlouris-blog-full-backup-$(date +%Y%m%d).tar.gz tobyrlouris-blog/
```

---

## Security Management

### Firewall Management (UFW)

**View firewall status:**
```bash
sudo ufw status verbose
sudo ufw status numbered  # Shows rule numbers
```

**Add firewall rules:**
```bash
# Allow new port
sudo ufw allow 8080/tcp

# Allow from specific IP
sudo ufw allow from 192.168.1.100 to any port 22

# Allow subnet
sudo ufw allow from 192.168.1.0/24
```

**Remove firewall rules:**
```bash
# By rule number
sudo ufw status numbered
sudo ufw delete [number]

# By rule specification
sudo ufw delete allow 8080/tcp
```

**Disable/Enable firewall:**
```bash
# Disable (use with caution!)
sudo ufw disable

# Enable
sudo ufw enable
```

### Fail2Ban Management

**Check Fail2Ban status:**
```bash
# Overall status
sudo systemctl status fail2ban

# Check SSH jail
sudo fail2ban-client status sshd

# View all jails
sudo fail2ban-client status
```

**View banned IPs:**
```bash
# SSH jail
sudo fail2ban-client status sshd

# View all banned IPs across all jails
sudo fail2ban-client banned
```

**Unban an IP:**
```bash
# Unban from SSH jail
sudo fail2ban-client set sshd unbanip 192.168.1.100

# Unban from all jails
sudo fail2ban-client unban 192.168.1.100
```

**View Fail2Ban logs:**
```bash
# Main log
sudo tail -f /var/log/fail2ban.log

# Search for specific IP
sudo grep "192.168.1.100" /var/log/fail2ban.log
```

**Restart Fail2Ban:**
```bash
sudo systemctl restart fail2ban
```

### SSL/TLS Certificates

**Check if certificates are installed:**
```bash
ls -la /etc/letsencrypt/live/tobyrlouris.blog/
```

**Install Let's Encrypt (when DNS is configured):**
```bash
# Install certbot
sudo apt install -y certbot python3-certbot-nginx

# Obtain certificate
sudo certbot --nginx -d tobyrlouris.blog -d www.tobyrlouris.blog

# Test renewal
sudo certbot renew --dry-run
```

**Certificate renewal (automatic):**
```bash
# Check renewal timer
sudo systemctl status certbot.timer

# Manual renewal
sudo certbot renew
```

### Password Management

**Change database passwords:**
```bash
# 1. Access database
PASSWORD=$(grep MYSQL_ROOT_PASSWORD /opt/tobyrlouris-blog/.env | cut -d'=' -f2)
sudo docker exec -it tobyrlouris-mysql mysql -uroot -p"$PASSWORD"

# 2. Change password
ALTER USER 'visitor_log_user'@'%' IDENTIFIED BY 'new_password_here';
FLUSH PRIVILEGES;
EXIT;

# 3. Update .env file
nano /opt/tobyrlouris-blog/.env
# Update MYSQL_PASSWORD=new_password_here

# 4. Rebuild backend container
cd /opt/tobyrlouris-blog
sudo docker compose restart backend
```

### Security Auditing

**Check for rootkits:**
```bash
sudo apt install -y rkhunter
sudo rkhunter --update
sudo rkhunter --check
```

**Check open ports:**
```bash
sudo netstat -tlnp
sudo ss -tlnp
```

**Check active connections:**
```bash
sudo netstat -an | grep ESTABLISHED
```

**Review auth logs:**
```bash
# SSH authentication attempts
sudo grep "Failed password" /var/log/auth.log
sudo grep "Accepted password" /var/log/auth.log

# Recent logins
last
lastlog
```

---

## Monitoring and Health Checks

### Automated Health Checks

**Health check script location:**
```bash
/usr/local/bin/health-check.sh
```

**Run health check manually:**
```bash
sudo /usr/local/bin/health-check.sh

# View results
sudo tail -50 /var/log/tobyrlouris-blog/health-check.log
```

**Health check schedule:**
```bash
# View cron jobs
sudo crontab -l

# Edit schedule
sudo crontab -e
```

### Manual Health Checks

**Check website availability:**
```bash
curl -I http://localhost/
curl http://localhost/api/health
```

**Check container health:**
```bash
cd /opt/tobyrlouris-blog
sudo docker compose ps

# Detailed health status
sudo docker inspect tobyrlouris-mysql --format='{{.State.Health.Status}}'
sudo docker inspect tobyrlouris-backend --format='{{.State.Health.Status}}'
sudo docker inspect tobyrlouris-nginx --format='{{.State.Health.Status}}'
```

**Check disk space:**
```bash
df -h
du -sh /opt/tobyrlouris-blog
du -sh /var/backups/tobyrlouris-blog
sudo docker system df  # Docker disk usage
```

**Check memory usage:**
```bash
free -h
sudo docker stats --no-stream
```

**Check CPU usage:**
```bash
top
htop  # If installed
```

### Performance Monitoring

**Database performance:**
```bash
# Active connections
PASSWORD=$(grep MYSQL_ROOT_PASSWORD /opt/tobyrlouris-blog/.env | cut -d'=' -f2)
sudo docker exec tobyrlouris-mysql mysql -uroot -p"$PASSWORD" -e "SHOW PROCESSLIST;"

# Database size
sudo docker exec tobyrlouris-mysql mysql -uroot -p"$PASSWORD" -e "
SELECT table_schema AS 'Database',
       ROUND(SUM(data_length + index_length) / 1024 / 1024, 2) AS 'Size (MB)'
FROM information_schema.TABLES
GROUP BY table_schema;"
```

**Nginx access statistics:**
```bash
# Top IP addresses
sudo docker exec tobyrlouris-nginx cat /var/log/nginx/access.log | \
    awk '{print $1}' | sort | uniq -c | sort -rn | head -20

# Most accessed pages
sudo docker exec tobyrlouris-nginx cat /var/log/nginx/access.log | \
    awk '{print $7}' | sort | uniq -c | sort -rn | head -20

# Status code distribution
sudo docker exec tobyrlouris-nginx cat /var/log/nginx/access.log | \
    awk '{print $9}' | sort | uniq -c | sort -rn
```

---

## Log Management

### Log Locations

**System logs:**
- `/var/log/tobyrlouris-blog/health-check.log` - Health checks
- Container logs: Via docker logs command

**Access logs:**
```bash
# View Nginx access logs
sudo docker logs tobyrlouris-nginx | grep -v "health"

# View backend access logs
sudo docker logs tobyrlouris-backend | grep "HTTP"
```

### Viewing Logs

**Real-time log monitoring:**
```bash
# Backend logs
sudo docker logs -f tobyrlouris-backend

# Nginx logs
sudo docker logs -f tobyrlouris-nginx

# All logs
cd /opt/tobyrlouris-blog
sudo docker compose logs -f
```

**Search logs:**
```bash
# Search for errors in backend
sudo docker logs tobyrlouris-backend 2>&1 | grep -i error

# Search for specific date
sudo docker logs tobyrlouris-backend | grep "2026-02-06"

# Count errors
sudo docker logs tobyrlouris-backend 2>&1 | grep -i error | wc -l
```

### Log Rotation

**Log rotation configuration:**
```bash
# View configuration
cat /etc/logrotate.d/tobyrlouris-blog

# Test rotation
sudo logrotate -d /etc/logrotate.d/tobyrlouris-blog

# Force rotation
sudo logrotate -f /etc/logrotate.d/tobyrlouris-blog
```

**Clean old Docker logs:**
```bash
# Clear all container logs
sudo sh -c 'truncate -s 0 /var/lib/docker/containers/*/*-json.log'

# Or configure Docker log rotation in /etc/docker/daemon.json
```

---

## System Updates

### Container Updates

**Update Docker images:**
```bash
cd /opt/tobyrlouris-blog

# Pull latest images
sudo docker compose pull

# Rebuild and restart
sudo docker compose up -d --build
```

**Update specific container:**
```bash
# Pull new image
sudo docker pull mariadb:10.11

# Recreate container
cd /opt/tobyrlouris-blog
sudo docker compose up -d --force-recreate mysql
```

### Application Updates

**Update backend code:**
```bash
# 1. Update code files
nano /opt/tobyrlouris-blog/backend/main.py

# 2. Commit changes to git
cd /opt/tobyrlouris-blog
git add backend/
git commit -m "Update backend functionality"

# 3. Rebuild container
sudo docker compose build backend
sudo docker compose up -d backend
```

**Update frontend:**
```bash
# 1. Update files
nano /opt/tobyrlouris-blog/frontend/index.html

# 2. Commit to git
cd /opt/tobyrlouris-blog
git add frontend/
git commit -m "Update frontend design"

# 3. No rebuild needed - Nginx serves static files
# Changes are immediately visible
```

### System Updates

**Update Ubuntu packages:**
```bash
# Update package lists
sudo apt update

# Upgrade packages
sudo apt upgrade -y

# Full upgrade (including kernel)
sudo apt full-upgrade -y

# Remove old packages
sudo apt autoremove -y
sudo apt autoclean
```

**Automatic updates are enabled:**
```bash
# Check status
sudo systemctl status unattended-upgrades

# View update logs
sudo tail -f /var/log/unattended-upgrades/unattended-upgrades.log
```

---

## Troubleshooting

### Container Won't Start

**Diagnosis:**
```bash
# Check container status
cd /opt/tobyrlouris-blog
sudo docker compose ps

# Check logs for errors
sudo docker logs tobyrlouris-backend
sudo docker logs tobyrlouris-mysql

# Check if port is already in use
sudo netstat -tlnp | grep :80
sudo netstat -tlnp | grep :3306

# Check Docker service
sudo systemctl status docker
```

**Solutions:**
```bash
# Restart Docker service
sudo systemctl restart docker

# Remove and recreate containers
cd /opt/tobyrlouris-blog
sudo docker compose down
sudo docker compose up -d

# Clean rebuild
sudo docker compose down
sudo docker compose build --no-cache
sudo docker compose up -d
```

### Database Connection Errors

**Note:** Database is MariaDB 10.11 (commands use `mysql` for compatibility)

**Diagnosis:**
```bash
# Check if MariaDB/MySQL is running
sudo docker ps | grep mysql

# Check database logs
sudo docker logs tobyrlouris-mysql | tail -100

# Test connection
PASSWORD=$(grep MYSQL_ROOT_PASSWORD /opt/tobyrlouris-blog/.env | cut -d'=' -f2)
sudo docker exec tobyrlouris-mysql mysqladmin ping -uroot -p"$PASSWORD"

# Verify database version
sudo docker exec tobyrlouris-mysql mysql --version
```

**Solutions:**
```bash
# Restart MySQL container
cd /opt/tobyrlouris-blog
sudo docker compose restart mysql

# Check environment variables
cat /opt/tobyrlouris-blog/.env

# Rebuild backend with correct connection string
sudo docker compose up -d --force-recreate backend
```

### Website Not Accessible

**Diagnosis:**
```bash
# Check if Nginx is running
sudo docker ps | grep nginx

# Test from server
curl http://localhost/

# Check firewall
sudo ufw status

# Check Nginx logs
sudo docker logs tobyrlouris-nginx | tail -50
```

**Solutions:**
```bash
# Restart Nginx
cd /opt/tobyrlouris-blog
sudo docker compose restart nginx

# Check Nginx configuration
sudo docker exec tobyrlouris-nginx nginx -t

# Ensure firewall allows HTTP
sudo ufw allow 80/tcp
```

### High Resource Usage

**Diagnosis:**
```bash
# Check container resources
sudo docker stats --no-stream

# Check system resources
top
free -h
df -h

# Check database processes
PASSWORD=$(grep MYSQL_ROOT_PASSWORD /opt/tobyrlouris-blog/.env | cut -d'=' -f2)
sudo docker exec tobyrlouris-mysql mysql -uroot -p"$PASSWORD" -e "SHOW PROCESSLIST;"
```

**Solutions:**
```bash
# Restart containers
cd /opt/tobyrlouris-blog
sudo docker compose restart

# Clean Docker system
sudo docker system prune -a

# Optimize database
PASSWORD=$(grep MYSQL_ROOT_PASSWORD /opt/tobyrlouris-blog/.env | cut -d'=' -f2)
sudo docker exec tobyrlouris-mysql mysqlcheck -uroot -p"$PASSWORD" --optimize --all-databases
```

### Slow Performance

**Diagnosis:**
```bash
# Check response times
time curl http://localhost/api/posts

# Check database performance
PASSWORD=$(grep MYSQL_ROOT_PASSWORD /opt/tobyrlouris-blog/.env | cut -d'=' -f2)
sudo docker exec tobyrlouris-mysql mysql -uroot -p"$PASSWORD" -e "SHOW FULL PROCESSLIST;"

# Check logs for slow queries
sudo docker logs tobyrlouris-backend | grep -i "slow"
```

**Solutions:**
```bash
# Add database indexes if needed
# Increase container resources in docker-compose.yml
# Enable caching in Nginx configuration
```

---

## Emergency Procedures

### Complete System Failure

**Step 1: Assess the situation**
```bash
# Check server accessibility
ssh devserver

# Check Docker service
sudo systemctl status docker

# Check containers
sudo docker ps -a
```

**Step 2: Restore from backup**
```bash
# Stop all containers
cd /opt/tobyrlouris-blog
sudo docker compose down

# Restore database
PASSWORD=$(grep MYSQL_ROOT_PASSWORD /opt/tobyrlouris-blog/.env | cut -d'=' -f2)
LATEST_BACKUP=$(ls -t /var/backups/tobyrlouris-blog/database_*.sql.gz | head -1)
gunzip -c "$LATEST_BACKUP" | sudo docker exec -i tobyrlouris-mysql mysql -uroot -p"$PASSWORD"

# Restart containers
sudo docker compose up -d
```

### Data Corruption

**Step 1: Stop services immediately**
```bash
cd /opt/tobyrlouris-blog
sudo docker compose stop backend
```

**Step 2: Backup current state**
```bash
sudo /usr/local/bin/backup-all.sh
```

**Step 3: Restore from known good backup**
```bash
# Follow restore procedures above
```

### Security Breach

**Step 1: Immediate actions**
```bash
# Check for suspicious activity
sudo fail2ban-client status sshd
sudo grep "Failed password" /var/log/auth.log | tail -100
sudo netstat -an | grep ESTABLISHED

# Block suspicious IPs
sudo ufw deny from [suspicious_ip]

# Change passwords immediately
```

**Step 2: Audit system**
```bash
# Check for unauthorized changes
cd /opt/tobyrlouris-blog
git status
git diff

# Check database for suspicious entries
PASSWORD=$(grep MYSQL_ROOT_PASSWORD /opt/tobyrlouris-blog/.env | cut -d'=' -f2)
sudo docker exec -it tobyrlouris-mysql mysql -uroot -p"$PASSWORD" visitor_log
# Run queries to check for SQL injection, etc.
```

**Step 3: Recovery**
```bash
# Restore from backup
# Update all passwords
# Review and tighten security
# Enable additional monitoring
```

### Contact Support

If you need additional assistance:
- Check logs first: `/var/log/tobyrlouris-blog/`
- Document the issue and steps taken
- Collect relevant error messages
- Note the time when the issue occurred

---

## Maintenance Schedule

### Daily
- [x] Automated backup (2:00 AM)
- [x] Automated health checks (hourly)

### Weekly
- [ ] Review logs for errors
- [ ] Check backup integrity
- [ ] Review resource usage
- [x] Weekly backup (Sundays 3:00 AM)

### Monthly
- [ ] System updates
- [ ] Security audit
- [ ] Database optimization
- [ ] Review and clean old backups
- [ ] Test disaster recovery procedures

### Quarterly
- [ ] Full security audit
- [ ] Performance optimization
- [ ] Documentation updates
- [ ] Capacity planning review

---

## Frequently Asked Questions

### Why is the container named "tobyrlouris-mysql" if it's MariaDB?

Container names are just labels. The container name was kept as `mysql` for simplicity and compatibility, but it actually runs MariaDB 10.11 inside.

### Can I use MySQL commands and tools?

Yes! MariaDB is 100% compatible with MySQL. All `mysql`, `mysqldump`, `mysqlcheck`, and other MySQL commands work identically.

### Will MySQL tutorials and guides work?

Absolutely. Any MySQL tutorial, guide, or documentation will work with MariaDB. The SQL syntax and commands are identical.

### What if I want to use MySQL instead?

If your server's CPU supports x86-64-v2 instruction set, you can switch to MySQL 8.0 by:
1. Backup your database
2. Edit `docker-compose.yml` and change `image: mariadb:10.11` to `image: mysql:8.0`
3. Recreate containers: `sudo docker compose up -d --force-recreate mysql`

However, MariaDB works perfectly and is often preferred for its performance and open-source nature.

### How do I check which version is running?

```bash
sudo docker exec tobyrlouris-mysql mysql --version
# Output: mysql  Ver 15.1 Distrib 10.11.x-MariaDB...
```

### Is my data compatible if I migrate to MySQL?

Yes! MariaDB maintains binary compatibility with MySQL. You can migrate databases between them using standard `mysqldump` and restore procedures.

---

## Quick Reference

### Most Common Commands

```bash
# View status
cd /opt/tobyrlouris-blog && sudo docker compose ps

# Restart everything
cd /opt/tobyrlouris-blog && sudo docker compose restart

# View logs
sudo docker logs -f tobyrlouris-backend

# Run backup
sudo /usr/local/bin/backup-all.sh

# Health check
sudo /usr/local/bin/health-check.sh

# Check website
curl http://localhost/api/health
```

### Important File Locations

```
/opt/tobyrlouris-blog/              # Main project directory
/opt/tobyrlouris-blog/.env          # Credentials (KEEP SECURE!)
/var/backups/tobyrlouris-blog/      # Backups
/var/log/tobyrlouris-blog/          # Logs
/usr/local/bin/health-check.sh      # Health check script
/usr/local/bin/backup-all.sh        # Backup script
```

---

**End of Administration Guide**

*For content management (adding blogs, managing comments), see the Content Management Guide.*
