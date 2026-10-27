# CareContinuum - Quick Start Guide

Get CareContinuum running in under 5 minutes.

## Prerequisites

- Docker Desktop installed and running

## Installation

### Windows

1. Open Command Prompt
2. Navigate to project directory:
   ```cmd
   cd path\to\carecontinuum
   ```
3. Run setup:
   ```cmd
   setup.bat
   ```

### macOS/Linux

1. Open Terminal
2. Navigate to project directory:
   ```bash
   cd path/to/carecontinuum
   ```
3. Run setup:
   ```bash
   chmod +x setup.sh
   ./setup.sh
   ```

## Access the Application

Open your browser and go to: **http://localhost:5173**

## Login Credentials

**Admin Panel:**
- Email: `admin@carecontinuum.com`
- Password: `admin123`

**Doctor Interface:**
- Email: `dr.smith@carecontinuum.com`
- Password: `doctor123`

**Staff Interface:**
- Email: `staff1@carecontinuum.com`
- Password: `staff123`

## What's Included

The setup script automatically:
- ✓ Configures environment variables
- ✓ Builds Docker containers
- ✓ Sets up PostgreSQL database
- ✓ Runs database migrations
- ✓ Seeds 50 synthetic patients
- ✓ Creates sample follow-up plans
- ✓ Generates test appointments
- ✓ Starts all services

## Key Features to Explore

### 1. Dashboard
- View key metrics at a glance
- See upcoming appointments
- Check priority tasks

### 2. Patients
- Browse patient list (50 pre-loaded)
- View patient timelines
- See consultation history

### 3. Priority Worklist (Staff)
- Explainable task prioritization
- Clear next actions
- Overdue and escalated cases

### 4. Analytics (Admin/Doctor)
- Follow-up completion rates
- Missed appointment tracking
- Staff workload distribution

## Common Commands

**View logs:**
```bash
docker-compose logs -f
```

**Stop services:**
```bash
docker-compose down
```

**Restart services:**
```bash
docker-compose restart
```

**Access database:**
```bash
docker-compose exec postgres psql -U carecontinuum
```

## Testing the Workflow

Follow **WORKFLOW_DEMO.md** for a complete step-by-step demonstration of all features.

## Need Help?

- **Detailed Setup**: See SETUP_GUIDE.md
- **Complete Documentation**: See PROJECT_SUMMARY.md
- **API Documentation**: http://localhost:8000/docs
- **Workflow Demo**: See WORKFLOW_DEMO.md

## Troubleshooting

**Services won't start:**
```bash
docker-compose down -v
./setup.sh  # or setup.bat on Windows
```

**Can't connect to backend:**
- Check backend is running: http://localhost:8000/health
- Should return: `{"status":"healthy"}`

**Login not working:**
- Ensure database was seeded properly
- Check backend logs: `docker-compose logs backend`

## Next Steps

1. ✓ Login with test credentials
2. ✓ Explore the dashboard
3. ✓ Browse patient records
4. ✓ Check the priority worklist
5. ✓ View analytics
6. ✓ Follow WORKFLOW_DEMO.md for complete tour
