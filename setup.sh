#!/bin/bash
# Setup script for CareContinuum

echo "====================================="
echo "CareContinuum Setup"
echo "====================================="

# Check for Docker
if ! command -v docker &> /dev/null; then
    echo "Error: Docker is not installed. Please install Docker first."
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "Error: Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

echo ""
echo "Step 1: Creating environment files..."

# Backend .env
if [ ! -f backend/.env ]; then
    cp backend/.env.example backend/.env
    echo "✓ Created backend/.env from .env.example"
else
    echo "✓ backend/.env already exists"
fi

# Frontend .env
if [ ! -f frontend/.env ]; then
    echo "VITE_API_URL=http://localhost:8000" > frontend/.env
    echo "✓ Created frontend/.env"
else
    echo "✓ frontend/.env already exists"
fi

echo ""
echo "Step 2: Building Docker containers..."
docker-compose build

echo ""
echo "Step 3: Starting services..."
docker-compose up -d postgres redis

echo "Waiting for PostgreSQL to be ready..."
sleep 5

echo ""
echo "Step 4: Running database migrations..."
docker-compose run --rm backend alembic upgrade head

echo ""
echo "Step 5: Seeding database with sample data..."
docker-compose run --rm backend python -m app.services.seed_data

echo ""
echo "Step 6: Starting all services..."
docker-compose up -d

echo ""
echo "====================================="
echo "✓ Setup Complete!"
echo "====================================="
echo ""
echo "Services are now running:"
echo "  - Frontend: http://localhost:5173"
echo "  - Backend API: http://localhost:8000"
echo "  - API Docs: http://localhost:8000/docs"
echo ""
echo "Test credentials:"
echo "  Admin: admin@carecontinuum.com / admin123"
echo "  Doctor: dr.smith@carecontinuum.com / doctor123"
echo "  Staff: staff1@carecontinuum.com / staff123"
echo ""
echo "To view logs:"
echo "  docker-compose logs -f"
echo ""
echo "To stop services:"
echo "  docker-compose down"
echo ""
