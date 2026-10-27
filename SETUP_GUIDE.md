# CareContinuum Setup Guide

This guide will help you set up and run CareContinuum locally.

## Prerequisites

- **Docker Desktop** (recommended) or:
  - Python 3.11+
  - Node.js 18+
  - PostgreSQL 15+

## Quick Start with Docker (Recommended)

### Windows

1. Open Command Prompt or PowerShell as Administrator
2. Navigate to the project directory
3. Run the setup script:
   ```cmd
   setup.bat
   ```

### Linux/Mac

1. Open Terminal
2. Navigate to the project directory
3. Make setup script executable and run:
   ```bash
   chmod +x setup.sh
   ./setup.sh
   ```

The setup script will:
- Create environment configuration files
- Build Docker containers
- Start PostgreSQL and Redis
- Run database migrations
- Seed sample data
- Start all services

## Manual Setup (Without Docker)

### Backend Setup

1. **Create Python virtual environment:**
   ```bash
   cd backend
   python -m venv venv
   
   # Windows
   venv\Scripts\activate
   
   # Linux/Mac
   source venv/bin/activate
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables:**
   ```bash
   cp .env.example .env
   ```
   
   Edit `.env` with your database credentials:
   ```
   DATABASE_URL=postgresql://user:password@localhost:5432/carecontinuum
   SECRET_KEY=your-secret-key-here
   ```

4. **Create database:**
   ```bash
   createdb carecontinuum
   ```

5. **Run migrations:**
   ```bash
   alembic upgrade head
   ```

6. **Seed sample data:**
   ```bash
   python -m app.services.seed_data
   ```

7. **Start backend server:**
   ```bash
   uvicorn app.main:app --reload
   ```

### Frontend Setup

1. **Install dependencies:**
   ```bash
   cd frontend
   npm install
   ```

2. **Create environment file:**
   ```bash
   echo "VITE_API_URL=http://localhost:8000" > .env
   ```

3. **Start development server:**
   ```bash
   npm run dev
   ```

## Accessing the Application

- **Frontend:** http://localhost:5173
- **Backend API:** http://localhost:8000
- **API Documentation:** http://localhost:8000/docs
- **Alternative API Docs:** http://localhost:8000/redoc

## Test Credentials

```
Admin:
  Email: admin@carecontinuum.com
  Password: admin123

Doctor:
  Email: dr.smith@carecontinuum.com
  Password: doctor123

Staff:
  Email: staff1@carecontinuum.com
  Password: staff123
```

## Verifying Installation

1. **Check backend health:**
   ```bash
   curl http://localhost:8000/health
   ```
   Should return: `{"status":"healthy"}`

2. **Login test:**
   - Navigate to http://localhost:5173
   - Login with test credentials
   - You should see the dashboard with sample data

3. **Check background scheduler:**
   - Backend logs should show: "Scheduler started with 4 jobs"

## Common Issues

### Port Already in Use

If ports 5173, 8000, 5432, or 6379 are already in use:

**Docker:**
Edit `docker-compose.yml` to change port mappings

**Manual setup:**
- Frontend: Change port in `vite.config.ts`
- Backend: Use `uvicorn app.main:app --port 8001`

### Database Connection Failed

**Check PostgreSQL is running:**
```bash
# Docker
docker-compose ps postgres

# Manual
psql -U postgres -c "SELECT version();"
```

**Verify connection string in `.env` matches your database setup**

### Frontend Can't Connect to Backend

1. Check backend is running: http://localhost:8000/health
2. Verify `VITE_API_URL` in `frontend/.env`
3. Check browser console for CORS errors

### Database Migrations Failed

Reset database and retry:
```bash
# Docker
docker-compose down -v
docker-compose up -d postgres
docker-compose run --rm backend alembic upgrade head

# Manual
dropdb carecontinuum
createdb carecontinuum
alembic upgrade head
```

## Development Workflow

### Running Tests

**Backend:**
```bash
cd backend
pytest
```

**Frontend:**
```bash
cd frontend
npm test
```

### Viewing Logs

**Docker:**
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f frontend
```

**Manual:**
Check terminal windows where services are running

### Stopping Services

**Docker:**
```bash
docker-compose down
```

**Manual:**
Press `Ctrl+C` in each terminal window

### Database Management

**Access PostgreSQL:**
```bash
# Docker
docker-compose exec postgres psql -U carecontinuum

# Manual
psql -U your_user -d carecontinuum
```

**Create new migration:**
```bash
cd backend
alembic revision --autogenerate -m "description"
alembic upgrade head
```

**Reset database:**
```bash
# Docker
docker-compose down -v
./setup.sh  # or setup.bat

# Manual
dropdb carecontinuum
createdb carecontinuum
alembic upgrade head
python -m app.services.seed_data
```

## Production Deployment

### Environment Variables

Update these for production in `.env`:

```bash
# Use strong random secret
SECRET_KEY=<generate-with-openssl-rand-hex-32>

# Use production database
DATABASE_URL=postgresql://user:pass@prod-host:5432/carecontinuum

# Set environment
ENVIRONMENT=production

# Configure email/SMS
SMTP_HOST=smtp.sendgrid.net
SMTP_USER=apikey
SMTP_PASSWORD=<your-sendgrid-key>
SMS_PROVIDER=twilio
SMS_API_KEY=<your-twilio-key>
```

### Security Checklist

- [ ] Change all default passwords
- [ ] Use strong SECRET_KEY
- [ ] Enable HTTPS
- [ ] Set proper CORS origins
- [ ] Use environment variables for secrets
- [ ] Enable database backups
- [ ] Set up monitoring and logging
- [ ] Review and apply security headers
- [ ] Implement rate limiting
- [ ] Regular security updates

### Build for Production

**Backend:**
```bash
cd backend
gunicorn app.main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

**Frontend:**
```bash
cd frontend
npm run build
# Serve dist/ directory with nginx or similar
```

## Support

For issues or questions:
1. Check logs for error messages
2. Review this guide's Common Issues section
3. Verify all prerequisites are installed
4. Ensure environment variables are set correctly

## Next Steps

After successful setup:
1. Explore the dashboard and sample data
2. Review the API documentation
3. Test the complete workflow from the acceptance criteria
4. Customize configuration for your use case
