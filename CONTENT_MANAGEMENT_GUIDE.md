# Technology Innovations Blog - Content Management Guide

**Version:** 1.1
**Last Updated:** February 7, 2026
**Website:** http://tobyrlouris.blog (or http://10.0.0.109)
**Database:** MariaDB 10.11 (MySQL-compatible)

---

## Table of Contents

1. [Getting Started](#getting-started)
2. [Managing Blog Posts](#managing-blog-posts)
3. [Managing Comments](#managing-comments)
4. [Contact Form Submissions](#contact-form-submissions)
5. [Newsletter Management](#newsletter-management)
6. [Content Workflow](#content-workflow)
7. [SEO and Optimization](#seo-and-optimization)
8. [Frequently Asked Questions](#frequently-asked-questions)
9. [Quick Reference](#quick-reference)

---

## Getting Started

### About the Database

**Database System:** MariaDB 10.11 (MySQL-compatible)
**Container Name:** `tobyrlouris-mysql`
**Important:** All commands in this guide use `mysql` commands - they work perfectly with MariaDB!

**Why MariaDB instead of MySQL?**
- Your server's CPU doesn't support MySQL 8.0's x86-64-v2 instruction set
- MariaDB is a drop-in replacement - 100% MySQL compatible
- All `mysql` commands, SQL syntax, and tools work identically
- You can follow any MySQL tutorial or guide without issues

**Key Points:**
- ✅ Container named "mysql" but runs MariaDB inside
- ✅ All `mysql` client commands work the same
- ✅ All SQL queries are identical
- ✅ No learning curve - if you know MySQL, you know this

### Accessing the System

**SSH to Server:**
```bash
ssh devserver
# Or: ssh ubuntu@10.0.0.109
```

**Database Access:**
```bash
# Get the database password
PASSWORD=$(grep MYSQL_ROOT_PASSWORD /opt/tobyrlouris-blog/.env | cut -d'=' -f2)

# Access database (uses mysql client, works with MariaDB)
sudo docker exec -it tobyrlouris-mysql mysql -uroot -p"$PASSWORD" visitor_log
```

**Verify Database Version:**
```bash
# Check that you're running MariaDB
sudo docker exec tobyrlouris-mysql mysql --version
# Output: mysql  Ver 15.1 Distrib 10.11.x-MariaDB...

# Or from inside the MySQL prompt:
# SELECT VERSION();
```

### Understanding the Database

**Main Tables:**
- `blog_posts` - All blog articles
- `comments` - User comments (requires approval)
- `contact_submissions` - Contact form messages
- `newsletter_subscribers` - Email subscribers
- `visitor_logs` - Website traffic data

**Quick Table Overview:**
```sql
-- Once connected to database
SHOW TABLES;
DESCRIBE blog_posts;
DESCRIBE comments;
DESCRIBE contact_submissions;
DESCRIBE newsletter_subscribers;
```

---

## Managing Blog Posts

### Viewing All Blog Posts

**Method 1: Via API**
```bash
# View all posts
curl http://localhost/api/posts | python3 -m json.tool

# View recent posts
curl http://localhost/api/posts?limit=10 | python3 -m json.tool

# View posts by category
curl "http://localhost/api/posts?category=Digital Strategy" | python3 -m json.tool
```

**Method 2: Via Database**
```sql
-- Access database first with the command above
USE visitor_log;

-- View all posts
SELECT id, title, category, featured, published, created_at
FROM blog_posts
ORDER BY created_at DESC;

-- View post counts by category
SELECT category, COUNT(*) as count
FROM blog_posts
WHERE published = TRUE
GROUP BY category;

-- View featured posts
SELECT id, title, category
FROM blog_posts
WHERE featured = TRUE;
```

### Adding a New Blog Post

**Step 1: Prepare Your Content**

Before adding to database, prepare:
- **Title** - Clear, descriptive (max 500 chars)
- **Slug** - URL-friendly version (e.g., "my-article-title")
- **Excerpt** - Short summary (150-200 chars)
- **Content** - Full article in HTML
- **Category** - One of:
  - Digital Strategy
  - Cybersecurity & Resilience
  - Project Lessons
  - Industry Trends & Regulation
- **Reading Time** - Estimated (e.g., "8 min read")

**Step 2: Add to Database**

```bash
# Access database
PASSWORD=$(grep MYSQL_ROOT_PASSWORD /opt/tobyrlouris-blog/.env | cut -d'=' -f2)
sudo docker exec -it tobyrlouris-mysql mysql -uroot -p"$PASSWORD" visitor_log
```

```sql
-- Insert new blog post
INSERT INTO blog_posts (
    slug,
    title,
    excerpt,
    content,
    category,
    author,
    featured,
    published,
    reading_time,
    created_at
) VALUES (
    'my-new-article',
    'My New Article Title',
    'This is a compelling summary of my article that will appear in the post list.',
    '<h2>Introduction</h2><p>Your full article content goes here in HTML format.</p><h2>Main Points</h2><p>More content...</p>',
    'Digital Strategy',
    'Toby R. Louris',
    FALSE,
    TRUE,
    '7 min read',
    NOW()
);

-- Verify it was added
SELECT id, title, slug FROM blog_posts ORDER BY id DESC LIMIT 1;
```

**Step 3: Verify on Website**

```bash
# Check API
curl http://localhost/api/posts | python3 -m json.tool | grep -A5 "my-new-article"

# Visit website
# http://tobyrlouris.blog/blogs.html
```

### Complete Blog Post Example

```sql
INSERT INTO blog_posts (
    slug,
    title,
    excerpt,
    content,
    category,
    author,
    featured,
    published,
    reading_time,
    image_url,
    created_at
) VALUES (
    'implementing-predictive-maintenance-wastewater',
    'Implementing Predictive Maintenance in Wastewater Operations',
    'Learn how predictive maintenance strategies can reduce downtime, extend equipment life, and optimize operations in wastewater treatment facilities.',
    '<p>Predictive maintenance represents a paradigm shift from reactive and preventive maintenance approaches. By leveraging data analytics and IoT sensors, utilities can anticipate equipment failures before they occur.</p>

<h2>The Business Case</h2>
<p>Traditional maintenance approaches cost wastewater utilities millions annually in unexpected downtime and emergency repairs. Predictive maintenance offers a smarter path forward.</p>

<div class="key-takeaways">
<h4>Key Takeaways</h4>
<ul>
<li>Predictive maintenance can reduce maintenance costs by 25-30%</li>
<li>Equipment uptime can improve by 10-20%</li>
<li>ROI typically achieved within 12-18 months</li>
<li>Start with critical assets for quick wins</li>
</ul>
</div>

<h2>Implementation Strategy</h2>
<p>Successful implementation requires a phased approach:</p>

<h3>1. Asset Prioritization</h3>
<p>Identify critical equipment where failures have the highest impact. Pumps, blowers, and motor control centers are typically good candidates.</p>

<h3>2. Sensor Deployment</h3>
<p>Install vibration, temperature, and performance sensors on priority assets. Modern wireless sensors minimize installation complexity.</p>

<h3>3. Data Infrastructure</h3>
<p>Ensure reliable data collection and storage. Cloud platforms offer scalable solutions for data aggregation and analysis.</p>

<h3>4. Analytics Development</h3>
<p>Start with simple threshold alerts, then progress to machine learning models as data accumulates.</p>

<h2>Lessons Learned</h2>
<p>From recent implementations, several lessons stand out:</p>

<blockquote>
"The technology is only part of the solution. Organizational change management and staff training are equally critical to success."
</blockquote>

<p>Engage maintenance staff early. Their domain expertise is invaluable for interpreting data patterns and validating predictions.</p>

<h2>Conclusion</h2>
<p>Predictive maintenance is no longer experimental—it is becoming a standard practice in modern wastewater operations. The question is not whether to implement, but how quickly you can realize the benefits.</p>',
    'Digital Strategy',
    'Toby R. Louris',
    TRUE,
    TRUE,
    '9 min read',
    NULL,
    '2025-02-06 10:00:00'
);
```

### Editing an Existing Blog Post

```sql
-- Find the post
SELECT id, title, slug FROM blog_posts WHERE slug LIKE '%search-term%';

-- Update specific fields
UPDATE blog_posts
SET
    title = 'Updated Title',
    content = '<p>Updated content...</p>',
    updated_at = NOW()
WHERE id = 123;

-- Update just the excerpt
UPDATE blog_posts
SET excerpt = 'New compelling excerpt'
WHERE slug = 'article-slug';

-- Publish a draft
UPDATE blog_posts
SET published = TRUE
WHERE id = 123;

-- Feature a post
UPDATE blog_posts
SET featured = TRUE
WHERE id = 123;

-- Un-feature all other posts (only one should be featured)
UPDATE blog_posts
SET featured = FALSE
WHERE id != 123;
```

### Deleting a Blog Post

```sql
-- Soft delete (unpublish)
UPDATE blog_posts
SET published = FALSE
WHERE id = 123;

-- Hard delete (permanent - use with caution!)
DELETE FROM blog_posts WHERE id = 123;

-- Delete post and related comments
DELETE FROM comments WHERE post_id = '123';
DELETE FROM blog_posts WHERE id = 123;
```

### Managing Featured Posts

```sql
-- View current featured post
SELECT id, title, slug FROM blog_posts WHERE featured = TRUE;

-- Set new featured post (and un-feature others)
-- First, un-feature all
UPDATE blog_posts SET featured = FALSE;

-- Then feature the new one
UPDATE blog_posts SET featured = TRUE WHERE id = 123;

-- Verify
SELECT id, title, featured FROM blog_posts WHERE featured = TRUE;
```

### Bulk Operations

**Import multiple posts:**
```sql
-- Create a file with multiple INSERT statements
-- blog_posts_import.sql

INSERT INTO blog_posts (slug, title, excerpt, content, category, author, published, reading_time, created_at) VALUES
('post-1', 'Title 1', 'Excerpt 1', '<p>Content 1</p>', 'Digital Strategy', 'Toby R. Louris', TRUE, '5 min read', '2025-02-01'),
('post-2', 'Title 2', 'Excerpt 2', '<p>Content 2</p>', 'Cybersecurity & Resilience', 'Toby R. Louris', TRUE, '6 min read', '2025-02-02'),
('post-3', 'Title 3', 'Excerpt 3', '<p>Content 3</p>', 'Project Lessons', 'Toby R. Louris', TRUE, '7 min read', '2025-02-03');
```

```bash
# Import the file
PASSWORD=$(grep MYSQL_ROOT_PASSWORD /opt/tobyrlouris-blog/.env | cut -d'=' -f2)
sudo docker exec -i tobyrlouris-mysql mysql -uroot -p"$PASSWORD" visitor_log < blog_posts_import.sql
```

**Update all posts in category:**
```sql
UPDATE blog_posts
SET author = 'Toby R. Louris'
WHERE category = 'Digital Strategy';
```

---

## Managing Comments

### Viewing Comments

**View all comments:**
```sql
SELECT
    id,
    post_id,
    author,
    email,
    LEFT(content, 50) as content_preview,
    approved,
    created_at
FROM comments
ORDER BY created_at DESC
LIMIT 50;
```

**View pending comments (need approval):**
```sql
SELECT
    c.id,
    c.author,
    c.email,
    LEFT(c.content, 100) as comment,
    b.title as post_title,
    c.created_at
FROM comments c
LEFT JOIN blog_posts b ON c.post_id = b.id
WHERE c.approved = FALSE
ORDER BY c.created_at DESC;
```

**View approved comments:**
```sql
SELECT
    c.id,
    c.author,
    b.title as post_title,
    c.created_at
FROM comments c
LEFT JOIN blog_posts b ON c.post_id = b.id
WHERE c.approved = TRUE
ORDER BY c.created_at DESC
LIMIT 20;
```

**Comments by post:**
```sql
SELECT
    id,
    author,
    LEFT(content, 100) as comment,
    approved,
    created_at
FROM comments
WHERE post_id = '123'
ORDER BY created_at DESC;
```

### Approving Comments

**Approve a single comment:**
```sql
-- View the comment first
SELECT id, author, content FROM comments WHERE id = 456;

-- Approve it
UPDATE comments
SET approved = TRUE
WHERE id = 456;
```

**Approve multiple comments:**
```sql
-- Approve all comments from today
UPDATE comments
SET approved = TRUE
WHERE DATE(created_at) = CURDATE()
AND approved = FALSE;

-- Approve comments from specific author
UPDATE comments
SET approved = TRUE
WHERE author = 'John Doe'
AND approved = FALSE;
```

**Bulk approve (careful!):**
```sql
-- Review first
SELECT id, author, email, LEFT(content, 50)
FROM comments
WHERE approved = FALSE;

-- Then approve
UPDATE comments SET approved = TRUE WHERE approved = FALSE;
```

### Deleting Comments

**Delete spam comments:**
```sql
-- Delete specific comment
DELETE FROM comments WHERE id = 456;

-- Delete all comments from an email
DELETE FROM comments WHERE email = 'spam@example.com';

-- Delete unapproved comments older than 30 days
DELETE FROM comments
WHERE approved = FALSE
AND created_at < DATE_SUB(NOW(), INTERVAL 30 DAY);
```

### Comment Statistics

```sql
-- Total comments
SELECT COUNT(*) as total_comments FROM comments;

-- Approved vs pending
SELECT
    approved,
    COUNT(*) as count
FROM comments
GROUP BY approved;

-- Comments by post
SELECT
    b.title,
    COUNT(c.id) as comment_count
FROM blog_posts b
LEFT JOIN comments c ON b.id = c.post_id AND c.approved = TRUE
GROUP BY b.id, b.title
ORDER BY comment_count DESC;

-- Recent comment activity
SELECT
    DATE(created_at) as date,
    COUNT(*) as comments
FROM comments
WHERE created_at > DATE_SUB(NOW(), INTERVAL 30 DAY)
GROUP BY DATE(created_at)
ORDER BY date DESC;
```

---

## Contact Form Submissions

### Viewing Contact Submissions

**View all submissions:**
```sql
SELECT
    id,
    name,
    email,
    organization,
    topic,
    LEFT(message, 50) as message_preview,
    submitted_at
FROM contact_submissions
ORDER BY submitted_at DESC
LIMIT 50;
```

**View by topic:**
```sql
SELECT
    id,
    name,
    email,
    topic,
    submitted_at
FROM contact_submissions
WHERE topic = 'speaking'
ORDER BY submitted_at DESC;
```

**View recent submissions:**
```sql
SELECT
    name,
    email,
    topic,
    submitted_at
FROM contact_submissions
WHERE submitted_at > DATE_SUB(NOW(), INTERVAL 7 DAY)
ORDER BY submitted_at DESC;
```

### Reading Full Submissions

```sql
-- Get full details of a submission
SELECT
    id,
    name,
    email,
    organization,
    topic,
    message,
    submitted_at
FROM contact_submissions
WHERE id = 123;
```

### Exporting Contact Submissions

**Export to CSV:**
```bash
PASSWORD=$(grep MYSQL_ROOT_PASSWORD /opt/tobyrlouris-blog/.env | cut -d'=' -f2)

# Export all submissions
sudo docker exec tobyrlouris-mysql mysql -uroot -p"$PASSWORD" visitor_log -e "
SELECT
    id,
    name,
    email,
    organization,
    topic,
    message,
    submitted_at
FROM contact_submissions
ORDER BY submitted_at DESC
" > ~/contact_submissions_$(date +%Y%m%d).csv

# Or export specific date range
sudo docker exec tobyrlouris-mysql mysql -uroot -p"$PASSWORD" visitor_log -e "
SELECT * FROM contact_submissions
WHERE submitted_at BETWEEN '2025-01-01' AND '2025-12-31'
" > ~/contact_submissions_2025.csv
```

### Email Notifications

**Get email addresses for follow-up:**
```sql
-- Get all emails that need response
SELECT
    email,
    name,
    topic,
    submitted_at
FROM contact_submissions
WHERE submitted_at > DATE_SUB(NOW(), INTERVAL 7 DAY)
ORDER BY submitted_at DESC;
```

**Set up email forwarding (future enhancement):**
```
Note: Currently, contact submissions are stored in the database only.
To receive email notifications, you can:
1. Set up a cron job to check for new submissions
2. Configure email forwarding in the FastAPI application
3. Use a monitoring service to alert on new submissions
```

### Contact Form Statistics

```sql
-- Total submissions
SELECT COUNT(*) as total FROM contact_submissions;

-- Submissions by topic
SELECT
    topic,
    COUNT(*) as count
FROM contact_submissions
GROUP BY topic
ORDER BY count DESC;

-- Submissions by month
SELECT
    DATE_FORMAT(submitted_at, '%Y-%m') as month,
    COUNT(*) as submissions
FROM contact_submissions
GROUP BY DATE_FORMAT(submitted_at, '%Y-%m')
ORDER BY month DESC;

-- Average submissions per day
SELECT
    AVG(daily_count) as avg_per_day
FROM (
    SELECT DATE(submitted_at) as date, COUNT(*) as daily_count
    FROM contact_submissions
    GROUP BY DATE(submitted_at)
) as daily_stats;
```

### Cleaning Up Old Submissions

```sql
-- Archive old submissions (older than 1 year)
-- First, export them
-- Then delete
DELETE FROM contact_submissions
WHERE submitted_at < DATE_SUB(NOW(), INTERVAL 1 YEAR);
```

---

## Newsletter Management

### Viewing Subscribers

**View all active subscribers:**
```sql
SELECT
    id,
    email,
    subscribed_at,
    active
FROM newsletter_subscribers
WHERE active = TRUE
ORDER BY subscribed_at DESC;
```

**View recent subscriptions:**
```sql
SELECT
    email,
    subscribed_at
FROM newsletter_subscribers
WHERE subscribed_at > DATE_SUB(NOW(), INTERVAL 30 DAY)
AND active = TRUE
ORDER BY subscribed_at DESC;
```

**View inactive/unsubscribed:**
```sql
SELECT
    email,
    subscribed_at
FROM newsletter_subscribers
WHERE active = FALSE
ORDER BY subscribed_at DESC;
```

### Exporting Subscriber List

**Export all active subscribers:**
```bash
PASSWORD=$(grep MYSQL_ROOT_PASSWORD /opt/tobyrlouris-blog/.env | cut -d'=' -f2)

# Export to CSV
sudo docker exec tobyrlouris-mysql mysql -uroot -p"$PASSWORD" visitor_log -e "
SELECT email, subscribed_at
FROM newsletter_subscribers
WHERE active = TRUE
ORDER BY subscribed_at DESC
" > ~/newsletter_subscribers_$(date +%Y%m%d).csv
```

**Export for email marketing tools:**
```sql
-- Mailchimp/SendGrid format
SELECT
    email as 'Email Address',
    'Toby' as 'First Name',
    'Reader' as 'Last Name',
    DATE_FORMAT(subscribed_at, '%Y-%m-%d') as 'Subscribed Date'
FROM newsletter_subscribers
WHERE active = TRUE;
```

### Managing Subscriptions

**Manually add subscriber:**
```sql
INSERT INTO newsletter_subscribers (email, subscribed_at, active)
VALUES ('newsubscriber@example.com', NOW(), TRUE);
```

**Unsubscribe a user:**
```sql
UPDATE newsletter_subscribers
SET active = FALSE
WHERE email = 'user@example.com';
```

**Reactivate subscription:**
```sql
UPDATE newsletter_subscribers
SET active = TRUE
WHERE email = 'user@example.com';
```

**Delete subscriber (permanent):**
```sql
-- Use with caution - prefer setting active=FALSE
DELETE FROM newsletter_subscribers
WHERE email = 'user@example.com';
```

### Subscriber Statistics

```sql
-- Total subscribers
SELECT
    COUNT(*) as total,
    SUM(CASE WHEN active = TRUE THEN 1 ELSE 0 END) as active,
    SUM(CASE WHEN active = FALSE THEN 1 ELSE 0 END) as inactive
FROM newsletter_subscribers;

-- Growth over time
SELECT
    DATE_FORMAT(subscribed_at, '%Y-%m') as month,
    COUNT(*) as new_subscribers
FROM newsletter_subscribers
GROUP BY DATE_FORMAT(subscribed_at, '%Y-%m')
ORDER BY month DESC;

-- Subscriptions by day (last 30 days)
SELECT
    DATE(subscribed_at) as date,
    COUNT(*) as signups
FROM newsletter_subscribers
WHERE subscribed_at > DATE_SUB(NOW(), INTERVAL 30 DAY)
GROUP BY DATE(subscribed_at)
ORDER BY date DESC;
```

### Removing Duplicates

```sql
-- Find duplicate emails
SELECT email, COUNT(*) as count
FROM newsletter_subscribers
GROUP BY email
HAVING count > 1;

-- Keep only the most recent subscription
DELETE n1 FROM newsletter_subscribers n1
INNER JOIN newsletter_subscribers n2
WHERE n1.id < n2.id AND n1.email = n2.email;
```

### GDPR Compliance

**Export user data (GDPR request):**
```sql
-- Get all data for a specific email
SELECT
    'Newsletter' as source,
    email,
    subscribed_at,
    active
FROM newsletter_subscribers
WHERE email = 'user@example.com'

UNION ALL

SELECT
    'Comments' as source,
    email,
    created_at,
    approved
FROM comments
WHERE email = 'user@example.com'

UNION ALL

SELECT
    'Contact' as source,
    email,
    submitted_at,
    NULL
FROM contact_submissions
WHERE email = 'user@example.com';
```

**Delete all user data (GDPR right to be forgotten):**
```sql
-- Delete from all tables
DELETE FROM newsletter_subscribers WHERE email = 'user@example.com';
DELETE FROM comments WHERE email = 'user@example.com';
DELETE FROM contact_submissions WHERE email = 'user@example.com';
```

---

## Content Workflow

### Standard Publishing Workflow

**1. Draft Creation**
```sql
-- Create draft (published = FALSE)
INSERT INTO blog_posts (
    slug, title, excerpt, content,
    category, author, published, reading_time
) VALUES (
    'draft-article',
    'Draft Article Title',
    'Summary...',
    '<p>Content...</p>',
    'Digital Strategy',
    'Toby R. Louris',
    FALSE,  -- Draft
    '5 min read'
);
```

**2. Review and Edit**
```sql
-- View drafts
SELECT id, title, created_at
FROM blog_posts
WHERE published = FALSE;

-- Edit draft
UPDATE blog_posts
SET content = '<p>Updated content...</p>',
    updated_at = NOW()
WHERE id = 123;
```

**3. Publish**
```sql
-- Publish the post
UPDATE blog_posts
SET published = TRUE,
    created_at = NOW()  -- Set publish date
WHERE id = 123;
```

**4. Promote (if needed)**
```sql
-- Feature the post
UPDATE blog_posts SET featured = FALSE;  -- Un-feature others
UPDATE blog_posts SET featured = TRUE WHERE id = 123;
```

### Content Calendar

**View upcoming posts:**
```sql
SELECT
    id,
    title,
    category,
    published,
    created_at as publish_date
FROM blog_posts
WHERE created_at > NOW()
ORDER BY created_at ASC;
```

**Schedule post for future:**
```sql
-- Insert with future date
INSERT INTO blog_posts (
    slug, title, excerpt, content,
    category, author, published, reading_time, created_at
) VALUES (
    'future-post',
    'Future Post Title',
    'Summary...',
    '<p>Content...</p>',
    'Digital Strategy',
    'Toby R. Louris',
    TRUE,
    '5 min read',
    '2025-03-01 10:00:00'  -- Future date
);
```

**Note:** The API filters by `published = TRUE`, but doesn't filter by date. You may want to add date filtering to the API or keep posts as drafts until publish date.

### Quality Checklist

Before publishing, verify:
- [ ] Title is clear and compelling
- [ ] Slug is URL-friendly (lowercase, hyphens, no special chars)
- [ ] Excerpt is concise and engaging (150-200 chars)
- [ ] Content is properly formatted HTML
- [ ] Category is correct
- [ ] Reading time is accurate
- [ ] Author name is correct
- [ ] Images have proper alt text (if using images)
- [ ] Links work correctly
- [ ] Content is proofread

---

## SEO and Optimization

### SEO Best Practices

**Title Optimization:**
```sql
-- Check title lengths (should be under 60 chars for SEO)
SELECT
    id,
    title,
    LENGTH(title) as title_length
FROM blog_posts
WHERE LENGTH(title) > 60;
```

**Excerpt Optimization:**
```sql
-- Check excerpt lengths (should be 150-160 chars)
SELECT
    id,
    title,
    LENGTH(excerpt) as excerpt_length
FROM blog_posts
WHERE LENGTH(excerpt) > 160 OR LENGTH(excerpt) < 120;
```

**Slug Optimization:**
```sql
-- Check for SEO-friendly slugs
SELECT id, title, slug
FROM blog_posts
WHERE slug LIKE '% %'  -- Contains spaces (should use hyphens)
OR slug LIKE '%_%'     -- Contains underscores
OR slug REGEXP '[A-Z]'; -- Contains uppercase
```

### Content Performance

**Most viewed categories:**
```sql
-- This requires visitor logging enhancements
-- For now, count posts by category
SELECT
    category,
    COUNT(*) as post_count
FROM blog_posts
WHERE published = TRUE
GROUP BY category
ORDER BY post_count DESC;
```

**Engagement metrics:**
```sql
-- Posts with most comments
SELECT
    b.title,
    COUNT(c.id) as comment_count
FROM blog_posts b
LEFT JOIN comments c ON b.id = c.post_id AND c.approved = TRUE
GROUP BY b.id, b.title
ORDER BY comment_count DESC
LIMIT 10;
```

---

## Frequently Asked Questions

### Why does the guide say "MySQL" but the database is MariaDB?

MariaDB is a fork of MySQL and is 100% compatible. All MySQL commands, tools, and SQL syntax work identically with MariaDB. The container is even named `tobyrlouris-mysql` for compatibility, though it runs MariaDB inside.

### Can I use MySQL tutorials and guides?

Absolutely! Any MySQL tutorial, documentation, or guide will work perfectly with MariaDB. The SQL syntax and commands are identical.

### Will my MySQL tools work with MariaDB?

Yes! Tools like MySQL Workbench, phpMyAdmin, DBeaver, and any other MySQL client tools work seamlessly with MariaDB.

### How do I check which version I'm running?

```bash
sudo docker exec tobyrlouris-mysql mysql --version
# Output: mysql  Ver 15.1 Distrib 10.11.x-MariaDB...
```

Or from inside the database:
```sql
SELECT VERSION();
```

### Can I migrate my data to MySQL if I want?

Yes! MariaDB maintains binary compatibility with MySQL. You can export with `mysqldump` and import into MySQL without any changes to your data or SQL.

### Why is it named "MySQL" in commands if it's MariaDB?

For compatibility and ease of use. The `mysql` command-line client works with both MySQL and MariaDB. It's like how "xerox" became a verb - the name stuck even though there are alternatives.

---

## Quick Reference

### Common SQL Commands

```sql
-- View recent blog posts
SELECT id, title, category, created_at
FROM blog_posts
ORDER BY created_at DESC LIMIT 10;

-- View pending comments
SELECT id, author, LEFT(content, 50), post_id
FROM comments
WHERE approved = FALSE;

-- View contact submissions
SELECT id, name, email, topic, submitted_at
FROM contact_submissions
ORDER BY submitted_at DESC LIMIT 20;

-- View newsletter subscribers
SELECT id, email, subscribed_at
FROM newsletter_subscribers
WHERE active = TRUE
ORDER BY subscribed_at DESC;

-- Approve a comment
UPDATE comments SET approved = TRUE WHERE id = 123;

-- Publish a draft
UPDATE blog_posts SET published = TRUE WHERE id = 123;

-- Feature a post
UPDATE blog_posts SET featured = FALSE;
UPDATE blog_posts SET featured = TRUE WHERE id = 123;
```

### Database Connection

```bash
# Quick database access (MariaDB, uses mysql client)
PASSWORD=$(grep MYSQL_ROOT_PASSWORD /opt/tobyrlouris-blog/.env | cut -d'=' -f2)
sudo docker exec -it tobyrlouris-mysql mysql -uroot -p"$PASSWORD" visitor_log

# Verify database version
sudo docker exec tobyrlouris-mysql mysql --version
```

### Export Commands

```bash
# Note: Database is MariaDB 10.11, uses mysql commands for compatibility

# Export blog posts
sudo docker exec tobyrlouris-mysql mysql -uroot -p"$PASSWORD" visitor_log \
    -e "SELECT * FROM blog_posts" > blog_posts_backup.csv

# Export contact submissions
sudo docker exec tobyrlouris-mysql mysql -uroot -p"$PASSWORD" visitor_log \
    -e "SELECT * FROM contact_submissions ORDER BY submitted_at DESC" > contacts.csv

# Export newsletter subscribers
sudo docker exec tobyrlouris-mysql mysql -uroot -p"$PASSWORD" visitor_log \
    -e "SELECT email FROM newsletter_subscribers WHERE active = TRUE" > subscribers.csv
```

### Quick Tasks

**Add a blog post:**
1. SSH to server: `ssh devserver`
2. Access database with password from `.env`
3. Run INSERT statement with your content
4. Verify: `curl http://localhost/api/posts | python3 -m json.tool`

**Approve comments:**
1. SSH to server
2. Access database
3. Run: `SELECT * FROM comments WHERE approved = FALSE;`
4. Run: `UPDATE comments SET approved = TRUE WHERE id = X;`

**Export email list:**
1. SSH to server
2. Run export command (see above)
3. Download file: `scp devserver:~/subscribers.csv .`

---

## Getting Help

### Troubleshooting Content Issues

**Post not showing up:**
```sql
-- Check if post exists
SELECT id, title, published FROM blog_posts WHERE slug = 'your-slug';

-- Ensure it's published
UPDATE blog_posts SET published = TRUE WHERE slug = 'your-slug';

-- Check via API
curl http://localhost/api/posts | python3 -m json.tool | grep "your-slug"
```

**Comments not appearing:**
```sql
-- Check if comment exists
SELECT * FROM comments WHERE post_id = '123';

-- Check approval status
SELECT id, author, approved FROM comments WHERE post_id = '123';

-- Approve if needed
UPDATE comments SET approved = TRUE WHERE post_id = '123';
```

### Common Mistakes

1. **Forgetting to set published = TRUE**
   - Posts won't appear if published is FALSE

2. **Wrong category name**
   - Must match exactly: Digital Strategy, Cybersecurity & Resilience, Project Lessons, Industry Trends & Regulation

3. **Missing author field**
   - Always set author = 'Toby R. Louris'

4. **Invalid HTML in content**
   - Test HTML before inserting

5. **Duplicate slugs**
   - Each slug must be unique

### Support Resources

- **Administration Guide:** ~/ADMINISTRATION_GUIDE.md
- **Project README:** /opt/tobyrlouris-blog/README.md
- **Logs:** /var/log/tobyrlouris-blog/
- **Backups:** /var/backups/tobyrlouris-blog/

---

## Appendix: HTML Templates

### Blog Post Content Template

```html
<p>Opening paragraph that hooks the reader and introduces the topic.</p>

<h2>Introduction</h2>
<p>Provide context and background for your article.</p>

<div class="key-takeaways">
<h4>Key Takeaways</h4>
<ul>
<li>First important point</li>
<li>Second important point</li>
<li>Third important point</li>
</ul>
</div>

<h2>Main Section 1</h2>
<p>Your main content here.</p>

<h3>Subsection 1.1</h3>
<p>More detailed information.</p>

<blockquote>
"A relevant quote that emphasizes your point."
</blockquote>

<h2>Main Section 2</h2>
<p>Continue your discussion.</p>

<h2>Conclusion</h2>
<p>Summarize your main points and provide takeaways for readers.</p>
```

### Common HTML Elements

```html
<!-- Paragraph -->
<p>Regular paragraph text.</p>

<!-- Headings -->
<h2>Main Section</h2>
<h3>Subsection</h3>

<!-- Bold -->
<strong>Important text</strong>

<!-- Italic -->
<em>Emphasized text</em>

<!-- List -->
<ul>
<li>First item</li>
<li>Second item</li>
</ul>

<!-- Numbered list -->
<ol>
<li>First step</li>
<li>Second step</li>
</ol>

<!-- Quote -->
<blockquote>
"Quote text here"
</blockquote>

<!-- Key takeaways box -->
<div class="key-takeaways">
<h4>Key Takeaways</h4>
<ul>
<li>Point one</li>
<li>Point two</li>
</ul>
</div>

<!-- Link -->
<a href="/post.html?id=123">Link text</a>
```

---

**End of Content Management Guide**

*For system administration tasks, see the Administration Guide.*
