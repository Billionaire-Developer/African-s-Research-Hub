# African Research Hub - Backend

Flask-based REST API for the African Research Hub platform, supporting abstract submission, review, payment integration, and user management.

---

## Table of Contents
- [Setup](#setup)
- [Development](#development)
- [Production Deployment](#production-deployment)
- [Configuration](#configuration)
- [API Documentation](#api-documentation)

---

## Setup

### Prerequisites
- Python 3.8+
- PostgreSQL (for production) or SQLite (for development)
- Virtual environment tool (venv or uv)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd backend
   ```

2. **Create virtual environment**
   ```bash
   # Using venv
   python -m venv .venv
   
   # Or using uv (recommended)
   uv venv
   ```

3. **Activate virtual environment**
   ```bash
   # Linux/Mac
   source .venv/bin/activate
   
   # Windows (Command Prompt)
   .venv\Scripts\activate.bat
   
   # Windows (PowerShell)
   .venv\Scripts\Activate.ps1
   
   # Windows (Git Bash)
   source .venv/Scripts/activate
   ```

4. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   # Or with uv: uv pip install -r requirements.txt
   ```

5. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your settings
   ```

---

## Development

### Running Locally

1. **Set development environment**
   ```bash
   export FLASK_CONFIG=development  # Linux/Mac
   set FLASK_CONFIG=development     # Windows CMD
   $env:FLASK_CONFIG="development"  # Windows PowerShell
   ```

2. **Initialize database**
   ```bash
   flask db upgrade
   # Or run with automatic table creation:
   python run.py
   ```

3. **Start the development server**
   ```bash
   python run.py
   ```

   The API will be available at `http://localhost:5000`

### Development Features
- **Auto-reload**: Code changes trigger automatic restart
- **Debug mode**: Detailed error pages
- **SQLite database**: No external database required
- **CORS enabled**: Works with local frontend (localhost:3000)

### Running Database Migrations

```bash
# Create a new migration
flask db migrate -m "Description of changes"

# Apply migrations
flask db upgrade

# Rollback migration
flask db downgrade
```

---

## Production Deployment

### Environment Configuration

1. **Create production `.env` file**
   ```bash
   cp .env.example .env
   ```

2. **Set required variables**
   ```env
   FLASK_CONFIG=production
   SECRET_KEY=<generate-strong-random-key>
   DATABASE_URL=postgresql+psycopg2://user:password@localhost/dbname
   JWT_SECRET_KEY=<generate-strong-random-key>
   
   # Email settings
   MAIL_SERVER=smtp.example.com
   MAIL_PORT=587
   MAIL_USERNAME=noreply@yourdomain.com
   MAIL_PASSWORD=<your-password>
   
   # Payment gateway
   PAYCHANGU_SECRET=<your-paychangu-secret>
   
   # URLs
   WEBSITE_URL=https://yourdomain.com
   FRONTEND_URL=https://yourdomain.com
   ```

### VPS Deployment (Full Guide)

For detailed step-by-step deployment instructions, see **[deployment_guide.md](deployment_guide.md)**.

#### Quick Deployment Steps

1. **Server Setup**
   ```bash
   sudo apt update && sudo apt upgrade -y
   sudo apt install python3-pip python3-venv nginx postgresql -y
   ```

2. **Database Setup**
   ```bash
   sudo -u postgres psql
   CREATE DATABASE arh_db;
   CREATE USER arh_user WITH PASSWORD 'secure_password';
   GRANT ALL PRIVILEGES ON DATABASE arh_db TO arh_user;
   \q
   ```

3. **Application Setup**
   ```bash
   cd /var/www/arh_backend/backend
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

4. **Systemd Service**
   ```bash
   sudo cp arh_backend.service /etc/systemd/system/
   sudo systemctl start arh_backend
   sudo systemctl enable arh_backend
   ```

5. **Nginx Configuration**
   ```bash
   sudo cp nginx.conf /etc/nginx/sites-available/arh_backend
   sudo ln -s /etc/nginx/sites-available/arh_backend /etc/nginx/sites-enabled/
   sudo systemctl restart nginx
   ```

6. **SSL Certificate**
   ```bash
   sudo apt install certbot python3-certbot-nginx
   sudo certbot --nginx -d yourdomain.com
   ```

---

## Configuration

### Environment Variables

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `FLASK_CONFIG` | Environment mode (`development`/`production`) | Yes | `development` |
| `SECRET_KEY` | Flask secret key | Yes | - |
| `DATABASE_URL` | Database connection string | Yes | SQLite (dev) |
| `JWT_SECRET_KEY` | JWT signing key | No | Uses `SECRET_KEY` |
| `MAIL_SERVER` | SMTP server | Yes | - |
| `MAIL_USERNAME` | SMTP username | Yes | - |
| `MAIL_PASSWORD` | SMTP password | Yes | - |
| `PAYCHANGU_SECRET` | PayChangu API secret | Yes | - |
| `WEBSITE_URL` | Backend URL | Yes | - |
| `FRONTEND_URL` | Frontend URL | Yes | - |

### Configuration Classes

- **`DevelopmentConfig`**: SQLite, DEBUG=True, relaxed security
- **`ProductionConfig`**: PostgreSQL required, DEBUG=False, strict security

---

## API Documentation

### Base URL
- **Development**: `http://localhost:5000/api`
- **Production**: `https://yourdomain.com/api`

### Key Endpoints

#### Authentication
- `POST /api/register` - User registration
- `POST /api/login` - User login
- `POST /api/logout` - User logout

#### Abstracts
- `GET /api/abstracts` - List published abstracts (paginated)
- `POST /api/submit` - Submit new abstract
- `GET /api/abstracts/<id>` - Get specific abstract
- `GET /api/abstracts/search` - Search abstracts

#### Payments
- `POST /api/payments/initiate` - Initiate payment
- `POST /api/payments/confirm` - Confirm payment

#### Admin
- `GET /api/admin` - Admin dashboard
- `POST /api/admin/review/<id>` - Review abstract

See full API documentation at `/api/docs` (when enabled).

---

## Project Structure

```
backend/
├── app/
│   ├── __init__.py           # Application factory
│   ├── config.py             # Configuration classes
│   ├── extensions.py         # Flask extensions
│   ├── routes.py             # API endpoints (Blueprint)
│   ├── models.py             # Database models
│   ├── utilities.py          # Decorators & helpers
│   ├── email_service.py      # Email functions
│   └── utils/
│       ├── email.py          # Email utilities
│       └── tokens.py         # Token management
├── migrations/               # Database migrations
├── uploads/                  # File uploads
├── run.py                    # Application entry point
├── requirements.txt          # Python dependencies
├── .env.example              # Environment template
├── arh_backend.service       # Systemd service file
└── README.md                 # This file
```

---

## Performance & Security Features

- **Rate Limiting**: Prevents API abuse
- **Pagination**: Efficient data loading
- **Query Optimization**: N+1 queries eliminated
- **Session Security**: HttpOnly, Secure cookies
- **CORS Protection**: Configured origins
- **Password Hashing**: Werkzeug security

---

## Troubleshooting

### Common Issues

**ImportError after installing packages**
```bash
# Deactivate and reactivate virtual environment
deactivate
source .venv/bin/activate
```

**Database connection failed**
```bash
# Check DATABASE_URL format
postgresql+psycopg2://username:password@localhost/database_name
```

**PowerShell activation failed**
```powershell
Set-ExecutionPolicy RemoteSigned
```

---

## Contributors

[Donald Banda](https://github.com/donalddbanda)
[NAZBROTECH](https://github.com/NAZBROTECH)
