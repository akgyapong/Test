# Shopwice Ecommerce Backend

🛒 **Django REST API for the Shopwice ecommerce platform**

This is a containerized Django backend designed for an ecommerce web application. The project uses Docker for consistent development environments across the team.

## 🚀 Quick Start for Team Members

### Prerequisites
- [Docker](https://docs.docker.com/get-docker/) and [Docker Compose](https://docs.docker.com/compose/install/)
- [Git](https://git-scm.com/downloads)
- Code editor (VS Code recommended)

### Option 1: Full Development Setup (Recommended for Backend Development)

1. **Clone the repository:**
   ```bash
   git clone https://github.com/ArntEech/shopwice-backend.git
   cd shopwice-backend
   ```

2. **Set up environment variables:**
   ```bash
   cp .env.example .env
   ```

3. **Generate your own SECRET_KEY:**
   ```bash
   python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
   ```
   Copy the generated key and replace `SECRET_KEY` in your `.env` file.

4. **Start the application:**
   ```bash
   docker compose up --build
   ```

5. **Access the application:**
   - 🌐 **Backend API:** http://localhost:8000
   - 🔧 **Admin Panel:** http://localhost:8000/admin
   - 🗄️ **Database:** PostgreSQL on port 5432

### Option 2: Quick Start with Published Image (Faster Setup and Testing Only) 

1. **Pull the latest image:**
   ```bash
   docker pull arnatech/shopwice-backend:latest
   ```

2. **Clone repository for source code:**
   ```bash
   git clone https://github.com/ArntEech/shopwice-backend.git
   cd shopwice-backend
   cp .env.example .env
   ```

3. **Edit your `.env` file and run:**
   ```bash
   docker compose -f compose.prod.yaml up
   ```

## 🔄 Development Workflow

### Working on Features

1. **Create feature branch:**
+ First checkout to the Development Branch: `git checkout Development`
+ Then create a feature branch using the command below:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes and test:**
   ```bash
   docker compose up --build
   ```

3. **Run migrations (if you created any):**
   ```bash
   docker compose exec web python manage.py makemigrations
   docker compose exec web python manage.py migrate
   ```

4. **Commit and push:**
   ```bash
   git add .
   git commit -m "Add: your feature description"
   git push origin feature/your-feature-name
   ```

5. **Create Pull Request on GitHub**

### Keeping Your Branch Updated

```bash
# Switch to development and pull latest changes
git checkout development
git pull origin main

# Switch back to your feature branch and merge development
git checkout feature/your-feature-name
git merge Development
```

## 🛠️ Common Development Commands

```bash
# Start services
docker compose up --build

# Run in background
docker compose up -d --build

# Stop services
docker compose down

# View logs
docker compose logs -f web

# Access Django shell
docker compose exec web python manage.py shell

# Run migrations
docker compose exec web python manage.py migrate

# Create superuser
docker compose exec web python manage.py createsuperuser

# Run tests
docker compose exec web python manage.py test

# Collect static files
docker compose exec web python manage.py collectstatic

# Reset database (⚠️ DANGER: Deletes all data)
docker compose down -v
docker compose up --build
```

## 📁 Project Structure

```
shopwice-backend/
├── 🐳 Dockerfile              # Container configuration
├── 🐳 compose.yaml           # Development environment
├── 🐳 compose.prod.yaml      # Production environment
├── ⚙️ requirements.txt        # Python dependencies
├── 🔧 .env.example           # Environment variables template
├── 🚫 .gitignore             # Git ignore rules
├── 📄 README.md              # This file
├── 🐍 manage.py              # Django management script
└── 📁 sw_backend/            # Main Django project
    ├── ⚙️ settings.py        # Django settings
    ├── 🌐 urls.py            # URL routing
    ├── 🚀 wsgi.py            # WSGI application
    └── 🚀 asgi.py            # ASGI application
```

## 🔧 Environment Configuration

Your `.env` file should contain:

```env
# Django Configuration
DEBUG=1
SECRET_KEY=your-generated-secret-key-here
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0

# Database Configuration
POSTGRES_DB=shopwice_db
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your-secure-password
POSTGRES_HOST=db
POSTGRES_PORT=5432
```

## 🏗️ Tech Stack

- **Backend Framework:** Django 5.2.7
- **Database:** PostgreSQL 15
- **Containerization:** Docker & Docker Compose
- **Python Version:** 3.11
- **WSGI Server:** Gunicorn (production)

## 🚨 Troubleshooting

### Common Issues:

1. **Port already in use:**
   ```bash
   docker compose down
   # Wait a few seconds, then try again
   docker compose up --build
   ```

2. **Database connection errors:**
   ```bash
   # Reset the database
   docker compose down -v
   docker compose up --build
   ```

3. **Permission errors on Windows:**
   - Make sure Docker Desktop is running
   - Try running terminal as Administrator

4. **Container won't start:**
   ```bash
   # View detailed logs
   docker compose logs web
   ```

## 🤝 Contributing

1. **Fork** the repository
2. **Create** a feature branch
3. **Make** your changes
4. **Test** thoroughly using Docker
5. **Submit** a Pull Request

### Code Style:
- Follow PEP 8 for Python code
- Use meaningful commit messages
- Write docstrings for functions and classes
- Add tests for new features

## 📞 Team Communication

- 🐛 **Bug Reports:** Create GitHub Issues
- 💡 **Feature Requests:** GitHub Discussions
- 🔄 **Code Reviews:** GitHub Pull Requests
- 💬 **Quick Questions:** Team Slack/Discord

## 🚀 Deployment

The application is containerized and ready for deployment to:
- **Development:** Local Docker
- **Staging:** Docker Hub + Cloud platforms
- **Production:** Kubernetes, AWS ECS, or similar

---

**Happy coding! 🎉**

For questions, contact the development team or check our [GitHub Issues](https://github.com/ArntEech/shopwice-backend/issues).
