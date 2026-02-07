# Technology Innovations for the Water Industry Blog

Professional blog focused on digital strategy, cybersecurity, and technology innovation in the wastewater industry.

## Architecture

### Containerized Services
- **Nginx**: Web server for static files and reverse proxy
- **FastAPI**: Python backend API
- **MySQL 8.0**: Database for visitor logs, comments, contact forms, and blog posts

### Directory Structure
```
tobyrlouris-blog/
├── frontend/           # Static website files
│   ├── css/           # Stylesheets
│   ├── js/            # JavaScript
│   ├── images/        # Images and assets
│   └── *.html         # HTML pages
├── backend/           # FastAPI application
│   ├── main.py        # Main application
│   ├── requirements.txt
│   └── Dockerfile
├── docker/            # Docker configurations
│   ├── nginx/         # Nginx configs
│   └── mysql/         # MySQL init scripts
├── docker-compose.yml # Container orchestration
└── .env               # Environment variables (not in git)
```

## Deployment

### Prerequisites
- Docker and Docker Compose installed
- Domain configured (for production)

### Quick Start

1. **Clone and navigate to project:**
   ```bash
   cd /opt/tobyrlouris-blog
   ```

2. **Start all services:**
   ```bash
   docker-compose up -d
   ```

3. **View logs:**
   ```bash
   docker-compose logs -f
   ```

4. **Check status:**
   ```bash
   docker-compose ps
   ```

5. **Access the website:**
   - Website: http://tobyrlouris.blog (or http://localhost)
   - API Health: http://tobyrlouris.blog/api/health

### Management Commands

**Stop all services:**
```bash
docker-compose down
```

**Restart a specific service:**
```bash
docker-compose restart backend
```

**View database logs:**
```bash
docker-compose logs -f mysql
```

**Access MySQL database:**
```bash
docker-compose exec mysql mysql -u visitor_log_user -p visitor_log
```

**Backup database:**
```bash
docker-compose exec mysql mysqldump -u root -p visitor_log > backup_$(date +%Y%m%d).sql
```

### Environment Variables

Copy `.env.example` to `.env` and update with secure passwords:

```bash
cp backend/.env.example .env
# Edit .env with your passwords
```

## API Endpoints

- `GET /api/health` - Health check
- `POST /api/visitor-log` - Log visitor
- `POST /api/contact` - Submit contact form
- `POST /api/comments` - Submit comment
- `GET /api/comments?post_id={id}` - Get comments
- `POST /api/newsletter` - Subscribe to newsletter
- `GET /api/posts` - Get all posts
- `GET /api/posts/featured` - Get featured post
- `GET /api/posts/{slug}` - Get specific post

## Security Notes

- `.env` file contains sensitive credentials - never commit to git
- MySQL root password is randomly generated
- All containers run on isolated network
- Nginx serves as reverse proxy for API
- Database backups recommended daily

## Maintenance

### Update Application
```bash
docker-compose down
docker-compose pull
docker-compose up -d --build
```

### View Container Resource Usage
```bash
docker stats
```

### Clean Up Unused Resources
```bash
docker system prune -a
```

## Support

For issues or questions, contact the administrator.

## License

© 2025 Technology Innovations for the Water Industry. All rights reserved.
