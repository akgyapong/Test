# Shopwice Backend Deployment Guide

## Prerequisites
- Python 3.9+
- PostgreSQL database (local) or hosting platform database
- Git repository access
- Environment variables configured

## Environment Variables Setup

### Development Environment
1. Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```

2. Configure your local development variables in `.env`:
```bash
ENVIRONMENT=development
DEBUG=1
SECRET_KEY=your-local-secret-key
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0

# Use your local PostgreSQL settings
POSTGRES_DB=shopwice_db
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your-local-password
POSTGRES_HOST=db  # or localhost if not using Docker
POSTGRES_PORT=5432
```

### Production Environment
Set these environment variables on your hosting platform:

**Required for all platforms:**
```bash
ENVIRONMENT=production
DEBUG=0
SECRET_KEY=your-super-secure-random-secret-key-50-chars-minimum
DJANGO_ALLOWED_HOSTS=your-domain.com,www.your-domain.com
```

**Database (most platforms auto-provide DATABASE_URL):**
```bash
DATABASE_URL=postgresql://user:password@host:port/database  # Auto-provided by hosting
```

**Optional (based on your features):**
```bash
# Cloudinary for image uploads
USE_CLOUDINARY=1
CLOUDINARY_CLOUD_NAME=your-cloudinary-name
CLOUDINARY_API_KEY=your-cloudinary-key
CLOUDINARY_API_SECRET=your-cloudinary-secret

# Email configuration
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=1
EMAIL_HOST_USER=your-email@domain.com
EMAIL_HOST_PASSWORD=your-app-password

# Social authentication
GOOGLE_OAUTH2_CLIENT_ID=your-google-client-id
GOOGLE_OAUTH2_CLIENT_SECRET=your-google-secret
FACEBOOK_APP_ID=your-facebook-app-id
FACEBOOK_APP_SECRET=your-facebook-secret
```

## Local Development Setup

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Setup Database
```bash
# Using Docker (recommended)
docker-compose up -d db

# Or install PostgreSQL locally and create database
createdb shopwice_db
```

### 3. Run Migrations
```bash
python manage.py migrate
```

### 4. Create Superuser
```bash
python manage.py createsuperuser
```

### 5. Collect Static Files
```bash
python manage.py collectstatic --noinput
```

### 6. Start Development Server
```bash
python manage.py runserver
```

## Production Deployment

### Pre-deployment Checklist
- [ ] All environment variables are set correctly
- [ ] `ENVIRONMENT=production` is set
- [ ] `DEBUG=0` is set
- [ ] `SECRET_KEY` is a strong, unique value
- [ ] `DJANGO_ALLOWED_HOSTS` includes your domain
- [ ] Database is provisioned and `DATABASE_URL` is available
- [ ] Static files storage is configured

### Platform-Specific Instructions

#### Heroku
1. **Create Heroku app:**
```bash
heroku create your-app-name
```

2. **Add PostgreSQL database:**
```bash
heroku addons:create heroku-postgresql:mini
```

3. **Set environment variables:**
```bash
heroku config:set ENVIRONMENT=production
heroku config:set DEBUG=0
heroku config:set SECRET_KEY=your-secret-key
heroku config:set DJANGO_ALLOWED_HOSTS=your-app-name.herokuapp.com
```

4. **Deploy:**
```bash
git push heroku main
```

5. **Run migrations:**
```bash
heroku run python manage.py migrate
heroku run python manage.py collectstatic --noinput
heroku run python manage.py createsuperuser
```

#### DigitalOcean App Platform
1. Connect your GitHub repository
2. Create a managed PostgreSQL database
3. Set environment variables in the App settings panel
4. Configure build and run commands:
   - Build: `pip install -r requirements.txt`
   - Run: `python manage.py migrate && python manage.py collectstatic --noinput && gunicorn sw_backend.wsgi:application`

#### Railway
1. Connect your GitHub repository
2. Add PostgreSQL service
3. Set environment variables in Railway dashboard
4. Deploy automatically triggers on git push

#### AWS Elastic Beanstalk
1. Install EB CLI: `pip install awsebcli`
2. Initialize: `eb init`
3. Create environment: `eb create production`
4. Set environment variables in AWS console
5. Deploy: `eb deploy`

## Post-Deployment Verification

### 1. Test Application Health
```bash
# Check if app is running
curl https://your-domain.com

# Test admin panel (should have proper CSS styling)
curl https://your-domain.com/admin/

# Test API endpoints
curl https://your-domain.com/api/
```

### 2. Check Logs
```bash
# Heroku
heroku logs --tail

# DigitalOcean
# Check logs in App Platform dashboard

# Railway
# Check logs in Railway dashboard
```

### 3. Verification Checklist
- [ ] Application starts without errors
- [ ] Admin panel loads with proper styling (CSS working)
- [ ] API endpoints respond correctly
- [ ] Database connections work
- [ ] Static files are served properly
- [ ] Environment variables are loaded correctly
- [ ] Logs are being generated
- [ ] Security headers are present (in production)

## Common Issues & Solutions

### Static Files Not Loading
- Ensure `python manage.py collectstatic` was run
- Check `STATIC_ROOT` and `STATICFILES_STORAGE` settings
- Verify WhiteNoise is in middleware

### Database Connection Issues
- Verify `DATABASE_URL` is set correctly
- Check database credentials and network access
- Ensure PostgreSQL dependencies are installed

### Environment Variables Not Working
- Double-check variable names (case-sensitive)
- Ensure `.env` file is not committed to git
- Verify hosting platform environment variables are set

### CORS Issues
- Add your frontend domain to `CORS_ALLOWED_ORIGINS`
- Check that `corsheaders.middleware.CorsMiddleware` is first in middleware

## Security Notes

- Never commit `.env` files to git
- Use strong, unique `SECRET_KEY` for production
- Always set `DEBUG=0` in production
- Use HTTPS in production (most platforms provide this automatically)
- Regularly update dependencies: `pip list --outdated`

## Scaling Considerations

- Use managed databases for production
- Consider CDN for static files if serving globally
- Monitor application performance and database queries
- Set up proper backup strategies for your database

## Support & Troubleshooting

If you encounter issues:
1. Check application logs first
2. Verify all environment variables are set
3. Test locally with `ENVIRONMENT=production` to simulate production settings
4. Check hosting platform documentation for specific requirements